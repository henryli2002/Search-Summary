#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# Search-By-Agent 便捷启动脚本
# ═══════════════════════════════════════════════════════════
#
# 用法:
#   ./run.sh "大模型代码生成技术"              # 首次运行
#   ./run.sh "大模型代码生成技术" --resume     # 断点续跑
#   ./run.sh --list                           # 列出运行记录
#   ./run.sh --status "大模型代码生成技术"      # 查看状态
#   ./run.sh --clean                          # 清理所有 checkpoint

set -euo pipefail

# ─── 项目根目录 ────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── 颜色定义 ─────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─── 辅助函数 ─────────────────────────────────────────────
info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ─── 检查 Python ──────────────────────────────────────────
PYTHON=""
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    error "未找到 Python。请安装 Python 3.9+。"
    exit 1
fi

info "使用 Python: $($PYTHON --version)"

# ─── 检查 .env 文件 ───────────────────────────────────────
check_env() {
    if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
        if [[ -f "$SCRIPT_DIR/.env.example" ]]; then
            warn ".env 文件不存在。正在从 .env.example 创建..."
            cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
            error "请编辑 .env 文件填入你的 API Key，然后重新运行。"
            echo ""
            echo "  必填: GOOGLE_API_KEY (Gemini API)"
            echo "  可选: S2AG_API_KEY (Semantic Scholar API)"
            echo ""
            echo "  获取 Gemini API Key: https://aistudio.google.com/apikey"
            exit 1
        else
            error "未找到 .env 或 .env.example 文件。"
            exit 1
        fi
    fi

    # 检查 GOOGLE_API_KEY 是否已设置
    if ! grep -q '^GOOGLE_API_KEY=.' "$SCRIPT_DIR/.env" && [[ -z "${GOOGLE_API_KEY:-}" ]]; then
        error "GOOGLE_API_KEY 未设置。请编辑 .env 文件或设置环境变量。"
        exit 1
    fi
}

# ─── 检查依赖 ─────────────────────────────────────────────
check_deps() {
    if ! $PYTHON -c "import google.genai, pydantic, tenacity, httpx, rich" 2>/dev/null; then
        info "正在安装依赖..."
        $PYTHON -m pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
        info "依赖安装完成。"
    fi
}

# ─── 清理 checkpoint ─────────────────────────────────────
clean_checkpoints() {
    if [[ -d "$SCRIPT_DIR/checkpoints" ]]; then
        echo -e "${YELLOW}将删除所有 checkpoint 数据:${NC}"
        echo "  $SCRIPT_DIR/checkpoints/"
        echo ""
        read -p "确认删除? (y/N) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$SCRIPT_DIR/checkpoints"
            info "所有 checkpoint 已清理。"
        else
            info "取消操作。"
        fi
    else
        info "没有找到 checkpoint 目录。"
    fi
}

# ─── 主逻辑 ───────────────────────────────────────────────
main() {
    # 特殊命令（不需要 env 检查）
    case "${1:-}" in
        --clean|-c)
            clean_checkpoints
            exit 0
            ;;
        --help|-h)
            echo "Search-By-Agent 便捷启动脚本"
            echo ""
            echo "用法:"
            echo "  ./run.sh \"查询内容\"                    # 首次运行"
            echo "  ./run.sh \"查询内容\" --resume           # 断点续跑"
            echo "  ./run.sh \"查询内容\" -o report.md       # 指定输出文件"
            echo "  ./run.sh --list                         # 列出运行记录"
            echo "  ./run.sh --status \"查询内容\"            # 查看 checkpoint 状态"
            echo "  ./run.sh --clean                        # 清理所有 checkpoint"
            echo ""
            exit 0
            ;;
    esac

    check_env
    check_deps

    # 转发所有参数给 Python
    info "启动 Pipeline..."
    echo ""
    $PYTHON "$SCRIPT_DIR/main.py" "$@"
}

main "$@"
