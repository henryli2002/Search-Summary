"""
模块 5：Reduce 阶段 — 模块化报告生成 (Modular Report Generation)
────────────────────────────────────────────────────────────────────
输入：已被 Python 强逻辑分组的文献集合
处理：按组别依次喂给 Pro 模型撰写评述，最后拼接为 Markdown
输出：完整 Markdown 报告字符串
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone, timedelta

from google import genai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from config import CONFIG
from schemas import EnrichedPaper

logger = logging.getLogger(__name__)

_GROUP_REVIEW_PROMPT = (
    "You are an academic review writer.\n"
    "Below is a set of papers belonging to the research school: **{group_name}**.\n\n"
    "For each paper you have:\n"
    "  - title, year, citation_count, url\n"
    "  - one_line_summary, core_problem, key_mechanisms\n\n"
    "Write a coherent, well-structured review section for this school.\n"
    "Rules:\n"
    "- ONLY use information from the papers provided. Do NOT add external knowledge.\n"
    "- Reference papers by their title.\n"
    "- Highlight key trends, commonalities, and differences within this group.\n"
    "- Write in Markdown format.\n"
    "- Length: 200-400 words.\n"
    "- Write the review in the same language as the original user query: {user_query}\n\n"
    "Papers:\n{papers_json}\n"
)


def _build_group_payload(papers: list[EnrichedPaper]) -> str:
    """构建单个分组的论文 JSON 数据。"""
    payload = []
    for ep in papers:
        payload.append({
            "title": ep.paper.title,
            "year": ep.paper.year,
            "citation_count": ep.paper.citation_count,
            "url": ep.paper.url,
            "one_line_summary": ep.analysis.one_line_summary,
            "core_problem": ep.analysis.core_problem,
            "key_mechanisms": ep.analysis.key_mechanisms,
        })
    return json.dumps(payload, ensure_ascii=False, indent=2)


@retry(
    wait=wait_random_exponential(multiplier=1, max=15),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _generate_group_review(
    group_name: str,
    papers: list[EnrichedPaper],
    user_query: str,
    *,
    client: genai.Client,
) -> str:
    """调用 Pro 模型为单个技术流派生成评述。"""
    papers_json = _build_group_payload(papers)
    prompt = _GROUP_REVIEW_PROMPT.format(
        group_name=group_name,
        papers_json=papers_json,
        user_query=user_query,
    )

    response = client.models.generate_content(
        model=CONFIG["llm"]["pro_model"],
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0.4,
        ),
    )

    return response.text


def reduce_report(
    grouped: dict[str, list[EnrichedPaper]],
    user_query: str,
    *,
    client: genai.Client,
) -> str:
    """按组生成评述并拼接为完整 Markdown 报告。

    Args:
        grouped: 模块 4 输出的 {流派名称: [EnrichedPaper, ...]} 字典。
        user_query: 用户原始查询（用于报告标题和语言适配）。
        client: Gemini API 客户端实例。

    Returns:
        完整的 Markdown 格式研究综述报告。
    """
    # ── 报告头 ──────────────────────────────────────────────────
    tz_cn = timezone(timedelta(hours=8))
    timestamp = datetime.now(tz_cn).strftime("%Y-%m-%d %H:%M:%S CST")

    total_papers = sum(len(papers) for papers in grouped.values())
    sections: list[str] = [
        f"# 文献综述报告: {user_query}\n",
        f"> 生成时间: {timestamp}  \n"
        f"> 分析论文数: {total_papers}  \n"
        f"> 技术流派数: {len(grouped)}\n",
        "---\n",
    ]

    # ── 目录 ────────────────────────────────────────────────────
    sections.append("## 目录\n")
    for i, (group_name, papers) in enumerate(grouped.items(), 1):
        anchor = group_name.lower().replace(" ", "-").replace("/", "-")
        sections.append(f"{i}. [{group_name}](#{anchor}) ({len(papers)} 篇)")
    sections.append("\n---\n")

    # ── 各流派评述 ──────────────────────────────────────────────
    for i, (group_name, papers) in enumerate(grouped.items(), 1):
        logger.info(f"Generating review for group {i}/{len(grouped)}: {group_name}")

        try:
            review_md = _generate_group_review(
                group_name, papers, user_query, client=client
            )
        except Exception as e:
            logger.error(f"Failed to generate review for '{group_name}': {e}")
            review_md = f"*（该流派评述生成失败: {e}）*"

        sections.append(f"## {i}. {group_name}\n")
        sections.append(review_md)
        sections.append("")

        # 论文列表附录
        sections.append(f"### 参考文献 — {group_name}\n")
        sections.append("| # | 论文标题 | 年份 | 引用数 | 链接 |")
        sections.append("|---|---------|------|--------|------|")
        for j, ep in enumerate(papers, 1):
            url_cell = f"[链接]({ep.paper.url})" if ep.paper.url else "N/A"
            title_escaped = ep.paper.title.replace("|", "\\|")
            sections.append(
                f"| {j} | {title_escaped} | "
                f"{ep.paper.year or 'N/A'} | "
                f"{ep.paper.citation_count} | {url_cell} |"
            )
        sections.append("\n---\n")

    # ── 全局参考文献表 ──────────────────────────────────────────
    sections.append("## 完整参考文献列表\n")
    sections.append(
        f"以下为本报告中分析的全部 **{total_papers}** 篇论文，"
        "按年份（降序）及引用数（降序）排列。\n"
    )

    # 收集所有论文并排序
    all_papers = []
    for papers in grouped.values():
        for ep in papers:
            all_papers.append(ep)
    all_papers.sort(
        key=lambda ep: (ep.paper.year or 0, ep.paper.citation_count),
        reverse=True,
    )

    for idx, ep in enumerate(all_papers, 1):
        authors_str = ", ".join(ep.paper.authors[:5])
        if len(ep.paper.authors) > 5:
            authors_str += " et al."
        year_str = str(ep.paper.year) if ep.paper.year else "N/A"
        title_escaped = ep.paper.title.replace("[", "\\[").replace("]", "\\]")

        if ep.paper.url:
            sections.append(
                f"**[{idx}]** {authors_str}. "
                f"*{title_escaped}*. "
                f"{year_str}. "
                f"(引用: {ep.paper.citation_count}) "
                f"[[链接]]({ep.paper.url})"
            )
        else:
            sections.append(
                f"**[{idx}]** {authors_str}. "
                f"*{title_escaped}*. "
                f"{year_str}. "
                f"(引用: {ep.paper.citation_count})"
            )
        sections.append("")  # 空行分隔

    sections.append("---\n")

    # ── 报告尾 ──────────────────────────────────────────────────
    sections.append(
        "*本报告由 Search-By-Agent Pipeline 自动生成，"
        "所有评述严格基于检索到的文献摘要，未引入外部知识。*\n"
    )

    return "\n".join(sections)
