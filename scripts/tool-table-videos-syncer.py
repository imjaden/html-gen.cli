#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A 型表格 videos 同步辅助脚本（HTML-GEN-CL002 / CL004 / CL006）。

以 yaml 为增量输入，按 country_zh 外键匹配 data JSON 行，将 json 尚未包含的
视频（按 url 去重）append 进对应行 videos 数组（v1.2 起三态增量：新增/更新/
跳过——url 已存在且 yaml title 非空且不同 → 全字段覆盖更新）；随后将 json
全部 videos 全局镜像回写 yaml（countries 段），并调用 html-gen.py table 重建
demos 产物。

用法 (CL004 参数体系):
    scripts/tool-table-videos-syncer.py                      # 缺省 yaml + 预览（默认 dry-run）
    scripts/tool-table-videos-syncer.py <yaml-path>          # 预览（默认 dry-run）
    scripts/tool-table-videos-syncer.py <yaml-path> --dry-run  # 预览，零写盘
    scripts/tool-table-videos-syncer.py <yaml-path> --apply    # 执行写盘
    scripts/tool-table-videos-syncer.py <yaml-path> --empty-video  # 列出 videos 为空的行（只读，零写盘）

yaml target 段扩展 rebuild: {github_url, home_url, favicon}（缺省用固定默认；
github_url 优先级: rebuild 配置 > 旧产物 github-corner 提取 > 固定默认）。

设计: documents/solutions/table-videos-syncer-design-v1.2-20260830.md
      documents/solutions/table-videos-syncer-design-v1.1-20260829.md
      documents/solutions/html-gen-favicon-urlstate-syncer-design-v1.0-20260829.md §5
依赖: 仅 PyYAML（dev 依赖 requirements-dev.txt），运行时 html-gen 零依赖不受影响
"""

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

# ── 常量 ─────────────────────────────────────────────────────────────
# scripts/ 的上级 = 项目根；target.data / target.html / html-gen.py 等相对路径
# 一律以项目根为基准解析（RIG-003 / HG-SEC-056），勿相对 yaml 所在目录（cache/）
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# CL004: 缺省 yaml 路径（I2, 项目根解析）
DEFAULT_YAML = PROJECT_ROOT / 'cache' / 'data' / '_countries-data.videos.yaml'

# CL004: rebuild 缺省默认（L1 / 1B / C1）
DEFAULT_GITHUB_URL = 'https://github.com/imjaden/html-gen.cli'
DEFAULT_HOME_URL = 'https://html-gen.cli.jaden.tech/'
DEFAULT_FAVICON = 'https://www.jaden.tech/static/img/favicon.png'

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
    """逐条计算三态增量（v1.2）：
    - new_items: url（strip）不在该行 videos 集合中 → 新增
    - updates:   url 已存在 + yaml title 非空 + ≠ json 既有 title → 覆盖更新
    - skipped:   其余（url 已存在且 title 相同，或 yaml title 为空）
    yaml 内部同 country+url 只取首条（去重口径与全包含统计 N/M 一致）。
    updates 保留 raw duration（HG-SEC-081：判空须针对 raw yaml 值，勿用
    normalize_duration 后的 'None' 字面量）与 old_title（取自 json 既有条目）。
    返回 (new_items, updates, skipped)。"""
    new_items = []
    updates = []
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
            continue  # yaml 内部同 country+url 只取首条
        seen.add(key)
        row = rows_by_country[cz]
        existing_map = {v.get('url', '').strip(): v for v in (row.get('videos') or [])}
        if url not in existing_map:
            new_items.append({
                'country_zh': cz,
                'title': (entry.get('title') or '').strip(),
                'url': url,
                'duration': normalize_duration(entry.get('duration')),
                'platform': entry.get('platform'),
            })
            continue
        existing_v = existing_map[url]
        yaml_title = (entry.get('title') or '').strip()
        if yaml_title and yaml_title != (existing_v.get('title') or '').strip():
            updates.append({
                'country_zh': cz,
                'title': yaml_title,
                'old_title': (existing_v.get('title') or '').strip(),
                'url': url,
                # HG-SEC-081: 更新步判空须用 raw 值（None/'' → 保留 json 现值）
                'raw_duration': entry.get('duration'),
                'platform': entry.get('platform'),
            })
        else:
            skipped.append({
                'country_zh': cz,
                'title': yaml_title,
                'url': url,
                'duration': normalize_duration(entry.get('duration')),
                'platform': entry.get('platform'),
            })
    return new_items, updates, skipped


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


def extract_corner_url(html_path):
    """E 重建前提取既有产物 github-corner 的 repo URL（FIND-002 fix）：
    旧 html 含 corner（HG-SEC-014 demo 页规范）时透传 --github-url，避免重建丢失。"""
    try:
        text = html_path.read_text(encoding='utf-8')
    except OSError:
        return None
    m = re.search(r'href="(https://github\.com/[^"]+)"[^>]*class="[^"]*github-corner', text)
    return m.group(1) if m else None


def resolve_rebuild_args(target, html_path):
    """rebuild 配置节 → html-gen 显式参数追加段（L1 / 2A / 1B）。

    github_url 优先级: rebuild.github_url > extract_corner_url(旧 html) > 固定默认 (2A)。
    home_url / favicon 缺省用固定默认（1B / C1）。
    HG-SEC-078: 任一键显式空串 = 禁用 → 不传该参数（跳过提取/默认）。
    """
    rebuild = target.get('rebuild') or {}
    extra = []
    if 'github_url' in rebuild:
        if rebuild['github_url']:
            extra += ['--github-url', rebuild['github_url']]
        # 空串 → 显式禁用, 不传 --github-url
    else:
        corner = extract_corner_url(html_path) or DEFAULT_GITHUB_URL
        extra += ['--github-url', corner]
    if 'home_url' in rebuild:
        if rebuild['home_url']:
            extra += ['--home-url', rebuild['home_url']]
        # 空串 → 显式禁用, 不传 --home-url
    else:
        extra += ['--home-url', DEFAULT_HOME_URL]
    if 'favicon' in rebuild:
        if rebuild['favicon']:
            extra += ['--favicon', rebuild['favicon']]
        # 空串 → 显式禁用, 不传 --favicon
    else:
        extra += ['--favicon', DEFAULT_FAVICON]
    return extra


def run_empty_video(data_doc):
    """--empty-video 只读：列出 videos 缺失或为空的 json 行（K1 / 4A）。

    输出逐行「首字段 (次字段)」：按 json 行内字段序取前两个非空字段，
    空字段显示 (空)；底部「共 N 条 videos 为空」。零写盘，exit 0。
    """
    rows = data_doc['data'] if isinstance(data_doc, dict) and 'data' in data_doc else data_doc
    if not rows:
        print('[empty-video] 无数据行')
        return 0
    keys = list(rows[0].keys())
    empty = [r for r in rows if not r.get('videos')]
    if not empty:
        print(f'全部 {len(rows)} 条均有 videos')
        return 0
    for row in empty:
        vals = [str(row[k]) for k in keys if row.get(k) not in (None, '')]
        vals = (vals[:2] + ['', ''])[:2]
        print(f'{vals[0] or "(空)"} ({vals[1] or "(空)"})')
    print(f'共 {len(empty)} 条 videos 为空')
    return 0


def run_apply(args, doc, target, countries, json_path, html_path, data_doc, rows,
              rows_by_country, new_items, updates):
    """执行写盘：append json（新增）→ 覆盖更新 → 写 json → W 回写 yaml → E 重建 html。"""
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

    # 6b. 更新步（v1.2）：url 已存在且 title 变更 → 全字段覆盖
    # - title：直接覆盖（触发条件已保证非空）
    # - duration：按 raw yaml 值判空（HG-SEC-081），非空才覆盖；空/缺省保留 json 现值
    # - platform：yaml 有值用 yaml；缺省 → detect_platform(url) 兜底；detect 空 → 保留既有（U1）
    updated_details = []
    for it in updates:
        row = rows_by_country[it['country_zh']]
        existing_entry = next((v for v in (row.get('videos') or [])
                               if v.get('url', '').strip() == it['url']), None)
        if existing_entry is None:
            continue  # 防御：url 已存在才进 updates，正常不会缺失
        existing_entry['title'] = it['title']
        if it['raw_duration'] is not None and it['raw_duration'] != '':
            existing_entry['duration'] = normalize_duration(it['raw_duration'])
        platform = it['platform'] or detect_platform(it['url'])
        if platform:
            existing_entry['platform'] = platform
        updated_details.append((it['country_zh'], it['old_title'], it['title']))
    if updated_details:
        print(f'[同步] 更新 {len(updated_details)} 条视频（title 变更）')
        for cz, old_title, new_title in updated_details:
            print(f'  - {cz}: {old_title} → {new_title}')

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
    cmd = [sys.executable, str(html_gen), 'table', '-d', str(json_path),
           '-o', str(html_path)]
    # CL004: rebuild 配置节 → 显式 --github-url/--home-url/--favicon 三参数 (D1/L1/2A)
    cmd += resolve_rebuild_args(target, html_path)
    print('[执行] ' + ' '.join(shlex.quote(str(a)) for a in cmd))
    result = subprocess.run(cmd, shell=False)
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
    parser.add_argument('yaml_path', nargs='?',
                        default=str(DEFAULT_YAML),
                        help='增量 yaml 路径（缺省 cache/data/_countries-data.videos.yaml）')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dry-run', action='store_true', help='预览模式（默认，零写盘）')
    group.add_argument('--apply', action='store_true', help='执行写盘（json → yaml 回写 → html 重建）')
    group.add_argument('--empty-video', action='store_true',
                       help='列出 videos 为空的行（只读，零写盘；与 --apply/--dry-run 互斥）')
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

    # CL004: --empty-video 只读列出（J1: 读 target.data 指向的 json; 零写盘 exit 0）
    if args.empty_video:
        return run_empty_video(data_doc)

    # 3. F3 校验先行（任一 country_zh 缺失 → 打印缺失键清单 exit 1 零写盘）
    missing = validate_countries(countries, rows_by_country)
    if missing:
        print('[错误] 以下国家键在 json 中不存在（或缺少 country_zh），未做任何修改:')
        for m in missing:
            print(f'  - {m}')
        return 1

    # 4. 逐条计算三态增量（v1.2：新增 / 更新 / 跳过；yaml 内部同 country+url 取首条）
    new_items, updates, skipped = build_increments(countries, rows_by_country)

    # 5. G 判定（v1.2 修订）：new 与 updates 双空才中断 → 打印统计提示 exit 0 零写盘（幂等）。
    #    N = 去重后 yaml 有效条目数、M = 去重国家数（口径与 build_increments 一致，
    #    畸形条目缺 country_zh/url 被 warn+continue 不计入，HG-SEC-085）
    if not new_items and not updates:
        all_items = new_items + updates + skipped
        n_count = len(all_items)
        m_count = len({it['country_zh'] for it in all_items})
        print(f'[提示] 所有 videos 均已包含，无需同步'
              f'（yaml 检查 {n_count} 条 / 涉及 {m_count} 个国家）')
        return 0

    # dry-run 预览（默认态，零写盘）
    if not args.apply:
        print(f'[预览] 新增 {len(new_items)} 条:')
        for it in new_items:
            print(f'  - {it["country_zh"]}: {it["title"]} {it["url"]} ({it["duration"]})')
        if updates:
            print(f'[预览] 更新 {len(updates)} 条（url 已存在, title 变更）:')
            for it in updates:
                print(f'  - {it["country_zh"]}: {it["old_title"]} → {it["title"]} {it["url"]}')
        if skipped:
            print(f'[预览] 跳过 {len(skipped)} 条（url 已存在, title 相同）:')
            for it in skipped:
                print(f'  - {it["country_zh"]}: {it["title"]} {it["url"]}')
        print(f'[预览] 将回写 yaml countries 段（全局镜像）+ 重建 {html_rel}')
        print('[提示] 使用 --apply 执行')
        return 0

    # --apply 执行
    return run_apply(args, doc, target, countries, json_path, html_path,
                     data_doc, rows, rows_by_country, new_items, updates)


if __name__ == '__main__':
    sys.exit(main())
