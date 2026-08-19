#!/usr/bin/env bash
# install.sh — 注册 html-gen 为系统命令（对齐 release-local.sh 入参模式）
# 用法: bash install.sh [options]（无参数默认显示帮助）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GEN_PY="$SCRIPT_DIR/html-gen.py"
BIN_DIR="${HOME}/.local/bin"
LINK_PATH="$BIN_DIR/html-gen"
PYTHON_BIN="python3"

DO_INSTALL=0
DO_UNINSTALL=0
DO_STATUS=0
DRY_RUN=0
VERBOSE=0
SHOW_HELP=0
HAS_ARGS=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--install|install)
            DO_INSTALL=1; HAS_ARGS=1; shift ;;
        -u|--uninstall)
            DO_UNINSTALL=1; HAS_ARGS=1; shift ;;
        -s|--status)
            DO_STATUS=1; HAS_ARGS=1; shift ;;
        -p|--prefix)
            BIN_DIR="$2"; LINK_PATH="$BIN_DIR/html-gen"; HAS_ARGS=1; shift 2 ;;
        -n|--dry-run)
            DRY_RUN=1; HAS_ARGS=1; shift ;;
        -v|--verbose)
            VERBOSE=1; HAS_ARGS=1; shift ;;
        -h|--help|help|*)
            SHOW_HELP=1; HAS_ARGS=1; shift ;;
    esac
done

# 无参数时显示帮助（对齐治理规范"无参数默认 help"）
if [[ $HAS_ARGS -eq 0 ]]; then
    SHOW_HELP=1
fi

# --help 优先
if [[ $SHOW_HELP -eq 1 ]]; then
    echo "Usage: bash install.sh [options]"
    echo ""
    echo "html-gen 全局命令注册脚本 — 安装/卸载/状态"
    echo ""
    echo "Options:"
    echo "  -i, --install       安装（注册 \$HOME/.local/bin/html-gen wrapper）"
    echo "  -u, --uninstall     卸载（移除注册）"
    echo "  -s, --status        查看注册状态（wrapper / PATH）"
    echo "  -p, --prefix <dir>  安装目录（默认 \$HOME/.local/bin）"
    echo "  -n, --dry-run       预览将执行的命令（不实际执行）"
    echo "  -v, --verbose       详细输出"
    echo "  -h, --help          显示帮助（无参数时默认显示）"
    echo ""
    echo "无参数行为: 显示帮助（同 release-local.sh）"
    echo "注册后需确保 \$HOME/.local/bin 在 PATH:"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc"
    exit 0
fi

run() {
    if [[ $DRY_RUN -eq 1 ]]; then
        echo "  [dry-run] $*"
    else
        "$@"
    fi
}

if [[ $DO_STATUS -eq 1 ]]; then
    echo "📋 html-gen 注册状态"
    if [[ -L "$LINK_PATH" || -f "$LINK_PATH" ]]; then
        echo "  ✅ 已注册: $LINK_PATH"
        if head -3 "$LINK_PATH" 2>/dev/null | grep -q 'html-gen.py'; then
            target=$(grep -o '"[^"]*html-gen.py"' "$LINK_PATH" | tr -d '"' || echo '?')
            echo "  → 目标: $target"
        fi
    else
        echo "  ⚠️  未注册: $LINK_PATH"
    fi
    if echo "$PATH" | grep -q "$BIN_DIR"; then
        echo "  ✅ $BIN_DIR 已在 PATH"
    else
        echo "  ⚠️  $BIN_DIR 不在 PATH（zshrc 添加后 source）"
    fi
    if [[ -f "$GEN_PY" ]]; then
        echo "  ✅ 源码: $GEN_PY"
    else
        echo "  ❌ 源码缺失: $GEN_PY"
    fi
    exit 0
fi

if [[ $DO_UNINSTALL -eq 1 ]]; then
    if [[ -L "$LINK_PATH" || -f "$LINK_PATH" ]]; then
        run rm "$LINK_PATH"
        echo "✅ 已移除: $LINK_PATH"
    else
        echo "⚠️  未找到: $LINK_PATH"
    fi
    exit 0
fi

# 默认动作: 安装
if [[ $DO_INSTALL -eq 1 || $HAS_ARGS -eq 1 ]]; then
    run mkdir -p "$BIN_DIR"
    run chmod +x "$GEN_PY"

    # 创建 wrapper（非软链 — 确保正确 python）
    run bash -c "cat > \"$LINK_PATH\" << 'WRAPPER'
#!/usr/bin/env bash
exec $PYTHON_BIN \"$GEN_PY\" \"\$@\"
WRAPPER"
    run chmod +x "$LINK_PATH"

    if [[ $VERBOSE -eq 1 || $DRY_RUN -eq 1 ]]; then
        if [[ $DRY_RUN -eq 1 ]]; then
            echo "🔍 已预览（dry-run，未实际安装）: $LINK_PATH → $GEN_PY"
        else
            echo "✅ 已安装: $LINK_PATH → $GEN_PY"
        fi
        if echo "$PATH" | grep -q "$BIN_DIR"; then
            echo "  ✅ $BIN_DIR 已在 PATH 中"
        else
            echo "  ⚠️  $BIN_DIR 不在 PATH 中，请手动添加"
        fi
    fi
    exit 0
fi

echo "⚠️  未指定动作（bash install.sh --help 查看）"
exit 1
