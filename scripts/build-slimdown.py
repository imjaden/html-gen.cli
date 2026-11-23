#!/usr/bin/env python3
"""slimdown 案例生成器 —— 动作库 / 训练方案 / 档案 三页一次重建。

案例编号: HTML-GEN-CL045（台账闭环编号；来源 2026-11-12 他人笔 b0f4b4f + review HG-SEC-231）
用途: 三页同源可重建（数据 → _src 模板 → 单文件产物），`--dry-run` 先看面再 `--apply` 落盘。

用法:
  python3 scripts/build-slimdown.py --dry-run   # 只打印将写哪些文件
  python3 scripts/build-slimdown.py --apply     # 写盘

产物（全部自包含单文件，无外链资源）:
  demos/slimdown/exercises.html   html-gen table 标准模板（数据 data/_slimdown-exercises.json）
  demos/slimdown/index.html       _src/plan.tpl + 数据内联（plan 页本体；目录首页，/demos/slimdown/ 直达）
  demos/slimdown/plan.html        跳转桩（v1.4 起旧链接兼容，透传 ? 与 # 后跳 index.html）
  demos/slimdown/archive.html     _src/archive.tpl + _src/archive.js

设计取舍:
  - 样式分两套：plan.html 走 _src/plan.css（深色暖调 + 四套 data-theme 变量），
    archive.html 走 _src/base.css（纸上质感）；两者互不影响。
  - exercises.html 由 html-gen CLI 生成，保证「动作库用标准模板」这条不被绕过。
  - 输出不含生成时间戳，同一份数据重复构建逐字节一致（便于 diff / 门禁）。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'demos' / 'slimdown' / '_src'
OUT = ROOT / 'demos' / 'slimdown'
DATA_EX = ROOT / 'data' / '_slimdown-exercises.json'
DATA_PLAN = ROOT / 'data' / '_slimdown-plan.json'
HTML_GEN = ROOT / 'html-gen.py'

PAGES = [
    ('exercises.html', '动作库'),
    ('index.html', '训练方案'),
    ('archive.html', '档案'),
]

# 旧链接兼容桩（v1.4）：plan.html → index.html，透传 query 与 hash（含 #p= 分享链接）
REDIRECT_STUB = '''<!DOCTYPE html>
<!-- slimdown:redirect auto -->
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>训练方案 · slimdown（已迁目录首页）</title>
<meta http-equiv="refresh" content="0;url=index.html">
<meta name="robots" content="noindex,follow">
<script>location.replace('index.html' + location.search + location.hash);</script>
</head>
<body>
<p>训练方案已迁到 <a href="index.html">目录首页</a>…</p>
</body>
</html>
'''


def nav_html(active):
    parts = []
    for href, label in PAGES:
        cls = ' class="on"' if href == active else ''
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
    return ''.join(parts)


def js_safe(obj):
    """内联到 <script> 里的 JSON：转义 </ 防止提前闭合标签。"""
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def read(p):
    return p.read_text(encoding='utf-8')


# 动作名拆中英：数据里给了 name_en 就用它，否则按「中文<空格>英文」拆。
# 只用于 plan.html 的载荷，动作库 JSON 与 exercises.html 不动（columns 是显式声明的）。
NAME_EN_RE = re.compile(r'^(.+?)\s+([A-Za-z][A-Za-z0-9\s\'&.\-–]*)$')


def name_en_of(row):
    explicit = (row.get('name_en') or '').strip()
    if explicit:
        return explicit
    m = NAME_EN_RE.match((row.get('name') or '').strip())
    return m.group(2).strip() if m else ''


def plan_exercise(row):
    """plan 载荷用的动作条目：显式带中/英文名，供卡片两行渲染。"""
    cn, en = name_parts(row)
    out = {k: row[k] for k in ('id', 'name', 'theme', 'equip', 'muscle', 'sets', 'reps')}
    out['name_cn'] = cn
    out['name_en'] = en
    return out


def name_parts(row):
    """返回 (中文名, 英文名)；英文名可为空串（纯中文动作）。"""
    full = (row.get('name') or '').strip()
    en = name_en_of(row)
    cn = full[:-len(en)].strip() if en and full.endswith(en) else full
    return cn, en


def render(tpl, css, js, nav, plan, title):
    html = read(tpl)
    return (html
            .replace('{{CSS}}', css)
            .replace('{{JS}}', js)
            .replace('{{NAV}}', nav)
            .replace('{{TITLE}}', title)
            .replace('{{VERSION}}', plan['version'])
            .replace('{{UPDATED}}', plan['updated'])
            .replace('{{SAFETY}}', plan['meta'].get('safety', '')))


def build_exercises(dry):
    cmd = [sys.executable, str(HTML_GEN), 'table',
           '-d', str(DATA_EX.relative_to(ROOT)),
           '-o', str((OUT / 'exercises.html').relative_to(ROOT)),
           '--title', '训练动作库 · slimdown',
           '--home-url', 'index.html']
    if dry:
        print('[dry]', ' '.join(cmd))
        return
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('html-gen table 失败:\n' + r.stderr + r.stdout)
    print(r.stdout.strip().splitlines()[0])


def main():
    ap = argparse.ArgumentParser(description='重建 slimdown 案例三页')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true', help='只打印计划，不写盘')
    g.add_argument('--apply', action='store_true', help='写盘')
    args = ap.parse_args()
    dry = args.dry_run

    plan = json.loads(read(DATA_PLAN))
    ex = json.loads(read(DATA_EX))
    css_plan = read(SRC / 'plan.css')
    css_base = read(SRC / 'base.css')
    # 三段按加载顺序拼接：状态层 → 出图层 → 页面逻辑（都是 IIFE，经 window.SB 通信）
    js_plan = '\n'.join(read(SRC / n) for n in ('state.js', 'shot.js', 'plan.js'))
    js_arc = read(SRC / 'archive.js')

    payload = {
        'plan': plan,
        'exercises': [plan_exercise(r) for r in ex['data']],
    }

    outputs = {
        'index.html': render(SRC / 'plan.tpl', css_plan, js_plan, nav_html('index.html'), plan,
                             '薄肌减脂 · 训练方案 · slimdown')
                      .replace('{{DATA}}', js_safe(payload)),
        'plan.html': REDIRECT_STUB,
        'archive.html': render(SRC / 'archive.tpl', css_base, js_arc, nav_html('archive.html'), plan,
                               '薄肌减脂 · 档案 · slimdown'),
    }

    build_exercises(dry)
    for name, content in outputs.items():
        left = re.findall(r'\{\{[A-Z_]+\}\}', content)
        if left:
            raise SystemExit(f'{name} 仍有未替换占位符: {sorted(set(left))}')
        p = OUT / name
        if dry:
            print(f'[dry] write {p.relative_to(ROOT)} ({len(content.encode("utf-8")):,} bytes)')
            continue
        p.write_text(content, encoding='utf-8')
        print(f'✅ {p.relative_to(ROOT)} ({len(content.encode("utf-8")):,} bytes)')

    if not dry:
        parts = []
        for p in plan.get('presets', []):
            days_ = p.get('days', [])
            parts.append(f'{p["id"]} {len(days_)} 天 / '
                         f'{sum(len(d.get("items") or []) for d in days_)} 条')
        print(f'✅ slimdown: {len(payload["exercises"])} 个动作 / ' + ' · '.join(parts) +
              f' / {len(plan.get("themes", []))} 套主题')


if __name__ == '__main__':
    main()
