"""
Search-By-Agent: 高可控轻量级文献综述 Pipeline
═══════════════════════════════════════════════════
主编排器：串联 5 个模块，执行完整的 Query → Report 流水线。
全链路 checkpoint 持久化，支持断点续跑。

用法:
    python main.py "大模型代码生成技术"
    python main.py "大模型代码生成技术" --resume          # 断点续跑
    python main.py --list                                # 列出所有运行记录
    python main.py --status "大模型代码生成技术"           # 查看 checkpoint 状态

环境变量:
    GOOGLE_API_KEY: Gemini API 密钥（必须设置）
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path

from google import genai
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from config import CONFIG
from checkpoint import CheckpointManager, list_runs
from m1_entity_extractor import extract_entities
from m2_fetch_score import fetch_and_score
from m3_map_extract import map_extract
from m4_shuffle_group import shuffle_group
from m5_reduce_report import reduce_report

# ─── 日志配置 ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
)
logger = logging.getLogger("pipeline")

console = Console()


def _init_client() -> genai.Client:
    """初始化 Gemini API 客户端。"""
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print(
            "[bold red]错误: 请设置 GOOGLE_API_KEY 或 GEMINI_API_KEY 环境变量。[/]"
        )
        sys.exit(1)
    return genai.Client(api_key=api_key)


def run_pipeline(query: str, *, resume: bool = False) -> str:
    """执行完整的 5 模块 Pipeline，支持断点续跑。

    Args:
        query: 用户原始搜索请求。
        resume: 是否从上次中断的位置恢复。

    Returns:
        Markdown 格式的文献综述报告。
    """
    client = _init_client()
    start_time = time.time()
    ckpt = CheckpointManager(query)

    # ── 0. 打印全局配置 & Checkpoint 状态 ──────────────────────
    resume_stage = ckpt.get_resume_stage()
    completed = ckpt.get_completed_stages()

    config_info = (
        f"[bold cyan]Search-By-Agent Pipeline[/]\n"
        f"Query: [yellow]{query}[/]\n"
        f"Run ID: [dim]{ckpt.run_id}[/]\n"
        f"Year Range: {CONFIG['search']['min_year']}-{CONFIG['search']['max_year']}\n"
        f"Flash Model: {CONFIG['llm']['flash_model']}\n"
        f"Pro Model: {CONFIG['llm']['pro_model']}\n"
        f"Domain Filter: {CONFIG['filter']['fields_of_study'] or '[dim]all fields[/]'}\n"
        f"Min Citations: {CONFIG['filter']['min_citations']} "
        f"(exempt ≥{CONFIG['filter']['citation_exempt_after_year']})\n"
        f"Citation Expand: {'✅ ' + CONFIG['expand']['direction'] + ' (' + str(CONFIG['expand']['seed_count']) + ' seeds)' if CONFIG['expand']['enabled'] else '[dim]disabled[/]'}"
    )

    if resume and completed:
        config_info += (
            f"\n\n[bold yellow]♻️  Resume Mode[/]\n"
            f"Completed: {', '.join(completed)}\n"
            f"Resume from: [bold]{resume_stage or 'ALL DONE'}[/]"
        )

    console.print(Panel(
        config_info,
        title="⚙️  Global Config",
        border_style="bright_blue",
    ))

    # 如果全部完成且在 resume 模式，直接加载报告
    if resume and resume_stage is None:
        console.print("[bold green]✅ All stages already complete! Loading report...[/]")
        return ckpt.load_m5()

    # 确定从哪个阶段开始
    should_run = _build_stage_plan(resume, resume_stage)

    # ── 1. Query 实体提取 ──────────────────────────────────────
    if should_run("m1_keywords"):
        with Progress(
            SpinnerColumn(), TextColumn("[bold green]模块 1: 提取研究关键词..."),
            console=console,
        ) as progress:
            progress.add_task("", total=None)
            keywords = extract_entities(query, client=client)
        ckpt.save_m1(keywords)
        console.print(f"  ✓ 关键词组: {keywords}\n")
    else:
        keywords = ckpt.load_m1()
        console.print(f"  ♻️  [dim]模块 1 已恢复: {keywords}[/]\n")

    # ── 2. 文献检索与评分 ──────────────────────────────────────
    if should_run("m2_papers"):
        with Progress(
            SpinnerColumn(), TextColumn("[bold green]模块 2: 检索 & 评分论文..."),
            console=console,
        ) as progress:
            progress.add_task("", total=None)
            top_papers = fetch_and_score(keywords)

        if not top_papers:
            console.print("[bold red]未检索到任何论文，流水线终止。[/]")
            return "# 未找到相关文献\n\n检索关键词未匹配到任何论文，请调整查询。"

        ckpt.save_m2(top_papers)
        console.print(f"  ✓ 进入 Map 阶段的论文数: {len(top_papers)}\n")
    else:
        top_papers = ckpt.load_m2()
        console.print(f"  ♻️  [dim]模块 2 已恢复: {len(top_papers)} 篇论文[/]\n")

    # ── 3. Map 阶段（支持增量恢复） ───────────────────────────
    if should_run("m3_enriched"):
        # 检查是否有部分结果可以恢复
        already_done = None
        if resume:
            already_done = ckpt.load_m3_partial()
            if already_done:
                console.print(
                    f"  ♻️  [dim]模块 3 恢复部分结果: "
                    f"{len(already_done)} 篇已完成[/]"
                )

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]模块 3: 并发提取论文要素 (Map)..."),
            console=console,
        ) as progress:
            progress.add_task("", total=None)
            enriched_papers = map_extract(
                top_papers,
                client=client,
                max_workers=5,
                already_done=already_done,
                on_progress=lambda eps: ckpt.save_m3_partial(eps),
                progress_interval=3,
            )

        if not enriched_papers:
            console.print("[bold red]所有论文的 Map 提取均失败，流水线终止。[/]")
            return "# Map 阶段失败\n\n无法提取任何论文的结构化信息。"

        ckpt.save_m3(enriched_papers)
        console.print(f"  ✓ 成功提取要素: {len(enriched_papers)} 篇\n")
    else:
        enriched_papers = ckpt.load_m3()
        console.print(
            f"  ♻️  [dim]模块 3 已恢复: {len(enriched_papers)} 篇论文[/]\n"
        )

    # ── 4. Shuffle 阶段 ───────────────────────────────────────
    if should_run("m4_grouped"):
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]模块 4: 技术流派分类 (Shuffle)..."),
            console=console,
        ) as progress:
            progress.add_task("", total=None)
            grouped = shuffle_group(enriched_papers, client=client)

        ckpt.save_m4(grouped)
        console.print(f"  ✓ 生成 {len(grouped)} 个技术流派:")
        for name, papers in grouped.items():
            console.print(f"    • {name}: {len(papers)} 篇")
        console.print()
    else:
        grouped = ckpt.load_m4()
        console.print(f"  ♻️  [dim]模块 4 已恢复: {len(grouped)} 个技术流派[/]")
        for name, papers in grouped.items():
            console.print(f"    [dim]• {name}: {len(papers)} 篇[/]")
        console.print()

    # ── 5. Reduce 阶段 ────────────────────────────────────────
    if should_run("m5_report"):
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]模块 5: 生成评述报告 (Reduce)..."),
            console=console,
        ) as progress:
            progress.add_task("", total=None)
            report = reduce_report(grouped, query, client=client)

        ckpt.save_m5(report)
    else:
        report = ckpt.load_m5()
        console.print(f"  ♻️  [dim]模块 5 已恢复: 报告已加载[/]\n")

    elapsed = time.time() - start_time
    console.print(
        f"\n[bold green]✓ Pipeline 完成![/] "
        f"耗时: {elapsed:.1f}s, 分析论文: {len(enriched_papers)} 篇"
    )

    return report


def _build_stage_plan(resume: bool, resume_stage: str | None):
    """构建阶段执行计划。返回一个判断函数。

    - 非 resume 模式：所有阶段都执行。
    - resume 模式：已完成的阶段跳过，从 resume_stage 开始执行。
    """
    stages_order = CheckpointManager.STAGES

    if not resume or resume_stage is None:
        # 全部执行
        return lambda stage: True

    resume_idx = stages_order.index(resume_stage)

    def should_run(stage: str) -> bool:
        return stages_order.index(stage) >= resume_idx

    return should_run


def cmd_list_runs():
    """列出所有历史运行记录。"""
    runs = list_runs()
    if not runs:
        console.print("[dim]没有找到任何运行记录。[/]")
        return

    table = Table(title="📋 历史运行记录")
    table.add_column("Run ID", style="cyan", no_wrap=True)
    table.add_column("查询", style="yellow")
    table.add_column("进度", style="green", justify="center")

    for run_id, query, progress in runs:
        table.add_row(run_id, query[:60], progress)

    console.print(table)


def cmd_status(query: str):
    """查看指定查询的 checkpoint 状态。"""
    ckpt = CheckpointManager(query)
    console.print(Panel(
        ckpt.status_summary(),
        title=f"📊 Checkpoint Status",
        border_style="bright_yellow",
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Search-By-Agent: 高可控轻量级文献综述 Pipeline（支持断点续跑）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            '  python main.py "大模型代码生成技术"              # 首次运行\n'
            '  python main.py "大模型代码生成技术" --resume     # 断点续跑\n'
            '  python main.py --list                           # 列出运行记录\n'
            '  python main.py --status "大模型代码生成技术"      # 查看状态\n'
        ),
    )
    parser.add_argument(
        "query",
        type=str,
        nargs="?",
        default=None,
        help="用户研究查询（自然语言）",
    )
    parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="从上次中断处恢复运行",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出 Markdown 文件路径（默认保存到 output/ 目录）",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        dest="list_runs",
        help="列出所有历史运行记录",
    )
    parser.add_argument(
        "--status", "-s",
        type=str,
        default=None,
        metavar="QUERY",
        help="查看指定查询的 checkpoint 状态",
    )

    args = parser.parse_args()

    # ── 特殊命令 ───────────────────────────────────────────────
    if args.list_runs:
        cmd_list_runs()
        return

    if args.status:
        cmd_status(args.status)
        return

    if not args.query:
        parser.print_help()
        return

    # ── 运行 Pipeline ─────────────────────────────────────────
    report = run_pipeline(args.query, resume=args.resume)

    # ── 保存报告 ───────────────────────────────────────────────
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        safe_name = "".join(
            c if c.isalnum() or c in " _-" else "_" for c in args.query
        )[:50]
        output_path = output_dir / f"report_{safe_name}.md"

    output_path.write_text(report, encoding="utf-8")
    console.print(f"\n[bold cyan]📄 报告已保存至: {output_path}[/]")

    # 同时输出到终端
    console.print("\n" + "=" * 60)
    console.print(report)


if __name__ == "__main__":
    main()
