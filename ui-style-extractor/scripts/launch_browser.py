"""
launch_browser.py — 启动 Chromium 并保持运行，等待手动登录
============================================================
运行后浏览器会打开，你可以手动登录任何网站。
登录完成后回来告诉 Claude Code，它会用 collect.py 连接这个浏览器采集数据。

用法：
    python scripts/launch_browser.py
"""

import asyncio
import sys
from playwright.async_api import async_playwright

CDP_PORT = 9222

async def main():
    print(f"""
╔══════════════════════════════════════════════╗
║         Browser Launcher                     ║
║  Chromium 启动后请手动登录目标网站            ║
║  登录完成后回到 Claude Code 继续              ║
╚══════════════════════════════════════════════╝
""")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                f"--remote-debugging-port={CDP_PORT}",
                "--no-first-run",
                "--no-default-browser-check",
                "--window-size=1440,900",
            ],
        )

        # 打开一个初始页面
        context = browser.contexts[0] if browser.contexts else await browser.new_context(
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()
        await page.goto("https://claude.ai")

        print(f"✓ Chromium running on port {CDP_PORT}")
        print(f"✓ Opened: https://claude.ai")
        print(f"")
        print(f"  → 在浏览器里完成登录")
        print(f"  → 登录后回到这里，按 Ctrl+C 结束等待")
        print(f"  → 或者直接告诉 Claude Code 你已经登录好了")
        print(f"")
        print(f"  注意：关掉这个脚本之前，collect.py 都可以复用这个 session")
        print(f"  (保持此窗口运行中...)")

        # 一直等着，直到用户 Ctrl+C
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n[launcher] Closing browser...")
            await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
