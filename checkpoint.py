"""
Checkpoint Manager — 全链路中间状态持久化与恢复
═══════════════════════════════════════════════════
每个 Pipeline 运行创建一个 checkpoint 目录，结构：

  checkpoints/<run_id>/
    meta.json           # 查询信息、配置快照、时间戳
    m1_keywords.json    # 模块 1 输出
    m2_papers.json      # 模块 2 输出
    m3_enriched.json    # 模块 3 输出（支持增量写入）
    m4_grouped.json     # 模块 4 输出
    m5_report.md        # 模块 5 输出（最终报告）
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from schemas import PaperData, EnrichedPaper, AbstractAnalysis

logger = logging.getLogger(__name__)

CHECKPOINT_DIR = Path("checkpoints")


def _make_run_id(query: str) -> str:
    """根据查询生成稳定的 run_id（query hash 前 8 位 + 安全文件名）。"""
    query_hash = hashlib.md5(query.encode("utf-8")).hexdigest()[:8]
    safe_name = "".join(
        c if c.isalnum() or c in " _-" else "_" for c in query
    )[:40].strip("_")
    return f"{safe_name}_{query_hash}"


class CheckpointManager:
    """管理 Pipeline 各阶段的中间状态持久化与恢复。"""

    STAGES = ["m1_keywords", "m2_papers", "m3_enriched", "m4_grouped", "m5_report"]

    def __init__(self, query: str, run_id: Optional[str] = None):
        self.query = query
        self.run_id = run_id or _make_run_id(query)
        self.run_dir = CHECKPOINT_DIR / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._save_meta()

    def _save_meta(self) -> None:
        """保存运行元信息。"""
        meta_path = self.run_dir / "meta.json"
        tz_cn = timezone(timedelta(hours=8))
        meta = {
            "query": self.query,
            "run_id": self.run_id,
            "created_at": datetime.now(tz_cn).isoformat(),
            "checkpoint_dir": str(self.run_dir),
        }
        # 不覆盖已有的 created_at
        if meta_path.exists():
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["created_at"] = existing.get("created_at", meta["created_at"])
            meta["updated_at"] = datetime.now(tz_cn).isoformat()
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ─── 存在性检查 ────────────────────────────────────────────

    def has_checkpoint(self, stage: str) -> bool:
        """检查指定阶段的 checkpoint 是否存在。"""
        path = self.run_dir / self._stage_filename(stage)
        return path.exists() and path.stat().st_size > 0

    def get_resume_stage(self) -> Optional[str]:
        """找到第一个缺失的 checkpoint，即需要从这里开始恢复。
        如果全部完成返回 None。"""
        for stage in self.STAGES:
            if not self.has_checkpoint(stage):
                return stage
        return None

    def get_completed_stages(self) -> List[str]:
        """返回所有已完成的阶段列表。"""
        return [s for s in self.STAGES if self.has_checkpoint(s)]

    # ─── 保存 ──────────────────────────────────────────────────

    def save_m1(self, keywords: List[str]) -> None:
        """保存模块 1 输出：关键词列表。"""
        self._write_json("m1_keywords", keywords)
        logger.info(f"💾 Checkpoint saved: m1_keywords ({len(keywords)} keywords)")

    def save_m2(self, papers: List[PaperData]) -> None:
        """保存模块 2 输出：评分后论文列表。"""
        data = [p.model_dump() for p in papers]
        self._write_json("m2_papers", data)
        logger.info(f"💾 Checkpoint saved: m2_papers ({len(papers)} papers)")

    def save_m3(self, enriched: List[EnrichedPaper]) -> None:
        """保存模块 3 输出：全部 enriched 论文。"""
        data = [ep.model_dump() for ep in enriched]
        self._write_json("m3_enriched", data)
        logger.info(f"💾 Checkpoint saved: m3_enriched ({len(enriched)} papers)")

    def save_m3_partial(self, enriched: List[EnrichedPaper]) -> None:
        """增量保存模块 3 的部分结果（容错用）。"""
        data = [ep.model_dump() for ep in enriched]
        self._write_json("m3_enriched_partial", data)

    def save_m4(self, grouped: Dict[str, List[EnrichedPaper]]) -> None:
        """保存模块 4 输出：按流派分组的数据。"""
        data = {
            name: [ep.model_dump() for ep in papers]
            for name, papers in grouped.items()
        }
        self._write_json("m4_grouped", data)
        logger.info(
            f"💾 Checkpoint saved: m4_grouped ({len(grouped)} groups, "
            f"{sum(len(v) for v in grouped.values())} papers)"
        )

    def save_m5(self, report: str) -> None:
        """保存模块 5 输出：最终 Markdown 报告。"""
        path = self.run_dir / "m5_report.md"
        path.write_text(report, encoding="utf-8")
        logger.info(f"💾 Checkpoint saved: m5_report.md")

    # ─── 加载 ──────────────────────────────────────────────────

    def load_m1(self) -> List[str]:
        """加载模块 1 checkpoint。"""
        data = self._read_json("m1_keywords")
        logger.info(f"📂 Checkpoint loaded: m1_keywords ({len(data)} keywords)")
        return data

    def load_m2(self) -> List[PaperData]:
        """加载模块 2 checkpoint。"""
        data = self._read_json("m2_papers")
        papers = [PaperData.model_validate(d) for d in data]
        logger.info(f"📂 Checkpoint loaded: m2_papers ({len(papers)} papers)")
        return papers

    def load_m3(self) -> List[EnrichedPaper]:
        """加载模块 3 checkpoint（优先完整版，其次部分版）。"""
        if self.has_checkpoint("m3_enriched"):
            data = self._read_json("m3_enriched")
        elif (self.run_dir / "m3_enriched_partial.json").exists():
            data = self._read_json("m3_enriched_partial")
            logger.warning("⚠️  Loading partial m3 checkpoint (incomplete run)")
        else:
            raise FileNotFoundError("No m3 checkpoint found")
        enriched = [EnrichedPaper.model_validate(d) for d in data]
        logger.info(f"📂 Checkpoint loaded: m3_enriched ({len(enriched)} papers)")
        return enriched

    def load_m3_partial(self) -> List[EnrichedPaper]:
        """加载模块 3 的部分结果（用于增量恢复）。"""
        partial_path = self.run_dir / "m3_enriched_partial.json"
        if partial_path.exists():
            data = json.loads(partial_path.read_text(encoding="utf-8"))
            return [EnrichedPaper.model_validate(d) for d in data]
        return []

    def load_m4(self) -> Dict[str, List[EnrichedPaper]]:
        """加载模块 4 checkpoint。"""
        data = self._read_json("m4_grouped")
        grouped = {
            name: [EnrichedPaper.model_validate(d) for d in papers]
            for name, papers in data.items()
        }
        total_papers = sum(len(v) for v in grouped.values())
        logger.info(
            f"📂 Checkpoint loaded: m4_grouped ({len(grouped)} groups, {total_papers} papers)"
        )
        return grouped

    def load_m5(self) -> str:
        """加载模块 5 checkpoint。"""
        path = self.run_dir / "m5_report.md"
        report = path.read_text(encoding="utf-8")
        logger.info(f"📂 Checkpoint loaded: m5_report.md")
        return report

    # ─── 状态汇总 ───────────────────────────────────────────────

    def status_summary(self) -> str:
        """返回当前 checkpoint 状态摘要。"""
        lines = [f"Run ID: {self.run_id}", f"Query: {self.query}", ""]
        for stage in self.STAGES:
            status = "✅" if self.has_checkpoint(stage) else "⬜"
            lines.append(f"  {status} {stage}")
        # 检查部分 m3
        if not self.has_checkpoint("m3_enriched"):
            partial = self.run_dir / "m3_enriched_partial.json"
            if partial.exists():
                data = json.loads(partial.read_text(encoding="utf-8"))
                lines.append(f"      ↳ partial: {len(data)} papers saved")
        resume = self.get_resume_stage()
        if resume:
            lines.append(f"\n  ▶ Resume from: {resume}")
        else:
            lines.append(f"\n  ✅ All stages complete!")
        return "\n".join(lines)

    # ─── 内部方法 ───────────────────────────────────────────────

    def _stage_filename(self, stage: str) -> str:
        if stage == "m5_report":
            return "m5_report.md"
        return f"{stage}.json"

    def _write_json(self, stage: str, data: Any) -> None:
        path = self.run_dir / f"{stage}.json"
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _read_json(self, stage: str) -> Any:
        path = self.run_dir / f"{stage}.json"
        return json.loads(path.read_text(encoding="utf-8"))


# ─── 工具函数 ──────────────────────────────────────────────────

def list_runs() -> List[Tuple[str, str, str]]:
    """列出所有已有的 checkpoint runs。
    Returns: List of (run_id, query, status)
    """
    results = []
    if not CHECKPOINT_DIR.exists():
        return results
    for run_dir in sorted(CHECKPOINT_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        meta_path = run_dir / "meta.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        # 计算完成状态
        completed = sum(
            1 for s in CheckpointManager.STAGES
            if (run_dir / CheckpointManager("", run_id=run_dir.name)._stage_filename(s)).exists()
        )
        total = len(CheckpointManager.STAGES)
        results.append((
            run_dir.name,
            meta.get("query", "?"),
            f"{completed}/{total}",
        ))
    return results
