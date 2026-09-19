#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""git-cloner.html 的 html-gen table 规范符合性只读审计（跨项目探针, 不修改目标仓）。

用途：对着 script-miner/efficiency/git-cloner.html 复跑「规范不符合」判据。
做法：把目标 html 复制到临时目录 + 造 stub API（list/info）→ 本地 http.server → Selenium headless 断言。
零写目标仓（只读源文件）。

用法：
  /usr/bin/python3 scripts/git-cloner-table-spec-audit.py \
      --target /Users/jadenli/CodeSpace/script-miner/efficiency/git-cloner.html \
      [--generator /Users/jadenli/CodeSpace/script-miner/efficiency/git-cloner.py] [--json]

判据（对应 HTML-GEN 审计记录 GITCLONER-SPEC-20260917）：
  C1 正常态表头 = 项目/GITHUB/大小/时间/操作（path initialHidden 默认收起）
  C2 分栏态左侧表头 = 仅「操作」（columnsSplit 键名非法 ⇒ 规范不符合, 期望 = 项目/操作 或 preview 列集）
  C3 搜索项目名命中 0 行（searchFields 含非法键 'name' ⇒ 规范不符合, 期望 = 命中 label 行）
  C4 搜索 github / path 片段命中 1 行（证明 searchFields 生效但键错）
  C5 ?split=0 打开不进入分栏（动态数据下 split 恢复失效）
  C6 ?q=xxx 打开可恢复并过滤
  C7 size 单元格显示 "1234KB"（number 列 + format=thousands 未生效）
  C8 无 SEVERE JS 错误
  C9 localStorage 键前缀（git-cloner-range + html-gen:table:* 混用）
  C10 生成器输出 vs 仓库产物（可选, --generator）：无 const COLUMNS ⇒ 生成器会覆盖回旧版
"""
import argparse
import functools
import http.server
import importlib.util
import json
import re
import shutil
import socket
import tempfile
import threading
from pathlib import Path

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


def start_server(root):
    port = free_port()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def static_checks(target, generator):
    html = target.read_text(encoding="utf-8")
    out = {
        "target_bytes": len(html),
        "has_runtime_columns": "const COLUMNS" in html,
        "has_data_table": 'class="data-table"' in html,
        "has_old_clonerTbody": "clonerTbody" in html,
        "ls_prefixes": sorted(set(re.findall(r"localStorage\.(?:get|set)Item\('([^']+)'", html))),
        "opt_blocks": re.findall(r"const OPTIONS = \{(.*?)\};", html, re.S),
        "tabs_empty": bool(re.search(r"const TABS\s*=\s*\[\s*\]", html)),
        "hardcoded_title_const": "const TITLE" in html and "const SUBTITLE" in html,
        "light_ui_colors": sorted(set(re.findall(r"#(?:f8f9fa|fefefe|0366d6|e9ecef)\b", html, re.I))),
    }
    if generator and generator.exists():
        spec = importlib.util.spec_from_file_location("gc_audit_mod", generator)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cls = next(v for v in vars(mod).values()
                   if isinstance(v, type) and hasattr(v, "_generate_html_table"))()
        gen = cls._generate_html_table([])
        out["generator"] = {
            "path": str(generator),
            "bytes": len(gen),
            "has_const_COLUMNS": "const COLUMNS" in gen,
            "has_clonerTbody": "clonerTbody" in gen,
            "title": (re.search(r"<title>(.*?)</title>", gen) or [None, None])[1],
            "overwrites_target": "const COLUMNS" not in gen,
        }
    return out


def browser_checks(url: str, port: int) -> dict:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    import time

    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1600,1000")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    d = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)
    out = {}

    def js(e):
        return d.execute_script("return " + e)

    def heads():
        return [e.text.strip() for e in d.find_elements(By.CSS_SELECTOR, "#thead th")]

    def rows():
        return len(d.find_elements(By.CSS_SELECTOR, "#tbody tr"))

    def search(q):
        d.execute_script(
            "var el=document.getElementById('searchInput');el.value=arguments[0];"
            "el.dispatchEvent(new Event('input'));", q)
        time.sleep(0.8)
        return rows()

    try:
        d.get(url)
        WebDriverWait(d, 10).until(lambda x: len(x.find_elements(By.CSS_SELECTOR, "#tbody tr")) > 0)
        out["C1_normal_headers"] = heads()
        out["rows_loaded"] = rows()
        out["size_cell"] = d.find_element(By.CSS_SELECTOR, "#tbody tr td:nth-child(3)").text
        out["C3_search_label"] = search("alpha-tool")
        out["C4_search_github"] = search("repo-one")
        out["C4b_search_path"] = search("beta-dir")
        search("")
        d.execute_script("window.openSplitAt(0,'label');")
        time.sleep(1.2)
        out["C2_split_headers"] = heads()
        out["split_detail_fields"] = len(d.find_elements(By.CSS_SELECTOR, "#splitPreviewBody .kv-label"))
        out["url_after_split"] = js("location.search")
        out["C9_ls_keys"] = js("Object.keys(localStorage)")
        # C11: range 是否进 URL（切 range 后 replaceState + 分享链接含 range）
        js("window.selectRange('all')")
        time.sleep(1.2)
        out["C11_url_after_range"] = js("location.search")
        out["C11_share_url"] = js("window.buildShareUrl ? window.buildShareUrl() : ''")
        out["C8_js_errors"] = [e["message"] for e in d.get_log("browser") if e["level"] == "SEVERE"]

        d.get(url + "?q=repo-one")
        WebDriverWait(d, 10).until(lambda x: len(x.find_elements(By.CSS_SELECTOR, "#tbody tr")) > 0)
        time.sleep(1.2)
        out["C6_q_restore_rows"] = rows()
        d.get(url + "?split=0")
        WebDriverWait(d, 10).until(lambda x: len(x.find_elements(By.CSS_SELECTOR, "#tbody tr")) > 0)
        time.sleep(1.5)
        out["C5_split_restore_active"] = js("!!window.splitActive")
        return out
    finally:
        d.quit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="/Users/jadenli/CodeSpace/script-miner/efficiency/git-cloner.html")
    ap.add_argument("--generator", default=None,
                    help="git-cloner.py 路径（给出则附加生成器 vs 产物静态比对）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    target = Path(args.target).expanduser()
    tmp = Path(tempfile.mkdtemp(prefix="gc-spec-audit-"))
    shutil.copy(target, tmp / "git-cloner.html")
    api = tmp / "api" / "tool-data" / "git-cloner"
    api.mkdir(parents=True, exist_ok=True)
    (api / "list").write_text(json.dumps(
        {"success": True, "command": "git-cloner-list", "error": "",
         "data": {"count": len(STUB_ITEMS), "items": STUB_ITEMS, "range": "today"}},
        ensure_ascii=False), encoding="utf-8")
    (api / "info").write_text(json.dumps(STUB_INFO, ensure_ascii=False), encoding="utf-8")

    httpd, port = start_server(tmp)
    report = {"target": str(target), "static": static_checks(target, Path(args.generator) if args.generator else None)}
    try:
        report["browser"] = browser_checks(f"http://127.0.0.1:{port}/git-cloner.html", port)
    finally:
        httpd.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

    b = report["browser"]
    h = b["C1_normal_headers"]
    verdicts = [
        ("C1 正常态 5 列(项目/GITHUB/大小/时间/操作)",
         len(h) == 5 and h[0] == "项目" and h[-1] == "操作" and h[2].startswith("大小")),
        ("C2 分栏态应保留项目列 [规范不符合]",
         set(b["C2_split_headers"]) >= {"项目", "操作"}),
        ("C3 搜项目名应命中 1 行 [规范不符合]", b["C3_search_label"] == 1),
        ("C4 搜 github/path 命中 1 行", b["C4_search_github"] == 1 and b["C4b_search_path"] == 1),
        ("C5 ?split 恢复分栏 [规范不符合]", b["C5_split_restore_active"] is True),
        ("C6 ?q 恢复过滤", b["C6_q_restore_rows"] == 1),
        ("C7 size 千分位(number+thousands)", "1,234" in b["size_cell"] or b["size_cell"] == "1,234"),
        ("C8 无 SEVERE JS 错误", not b["C8_js_errors"]),
        ("C9 localStorage 键已按页面隔离(源内键名)",
         not any(k.startswith("html-gen:table:") for k in report["static"]["ls_prefixes"])),
        ("C11 切 range 后 URL/分享链接含 range [规范不符合]",
         "range=all" in (b.get("C11_url_after_range") or "") and "range=all" in (b.get("C11_share_url") or "")),
    ]
    if "generator" in report["static"]:
        verdicts.append(("C10 生成器产物含 runtime const COLUMNS", report["static"]["generator"]["has_const_COLUMNS"]))
    report["verdicts"] = [{"check": c, "pass": bool(p)} for c, p in verdicts]

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"目标: {target}")
        for c, p in verdicts:
            print(("  ✅ " if p else "  ❌ ") + c)
        print(f"\n静态: bytes={report['static']['target_bytes']} "
              f"runtime={report['static']['has_runtime_columns']} "
              f"ls_prefixes={report['static']['ls_prefixes']}")
        if "generator" in report["static"]:
            g = report["static"]["generator"]
            print(f"生成器: {g['bytes']}B const_COLUMNS={g['has_const_COLUMNS']} "
                  f"clonerTbody={g['has_clonerTbody']} title={g['title']!r} "
                  f"⇒ 会覆盖产物={g['overwrites_target']}")
        print("\n明细: 加 --json 打印完整报告")


if __name__ == "__main__":
    main()
