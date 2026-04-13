"""
模块 2：文献获取与沙盒漏斗 (Fetch & Score Funnel)
──────────────────────────────────────────────────
输入：关键词组、Config 参数
处理：
  1. 遍历关键词组调用 S2AG API 搜索（支持领域过滤）
  2. 引用链扩展（Citation Snowballing）：用高引种子论文发现相关文献
  3. 聚合去重
  4. 引用数过滤（支持豁免年份）
  5. 双池选拔：新论文池 + 经典论文池（去马太效应）
  6. 对数平滑双维加权排序
输出：按得分降序的 Top N 篇 PaperData 列表
"""

from __future__ import annotations

import math
import logging
import time

import httpx
from google import genai
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
    wait=wait_random_exponential(multiplier=5, max=120),
    retry=retry_if_exception_type(_RateLimitError),
    reraise=False,
)
def _search_s2ag(keyword: str, *, http_client: httpx.Client) -> list[dict]:
    """调用 Semantic Scholar Academic Graph API 搜索单个关键词。

    429/5xx 会无限重试（指数退避 5-120s），直到成功。
    其他 HTTP 错误返回空结果。
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


# ─── 引用链扩展 (Citation Snowballing) ─────────────────────────────

@retry(
    wait=wait_random_exponential(multiplier=5, max=120),
    retry=retry_if_exception_type(_RateLimitError),
    reraise=False,
)
def _fetch_related(
    paper_id: str,
    direction: str,
    *,
    http_client: httpx.Client,
    limit: int = 20,
) -> list[dict]:
    """获取论文的引用/被引关系。

    Args:
        paper_id: S2AG 论文 ID。
        direction: 'references' 或 'citations'。
        http_client: httpx 客户端。
        limit: 每个方向最多获取数量。

    Returns:
        论文 raw dict 列表。
    """
    url = f"{CONFIG['s2ag']['base_url']}/paper/{paper_id}/{direction}"
    params = {
        "fields": CONFIG["s2ag"]["fields"],
        "limit": limit,
    }
    headers = {}
    api_key = CONFIG["s2ag"]["api_key"]
    if api_key:
        headers["x-api-key"] = api_key

    resp = http_client.get(
        url, params=params, headers=headers,
        timeout=CONFIG["s2ag"]["request_timeout"],
    )

    if resp.status_code == 429:
        raise _RateLimitError(f"429 for {direction} of {paper_id}")
    if resp.status_code >= 500:
        raise _RateLimitError(f"{resp.status_code} for {direction} of {paper_id}")
    if resp.status_code >= 400:
        logger.warning(f"Skipping {direction} for {paper_id}: HTTP {resp.status_code}")
        return []

    data = resp.json()
    results = []
    # API 返回格式: {"data": [{"citingPaper": {...}} or {"citedPaper": {...}}, ...]}
    key = "citedPaper" if direction == "references" else "citingPaper"
    for item in data.get("data", []):
        paper = item.get(key, {})
        if paper and paper.get("paperId"):
            results.append(paper)
    return results


_SEED_SELECT_PROMPT = (
    "You are a research relevance judge.\n"
    "Given the user's research query and a list of candidate papers, "
    "select the papers that are MOST directly relevant to the query topic.\n\n"
    "User Query: {query}\n\n"
    "Candidate Papers:\n{candidates_json}\n\n"
    "Return a JSON array of paper_ids for the papers that are most relevant "
    "to the query. Select at most {select_count} papers.\n"
    "ONLY select papers that are directly on-topic. "
    "Reject papers that are tangentially related or from a different field.\n"
    "Return format: [\"paper_id_1\", \"paper_id_2\", ...]\n"
)


@retry(
    wait=wait_random_exponential(multiplier=1, max=30),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _llm_select_seeds(
    candidates: list[dict],
    *,
    query: str,
    client: genai.Client,
    select_count: int,
) -> list[dict]:
    """用 LLM 从候选论文中筛选与查询最相关的种子论文。

    Args:
        candidates: 候选论文 raw dict 列表（已按引用数排序）。
        query: 用户原始查询。
        client: Gemini API 客户端。
        select_count: 最多选择多少篇。

    Returns:
        筛选后的种子论文 raw dict 列表。
    """
    if not candidates:
        return []

    # 构建候选列表 JSON
    cands_payload = []
    for p in candidates:
        cands_payload.append({
            "paper_id": p.get("paperId", ""),
            "title": p.get("title", "Untitled"),
            "year": p.get("year"),
            "citation_count": p.get("citationCount", 0) or 0,
            "abstract": (p.get("abstract") or "")[:200],  # 截断摘要节省 token
        })

    import json
    prompt = _SEED_SELECT_PROMPT.format(
        query=query,
        candidates_json=json.dumps(cands_payload, ensure_ascii=False, indent=2),
        select_count=select_count,
    )

    try:
        response = client.models.generate_content(
            model=CONFIG["llm"]["flash_model"],
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        selected_ids = json.loads(response.text)

        # 兼容格式：可能返回 {"paper_ids": [...]} 或直接 [...]
        if isinstance(selected_ids, dict):
            selected_ids = (
                selected_ids.get("paper_ids")
                or selected_ids.get("selected")
                or selected_ids.get("ids")
                or list(selected_ids.values())[0]
            )

        if not isinstance(selected_ids, list):
            raise ValueError(f"Unexpected LLM response: {type(selected_ids)}")

        # 映射回原始 dict
        id_to_paper = {p.get("paperId"): p for p in candidates}
        seeds = [id_to_paper[pid] for pid in selected_ids if pid in id_to_paper]

        logger.info(
            f"🧠 LLM seed selection: {len(candidates)} candidates → "
            f"{len(seeds)} seeds selected"
        )
        for s in seeds:
            logger.info(
                f"  ✓ [{s.get('citationCount', 0)} cites] "
                f"{s.get('title', '?')[:60]}"
            )

        # 如果 LLM 没选到任何论文，回退到引用数排序
        if not seeds:
            logger.warning("LLM selected 0 seeds, falling back to top-cited")
            seeds = candidates[:select_count]

        return seeds[:select_count]

    except Exception as e:
        logger.warning(f"LLM seed selection failed ({e}), falling back to top-cited")
        return candidates[:select_count]
    raw_papers: dict[str, dict],
    *,
    http_client: httpx.Client,
    query: str,
    client: genai.Client,
    seed_count: int,
    direction: str,
    per_seed_limit: int,
    min_year: int,
    max_year: int,
) -> dict[str, dict]:
    """用高引种子论文的引用图发现更多相关文献。

    种子选择经过 LLM 筛选，避免离题的高引论文把扩展方向带偏。

    Args:
        raw_papers: 已有论文池（会被原地扩展）。
        query: 用户原始查询（用于 LLM 判断相关性）。
        client: Gemini API 客户端。
        seed_count: 种子论文数量。
        direction: 'references', 'citations', 或 'both'。
        per_seed_limit: 每个种子每个方向的最大获取数。
        min_year, max_year: 年份范围过滤。

    Returns:
        扩展后的 raw_papers dict。
    """
    # 候选种子：取引用数最高的 2x seed_count 篇，然后用 LLM 筛选
    candidate_count = seed_count * 3
    sorted_papers = sorted(
        raw_papers.values(),
        key=lambda p: p.get("citationCount", 0) or 0,
        reverse=True,
    )
    candidates = sorted_papers[:candidate_count]

    # LLM 筛选种子
    seeds = _llm_select_seeds(
        candidates=candidates,
        query=query,
        client=client,
        select_count=seed_count,
    )

    logger.info(
        f"\U0001f331 Citation expansion: {len(seeds)} seeds, "
        f"direction={direction}, limit={per_seed_limit}/seed"
    )
    for s in seeds:
        logger.info(
            f"  Seed: [{s.get('citationCount', 0)} cites] "
            f"{s.get('title', '?')[:60]}..."
        )

    directions = []
    if direction in ("references", "both"):
        directions.append("references")
    if direction in ("citations", "both"):
        directions.append("citations")

    before_count = len(raw_papers)

    for seed in seeds:
        seed_id = seed["paperId"]
        seed_title = seed.get("title", "?")[:50]

        for d in directions:
            time.sleep(_S2AG_COOLDOWN)
            logger.info(f"  → Fetching {d} for: {seed_title}...")
            try:
                related = _fetch_related(
                    seed_id, d,
                    http_client=http_client,
                    limit=per_seed_limit,
                )
            except Exception as e:
                logger.warning(f"  Failed to fetch {d} for {seed_id}: {e}")
                continue

            added = 0
            for paper in related:
                pid = paper.get("paperId")
                if not pid or pid in raw_papers:
                    continue
                # 年份范围过滤
                year = paper.get("year")
                if year is not None and (year < min_year or year > max_year):
                    continue
                raw_papers[pid] = paper
                added += 1

            logger.info(
                f"    +{added} new papers from {d} "
                f"({len(raw_papers)} total)"
            )
            time.sleep(1.5)

    logger.info(
        f"\U0001f331 Expansion complete: {before_count} → {len(raw_papers)} "
        f"(+{len(raw_papers) - before_count} new)"
    )
    return raw_papers


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
            except Exception as e:
                logger.warning(f"Search failed for '{kw}': {e}")
                results = []

            for paper in results:
                pid = paper.get("paperId")
                if pid and pid not in raw_papers:
                    raw_papers[pid] = paper

            logger.info(
                f"  → {len(results)} results, "
                f"{len(raw_papers)} unique total"
            )

            time.sleep(1.5)

        # ── 1.5 引用链扩展 ─────────────────────────────────────
        expand_cfg = CONFIG["expand"]
        if expand_cfg["enabled"] and raw_papers:
            raw_papers = _expand_via_citations(
                raw_papers,
                http_client=http_client,
                query=query,
                client=client,
                seed_count=expand_cfg["seed_count"],
                direction=expand_cfg["direction"],
                per_seed_limit=expand_cfg["per_seed_limit"],
                min_year=CONFIG["search"]["min_year"],
                max_year=CONFIG["search"]["max_year"],
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
