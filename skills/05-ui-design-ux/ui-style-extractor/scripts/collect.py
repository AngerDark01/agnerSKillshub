"""
collect.py — 纯 Playwright 数据采集工具（无 LLM）
=================================================
这是 Claude Code 的"手"——机械执行，不做判断。
判断和分析由 Claude Code 本身完成。

用法：
    python scripts/collect.py screenshot <url> <output_path> [--full]
    python scripts/collect.py css <url> <output_path>
    python scripts/collect.py click <url> <selector> <screenshot_output>
    python scripts/collect.py hover <url> <selector> <screenshot_output>
    python scripts/collect.py scroll <url> <position:top|middle|bottom> <screenshot_output>
    python scripts/collect.py multi <url> <output_dir>   # 一次采集多个截图+CSS

所有命令都尝试连接 localhost:9222（已打开的 Chrome）。
如果没有，自动用 Playwright 内置 Chromium 新开浏览器。
"""

import asyncio
import json
import sys
import os
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser

CDP_URL = "http://localhost:9222"
CSS_JS = (Path(__file__).parent / "css_injector.js").read_text(encoding="utf-8")


async def get_browser(playwright):
    """优先连接已打开的 Chrome，否则启动新浏览器"""
    try:
        browser = await playwright.chromium.connect_over_cdp(CDP_URL)
        print(f"[collect] Connected to existing Chrome at {CDP_URL}", flush=True)
        return browser, "cdp"
    except Exception:
        print("[collect] No Chrome on 9222, launching new Chromium...", flush=True)
        browser = await playwright.chromium.launch(headless=False)
        return browser, "new"


async def get_page(browser, mode: str, url: str) -> Page:
    """获取页面并导航到 URL"""
    if mode == "cdp":
        contexts = browser.contexts
        if contexts and contexts[0].pages:
            page = contexts[0].pages[0]
        else:
            context = await browser.new_context()
            page = await context.new_page()
    else:
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()

    await page.goto(url, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(1500)  # 等动画/懒加载
    return page


# ─── 命令实现 ────────────────────────────────────────────────────────────────

async def cmd_screenshot(url: str, output_path: str, full_page: bool = False):
    async with async_playwright() as p:
        browser, mode = await get_browser(p)
        page = await get_page(browser, mode, url)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=output_path, full_page=full_page)
        print(f"[collect] Screenshot saved: {output_path}", flush=True)
        if mode == "new":
            await browser.close()


async def cmd_css(url: str, output_path: str):
    async with async_playwright() as p:
        browser, mode = await get_browser(p)
        page = await get_page(browser, mode, url)
        raw = await page.evaluate(CSS_JS)
        data = json.loads(raw)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[collect] CSS tokens saved: {output_path}", flush=True)
        print(f"[collect] Variables: {len(data.get('cssVariables', {}))}, Colors: {len(data.get('colors', []))}", flush=True)
        if mode == "new":
            await browser.close()


async def cmd_click(url: str, selector: str, output_path: str):
    """点击元素后截图（用于探索交互状态）"""
    async with async_playwright() as p:
        browser, mode = await get_browser(p)
        page = await get_page(browser, mode, url)
        try:
            await page.click(selector, timeout=5000)
            await page.wait_for_timeout(800)
        except Exception as e:
            print(f"[collect] Click failed ({selector}): {e}", flush=True)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=output_path, full_page=False)
        print(f"[collect] Click screenshot saved: {output_path}", flush=True)
        if mode == "new":
            await browser.close()


async def cmd_hover(url: str, selector: str, output_path: str):
    """hover 元素后截图（用于探索 hover 样式）"""
    async with async_playwright() as p:
        browser, mode = await get_browser(p)
        page = await get_page(browser, mode, url)
        try:
            await page.hover(selector, timeout=5000)
            await page.wait_for_timeout(400)
        except Exception as e:
            print(f"[collect] Hover failed ({selector}): {e}", flush=True)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=output_path)
        print(f"[collect] Hover screenshot saved: {output_path}", flush=True)
        if mode == "new":
            await browser.close()


async def cmd_scroll(url: str, position: str, output_path: str):
    """滚动到指定位置截图"""
    async with async_playwright() as p:
        browser, mode = await get_browser(p)
        page = await get_page(browser, mode, url)
        scroll_map = {"top": 0, "middle": 0.5, "bottom": 1.0}
        ratio = scroll_map.get(position, 0)
        if ratio > 0:
            height = await page.evaluate("document.body.scrollHeight")
            await page.evaluate(f"window.scrollTo(0, {int(height * ratio)})")
            await page.wait_for_timeout(600)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=output_path)
        print(f"[collect] Scroll({position}) screenshot saved: {output_path}", flush=True)
        if mode == "new":
            await browser.close()


async def cmd_multi(url: str, output_dir: str):
    """一次采集：viewport截图 + 全页截图 + CSS tokens"""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser, mode = await get_browser(p)
        page = await get_page(browser, mode, url)

        # viewport 截图
        await page.screenshot(path=str(out / "viewport.png"), full_page=False)
        print(f"[collect] viewport.png saved", flush=True)

        # 滚动到中间截图
        height = await page.evaluate("document.body.scrollHeight")
        await page.evaluate(f"window.scrollTo(0, {height // 2})")
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(out / "middle.png"))
        print(f"[collect] middle.png saved", flush=True)

        # 全页截图
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(out / "fullpage.png"), full_page=True)
        print(f"[collect] fullpage.png saved", flush=True)

        # CSS tokens
        raw = await page.evaluate(CSS_JS)
        data = json.loads(raw)
        css_path = out / "css_tokens.json"
        css_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[collect] css_tokens.json saved ({len(data.get('cssVariables',{}))} vars)", flush=True)

        # 页面基本信息
        info = {
            "url": page.url,
            "title": await page.title(),
            "viewport_height": await page.evaluate("window.innerHeight"),
            "total_height": height,
        }
        (out / "page_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        print(f"[collect] page_info.json saved", flush=True)

        if mode == "new":
            await browser.close()


# ─── CLI 入口 ────────────────────────────────────────────────────────────────

def usage():
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        usage()

    cmd = args[0]

    if cmd == "screenshot" and len(args) >= 3:
        full = "--full" in args
        asyncio.run(cmd_screenshot(args[1], args[2], full))

    elif cmd == "css" and len(args) >= 3:
        asyncio.run(cmd_css(args[1], args[2]))

    elif cmd == "click" and len(args) >= 4:
        asyncio.run(cmd_click(args[1], args[2], args[3]))

    elif cmd == "hover" and len(args) >= 4:
        asyncio.run(cmd_hover(args[1], args[2], args[3]))

    elif cmd == "scroll" and len(args) >= 4:
        asyncio.run(cmd_scroll(args[1], args[2], args[3]))

    elif cmd == "multi" and len(args) >= 3:
        asyncio.run(cmd_multi(args[1], args[2]))

    else:
        usage()
