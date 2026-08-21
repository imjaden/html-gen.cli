#!/usr/bin/env python3
"""
company-report.py — 公司调研报告生成器

从 company-research-schema.json 生成完整的 C 型知识库：
  1. groups JSON + items JSON
  2. 最终 C 型 HTML

用法:
  python company-report.py schema.json

示例:
  python company-report.py company-research-schema.json
"""

import json, sys, os, subprocess
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent  # scripts/ 的上级 = 项目根
HTML_DEMOS = SKILLS_DIR
HTML_GEN   = SKILLS_DIR / 'html-gen.py'


def _safe_path(prefix, rel_path):
    """Resolve and validate path — reject traversal outside prefix."""
    full = (prefix / rel_path).resolve()
    if not str(full).startswith(str(prefix.resolve()) + os.sep) and full != prefix.resolve():
        print(f"❌ 路径穿越拒绝: {rel_path}", file=sys.stderr)
        sys.exit(1)
    return full


def load_schema(path):
    with open(path) as f:
        return json.load(f)


def generate_content_pages(out, items):
    """items 含 content/metrics → 自动生成内容页（doc 产物，数据卡表格置顶）."""
    content_dir = _safe_path(HTML_DEMOS / 'demos', out['content_dir'])
    content_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in items:
        content = item.get('content')
        if not content:
            continue
        name = Path(item['url']).stem
        md = f"# {item['title']}\n\n"
        metrics = item.get('metrics')
        if metrics:
            md += '## 核心数据\n\n| 指标 | 数据 |\n|:---|:---|\n'
            for m in metrics:
                md += f"| {m.get('label', '')} | {m.get('value', '')} |\n"
            md += '\n'
        md += content.rstrip() + '\n'
        md_path = content_dir / f'{name}.md'
        html_path = content_dir / f'{name}.html'
        md_path.write_text(md, encoding='utf-8')
        r = subprocess.run([sys.executable, str(HTML_GEN), 'doc', '-i', str(md_path),
                            '-o', str(html_path), '--title', item['title']],
                           capture_output=True, text=True)
        if r.returncode == 0:
            count += 1
            print(f"  ✅ {out['content_dir']}/{name}.html")
        else:
            print(f"  ❌ {out['content_dir']}/{name}.html: {r.stderr[:100]}")
    return count


def generate(schema):
    company = schema['company']
    out     = schema['output']
    groups  = schema['groups']
    items   = schema['items']

    # 0. Generate content pages from schema (metrics + content)
    n_content = generate_content_pages(out, items)
    if n_content:
        print(f"  ✅ 内容页 {n_content} 个（schema 自动生成）")

    # 1. Write groups JSON (path-validated)
    groups_path = _safe_path(HTML_DEMOS, out['groups_file'])
    with open(groups_path, 'w') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)
    print(f"  ✅ {out['groups_file']}")

    # 2. Write items JSON (path-validated)
    clean_items = []
    for item in items:
        entry = {}
        for key in ['title', 'group', 'section', 'badge', 'url', 'desc']:
            if key in item:
                entry[key] = item[key]
        clean_items.append(entry)

    data_path = _safe_path(HTML_DEMOS, out['data_file'])
    with open(data_path, 'w') as f:
        json.dump(clean_items, f, ensure_ascii=False, indent=2)
    print(f"  ✅ {out['data_file']} ({len(clean_items)} items)")

    # 3. Run html-gen knowledge (path-validated)
    html_path = _safe_path(HTML_DEMOS, out['html_file'])
    result = subprocess.run([
        sys.executable, str(HTML_GEN), 'knowledge',
        '-d', str(data_path),
        '-g', str(groups_path),
        '--title', company.get('title_prefix', company['name']),
        '--subtitle', company.get('subtitle', ''),
        '--welcome', company.get('welcome', ''),
        '-o', str(html_path),
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  ✅ {out['html_file']}")
        return True
    else:
        print(f"  ❌ html-gen failed: {result.stderr}")
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    schema_path = Path(sys.argv[1])
    if not schema_path.exists():
        print(f"❌ 文件不存在: {schema_path}")
        sys.exit(1)

    schema = load_schema(schema_path)
    print(f"📋 {schema['company']['name']}")
    generate(schema)
    print(f"\n✅ 完成")


if __name__ == '__main__':
    main()
