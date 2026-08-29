#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A 型表格 videos 同步辅助脚本（HTML-GEN-CL002）。

以 yaml 为增量输入，按 country_zh 外键匹配 data JSON 行，将 json 尚未包含的
视频（按 url 去重）append 进对应行 videos 数组；随后将 json 全部 videos 全局
镜像回写 yaml（countries 段），并调用 html-gen.py table 重建 demos 产物。

用法:
    scripts/tool-table-videos-syncer.py <yaml-path>            # 预览（默认 dry-run）
    scripts/tool-table-videos-syncer.py <yaml-path> --dry-run  # 预览，零写盘
    scripts/tool-table-videos-syncer.py <yaml-path> --apply    # 执行写盘

设计: documents/solutions/table-videos-syncer-design-v1.1-20260829.md
依赖: 仅 PyYAML（dev 依赖 requirements-dev.txt），运行时 html-gen 零依赖不受影响
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

# ── 常量 ─────────────────────────────────────────────────────────────
# scripts/ 的上级 = 项目根；target.data / target.html / html-gen.py 等相对路径
# 一律以项目根为基准解析（RIG-003 / HG-SEC-056），勿相对 yaml 所在目录（cache/）
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# duration int 容错阈值：M:SS 上界 59:59 = 3599s，故 < 3600（HG-SEC-061）
DURATION_INT_THRESHOLD = 3600


class SyncerDumper(yaml.SafeDumper):
    """专用 SafeDumper：str 回写时对会被 YAML 解析为非字符串的标量强制双引号。

    duration 如 "6:55" 未引号时会被 PyYAML 按 60 进制解析成 int 415（sexagesimal
    坑）；"3723" 未引号会被解析成 int。回写 yaml 时 duration 统一带引号。
    """


def _represent_str(dumper, data):
    try:
        resolved = yaml.safe_load(data)
    except Exception:
        resolved = None
    if not isinstance(resolved, str):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
    return dumper.represent_str(data)


yaml.add_representer(str, _represent_str, Dumper=SyncerDumper)


# ── 解析与校验 ───────────────────────────────────────────────────────
def parse_target(target_section):
    """target 段 → {data, html}。支持规范列表形态 [{data}, {html}] 与字典形态。"""
    if isinstance(target_section, dict):
        return target_section
    out = {}
    if isinstance(target_section, list):
        for item in target_section:
            if isinstance(item, dict):
                out.update(item)
    return out


def detect_platform(url):
    """C1：platform 缺省时按 URL host 自动识别；其他 → None（省略）。"""
    m = re.search(r'https?://([^/]+)', url or '')
    host = m.group(1).lower() if m else ''
    if 'v.douyin.com' in host or 'douyin' in host:
        return 'douyin'
    if 'bilibili' in host:
        return 'bilibili'
    if 'youtube' in host or 'youtu.be' in host:
        return 'youtube'
    return None


def normalize_duration(value):
    """duration 归一化：str 原样（strip 空白）；int 容错仅支持 M:SS（< 3600 按秒数
    归一化，如 415 → "6:55"）；H:MM:SS 形态（≥ 3600）不在容错语义内，保留原值字符串
    （回写带引号，不自动归一化）【HG-SEC-057 / HG-SEC-061】。"""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, int) and not isinstance(value, bool):
        if 0 <= value < DURATION_INT_THRESHOLD:
            return f'{value // 60}:{value % 60:02d}'
        return str(value)
    return str(value)


def validate_countries(countries, rows_by_country):
    """F3 校验：countries 每条 country_zh 必须在 json 行存在；返回缺失键清单。"""
    missing = []
    for i, entry in enumerate(countries, 1):
        cz = (entry.get('country_zh') or '').strip()
        if not cz:
            missing.append(f'第 {i} 条（缺 country_zh）')
        elif cz not in rows_by_country:
            missing.append(cz)
    return missing


def build_increments(countries, rows_by_country):
    """逐条计算增量：url（strip）不在该行 videos 集合中 → 新增；yaml 内部同
    country+url 只取首条。返回 (new_items, skipped)。"""
    new_items = []
    skipped = []
    seen = set()
    for entry in countries:
        cz = (entry.get('country_zh') or '').strip()
        url = (entry.get('url') or '').strip()
        if not cz or not url:
            print(f'[警告] 忽略畸形条目（缺 country_zh 或 url）: {entry}', file=sys.stderr)
            continue
        key = (cz, url)
        if key in seen:
            continue  # yaml 内部同 url 只取首条
        seen.add(key)
        row = rows_by_country[cz]
        existing = {v.get('url', '').strip() for v in (row.get('videos') or [])}
        item = {
            'country_zh': cz,
            'title': (entry.get('title') or '').strip(),
            'url': url,
            'duration': normalize_duration(entry.get('duration')),
            'platform': entry.get('platform'),
        }
        if url in existing:
            skipped.append(item)
        else:
            new_items.append(item)
    return new_items, skipped


def build_mirror_countries(rows):
    """W 回写：将 json 全部行的 videos 展平为 countries 平铺列表（无 videos 的
    行不产生条目）；platform 写 json 现值，缺省省略。"""
    out = []
    for row in rows:
        videos = row.get('videos') or []
        if not videos:
            continue
        for v in videos:
            item = {
                'country_zh': (row.get('country_zh') or '').strip(),
                'title': (v.get('title') or '').strip(),
                'url': (v.get('url') or '').strip(),
                'duration': normalize_duration(v.get('duration')),
            }
            platform = v.get('platform')
            if platform:
                item['platform'] = platform
            out.append(item)
    return out


def run_apply(args, doc, target, countries, json_path, html_path, data_doc, rows,
              rows_by_country, new_items):
    """执行写盘：append json → 写 json → W 回写 yaml → E 重建 html。"""
    # 6. 按 country_zh 分组补充（videos 缺失先初始化 []；platform 缺省按 C1 识别）
    for it in new_items:
        row = rows_by_country[it['country_zh']]
        videos = row.get('videos')
        if videos is None:
            videos = []
            row['videos'] = videos
        platform = it['platform'] or detect_platform(it['url'])
        entry = {'title': it['title'], 'url': it['url'], 'duration': it['duration']}
        if platform:
            entry['platform'] = platform
        videos.append(entry)
    print(f'[同步] 新增 {len(new_items)} 条视频')
    for it in new_items:
        print(f'  - {it["country_zh"]}: {it["title"]} {it["url"]} ({it["duration"]})')

    # 写 json（indent=2 与现文件格式一致）
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data_doc, f, ensure_ascii=False, indent=2)
    print(f'[写盘] {json_path.relative_to(PROJECT_ROOT)}')

    # 7. W 全局镜像回写 yaml（target 段保留原样）
    new_doc = {'target': doc.get('target'), 'countries': build_mirror_countries(rows)}
    with open(args.yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(new_doc, f, Dumper=SyncerDumper, allow_unicode=True,
                  default_flow_style=False, sort_keys=False)
    print(f'[回写] yaml countries 段已重建（{len(new_doc["countries"])} 条）')

    # 8. E 重建 html（RIG-002：列表参数 + shell=False，禁 shell=True / 字符串拼接）
    html_gen = PROJECT_ROOT / 'html-gen.py'
    if not html_gen.is_file():
        print(f'[错误] 未找到 html-gen.py: {html_gen}', file=sys.stderr)
        return 1
    result = subprocess.run(
        [sys.executable, str(html_gen), 'table', '-d', str(json_path),
         '-o', str(html_path)],
        shell=False)
    if result.returncode != 0:
        print(f'[错误] html 重建失败（exit {result.returncode}）', file=sys.stderr)
        return result.returncode
    print(f'[重建] {html_path.relative_to(PROJECT_ROOT)}')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='tool-table-videos-syncer.py',
        description='table videos 同步辅助脚本：yaml 增量 → json videos 补充 + yaml 全局镜像 + html 重建',
    )
    parser.add_argument('yaml_path', help='增量 yaml 路径（如 cache/data/_countries-data.videos.yaml）')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dry-run', action='store_true', help='预览模式（默认，零写盘）')
    group.add_argument('--apply', action='store_true', help='执行写盘（json → yaml 回写 → html 重建）')
    args = parser.parse_args(argv)

    # 1. 解析 yaml（RIG-001：必须 yaml.safe_load，禁 yaml.load / FullLoader，
    #    防 !!python/object 任意代码执行）
    try:
        with open(args.yaml_path, encoding='utf-8') as f:
            doc = yaml.safe_load(f) or {}
    except Exception as e:
        print(f'[错误] 无法解析 yaml: {e}', file=sys.stderr)
        return 1

    target_section = doc.get('target')
    if not target_section:
        print('[错误] yaml 缺少 target 段', file=sys.stderr)
        return 1
    target = parse_target(target_section)
    data_rel, html_rel = target.get('data'), target.get('html')
    if not data_rel or not html_rel:
        print('[错误] target 段需含 data 与 html 相对路径', file=sys.stderr)
        return 1
    countries = doc.get('countries') or []

    # 2. 相对路径以项目根为基准解析（RIG-003 / HG-SEC-056）
    json_path = PROJECT_ROOT / data_rel
    html_path = PROJECT_ROOT / html_rel
    if not json_path.is_file():
        print(f'[错误] 数据文件不存在: {json_path}', file=sys.stderr)
        return 1

    with open(json_path, encoding='utf-8') as f:
        data_doc = json.load(f)
    rows = data_doc['data'] if isinstance(data_doc, dict) and 'data' in data_doc else data_doc
    rows_by_country = {}
    for row in rows:
        cz = row.get('country_zh')
        if cz:
            rows_by_country.setdefault(cz, row)

    # 3. F3 校验先行（任一 country_zh 缺失 → 打印缺失键清单 exit 1 零写盘）
    missing = validate_countries(countries, rows_by_country)
    if missing:
        print('[错误] 以下国家键在 json 中不存在（或缺少 country_zh），未做任何修改:')
        for m in missing:
            print(f'  - {m}')
        return 1

    # 4. 逐条计算增量（yaml 内部同 url 只取首条）
    new_items, skipped = build_increments(countries, rows_by_country)

    # 5. G 判定：无增量 → 打印提示中断 exit 0，不写任何文件（幂等）
    if not new_items:
        print('[提示] 所有 videos 均已包含，无需同步')
        return 0

    # dry-run 预览（默认态，零写盘）
    if not args.apply:
        print(f'[预览] 新增 {len(new_items)} 条:')
        for it in new_items:
            print(f'  - {it["country_zh"]}: {it["title"]} {it["url"]} ({it["duration"]})')
        if skipped:
            print(f'[预览] 跳过 {len(skipped)} 条（url 已存在）:')
            for it in skipped:
                print(f'  - {it["country_zh"]}: {it["title"]} {it["url"]}')
        print(f'[预览] 将回写 yaml countries 段（全局镜像）+ 重建 {html_rel}')
        print('[提示] 使用 --apply 执行')
        return 0

    # --apply 执行
    return run_apply(args, doc, target, countries, json_path, html_path,
                     data_doc, rows, rows_by_country, new_items)


if __name__ == '__main__':
    sys.exit(main())
