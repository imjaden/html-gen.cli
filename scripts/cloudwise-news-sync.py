#!/usr/bin/env python3
"""cloudwise-news-sync.py — 云智慧公众号文章 → 知识库「新闻动态」同步器

从 web2md 索引（web2md_index.json）读取 author=云智慧 的文章，
增量同步到 data/_cloudwise-news.json，并可触发知识库重建 + git commit。

用法:
  python3 scripts/cloudwise-news-sync.py                 # 增量同步（默认全流程: 同步+重建+commit）
  python3 scripts/cloudwise-news-sync.py --dry-run       # 只报告将新增，不写文件不重建
  python3 scripts/cloudwise-news-sync.py --rebuild       # 从索引全量重建 news JSON（覆盖现有）
  python3 scripts/cloudwise-news-sync.py --no-rebuild    # 只更新 news JSON，不重建知识库
  python3 scripts/cloudwise-news-sync.py --no-commit     # 重建但不 commit

输出: 周报文本（stdout）— 供 cron 投递飞书
"""

import argparse
import html as _html
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NEWS_FILE = PROJECT_ROOT / 'data' / '_cloudwise-news.json'
INDEX_FILE = Path(os.environ.get('WEB2MD_INDEX', '/Users/jadenli/Documents/10-DataDrived/web2md_index.json'))
AUTHOR = '云智慧'

SUMMARY_LEN = 200  # 摘要长度（字符）


def load_index():
    if not INDEX_FILE.exists():
        print(f'❌ web2md 索引不存在: {INDEX_FILE}', file=sys.stderr)
        sys.exit(1)
    with open(INDEX_FILE, encoding='utf-8') as f:
        return json.load(f)


def load_news():
    if not NEWS_FILE.exists():
        return []
    with open(NEWS_FILE, encoding='utf-8') as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def save_news(news):
    NEWS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print(f'  ✅ {NEWS_FILE.relative_to(PROJECT_ROOT)} ({len(news)} 条)')


def extract_summary(step1_path):
    """从 step1-article.md 提取正文前 N 字纯文本摘要。"""
    if not step1_path or not os.path.exists(step1_path):
        return ''
    try:
        txt = open(step1_path, encoding='utf-8').read()
    except Exception:
        return ''
    # 去掉 front matter：第一个 --- 之后才是正文（后续 --- 是正文分隔线）
    parts = txt.split('---', 1)
    body = parts[1] if len(parts) > 1 else txt
    # 去掉 markdown 图片 / 链接语法
    body = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', body)
    body = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', body)
    body = re.sub(r'```.*?```', '', body, flags=re.S)
    # 去掉标题/列表/表格/分隔线符号，压缩空白
    body = re.sub(r'^#{1,6}\s*', '', body, flags=re.M)
    body = re.sub(r'^\s*[-*+]\s+', '', body, flags=re.M)
    body = re.sub(r'^\s*[-*_]{3,}\s*$', '', body, flags=re.M)
    body = re.sub(r'^\s*\|.*\|\s*$', '', body, flags=re.M)
    body = body.replace('**', '').replace('`', '')
    text = re.sub(r'\s+', ' ', body).strip()
    if not text:
        return ''
    if len(text) <= SUMMARY_LEN:
        return text
    cut = text[:SUMMARY_LEN]
    # 尽量在句子边界截断
    for sep in ('。', '！', '？', '；'):
        idx = cut.rfind(sep)
        if idx > SUMMARY_LEN * 0.5:
            return cut[:idx + 1]
    return cut + '…'


def format_date(d):
    """20260827 → 2026-08-27；空 → ''"""
    d = str(d or '').strip()
    if len(d) == 8 and d.isdigit():
        return f'{d[:4]}-{d[4:6]}-{d[6:]}'
    return d


def resolve_step1(idx_item):
    """解析 step1 文件路径：优先索引路径，兜底尝试无日期前缀目录。"""
    p = idx_item.get('step1_path') or ''
    if p and os.path.exists(p):
        return p
    aid = idx_item.get('article_id') or ''
    if aid:
        # 兜底: web2md/{id}/step1-article.md（web2md 偶发索引路径带日期前缀但实际目录无前缀）
        alt = INDEX_FILE.parent / 'web2md' / aid / 'step1-article.md'
        if alt.exists():
            return str(alt)
    return p


def build_news_entry(idx_item):
    pub = format_date(idx_item.get('publish_date'))
    return {
        'title': idx_item.get('title', '未命名'),
        'url': idx_item.get('url', ''),
        'article_id': idx_item.get('article_id', ''),
        'publish_date': pub,
        'section': pub[:7] if len(pub) >= 7 else '动态',
        'summary': extract_summary(resolve_step1(idx_item)),
        'archived_at': datetime.now().isoformat(timespec='seconds'),
    }


def rebuild_kb():
    schema = PROJECT_ROOT / 'scripts' / 'company-research-cloudwise-schema.json'
    if not schema.exists():
        print('  ⚠️ schema 不存在，跳过知识库重建')
        return None
    r = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / 'scripts' / 'company-report.py'), str(schema)],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f'  ❌ 知识库重建失败: {r.stderr[-500:]}', file=sys.stderr)
        return None
    print(r.stdout.rstrip())
    return r.stdout


def git_commit(message):
    r = subprocess.run(['git', '-C', str(PROJECT_ROOT), 'add', '-A'], capture_output=True, text=True)
    if r.returncode != 0:
        print(f'  ❌ git add 失败: {r.stderr}', file=sys.stderr)
        return None
    status = subprocess.run(['git', '-C', str(PROJECT_ROOT), 'status', '--porcelain'],
                            capture_output=True, text=True)
    if not status.stdout.strip():
        print('  ℹ️ 无变更，跳过 commit')
        return None
    r = subprocess.run(['git', '-C', str(PROJECT_ROOT), 'commit', '-m', message],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f'  ❌ git commit 失败: {r.stderr}', file=sys.stderr)
        return None
    m = re.search(r'\[main [0-9a-f]+', r.stdout)
    short = m.group(0).split()[-1] if m else '?'
    return short


def main():
    ap = argparse.ArgumentParser(description='云智慧公众号文章 → 知识库新闻动态 同步器')
    ap.add_argument('--dry-run', action='store_true', help='只报告将新增，不写文件不重建')
    ap.add_argument('--rebuild', action='store_true', help='从索引全量重建 news JSON')
    ap.add_argument('--no-rebuild', action='store_true', help='不触发知识库重建')
    ap.add_argument('--no-commit', action='store_true', help='重建但不 commit')
    args = ap.parse_args()

    index = load_index()
    articles = [a for a in index if a.get('author') == AUTHOR]
    articles.sort(key=lambda a: a.get('publish_date', ''), reverse=True)

    existing = load_news()
    existing_ids = {e.get('article_id') for e in existing if e.get('article_id')}

    if args.rebuild:
        new_entries = [build_news_entry(a) for a in articles]
        news = new_entries
        added = [e for e in new_entries]
        print(f'🔁 全量重建 news JSON（{len(news)} 条）')
    else:
        new_entries = [build_news_entry(a) for a in articles if a.get('article_id') not in existing_ids]
        news = existing + new_entries
        news.sort(key=lambda e: e.get('publish_date', ''), reverse=True)
        added = new_entries
        print(f'📰 索引 {len(articles)} 篇 / 已归档 {len(existing)} / 新增 {len(added)}')

    if args.dry_run:
        print('── dry-run ──')
        if added:
            for e in added:
                print(f'  + {e.get("publish_date", "????-??-??")} {e.get("title", "")}')
                print(f'    {e.get("url", "")}')
        else:
            print('  无新增文章')
        return

    changed = bool(added) or args.rebuild
    if changed:
        save_news(news)
    else:
        print('  ℹ️ 无新增文章，news JSON 不变')

    # 周报正文
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    report = []
    report.append(f'📰 云智慧公众号周报（{now}）')
    report.append('─' * 30)
    if added:
        report.append(f'本周新增：{len(added)} 篇')
        for e in added:
            report.append(f'  · {e.get("publish_date", "????-??-??")} 《{e.get("title", "")}》')
            report.append(f'    {e.get("url", "")}')
    else:
        report.append('本周无新增文章。')
    if changed:
        # 重建知识库（除非 --no-rebuild 或 dry-run 已返回）
        if not args.no_rebuild:
            print('  🔨 重建知识库…')
            rebuild_kb()
        # commit（除非 --no-commit）
        if not args.no_commit:
            short = git_commit(f'sync@html-gen: cloudwise news weekly - {len(added)} new')
            if short:
                report.append('─' * 30)
                report.append(f'✅ 知识库已更新并 commit（{short}），请核实。')
    print('─' * 30)
    print('\n'.join(report))


if __name__ == '__main__':
    main()
