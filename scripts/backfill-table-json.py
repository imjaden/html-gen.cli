#!/usr/bin/env python3
"""从产物 HTML 回填 table 数据源的 columns/data（CL038）。

背景：页面被改过（列被扩/收缩）而 `data/_<x>.json` 没跟上时，任何一次「按数据源重刷」
都会把页面改回去（丢列）。本脚本反向回收产物内嵌的 `const COLUMNS` / `const DATA`，
写回数据文件，并做**字段级**差异报告（不看 unified diff —— DATA 是压缩单行，肉眼看不出改了哪个字段）。

用法：
    python3 scripts/backfill-table-json.py --pair demos/drama/daming-strategy-table.html=data/_drama-table-daming-strategy.json --dry-run
    python3 scripts/backfill-table-json.py --pair ... --apply

约定：只回填 columns/data；tabs/options 等其余键原样保留（产物里也有 OPTIONS，但两份当前一致，
不做覆盖以免把「数据源是权威」这条反过来用）。
"""
import argparse
import json
import pathlib
import re
import sys

COLS_RE = re.compile(r'const COLUMNS\s*=\s*(\[.*?\]);', re.S)
DATA_RE = re.compile(r'const DATA\s*=\s*(\[.*?\]);', re.S)
# 行内字段名 = 该行所有 key 的并集（列被删/加时表结构变化也在这里体现）
SKIP_KEYS = {'tabs', 'options', 'title', 'subtitle', 'output'}


def _embedded(html: str, pat, name: str):
    m = pat.search(html)
    if not m:
        raise SystemExit(f'产物里找不到 const {name}')
    return json.loads(m.group(1))


def field_diff(old_rows, new_rows):
    out = []
    for i, (o, n) in enumerate(zip(old_rows, new_rows)):
        if o == n:
            continue
        changed = {k: (o.get(k), n.get(k)) for k in n
                   if o.get(k) != n.get(k)}
        extra = {k: ('<none>', None) for k in o if k not in n}
        gone = {k: (None, '<dropped>') for k in n if k not in o}
        out.append((i, {**changed, **extra, **gone}))
    if len(old_rows) != len(new_rows):
        out.append(('rows', {'count': (len(old_rows), len(new_rows))}))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='从产物回填 columns/data（CL038）')
    ap.add_argument('--pair', action='append', required=True,
                    metavar='HTML=JSON', help='产物路径=数据源路径（可多次）')
    ap.add_argument('--apply', action='store_true', help='真正写盘（缺省只报告）')
    ap.add_argument('--drop-orphans', action='store_true',
                    help='允许丢弃旧行里产物不再渲染的字段（缺省保留为未渲染键）')
    a = ap.parse_args(argv)

    rc = 0
    for spec in a.pair:
        html_p, json_p = (pathlib.Path(x) for x in spec.split('=', 1))
        html = html_p.read_text(encoding='utf-8')
        raw = json.loads(json_p.read_text(encoding='utf-8'))
        cols = _embedded(html, COLS_RE, 'COLUMNS')
        data = _embedded(html, DATA_RE, 'DATA')

        old_cols = [(c.get('key'), c.get('label'), c.get('width')) for c in raw.get('columns', [])]
        new_cols = [(c.get('key'), c.get('label'), c.get('width')) for c in cols]
        added = [c for c in new_cols if c[0] not in {x[0] for x in old_cols}]
        dropped = [c for c in old_cols if c[0] not in {x[0] for x in new_cols}]
        width_chg = [(o[0], o[2], n[2]) for o, n in zip(old_cols, new_cols)
                     if o[0] == n[0] and o[2] != n[2]]
        # 旧行里「产物已不再渲染」的字段（典型：schema 迁移后被拆成多列的 idiom）不能静默丢弃：
        # 缺省存到**顶层 legacy 段**（{字段: {行标识: 值}}）—— 模板只序列化 columns/data，
        # 顶层额外键不进产物 ⇒ 既不丢数据、也不改页面字节。--drop-orphans 才允许丢。
        orphans = {}
        if not a.drop_orphans:
            legacy = raw.setdefault('legacy', {})
            for idx, (old, new) in enumerate(zip(raw.get('data', []), data)):
                rid = str(old.get('strategy') or f'row{idx}')
                for k, v in old.items():
                    if k not in new and v not in (None, ''):
                        orphans[k] = orphans.get(k, 0) + 1
                        legacy.setdefault(k, {})[rid] = v
        diffs = field_diff(raw.get('data', []), data)

        print(f'== {json_p} ← {html_p}')
        print(f'   columns {len(old_cols)} → {len(new_cols)}；新增 {[c[0] for c in added]}；'
              f'移除 {[c[0] for c in dropped]}；宽度变更 {width_chg}')
        print(f'   data 行 {len(raw.get("data", []))} → {len(data)}；字段差异 {len(diffs)} 行'
              + (f'；保留未渲染字段 {dict(orphans)}（不丢数据，--drop-orphans 才丢）' if orphans else ''))
        for i, d in diffs[:5]:
            print(f'     行 {i}: ' + ', '.join(f'{k}: {v[0]!r}→{v[1]!r}' for k, v in list(d.items())[:4]))

        if a.apply:
            raw['columns'], raw['data'] = cols, data
            json_p.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print('   ✅ 已回填')
        else:
            print('   （dry-run，未写盘）')
    return rc


if __name__ == '__main__':
    sys.exit(main())
