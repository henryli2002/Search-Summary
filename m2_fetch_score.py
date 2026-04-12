"""
模块 2：文献获取与沙盒漏斗 (Fetch & Score Funnel)
──────────────────────────────────────────────────
输入：关键词组、Config 参数
处理：
  1. 遍历关键词组调用 S2AG API 搜索（支持领域过滤）
  2. 聚合去重
  3. 引用数过滤（支持豁免年份）
  4. 双池选拔：新论文池 + 经典论文池（去马太效应）
  5. 对数平滑双维加权排序
输出：按得分降序的 Top N 篇 PaperData 列表
"""

from __future__ import annotations

import math
import logging
import time

import httpx
from tenacity import (
    retry, stop_after_attempt, wait_random_exponential,
    retry_if_exception_type,
)

from config import CONFIG
from schemas import PaperData

logger = logging.getLogger(__name__)


# S2AG 免费 API 速率限制：100 req / 5min (无 key)，1 req/sec (有 key)
_S2AG_COOLDOWN = 3.0  # 关键词之间的冷却延迟（秒）


class _RateLimitError(Exception):
    """429 特殊处理：需要更长的退避时间。"""
    pass


@retry(
    wait=wait_random_exponential(multiplier=3, max=60),
    stop=stop_after_attempt(6),
    retry=retry_if_exception_type(_RateLimitError),
    reraise=True,
)
def _search_s2ag(keyword: str, *, http_client: httpx.Client) -> list[dict]:
    """调用 Semantic Scholar Academic Graph API 搜索单个关键词。

    429 会被转换为 _RateLimitError 触发更长的退避重试。
    其他 HTTP 错误直接忽略带空结果返回。
    """
    url = f"{CONFIG['s2ag']['base_url']}/paper/search"
    params = {
        "query": keyword,
        "limit": CONFIG["search"]["fetch_limit"],
        "fields": CONFIG["s2ag"]["fields"],
        "year": f"{CONFIG['search']['min_year']}-{CONFIG['search']['max_year']}",
    }

    # 领域过滤：如果配置了 fields_of_study，附加到查询参数
    fields_of_study = CONFIG["filter"]["fields_of_study"]
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study

    # 如果配置了 S2AG API Key，附加到请求头以提升速率限制
    headers = {}
    api_key = CONFIG["s2ag"]["api_key"]
    if api_key:
        headers["x-api-key"] = api_key

    resp = http_client.get(
        url, params=params, headers=headers,
        timeout=CONFIG["s2ag"]["request_timeout"],
    )

    # 429 → 触发长退避重试
    if resp.status_code == 429:
        logger.warning(f"⏳ Rate limited (429) for '{keyword}', backing off...")
        raise _RateLimitError(f"429 for '{keyword}'")

    # 5xx → 服务端临时错误，也触发重试
    if resp.status_code >= 500:
        logger.warning(f"⏳ Server error ({resp.status_code}) for '{keyword}', retrying...")
        raise _RateLimitError(f"{resp.status_code} for '{keyword}'")

    # 其他客户端错误 (400, 404 等) → 跳过，不重试
    if resp.status_code >= 400:
        logger.warning(f"Skipping '{keyword}': HTTP {resp.status_code}")
        return []

    data = resp.json()
    return data.get("data", [])


def _parse_authors(raw_authors: list[dict] | None) -> list[str]:
    """安全提取作者姓名列表。"""
    if not raw_authors:
        return []
    return [a.get("name", "Unknown") for a in raw_authors if isinstance(a, dict)]


def _passes_citation_filter(
    citation_count: int,
    year: int | None,
    *,
    min_citations: int,
    exempt_after_year: int,
) -> bool:
    """引用数过滤规则。

    Args:
        citation_count: 论文引用数。
        year: 论文发表年份。
        min_citations: 最低引用数阈值。
        exempt_after_year: 豁免年份，该年份及之后的论文不受限制。

    Returns:
        True 表示通过过滤，False 表示被过滤掉。
    """
    if min_citations <= 0:
        return True  # 没有设置过滤阈值

    # 豁免规则：近年论文不受引用数限制
    if year is not None and year >= exempt_after_year:
        return True

    return citation_count >= min_citations


def _compute_score(
    year: int | None,
    citation_count: int,
    *,
    min_year: int,
    max_year: int,
    max_citations: int,
    recency_weight: float,
) -> float:
    """对数平滑双维加权评分。

    Score = recency_weight * recency_norm + (1 - recency_weight) * citation_norm

    其中：
      recency_norm  = (year - min_year) / (max_year - min_year)
      citation_norm = log(1 + citations) / log(1 + max_citations)
    """
    # Recency 归一化
    if year is None or max_year == min_year:
        recency_norm = 0.0
    else:
        recency_norm = (year - min_year) / (max_year - min_year)
        recency_norm = max(0.0, min(1.0, recency_norm))

    # Citation 对数平滑归一化
    if max_citations <= 0:
        citation_norm = 0.0
    else:
        citation_norm = math.log(1 + citation_count) / math.log(1 + max_citations)

    return recency_weight * recency_norm + (1 - recency_weight) * citation_norm


def _anti_matthew_score(citation_count: int) -> float:
    """去马太效应评分：用 log 压缩引用数，防止高引论文垄断。

    log(1 + c) 对比线性 c 的效果：
      - c=10   → 2.4  vs 10    (正常论文，权重保持)
      - c=100  → 4.6  vs 100   (10x 引用只获得 ~2x 权重)
      - c=1000 → 6.9  vs 1000  (100x 引用只获得 ~3x 权重)
    """
    return math.log(1 + citation_count)


def _dual_pool_select(
    all_papers: list[dict],
    *,
    process_limit: int,
    exempt_after_year: int,
    recent_limit: int,
) -> list[dict]:
    """双池选拔策略：新论文池 + 经典论文池。

    去马太效应核心逻辑：
    1. 将论文分为「新论文」(year >= exempt_year) 和「经典论文」两个池
    2. 新论文池：按引用数排序，取 top recent_limit（保护前沿研究）
    3. 经典论文池：按 log(1+citations) 排序（去马太效应，压制垄断）
    4. 两池合并，总数不超过 process_limit

    Args:
        all_papers: 去重后的全部论文 raw dict 列表。
        process_limit: 最终输出总数上限。
        exempt_after_year: 新旧论文分界年份。
        recent_limit: 新论文池的最大容量。

    Returns:
        选中的论文 raw dict 列表。
    """
    # ── 分池 ────────────────────────────────────────────────────
    recent_pool: list[dict] = []
    classic_pool: list[dict] = []

    for p in all_papers:
        year = p.get("year")
        if year is not None and year >= exempt_after_year:
            recent_pool.append(p)
        else:
            classic_pool.append(p)

    logger.info(
        f"Dual-pool split: {len(recent_pool)} recent "
        f"(>={exempt_after_year}), {len(classic_pool)} classic"
    )

    # ── 新论文池：按引用数排序，取 top recent_limit ────────────
    recent_pool.sort(
        key=lambda p: p.get("citationCount", 0) or 0, reverse=True
    )
    if recent_limit > 0 and len(recent_pool) > recent_limit:
        logger.info(
            f"Recent pool: {len(recent_pool)} → capped at {recent_limit} "
            f"(by citation count)"
        )
        recent_pool = recent_pool[:recent_limit]

    # ── 经典论文池：按 anti-Matthew score 排序 ─────────────────
    # 确定经典池配额 = 总配额 - 新论文已占用
    classic_slots = max(0, process_limit - len(recent_pool))

    classic_pool.sort(
        key=lambda p: _anti_matthew_score(p.get("citationCount", 0) or 0),
        reverse=True,
    )
    if len(classic_pool) > classic_slots:
        # 日志：展示马太效应的压制效果
        if classic_pool:
            top_raw = classic_pool[0].get("citationCount", 0) or 0
            cutoff_raw = classic_pool[min(classic_slots, len(classic_pool)) - 1].get("citationCount", 0) or 0
            logger.info(
                f"Classic pool (anti-Matthew): {len(classic_pool)} → {classic_slots} "
                f"(top: {top_raw} cites → score {_anti_matthew_score(top_raw):.1f}, "
                f"cutoff: {cutoff_raw} cites → score {_anti_matthew_score(cutoff_raw):.1f})"
            )
        classic_pool = classic_pool[:classic_slots]

    # ── 合并 ────────────────────────────────────────────────────
    selected = recent_pool + classic_pool
    logger.info(
        f"Dual-pool result: {len(recent_pool)} recent + "
        f"{len(classic_pool)} classic = {len(selected)} total"
    )
    return selected


def fetch_and_score(keywords: list[str]) -> list[PaperData]:
    """主入口：搜索、去重、过滤、双池选拔、评分、排序。

    Args:
        keywords: 模块 1 输出的关键词列表。

    Returns:
        按评分降序排列的 Top N 篇 PaperData。
    """
    # ── 0. 加载过滤配置 ──────────────────────────────────────────
    min_citations = CONFIG["filter"]["min_citations"]
    exempt_after_year = CONFIG["filter"]["citation_exempt_after_year"]
    fields_of_study = CONFIG["filter"]["fields_of_study"]
    recent_limit = CONFIG["filter"]["recent_limit"]
    process_limit = CONFIG["search"]["process_limit"]

    if fields_of_study:
        logger.info(f"Domain filter: {fields_of_study}")
    if min_citations > 0:
        logger.info(
            f"Citation filter: min={min_citations}, "
            f"exempt papers from {exempt_after_year}+"
        )

    # ── 1. 搜索 & 聚合 ──────────────────────────────────────────
    raw_papers: dict[str, dict] = {}  # paperId -> raw dict (去重)

    with httpx.Client() as http_client:
        for i, kw in enumerate(keywords):
            # 关键词之间冷却，避免触发速率限制
            if i > 0:
                logger.info(f"⏳ Cooldown {_S2AG_COOLDOWN}s before next query...")
                time.sleep(_S2AG_COOLDOWN)

            logger.info(f"Searching S2AG for: '{kw}' [{i+1}/{len(keywords)}]")
            try:
                results = _search_s2ag(kw, http_client=http_client)
            except _RateLimitError:
                logger.warning(
                    f"Rate limit exhausted for '{kw}' after retries, skipping."
                )
                continue
            except Exception as e:
                logger.warning(f"Search failed for '{kw}': {e}")
                continue

            for paper in results:
                pid = paper.get("paperId")
                if pid and pid not in raw_papers:
                    raw_papers[pid] = paper

            logger.info(
                f"  → {len(results)} results, "
                f"{len(raw_papers)} unique total"
            )

    logger.info(f"Aggregated {len(raw_papers)} unique papers after deduplication.")

    if not raw_papers:
        return []

    # ── 2. 引用数过滤 ───────────────────────────────────────────
    if min_citations > 0:
        before_filter = len(raw_papers)
        raw_papers = {
            pid: p for pid, p in raw_papers.items()
            if _passes_citation_filter(
                citation_count=p.get("citationCount", 0) or 0,
                year=p.get("year"),
                min_citations=min_citations,
                exempt_after_year=exempt_after_year,
            )
        }
        filtered_out = before_filter - len(raw_papers)
        logger.info(
            f"Citation filter: {filtered_out} papers removed, "
            f"{len(raw_papers)} remaining "
            f"(papers from {exempt_after_year}+ exempted)"
        )

    if not raw_papers:
        logger.warning("No papers remaining after citation filter.")
        return []

    # ── 3. 双池选拔（去马太效应） ───────────────────────────────
    all_raw = list(raw_papers.values())

    if len(all_raw) > process_limit:
        selected_raw = _dual_pool_select(
            all_raw,
            process_limit=process_limit,
            exempt_after_year=exempt_after_year,
            recent_limit=recent_limit,
        )
    else:
        selected_raw = all_raw
        logger.info(
            f"Total papers ({len(all_raw)}) <= process_limit ({process_limit}), "
            f"skipping dual-pool selection."
        )

    # ── 4. 统计全局极值（基于选中的论文） ───────────────────────
    all_years = [
        p["year"] for p in selected_raw if p.get("year") is not None
    ]
    all_citations = [
        p.get("citationCount", 0) or 0 for p in selected_raw
    ]

    global_min_year = min(all_years) if all_years else CONFIG["search"]["min_year"]
    global_max_year = max(all_years) if all_years else CONFIG["search"]["max_year"]
    global_max_citations = max(all_citations) if all_citations else 1

    logger.info(
        f"Year range: [{global_min_year}, {global_max_year}], "
        f"Max citations: {global_max_citations}"
    )

    # ── 5. 评分 & 转换 ──────────────────────────────────────────
    scored_papers: list[PaperData] = []
    for raw in selected_raw:
        citation_count = raw.get("citationCount", 0) or 0
        score = _compute_score(
            year=raw.get("year"),
            citation_count=citation_count,
            min_year=global_min_year,
            max_year=global_max_year,
            max_citations=global_max_citations,
            recency_weight=CONFIG["search"]["recency_weight"],
        )

        scored_papers.append(
            PaperData(
                paper_id=raw["paperId"],
                title=raw.get("title", "Untitled"),
                abstract=raw.get("abstract"),
                year=raw.get("year"),
                citation_count=citation_count,
                authors=_parse_authors(raw.get("authors")),
                url=raw.get("url"),
                score=score,
            )
        )

    # ── 6. 排序 ─────────────────────────────────────────────────
    scored_papers.sort(key=lambda p: p.score, reverse=True)

    logger.info(
        f"Returning {len(scored_papers)} papers "
        f"(score range: {scored_papers[0].score:.3f} – "
        f"{scored_papers[-1].score:.3f})"
    )
    return scored_papers
