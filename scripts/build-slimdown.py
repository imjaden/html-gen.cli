#!/usr/bin/env python3
"""slimdown 案例生成器 —— 动作库 / 训练方案 / 档案 三页一次重建。

用法:
  python3 scripts/build-slimdown.py --dry-run   # 只打印将写哪些文件
  python3 scripts/build-slimdown.py --apply     # 写盘

产物（全部自包含单文件，无外链资源）:
  demos/slimdown/exercises.html   html-gen table 标准模板（数据 data/_slimdown-exercises.json）
  demos/slimdown/plan.html        _src/plan.tpl + _src/plan.js + 数据内联
  demos/slimdown/archive.html     _src/archive.tpl + _src/archive.js

设计取舍:
  - 页面样式统一走 _src/base.css（纸上质感），不复用深色 table 模板的 CSS；
    exercises.html 由 html-gen CLI 生成，保证「动作库用标准模板」这条不被绕过。
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
    ('plan.html', '训练方案'),
    ('archive.html', '档案'),
]


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
           '--home-url', 'plan.html']
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
    css = read(SRC / 'base.css')
    js_plan = read(SRC / 'plan.js')
    js_arc = read(SRC / 'archive.js')

    payload = {
        'plan': plan,
        'exercises': [{k: r[k] for k in ('id', 'name', 'theme', 'equip', 'muscle', 'sets', 'reps')}
                      for r in ex['data']],
    }

    outputs = {
        'plan.html': render(SRC / 'plan.tpl', css, js_plan, nav_html('plan.html'), plan,
                            '薄肌减脂 · 训练方案 · slimdown')
                     .replace('{{DATA}}', js_safe(payload)),
        'archive.html': render(SRC / 'archive.tpl', css, js_arc, nav_html('archive.html'), plan,
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
        print(f'✅ slimdown: {len(payload["exercises"])} 个动作 / {len(plan["days"])} 天 / '
              f'{sum(len(d["items"]) for d in plan["days"])} 条安排')


if __name__ == '__main__':
    main()
