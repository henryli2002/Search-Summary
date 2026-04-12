"""
强类型 Pydantic 模型定义。
所有模块的输入/输出均通过这些 Schema 绑定，消除隐式数据结构。
"""

from __future__ import annotations
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ─── 模块 1：Query 实体提取 ────────────────────────────────────────
class QueryEntities(BaseModel):
    """LLM 从用户 Query 中提取的同义词/近义词关键词组。"""
    keywords: list[str] = Field(
        ...,
        description="A list of synonym phrases for the user query topic. "
                    "Each item is an alternative way to describe the same research area.",
        min_length=1,
        max_length=10,
    )


# ─── 模块 2：论文数据结构 ──────────────────────────────────────────
class PaperData(BaseModel):
    """从 Semantic Scholar API 获取并评分后的论文数据。"""
    paper_id: str
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    citation_count: int = 0
    authors: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    score: float = 0.0


# ─── 模块 3：Map 阶段输出 ──────────────────────────────────────────
class AbstractAnalysis(BaseModel):
    """Flash 模型对单篇论文摘要的结构化事实提取结果。"""
    core_problem: str = Field(
        ..., description="The specific problem this paper addresses."
    )
    key_mechanisms: List[str] = Field(
        ...,
        description="Concrete technical methods used, e.g. 'RLHF', 'AST parsing', 'Transformer'.",
    )
    one_line_summary: str = Field(
        ..., description="A single-sentence factual summary of the paper."
    )


class EnrichedPaper(BaseModel):
    """论文原始数据 + Map 阶段提取的分析结果。"""
    paper: PaperData
    analysis: AbstractAnalysis


# ─── 模块 4：Shuffle 阶段输出 ─────────────────────────────────────
class TaxonomyGroup(BaseModel):
    """单个技术流派分组。"""
    group_name: str = Field(
        ..., description="The name of the technical school/taxonomy."
    )
    paper_ids: List[str] = Field(
        ..., description="List of paper_ids belonging to this group."
    )


class TaxonomyMapping(BaseModel):
    """Pro 模型生成的技术流派映射。
    使用 List[TaxonomyGroup] 而非 Dict，避免 Gemini API 的 additionalProperties 限制。"""
    groups: List[TaxonomyGroup] = Field(
        ...,
        description="A list of 3-5 mutually exclusive and collectively exhaustive "
                    "taxonomy groups. Each group has a name and a list of paper_ids.",
    )


# ─── 模块 5：Reduce 阶段输出 ─────────────────────────────────────
class GroupReport(BaseModel):
    """单个技术流派的评述段。"""
    group_name: str
    markdown_content: str
