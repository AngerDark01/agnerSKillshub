#!/usr/bin/env bash
# ─── 用远程调试端口启动 Chrome ────────────────────────────────────────────────
# 已登录的账号、Cookie、扩展全部保留（复用你现有的 Chrome profile）
#
# 使用方法：
#   ./launch_chrome.sh              # 用默认 profile 启动
#   ./launch_chrome.sh --fresh      # 用临时空 profile 启动（干净环境）

DEBUGPORT=9222

# ── 检查端口是否已被占用 ──────────────────────────────────────────────────────
if curl -s "http://localhost:$DEBUGPORT/json/version" > /dev/null 2>&1; then
    echo "✓ Chrome already running with debug port $DEBUGPORT"
    echo "  (Existing session detected — your logins are available)"
    exit 0
fi

# ── 检测 Chrome 路径 ──────────────────────────────────────────────────────────
if [[ "$OSTYPE" == "msys" || "$OS" == "Windows_NT" ]]; then
    CHROME_PATHS=(
        "/c/Program Files/Google/Chrome/Application/chrome.exe"
        "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        "$LOCALAPPDATA/Google/Chrome/Application/chrome.exe"
    )
elif [[ "$OSTYPE" == "darwin"* ]]; then
    CHROME_PATHS=(
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        "/Applications/Chromium.app/Contents/MacOS/Chromium"
    )
else
    CHROME_PATHS=(
        "/usr/bin/google-chrome"
        "/usr/bin/chromium-browser"
        "/usr/bin/chromium"
    )
fi

CHROME=""
for path in "${CHROME_PATHS[@]}"; do
    if [ -f "$path" ]; then
        CHROME="$path"
        break
    fi
done

if [ -z "$CHROME" ]; then
    echo "❌ Chrome not found. Install Google Chrome or set CHROME_PATH."
    echo "   export CHROME_PATH=\"/path/to/chrome\""
    exit 1
fi

echo "🚀 Launching Chrome with remote debugging on port $DEBUGPORT"
echo "   Binary: $CHROME"

if [[ "$1" == "--fresh" ]]; then
    # 临时 profile（不携带登录状态）
    TMPDIR=$(mktemp -d)
    echo "   Profile: fresh temp profile at $TMPDIR"
    "$CHROME" \
        --remote-debugging-port=$DEBUGPORT \
        --user-data-dir="$TMPDIR" \
        --no-first-run \
        --disable-default-apps \
        about:blank &
else
    # 使用你现有的 Chrome profile（保留所有登录状态）
    echo "   Profile: your existing Chrome profile (logins preserved)"
    "$CHROME" \
        --remote-debugging-port=$DEBUGPORT \
        --no-first-run \
        about:blank &
fi

# 等待 Chrome 启动
sleep 2
if curl -s "http://localhost:$DEBUGPORT/json/version" > /dev/null 2>&1; then
    echo "✓ Chrome ready at http://localhost:$DEBUGPORT"
    echo ""
    echo "Now run:"
    echo "  python scripts/collect.py multi \"https://target-product.com\" output/manual_run"
else
    echo "⚠  Chrome may still be starting. If it fails, try:"
    echo "   curl http://localhost:$DEBUGPORT/json/version"
fi
