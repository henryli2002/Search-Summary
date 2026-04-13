"""
模块 1：Query 实体提取器 (Entity Extractor)
──────────────────────────────────────────
输入：用户原始 Query
处理：强制使用 response_schema 绑定 Pydantic，让模型仅输出同义词组
输出：List[str]
"""

from __future__ import annotations

import json

from google import genai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from config import CONFIG
from schemas import QueryEntities


@retry(
    wait=wait_random_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(5),
    reraise=True,
)
def extract_entities(query: str, *, client: genai.Client) -> list[str]:
    """从用户自然语言 Query 中提取研究主题的同义词/近义词关键词组。

    Args:
        query: 用户原始搜索请求。
        client: Gemini API 客户端实例。

    Returns:
        关键词列表，每个元素是该研究领域的一种表述方式。
    """
    prompt = (
        "You are an academic keyword expansion expert.\n"
        "Your goal is to generate 3-5 highly specific search queries for the user's research topic.\n"
        "Constraints:\n"
        "1. BE SPECIFIC: Never generalize to broader parent categories (e.g., if the query is 'Agent Memory Compression', NEVER output 'Artificial Intelligence' or 'Machine Learning').\n"
        "2. Keep the keywords directly focused on the exact technical problem or methodology requested.\n"
        "3. Output MUST be valid, exact keyword phrases used in academic database searches.\n"
        "4. No boolean operators (AND, OR, NOT).\n"
        "5. ALL KEYWORDS MUST BE IN ENGLISH: Even if the user query is in Chinese or another language, translate the intent and output strictly English academic terms.\n\n"
        f"User Query: {query}"
    )

    response = client.models.generate_content(
        model=CONFIG["llm"]["flash_model"],
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QueryEntities,
            temperature=0.3,
        ),
    )

    parsed = QueryEntities.model_validate(json.loads(response.text))
    return parsed.keywords
