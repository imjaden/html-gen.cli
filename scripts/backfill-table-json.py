#!/usr/bin/env python3
"""从产物 HTML 回填 table 数据源的 columns/data（CL038 / CL040）。

背景：页面被改过（列被扩/收缩）而 `data/_<x>.json` 没跟上时，任何一次「按数据源重刷」
都会把页面改回去（丢列）。本脚本反向回收产物内嵌的 `const COLUMNS` / `const DATA`，
写回数据文件，并做**字段级**差异报告（不看 unified diff —— DATA 是压缩单行，肉眼看不出改了哪个字段）。

用法：
    python3 scripts/backfill-table-json.py --pair <html>=<json>              # 只报告
    python3 scripts/backfill-table-json.py --pair <html>=<json> --dry-run    # 同上（显式）
    python3 scripts/backfill-table-json.py --pair <html>=<json> --apply      # 写盘

退出码（CL040 D4）：0 正常（含 dry-run）/ 2 输入被拒（行数不等、行标识重复，未写盘）/ 1 保留给渲染或 IO 失败。

数据保全（CL040 D3/D4）：旧行里「产物已不再渲染」的字段（典型：schema 迁移后被拆成多列的 idiom）
缺省存到**顶层 legacy 段**（{字段: {行标识: 值}}）—— 模板只序列化 columns/data，顶层额外键不进产物，
既不丢数据也不改页面字节。`--drop-orphans` = 已知旧行/旧字段可丢：不写 legacy 并清掉既有 legacy 段。

约定：只回填 columns/data；tabs/options 等其余键原样保留（产物里也有 OPTIONS，两份当前一致，
不做覆盖以免把「数据源是权威」这条反过来用）。
"""
import argparse
import json
import pathlib
import re
import sys

COLS_RE = re.compile(r'const COLUMNS\s*=\s*(\[.*?\]);', re.S)
DATA_RE = re.compile(r'const DATA\s*=\s*(\[.*?\]);', re.S)


def _embedded(html: str, pat, name: str):
    m = pat.search(html)
    if not m:
        raise SystemExit(f'产物里找不到 const {name}')
    return json.loads(m.group(1))


def row_key(row, idx):
    """行标识：优先业务键 strategy，缺省回退 row{idx}（legacy 段与悬空报告共用同一口径）。"""
    return str(row.get('strategy') or f'row{idx}')


def field_diff(old_rows, new_rows):
    """逐行字段差异：added = 新行有旧行无；dropped = 旧行有新行无；changed = 两边值不同。

    CL040 D5 前这里把 added/dropped 的名字与值双向错位，且两侧都丢真值（只留 '<none>'/'<dropped>'）
    ⇒ 复核者看不到「被摘掉的是什么值」。现在三类各带自己的真值。
    """
    out = []
    for i, (o, n) in enumerate(zip(old_rows, new_rows)):
        if o == n:
            continue
        added = {k: n[k] for k in n if k not in o}
        dropped = {k: o[k] for k in o if k not in n}
        changed = {k: (o[k], n[k]) for k in n if k in o and o[k] != n[k]}
        out.append((i, {'added': added, 'dropped': dropped, 'changed': changed}))
    if len(old_rows) != len(new_rows):
        out.append(('rows', {'added': {}, 'dropped': {},
                             'changed': {'rows': (len(old_rows), len(new_rows))}}))
    return out


def fmt_diff(d):
    parts = [f'+{k}={v!r}' for k, v in d['added'].items()]
    parts += [f'-{k}={v!r}' for k, v in d['dropped'].items()]
    parts += [f'~{k}={a!r}→{b!r}' for k, (a, b) in d['changed'].items()]
    return ' '.join(parts)


def dangling_legacy(raw):
    """legacy 段里按行标识 join 不到任何行的键（改名即断链的当场暴露面，CL040 D3）。"""
    keys = {row_key(r, i) for i, r in enumerate(raw.get('data', []))}
    bad = []
    for field, mapping in (raw.get('legacy') or {}).items():
        if not isinstance(mapping, dict):
            continue
        for rid in mapping:
            if rid not in keys:
                bad.append(f'{field}.{rid}')
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description='从产物回填 columns/data（CL038/CL040）')
    ap.add_argument('--pair', action='append', required=True,
                    metavar='HTML=JSON', help='产物路径=数据源路径（可多次）')
    ap.add_argument('--apply', action='store_true', help='真正写盘（缺省只报告）')
    ap.add_argument('--dry-run', action='store_true', help='显式只报告（与缺省同义，防文档/实现背离）')
    ap.add_argument('--drop-orphans', action='store_true',
                    help='允许丢弃旧行里产物不再渲染的字段（并清掉既有 legacy 段）')
    a = ap.parse_args(argv)
    if a.apply and a.dry_run:
        print('❌ --apply 与 --dry-run 互斥', file=sys.stderr)
        return 2

    rc = 0
    for spec in a.pair:
        html_p, json_p = (pathlib.Path(x) for x in spec.split('=', 1))
        html = html_p.read_text(encoding='utf-8')
        raw = json.loads(json_p.read_text(encoding='utf-8'))
        cols = _embedded(html, COLS_RE, 'COLUMNS')
        data = _embedded(html, DATA_RE, 'DATA')

        old_rows = raw.get('data', [])
        old_cols = [(c.get('key'), c.get('label'), c.get('width')) for c in raw.get('columns', [])]
        new_cols = [(c.get('key'), c.get('label'), c.get('width')) for c in cols]
        added = [c for c in new_cols if c[0] not in {x[0] for x in old_cols}]
        dropped = [c for c in old_cols if c[0] not in {x[0] for x in new_cols}]
        width_chg = [(o[0], o[2], n[2]) for o, n in zip(old_cols, new_cols)
                     if o[0] == n[0] and o[2] != n[2]]

        print(f'== {json_p} ← {html_p}')
        print(f'   columns {len(old_cols)} → {len(new_cols)}；新增 {[c[0] for c in added]}；'
              f'移除 {[c[0] for c in dropped]}；宽度变更 {width_chg}')
        print(f'   data 行 {len(old_rows)} → {len(data)}')

        # ── 前置校验（CL040 D4）：静默丢数据比拒绝严重得多 ──
        problems = []
        if len(old_rows) != len(data):
            problems.append(f'行数不等：源 {len(old_rows)} 行 / 产物 {len(data)} 行'
                            '（按索引 zip 会让尾部旧行整行消失）')
        seen, dups = set(), set()
        for i, r in enumerate(old_rows):
            k = row_key(r, i)
            if k in seen:
                dups.add(k)
            seen.add(k)
        if dups:
            problems.append(f'行标识重复：{sorted(dups)}（legacy 段会互相覆盖）')
        if problems:
            if a.drop_orphans:
                for p in problems:
                    print(f'   ⚠️ {p}（--drop-orphans 已声明旧行可丢，继续）', file=sys.stderr)
            else:
                for p in problems:
                    print(f'   ❌ {p}', file=sys.stderr)
                print('   → 拒绝写入（rc=2）。确认旧行本就可丢时加 --drop-orphans。', file=sys.stderr)
                rc = 2
                continue

        # ── 孤儿字段 → legacy（数据保全） ──
        orphans = {}
        if a.drop_orphans:
            raw.pop('legacy', None)
        else:
            legacy = raw.setdefault('legacy', {})
            for idx, (old, new) in enumerate(zip(old_rows, data)):
                rid = row_key(old, idx)
                for k, v in old.items():
                    if k not in new and v not in (None, ''):
                        orphans[k] = orphans.get(k, 0) + 1
                        legacy.setdefault(k, {})[rid] = v

        diffs = field_diff(old_rows, data)
        print(f'   字段差异 {len(diffs)} 行')
        for i, d in diffs[:5]:
            print(f'     行 {i}: {fmt_diff(d)}')
        if orphans:
            print(f'   保留未渲染字段 {dict(orphans)}（存顶层 legacy；--drop-orphans 才丢）')

        bad = dangling_legacy(raw)
        if bad:
            print(f'   ⚠️ legacy 悬空键 {len(bad)} 条（行已改名 ⇒ 无法按名 join）：{bad[:5]}'
                  + (' …' if len(bad) > 5 else ''))

        if a.apply:
            raw['columns'], raw['data'] = cols, data
            json_p.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print('   ✅ 已回填')
        else:
            print('   （dry-run，未写盘）')
    return rc


if __name__ == '__main__':
    sys.exit(main())
