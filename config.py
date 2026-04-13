"""
第 0 层：全局配置字典 (Global Context)
系统启动的首要动作是冻结所有超参数，确保全程逻辑一致且可控。
支持通过环境变量覆盖默认值（.env 文件或 export）。
"""

import os
from types import MappingProxyType
from pathlib import Path


# ─── 加载 .env 文件（轻量实现，无需 python-dotenv 依赖） ──────────
def _load_dotenv(env_path: Path = Path(".env")) -> None:
    """从项目根目录的 .env 文件加载环境变量。
    仅在变量未被系统环境变量覆盖时生效。
    """
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            # 不覆盖已存在的系统环境变量
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()


def _env(key: str, default: str) -> str:
    """从环境变量读取配置，不存在则返回默认值。"""
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    """从环境变量读取整型配置。"""
    val = os.environ.get(key)
    return int(val) if val else default


def _env_float(key: str, default: float) -> float:
    """从环境变量读取浮点型配置。"""
    val = os.environ.get(key)
    return float(val) if val else default


# ─── 可变原始配置（仅用于初始化） ──────────────────────────────────
_CONFIG = {
    "search": {
        "min_year": _env_int("SEARCH_MIN_YEAR", 2020),
        "max_year": _env_int("SEARCH_MAX_YEAR", 2026),
        "fetch_limit": _env_int("SEARCH_FETCH_LIMIT", 50),
        "process_limit": _env_int("SEARCH_PROCESS_LIMIT", 30),
        "recency_weight": _env_float("SEARCH_RECENCY_WEIGHT", 0.65),
    },
    "filter": {
        # 学科领域过滤（逗号分隔），留空则不限领域
        # 可选值: Computer Science, Physics, Mathematics, Biology,
        #         Medicine, Chemistry, Engineering, Environmental Science,
        #         Materials Science, Psychology, Economics, Business,
        #         Political Science, Sociology, Geography, History,
        #         Art, Philosophy, Linguistics, Education
        "fields_of_study": _env("FILTER_FIELDS_OF_STUDY", ""),

        # 最低引用数阈值 (通用规则)
        # 设为 0 则不过滤
        "min_citations": _env_int("FILTER_MIN_CITATIONS", 0),

        # 引用豁免年份：该年份 (含) 之后发表的论文不受 min_citations 限制
        # 因为新论文还没来得及积累引用量
        # 例如设为 2024，则 2024/2025/2026 的论文不受引用数限制
        "citation_exempt_after_year": _env_int("FILTER_CITATION_EXEMPT_YEAR", 2024),

        # 新论文独立配额：exempt_year 之后的论文最多保留多少篇
        # 这些论文按引用数排序，独立于总 process_limit
        # 设为 0 则不限制新论文数量
        "recent_limit": _env_int("FILTER_RECENT_LIMIT", 15),
    },
    "llm": {
        "flash_model": _env("LLM_FLASH_MODEL", "gemini-2.5-flash"),
        "pro_model": _env("LLM_PRO_MODEL", "gemini-2.5-pro"),
    },
    "s2ag": {
        "base_url": "https://api.semanticscholar.org/graph/v1",
        "api_key": _env("S2AG_API_KEY", ""),   # 可选，设置后提升 API 速率限制
        "fields": "paperId,title,abstract,year,citationCount,authors,url",
        "request_timeout": _env_int("S2AG_REQUEST_TIMEOUT", 30),
    },
    "expand": {
        # 引用链扩展（Citation Snowballing）
        # 用高引论文的引用/被引关系发现更多相关文献
        "enabled": _env("EXPAND_ENABLED", "true").lower() in ("true", "1", "yes"),

        # 种子论文数量：从关键词检索结果中取引用数最高的 N 篇作为种子
        "seed_count": _env_int("EXPAND_SEED_COUNT", 3),

        # 扩展方向：references (引用的论文), citations (被引的论文), both (双向)
        "direction": _env("EXPAND_DIRECTION", "both"),

        # 每个种子论文最多获取多少篇引用/被引
        "per_seed_limit": _env_int("EXPAND_PER_SEED_LIMIT", 20),
    },
}

# ─── 冻结配置：运行时不可修改 ───────────────────────────────────────
CONFIG = MappingProxyType({
    k: MappingProxyType(v) if isinstance(v, dict) else v
    for k, v in _CONFIG.items()
})
