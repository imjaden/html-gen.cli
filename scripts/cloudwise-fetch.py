#!/usr/bin/env python3
"""cloudwise-fetch.py — 云智慧公众号新文章处理入口（B1：拿到 URL 自动全处理）

人工发现云智慧公众号新文章后，把 URL 交给本脚本：
  1. 调用 web2md <URL>（自动 step1 全文抓取 + step2 智读分析）
  2. 处理完成后文章进入 web2md 索引
  3. 可选立即同步进知识库新闻 JSON（每周 cron 也会自动收口，但人工喂后可即时生效）

用法:
  python3 scripts/cloudwise-fetch.py <URL>                      # 只调 web2md 全处理
  python3 scripts/cloudwise-fetch.py <URL> --sync               # 处理后立即增量同步 news JSON
  python3 scripts/cloudwise-fetch.py <URL> --sync --rebuild-kb  # 同步 + 重建知识库
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description='云智慧公众号新文章处理入口（B1）')
    ap.add_argument('url', help='公众号文章 URL')
    ap.add_argument('--sync', action='store_true', help='处理后立即增量同步进 news JSON')
    ap.add_argument('--rebuild-kb', action='store_true', help='同步后重建知识库（需 --sync）')
    args = ap.parse_args()

    web2md = shutil.which('web2md')
    if not web2md:
        print('❌ 未找到 web2md 命令（~/.local/bin/web2md），请确认 script-miner 已注册', file=sys.stderr)
        sys.exit(1)

    # 1. 调用 web2md 全处理（默认 all = step1 + step2）
    print(f'🔍 web2md 处理: {args.url}')
    r = subprocess.run([web2md, args.url])
    if r.returncode != 0:
        print(f'❌ web2md 处理失败（exit={r.returncode}）', file=sys.stderr)
        sys.exit(1)
    print('  ✅ web2md 处理完成（step1 全文 + step2 智读）')

    # 2. 可选：增量同步进知识库新闻 JSON
    if args.sync:
        sync = PROJECT_ROOT / 'scripts' / 'cloudwise-news-sync.py'
        cmd = [sys.executable, str(sync)]
        if args.rebuild_kb:
            cmd += ['--no-commit']  # 人工触发不自动 commit，由每周 cron / 人工核实后统一 commit
        print('  🔄 增量同步 news JSON…')
        subprocess.run(cmd)
        if args.rebuild_kb:
            print('  🔨 重建知识库…')
            schema = PROJECT_ROOT / 'scripts' / 'company-research-cloudwise-schema.json'
            subprocess.run([sys.executable, str(PROJECT_ROOT / 'scripts' / 'company-report.py'), str(schema)])
    print('✅ 完成。每周六 10:00 cron 会自动汇总新文章并推飞书。')


if __name__ == '__main__':
    main()
