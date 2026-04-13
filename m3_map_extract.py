"""
模块 3：Map 阶段 — 隔离式要素提取 (Isolated Extraction)
──────────────────────────────────────────────────────────
输入：Top N 篇文献的摘要（并发处理）
处理：调用 Flash 模型，仅提取结构化事实
输出：EnrichedPaper 列表

支持增量恢复：可传入已完成的 paper_ids，跳过重复处理。
每处理完一批论文，回调保存部分 checkpoint。
"""

from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional, Set

from google import genai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from config import CONFIG
from schemas import AbstractAnalysis, EnrichedPaper, PaperData

logger = logging.getLogger(__name__)

# ─── Map 单篇提取 ─────────────────────────────────────────────────

_MAP_PROMPT_TEMPLATE = (
    "You are a factual information extractor and relevance judge for academic papers.\n"
    "Given the user's ORIGINAL RESEARCH QUERY and the paper title and abstract below:\n"
    "1. FIRST, carefully determine if this paper is actually relevant to the user's ORIGINAL QUERY topic. "
    "Set `is_relevant_to_query` to True ONLY IF the paper directly addresses or provides meaningful insight into the query topic. "
    "If it is tangentially related or from a different domain entirely, set it to False.\n"
    "2. THEN, extract the core factual information fields. You MUST write the extracted facts STRICTLY IN ENGLISH, regardless of the language of the original query.\n"
    "Do NOT classify or categorize the paper. Only extract factual information.\n\n"
    "User's Original Query: {query}\n\n"
    "Paper Article:\n"
    "Title: {title}\n"
    "Abstract: {abstract}\n"
)


@retry(
    wait=wait_random_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _fetch_abstract_analysis(
    paper: PaperData, *, query: str, client: genai.Client
) -> AbstractAnalysis:
    """对单篇论文摘要进行结构化事实提取。

    使用 tenacity 的随机抖动指数退避重试，彻底抛弃 sleep()。
    """
    abstract_text = paper.abstract or "No abstract available."
    prompt = _MAP_PROMPT_TEMPLATE.format(
        query=query, title=paper.title, abstract=abstract_text
    )

    response = client.models.generate_content(
        model=CONFIG["llm"]["flash_model"],
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AbstractAnalysis,
            temperature=0.1,
        ),
    )

    return AbstractAnalysis.model_validate(json.loads(response.text))


# ─── Map 并发调度（支持增量恢复） ──────────────────────────────────

def map_extract(
    papers: list[PaperData],
    *,
    query: str,
    client: genai.Client,
    max_workers: int = 5,
    already_done: Optional[list[EnrichedPaper]] = None,
    on_progress: Optional[Callable[[list[EnrichedPaper]], None]] = None,
    progress_interval: int = 3,
) -> list[EnrichedPaper]:
    """并发对所有论文执行 Map 提取。

    Args:
        papers: 模块 2 输出的评分后论文列表。
        query: 用户原始查询。
        client: Gemini API 客户端实例。
        max_workers: 最大并发线程数。
        already_done: 之前已完成的 EnrichedPaper 列表（增量恢复用）。
        on_progress: 每完成 progress_interval 篇论文时的回调函数，
                     用于保存部分 checkpoint。
        progress_interval: 触发 on_progress 回调的间隔篇数。

    Returns:
        带有分析结果的 EnrichedPaper 列表（包含恢复的 + 新处理的）。
    """
    # ── 1. 计算需要跳过的 paper_ids ─────────────────────────────
    enriched: list[EnrichedPaper] = list(already_done) if already_done else []
    done_ids: Set[str] = {ep.paper.paper_id for ep in enriched}

    papers_to_process = [p for p in papers if p.paper_id not in done_ids]

    if done_ids:
        logger.info(
            f"♻️  Resuming Map: {len(done_ids)} already done, "
            f"{len(papers_to_process)} remaining"
        )

    if not papers_to_process:
        logger.info("All papers already processed, skipping Map stage.")
        return enriched

    # ── 2. 并发处理 ─────────────────────────────────────────────
    failed_count = 0
    new_since_last_save = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_paper = {
            executor.submit(
                _fetch_abstract_analysis, paper, query=query, client=client
            ): paper
            for paper in papers_to_process
        }

        for future in as_completed(future_to_paper):
            paper = future_to_paper[future]
            try:
                analysis = future.result()
                enriched.append(EnrichedPaper(paper=paper, analysis=analysis))
                new_since_last_save += 1
                logger.info(
                    f"✓ [{len(enriched)}/{len(papers)}] "
                    f"Mapped (Relevant: {analysis.is_relevant_to_query}): "
                    f"{paper.title[:60]}..."
                )

                # 定期触发 checkpoint 回调
                if on_progress and new_since_last_save >= progress_interval:
                    on_progress(enriched)
                    new_since_last_save = 0

            except Exception as e:
                failed_count += 1
                logger.error(
                    f"✗ Map failed for '{paper.title[:60]}...': {e}"
                )

    # ── 3. 最终保存 ─────────────────────────────────────────────
    if on_progress and new_since_last_save > 0:
        on_progress(enriched)

    logger.info(
        f"Map complete: {len(enriched)} total ({len(enriched) - len(done_ids)} new), "
        f"{failed_count} failed."
    )
    return enriched
