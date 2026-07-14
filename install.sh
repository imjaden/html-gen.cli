#!/usr/bin/env bash
# install.sh — 注册 html-gen 为系统命令
# 用法: bash install.sh [--uninstall]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GEN_PY="$SCRIPT_DIR/html-gen.py"
BIN_DIR="${HOME}/.local/bin"
LINK_PATH="$BIN_DIR/html-gen"

uninstall() {
    if [[ -L "$LINK_PATH" ]]; then
        rm "$LINK_PATH"
        echo "✅ 已移除: $LINK_PATH"
    elif [[ -f "$LINK_PATH" ]]; then
        rm "$LINK_PATH"
        echo "✅ 已移除: $LINK_PATH"
    else
        echo "⚠️  未找到: $LINK_PATH"
    fi
}

install() {
    mkdir -p "$BIN_DIR"

    # Ensure html-gen.py is executable
    chmod +x "$GEN_PY"

    # Create wrapper script (not symlink — ensures correct python)
    cat > "$LINK_PATH" << 'WRAPPER'
#!/usr/bin/env bash
exec python3 "/Users/jadenli/CodeSpace/html-gen/html-gen.py" "$@"
WRAPPER
    # Replace the hardcoded path with the actual script dir
    sed -i '' "s|/Users/jadenli/CodeSpace/html-gen|$SCRIPT_DIR|g" "$LINK_PATH"
    chmod +x "$LINK_PATH"

    echo "✅ 已安装: $LINK_PATH → $GEN_PY"
    echo ""
    echo "确保 $BIN_DIR 在 PATH 中:"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"

    # Check if already in PATH
    if echo "$PATH" | grep -q "$BIN_DIR"; then
        echo "  ✅ $BIN_DIR 已在 PATH 中"
    else
        echo "  ⚠️  $BIN_DIR 不在 PATH 中，请手动添加"
    fi
}

if [[ "${1:-}" == "--uninstall" ]]; then
    uninstall
else
    install
fi
