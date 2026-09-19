#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""git-cloner-v2.html 修正后回归核查（只读：临时目录 + stub API + headless Chrome）。

覆盖审计清单之外的行为面：size 千分位文本 / range 深色样式 / ⚙️ 列开关 / Esc 退出分栏 /
?split 与 ?range 直接加载 / info 失败错误条 / README 弹窗深色 / localStorage 键隔离 / JS 错误。

用法: /usr/bin/python3 scripts/git-cloner-v2-postfix-check.py [--target <html>]
"""
import argparse
import functools
import http.server
import json
import shutil
import socket
import tempfile
import threading
import time
from pathlib import Path

sys_stub = None  # noqa: F841 (占位, 保持与审计脚本同风格)

STUB_ITEMS = [
    {"label": "alpha-tool", "path": "~/CodeSpace/clone/beta-dir",
     "github": "https://github.com/acme/repo-one", "size": "1234KB", "time": "2026-09-17 16:21"},
    {"label": "gamma-kit", "path": "~/CodeSpace/clone/delta-dir",
     "github": "https://github.com/acme/repo-two", "size": "7KB", "time": "2026-09-16 10:02"},
    {"label": "epsilon-lib", "path": "~/CodeSpace/clone/zeta-dir",
     "github": "https://github.com/acme/repo-three", "size": "-", "time": "2026-09-15 09:00"},
]
STUB_INFO = {
    "success": True, "command": "git-cloner-info", "error": "",
    "data": {"label": "alpha-tool", "github": "https://github.com/acme/repo-one",
             "path": "~/CodeSpace/clone/beta-dir", "clone_time": "2026-09-17 16:21",
             "stats": {"files": 42, "language": "Python", "stars": 1200, "forks": 88,
                       "watchers": 12, "open_issues": 3, "description": "a demo repo",
                       "license": "MIT", "last_commit": "2026-09-10"},
             "sync": {"commits_behind": 2, "has_conflicts": False}},
}
CHROMEDRIVER = "/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver"


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="/Users/jadenli/CodeSpace/script-miner/efficiency/git-cloner-v2.html")
    args = ap.parse_args()
    target = Path(args.target).expanduser()

    tmp = Path(tempfile.mkdtemp(prefix="gc-v2-check-"))
    shutil.copy(target, tmp / "page.html")
    api = tmp / "api" / "tool-data" / "git-cloner"
    api.mkdir(parents=True, exist_ok=True)
    (api / "list").write_text(json.dumps(
        {"success": True, "command": "git-cloner-list", "error": "",
         "data": {"count": len(STUB_ITEMS), "items": STUB_ITEMS, "range": "today"}},
        ensure_ascii=False), encoding="utf-8")
    (api / "info").write_text(json.dumps(STUB_INFO, ensure_ascii=False), encoding="utf-8")
    port = free_port()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(tmp))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}/page.html"

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1600,1000")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    d = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    def js(e):
        return d.execute_script("return " + e)

    def run(e):
        return d.execute_script(e)

    def heads():
        return [x.text.strip() for x in d.find_elements(By.CSS_SELECTOR, "#thead th")]

    res = {}

    def check(name, cond, detail=None):
        res[name] = {"pass": bool(cond), "detail": "" if detail is None else str(detail)[:200]}
        print(("  ✅ " if cond else "  ❌ ") + name + ("" if cond else f"  [{res[name]['detail']}]"), flush=True)
    try:
        d.get(url)
        WebDriverWait(d, 10).until(lambda x: len(x.find_elements(By.CSS_SELECTOR, "#tbody tr")) > 0)
        time.sleep(0.6)

        check("默认 5 列", heads() == ["项目", "GITHUB", "大小 (KB)", "时间", "操作"], heads())
        check("size 千分位 1,234", d.find_element(By.CSS_SELECTOR, "#tbody tr td:nth-child(3)").text == "1,234",
              d.find_element(By.CSS_SELECTOR, "#tbody tr td:nth-child(3)").text)
        check("size 空值行显示空", d.find_elements(By.CSS_SELECTOR, "#tbody tr")[2]
              .find_elements(By.CSS_SELECTOR, "td")[2].text == "",
              d.find_elements(By.CSS_SELECTOR, "#tbody tr")[2].find_elements(By.CSS_SELECTOR, "td")[2].text)
        tabs_bg = js("getComputedStyle(document.querySelector('.range-tab')).backgroundColor")
        check("range tab 深色（非浅底）", tabs_bg not in ("rgb(248, 249, 250)", "rgba(0, 0, 0, 0)"), tabs_bg)

        # 搜索项目名
        run("var el=document.getElementById('searchInput');el.value='alpha-tool';el.dispatchEvent(new Event('input'));")
        time.sleep(0.8)
        check("搜项目名命中 1 行", len(d.find_elements(By.CSS_SELECTOR, "#tbody tr")) == 1)
        run("var el=document.getElementById('searchInput');el.value='';el.dispatchEvent(new Event('input'));")
        time.sleep(0.8)

        # 点项目名 → 分栏
        d.find_elements(By.CSS_SELECTOR, "#tbody tr td")[0].click()
        WebDriverWait(d, 10).until(lambda x: x.execute_script("return !!window.splitActive"))
        time.sleep(1.2)
        check("分栏态表头 = 项目/操作", heads() == ["项目", "操作"], heads())
        check("分栏详情 17 字段", len(d.find_elements(By.CSS_SELECTOR, "#splitPreviewBody .kv-label")) == 17,
              len(d.find_elements(By.CSS_SELECTOR, "#splitPreviewBody .kv-label")))

        # Esc 退出分栏
        d.find_element(By.TAG_NAME, "body").send_keys("\ue00c")
        time.sleep(0.6)
        check("Esc 退出分栏", not js("!!window.splitActive"))

        # ⚙️ 开启本地路径列
        d.find_element(By.ID, "colToggleBtn").click()
        time.sleep(0.4)
        for cb in d.find_elements(By.CSS_SELECTOR, "#colToggleDropdown input[type=checkbox]"):
            parent = cb.find_element(By.XPATH, "./..")
            if parent.tag_name == "label" and parent.text == "本地路径" and not cb.is_selected():
                cb.click()
                break
        time.sleep(0.6)
        check("⚙️ 开启 path 列后可见", "本地路径" in heads(), heads())
        d.execute_script("window.toggleCol('path', false);")
        time.sleep(0.4)

        # range → URL + 分享链接
        js("window.selectRange('all')")
        time.sleep(1.2)
        check("切 range → URL 含 range=all", "range=all" in js("location.search"), js("location.search"))
        check("分享链接含 range=all", "range=all" in js("window.buildShareUrl()"), js("window.buildShareUrl()"))
        js("window.selectRange('today')")
        time.sleep(1.0)

        # README 弹窗（深色）
        run("var dd=document.getElementById('colToggleDropdown'); if(dd) dd.classList.remove('show');")
        time.sleep(0.2)
        btn = d.find_element(By.CSS_SELECTOR, "#tbody tr td:last-child button[title='README']")
        btn.click()
        time.sleep(0.5)
        modal_bg = js("getComputedStyle(document.querySelector('.gc-modal-content')).backgroundColor")
        check("README 弹窗打开且深色", js("getComputedStyle(document.getElementById('readmeModal')).display") == "block"
              and modal_bg not in ("rgb(254, 254, 254)",), modal_bg)
        js("window.closeReadmeModal()")
        time.sleep(0.3)

        # info 失败 → 错误条
        run("""window.__origFetch = window.fetch;
              window.fetch = function(u){ if(String(u).indexOf('/info') !== -1){
                  return Promise.resolve({json:function(){return Promise.resolve({success:false,error:'stub 失败'});}});
              } return window.__origFetch.apply(window, arguments); };""")
        d.find_elements(By.CSS_SELECTOR, "#tbody tr td")[0].click()
        time.sleep(1.2)
        banner = d.find_elements(By.CSS_SELECTOR, "#splitPreviewBody .gc-info-error")
        check("info 失败显示错误条", bool(banner) and "stub 失败" in banner[0].text,
              banner[0].text if banner else "无")
        js("window.fetch = window.__origFetch;")

        # localStorage 键隔离
        run("window.setDensity('compact'); window.toggleCol('path', true);")
        time.sleep(0.5)
        keys = js("Object.keys(localStorage)")
        check("localStorage 键全部 git-cloner: 前缀", all(k.startswith("git-cloner:") for k in keys), keys)
        check("无 html-gen:table: 残留键", not any(k.startswith("html-gen:table:") for k in keys), keys)

        # ?range / ?split 直接加载
        d.get(url + "?range=all")
        WebDriverWait(d, 10).until(lambda x: len(x.find_elements(By.CSS_SELECTOR, "#tbody tr")) > 0)
        time.sleep(0.8)
        check("?range=all 恢复激活态",
              d.find_element(By.CSS_SELECTOR, ".range-tab.active").text == "所有",
              d.find_element(By.CSS_SELECTOR, ".range-tab.active").text)
        d.get(url + "?split=0")
        WebDriverWait(d, 10).until(lambda x: x.execute_script("return !!window.splitActive"))
        time.sleep(1.0)
        check("?split=0 直接加载进入分栏", js("!!window.splitActive") and heads() == ["项目", "操作"], heads())

        # README iframe 指向 git-cloner/<repo>/README.md.html，stub 环境必然 404 → 只统计 JS 错误本身
        severe = [e["message"] for e in d.get_log("browser")
                  if e["level"] == "SEVERE" and "Failed to load resource" not in e["message"]]
        check("全程无 SEVERE JS 错误（排除 stub 环境 iframe 404）", not severe, severe[:3])

        d.save_screenshot("/tmp/git-cloner-v2-split.png")
    finally:
        d.quit()
        httpd.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"目标: {target}\n截图: /tmp/git-cloner-v2-split.png")
    npass = 0
    for name, r in res.items():
        npass += r["pass"]
        print(("  ✅ " if r["pass"] else "  ❌ ") + name + (f"  [{r['detail']}]" if not r["pass"] else ""))
    print(f"\n结果: {npass}/{len(res)} 通过")
    return 0 if npass == len(res) else 1


if __name__ == "__main__":
    raise SystemExit(main())
