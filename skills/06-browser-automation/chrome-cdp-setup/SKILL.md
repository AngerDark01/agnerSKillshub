---
name: chrome-cdp-setup
description: chrome-cdp 首次安装配置向导。当用户说「安装 chrome-cdp」「配置浏览器调试」「chrome-cdp 报错」「cdp 连不上」时触发。覆盖 Linux/macOS 全部已知坑。
---

# Chrome CDP 安装配置向导

## 快速检查

```bash
# 验证是否已就绪（全部通过则跳过本文档）
node --version          # 需要 v22+
skills/chrome-cdp/scripts/cdp list  # 能列出标签页则配置完成
```

---

## Step 1：安装 Node.js 22+

**坑**：cdp.mjs 使用了 Node 22 内置的 WebSocket，Node 20 及以下会报错 `WebSocket is not defined`。

```bash
# 检查当前版本
node --version

# 如果 < 22，用 nvm 安装（不需要 sudo）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 重新加载 shell（或新开终端）
export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"

# 安装 Node 22
nvm install 22
nvm use 22

# 验证
node --version  # 应显示 v22.x.x
```

> 已安装的 wrapper 脚本 `scripts/cdp` 会自动查找 nvm 里的 Node 22，不需要每次手动 source nvm。

---

## Step 2：启动 Chrome（带远程调试端口）

### 坑一：Chrome 146+ 不允许对默认 Profile 开启远程调试

Chrome 146 引入了安全限制：使用 `--remote-debugging-port` 必须同时指定 `--user-data-dir`，否则报错：

```
DevTools remote debugging requires a non-default data directory.
```

**解决方案**：复制当前 Profile 到临时目录（保留登录态），然后用调试参数启动：

```bash
# Linux
mkdir -p /tmp/chrome-cdp-profile
cp -r ~/.config/google-chrome/Default /tmp/chrome-cdp-profile/
cp ~/.config/google-chrome/"Local State" /tmp/chrome-cdp-profile/ 2>/dev/null || true

WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/$(id -u) \
  google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp-profile \
  2>/dev/null &

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp-profile \
  2>/dev/null &
```

等待 3~5 秒，验证端口已开启：

```bash
curl -s http://127.0.0.1:9222/json/version | head -3
# 应看到 "Browser": "Chrome/..." 字样
```

### 坑二：Chrome 已在运行，新实例被重定向

如果 Chrome 已在运行（没有带调试参数），新启动的实例会把命令转发给旧实例然后退出，导致端口始终不开。

**解决方案**：先完全关闭 Chrome：

```bash
# Linux
pkill -f "/opt/google/chrome/chrome"
sleep 2
# 再执行上面的启动命令
```

---

## Step 3：更新 DevToolsActivePort 文件

cdp.mjs 通过读取 `~/.config/google-chrome/DevToolsActivePort` 文件找到 Chrome 的 WebSocket 地址。

**坑**：使用 `--user-data-dir=/tmp/chrome-cdp-profile` 时，Chrome 不会写默认位置的 DevToolsActivePort 文件，导致 `cdp list` 报错 `No DevToolsActivePort found`。

**解决方案**：手动同步（每次重启 Chrome 后执行一次）：

```bash
# 获取新会话的 WebSocket 路径
WS_PATH=$(curl -s http://127.0.0.1:9222/json/version | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d['webSocketDebuggerUrl'].split('9222')[1])")

# 写入默认位置
mkdir -p ~/.config/google-chrome
printf "9222\n%s" "$WS_PATH" > ~/.config/google-chrome/DevToolsActivePort

# 验证
cat ~/.config/google-chrome/DevToolsActivePort
```

---

## Step 4：验证

```bash
skills/chrome-cdp/scripts/cdp list
```

应输出类似：
```
A1B2C3D4  My Page Title    https://example.com
```

如果输出为空（无标签），检查 Chrome 里是否有普通页面（非 chrome:// 页面）打开。

---

## Step 5：「允许调试？」弹框机制

**规则：每个 tab，每次启动 Chrome，弹一次。**

- cdp 首次访问某个 tab 时，Chrome 弹出「允许调试？」，需手动点「允许」
- 点击后，后台 daemon 保持该 tab 的 WebSocket 连接，**后续所有命令不再弹框**
- 使用 `nav` 在同一个 tab 内跳转多个页面 → 全程只弹一次
- 使用 `open` 开新 tab → 每个新 tab 各弹一次

**最佳实践**：分析流程中用 `nav` 跳转，不用 `open`，整个 workflow 只弹一次。

**什么时候会再弹：**
1. 重启 Chrome（所有 daemon 清空，下次各 tab 各弹一次）
2. daemon 超时（pack 已改为 8 小时，正常使用不会遇到）

**不是 bug**，是 Chrome 的安全设计，无法完全消除，只能通过上述方式最小化。

---

## 常见报错速查

| 报错信息 | 原因 | 解决 |
|---------|------|------|
| `WebSocket is not defined` | Node < 22 | `nvm install 22 && nvm use 22` |
| `No DevToolsActivePort found` | Chrome 未开调试端口，或文件路径不对 | 执行 Step 2 + Step 3 |
| `DevTools remote debugging requires a non-default data directory` | Chrome 146+ 限制 | 加 `--user-data-dir` 参数（Step 2） |
| `WebSocket error: Received network error or non-101 status code` | DevToolsActivePort 文件内容是旧会话 | 重新执行 Step 3 |
| `No target matching prefix "..."` | targetId 前缀错误或不足 8 位 | 重新执行 `cdp list` 复制正确的前缀 |
| 端口连接被拒绝 | Chrome 用了旧 profile 启动（被重定向） | 先 `pkill chrome`，再启动 |
