"""
模块 4：Shuffle 阶段 — 上帝视角归约 (Taxonomy & Grouping)
─────────────────────────────────────────────────────────────
输入：包含 N 篇论文信息的 JSON 数组（含模块 3 提取的技术要素）
处理：将完整数组一次性发送给 Pro 模型，生成 3-5 个互斥穷尽的技术流派分类
输出：Dict[str, List[EnrichedPaper]]（按流派分组的结构化数据）
"""

from __future__ import annotations

import json
import logging

from google import genai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from config import CONFIG
from schemas import EnrichedPaper, TaxonomyMapping

logger = logging.getLogger(__name__)

_TAXONOMY_PROMPT = (
    "You are an architect with a global perspective on research trends.\n"
    "Below is a JSON array of academic papers, each containing:\n"
    "  - paper_id, title, year, citation_count\n"
    "  - core_problem, key_mechanisms, one_line_summary\n\n"
    "Your task:\n"
    "1. Read ALL papers thoroughly.\n"
    "2. Identify 1-5 mutually exclusive and collectively exhaustive "
    "core technical schools/taxonomies.\n"
    "3. Assign every paper to exactly one taxonomy.\n"
    "4. Return a list of groups, each with a group_name and a list of paper_ids.\n\n"
    "Rules:\n"
    "- Every paper_id from the input MUST appear in exactly one group.\n"
    "- Group names should be concise, descriptive, and STRICTLY IN ENGLISH, regardless of the input language or previous text.\n"
    "- Do NOT create an 'Other' or 'Miscellaneous' category unless absolutely necessary.\n\n"
    "Papers:\n{papers_json}\n"
)


def _build_papers_payload(enriched_papers: list[EnrichedPaper]) -> str:
    """将 EnrichedPaper 列表转换为精简 JSON 字符串，用于 Prompt 注入。"""
    payload = []
    for ep in enriched_papers:
        payload.append({
            "paper_id": ep.paper.paper_id,
            "title": ep.paper.title,
            "year": ep.paper.year,
            "citation_count": ep.paper.citation_count,
            "core_problem": ep.analysis.core_problem,
            "key_mechanisms": ep.analysis.key_mechanisms,
            "one_line_summary": ep.analysis.one_line_summary,
        })
    return json.dumps(payload, ensure_ascii=False, indent=2)


@retry(
    wait=wait_random_exponential(multiplier=1, max=15),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _call_taxonomy_llm(
    papers_json: str, *, client: genai.Client
) -> TaxonomyMapping:
    """调用 Pro 模型生成技术流派映射。

    注意：不使用 response_schema，因为 Gemini API 对嵌套对象的
    additionalProperties 有兼容性限制。改为在 Prompt 中约束输出格式，
    然后通过 Pydantic 做解析校验。
    """
    prompt = _TAXONOMY_PROMPT.format(papers_json=papers_json)

    response = client.models.generate_content(
        model=CONFIG["llm"]["pro_model"],
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )

    # 手动解析并通过 Pydantic 校验
    raw = json.loads(response.text)
    logger.debug(f"Raw taxonomy response type: {type(raw).__name__}")

    # 兼容多种 LLM 输出格式：
    # 格式 A: {"groups": [{"group_name": "...", "paper_ids": [...]}]}
    # 格式 B: {"GroupA": ["id1", ...], "GroupB": ["id2", ...]}
    # 格式 C: [{"group_name": "...", "paper_ids": [...]}, ...]
    # 格式 D: [{"name": "...", "papers": [...]}, ...] (变体)

    if isinstance(raw, dict) and "groups" in raw and isinstance(raw["groups"], list):
        # 格式 A：标准结构化格式
        return TaxonomyMapping.model_validate(raw)

    if isinstance(raw, list):
        # 格式 C/D：LLM 返回了列表
        groups = []
        for item in raw:
            if isinstance(item, dict):
                # 尝试多种字段名
                name = (item.get("group_name") or item.get("name")
                        or item.get("category") or item.get("taxonomy") or "Unknown")
                ids = (item.get("paper_ids") or item.get("papers")
                       or item.get("ids") or item.get("paper_id_list") or [])
                if isinstance(ids, list) and ids:
                    groups.append({"group_name": str(name), "paper_ids": ids})
        if groups:
            return TaxonomyMapping.model_validate({"groups": groups})

    if isinstance(raw, dict):
        # 格式 B：dict 映射 {name: [ids]}
        groups = []
        for name, ids in raw.items():
            if isinstance(ids, list):
                groups.append({"group_name": name, "paper_ids": ids})
        if groups:
            return TaxonomyMapping.model_validate({"groups": groups})

    # 所有格式都匹配失败
    raise ValueError(
        f"Cannot parse taxonomy response. Type: {type(raw).__name__}, "
        f"Content preview: {str(raw)[:200]}"
    )


def shuffle_group(
    enriched_papers: list[EnrichedPaper],
    *,
    client: genai.Client,
) -> dict[str, list[EnrichedPaper]]:
    """执行 Shuffle 阶段：LLM 分类 + Python 逻辑分组。

    Args:
        enriched_papers: 模块 3 输出的全部带分析结果的论文。
        client: Gemini API 客户端实例。

    Returns:
        按技术流派分组的 {流派名称: [EnrichedPaper, ...]} 字典。
    """
    # ── 1. 构建 payload 并调用 LLM ──────────────────────────────
    papers_json = _build_papers_payload(enriched_papers)
    taxonomy = _call_taxonomy_llm(papers_json, client=client)

    logger.info(
        f"Taxonomy generated with {len(taxonomy.groups)} categories: "
        f"{[g.group_name for g in taxonomy.groups]}"
    )

    # ── 2. Python 接管：按映射表分组 ────────────────────────────
    id_to_paper: dict[str, EnrichedPaper] = {
        ep.paper.paper_id: ep for ep in enriched_papers
    }

    grouped: dict[str, list[EnrichedPaper]] = {}
    assigned_ids: set[str] = set()

    for group in taxonomy.groups:
        group_papers = []
        for pid in group.paper_ids:
            if pid in id_to_paper:
                group_papers.append(id_to_paper[pid])
                assigned_ids.add(pid)
            else:
                logger.warning(
                    f"LLM returned unknown paper_id '{pid}' "
                    f"in group '{group.group_name}'"
                )
        if group_papers:
            grouped[group.group_name] = group_papers

    # ── 3. 兜底：处理未被 LLM 分配的论文 ──────────────────────
    unassigned = [
        ep for ep in enriched_papers if ep.paper.paper_id not in assigned_ids
    ]
    if unassigned:
        logger.warning(
            f"{len(unassigned)} papers were not assigned by LLM. "
            f"Adding to 'Unclassified' group."
        )
        grouped["Unclassified"] = unassigned

    for name, papers in grouped.items():
        logger.info(f"  {name}: {len(papers)} papers")

    return grouped
