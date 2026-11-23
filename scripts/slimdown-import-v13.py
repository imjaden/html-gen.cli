#!/usr/bin/env python3
"""slimdown v1.3 数据导入 —— 把两份参考页（按星期 / 按主题）搬进单一数据源。

来源（只读，用户 Downloads）：居家训练计划（按星期）-v1.3-20261123.html
                             居家训练计划（按主题）-v1.3-20261123.html
落点：data/_slimdown-plan.json（presets[home,strength] + themes[4]）
      data/_slimdown-exercises.json（append ex73–ex80 + 新增「居家自重」tab + 计数文案）

用法:
  python3 scripts/slimdown-import-v13.py --dry-run
  python3 scripts/slimdown-import-v13.py --apply

设计取舍:
  - 参考页里的数据是 JS 字面量（非 JSON），这里只用正则取字段，不 eval、不 execute。
  - 动作名 → 库 id 的映射是显式表；出现表外动作名直接报错退出（fail-closed），不静默丢条目。
  - 旧的七日力量版原样搬进 presets[strength]，不重算数值（避免「顺手改了没说的」）。
  - 幂等：库条目按 id 判断是否已存在；plan 页忽略生成本身的时间戳，重复跑逐字节一致。
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PLAN = ROOT / 'data' / '_slimdown-plan.json'
DATA_EX = ROOT / 'data' / '_slimdown-exercises.json'
REF_WEEK = Path.home() / 'Downloads' / '居家训练计划（按星期）-v1.3-20261123.html'
REF_THEME = Path.home() / 'Downloads' / '居家训练计划（按主题）-v1.3-20261123.html'

VERSION = 'v1.3'
UPDATED = '2026-11-23'
SETS_HINT = '3–5'

# 参考页动作名 → 库 id（ex47 平板支撑 / ex51 标准俯卧撑 复用既有条目）
NAME2ID = {
    '深蹲': 'ex73',
    '平板支撑': 'ex47',
    '卷腹': 'ex74',
    '开合跳': 'ex75',
    '弓步蹲': 'ex76',
    '靠墙静蹲': 'ex77',
    '仰卧起坐': 'ex78',
    '后踢腿': 'ex79',
    '俯卧撑': 'ex51',
    '马步蹲': 'ex80',
}

# 新增库条目（id 顺序即数组顺序；只许 append，插队会破坏分享链接的库内序号）
NEW_EX = [
    ('ex73', '自重深蹲 Bodyweight Squat', '居家自重', '徒手', '股四·臀', '3×20 次', 3, '20 次', '徒手深蹲 · 空手深蹲'),
    ('ex74', '卷腹 Crunch', '居家自重', '瑜伽垫', '腹直肌', '3×25 次', 3, '25 次', '仰卧卷腹'),
    ('ex75', '开合跳 Jumping Jack', '居家自重', '徒手', '全身有氧', '3×35 次', 3, '35 次', '开合跳 · 星星跳'),
    ('ex76', '弓步蹲 Lunge', '居家自重', '徒手', '股四·臀', '3×15 次', 3, '15 次', '箭步蹲 · 前弓步'),
    ('ex77', '靠墙静蹲 Wall Sit', '居家自重', '墙面', '股四', '3×30 秒', 3, '30 秒', '贴墙静蹲'),
    ('ex78', '仰卧起坐 Sit-up', '居家自重', '瑜伽垫', '腹直肌', '3×15 次', 3, '15 次', '屈膝仰卧起坐'),
    ('ex79', '后踢腿 Back Kick', '居家自重', '瑜伽垫', '臀·腘绳', '3×20 次', 3, '20 次', '跪姿后踢 · 驴踢'),
    ('ex80', '马步蹲 Horse Stance Squat', '居家自重', '徒手', '股四', '3×60 次', 3, '60 次', '马步 · 桩功蹲'),
]

DAY_RE = re.compile(r"key:'(\w+)', label:'([^']*)'")
ITEM_RE = re.compile(r"\{ n:'([^']*)',\s*r:'([^']*)',\s*m:'([^']*)'\s*\}")
THEME_RE = re.compile(r"\{ cn:'([^']*)',\s*en:'([^']*)',\s*m:'([^']*)'(?:,\s*note:'([^']*)')?\s*\}")
SHORT = {'mon': '一', 'tue': '二', 'wed': '三', 'thu': '四', 'fri': '五', 'sat': '六', 'sun': '日'}


def read(p):
    return p.read_text(encoding='utf-8')


def grab(chunk, key):
    m = re.search(key + r":'([^']*)'", chunk)
    return m.group(1) if m else ''


def parse_days(html):
    """按 key:'xx' 切块，逐块取主题/时长/口号/动作；周日取 recover 清单。"""
    marks = list(DAY_RE.finditer(html))
    if len(marks) != 7:
        raise SystemExit(f'参考页应有 7 天，实际 {len(marks)}')
    days = []
    for i, m in enumerate(marks):
        chunk = html[m.start(): marks[i + 1].start() if i + 1 < len(marks) else len(html)]
        key, label = m.group(1), m.group(2)
        day = {
            'key': key,
            'label': label,
            'short': SHORT.get(key, label[-1]),
            'theme': grab(chunk, 'theme'),
            'duration': grab(chunk, 'time'),
            'slogan': grab(chunk, 'slogan'),
        }
        if 'rest:true' in chunk:
            rec = re.search(r'recover:\[([^\]]*)\]', chunk)
            day['rest'] = True
            day['recover'] = re.findall(r"'([^']*)'", rec.group(1)) if rec else []
            days.append(day)
            continue
        day['setsHint'] = SETS_HINT
        items = []
        for name, reps, muscle in ITEM_RE.findall(chunk):
            if name not in NAME2ID:
                raise SystemExit(f'动作名未映射: {name}')
            items.append({'id': NAME2ID[name], 'reps': reps, 'muscle': muscle})
        day['items'] = items
        days.append(day)
    return days


def parse_themes(html):
    blocks = re.split(r"\n\s*\{\n\s*tag:", html)
    out = []
    for b in blocks[1:]:
        tag = re.match(r"'([^']*)'", b).group(1)
        name = grab(b, 'name')
        video = re.search(r"video:\{\s*\n?\s*title:'([^']*)',\s*\n?\s*url:'([^']*)'", b)
        items = []
        for cn, en, muscle, note in THEME_RE.findall(b):
            it = {'cn': cn, 'en': en, 'm': muscle}
            if note:
                it['note'] = note
            items.append(it)
        if not items or not video:
            raise SystemExit(f'主题块解析失败: {tag}')
        out.append({
            'id': 't%02d' % (len(out) + 1),
            'tag': tag,
            'name': name,
            'time': grab(b, 'time'),
            'pace': grab(b, 'pace'),
            'sets': int(re.search(r'suggestSets:(\d+)', b).group(1)),
            'video': {'title': video.group(1).strip(), 'url': video.group(2)},
            'items': items,
        })
    return out


def build_plan(old, days, themes):
    strength = None
    for p in old.get('presets') or []:
        if p.get('id') == 'strength':
            strength = p
    if strength is None:
        strength = {'id': 'strength', 'label': '力量版', 'version': old.get('version', 'v1.2'),
                    'days': old.get('days') or []}
    plan = {
        'version': VERSION,
        'updated': UPDATED,
        'title': '居家训练计划',
        'subtitle': '按星期或按主题看今天练什么 · 右下角可编辑 / 存图',
        'meta': old.get('meta') or {},
        'defaultPreset': 'home',
        'presets': [
            {'id': 'home', 'label': '居家七日', 'version': VERSION,
             'slogan': '干净饮食 · 热量缺口 · 减脂增肌', 'days': days},
            strength,
        ],
        'themes': themes,
    }
    return plan


def build_ex(raw, plan):
    rows = raw['data']
    have = {r['id'] for r in rows}
    added = 0
    for rid, name, theme, equip, muscle, load, sets, reps, alias in NEW_EX:
        if rid in have:
            continue
        rows.append({'id': rid, 'name': name, 'theme': theme, 'equip': equip,
                     'muscle': muscle, 'load': load, 'sets': sets, 'reps': reps, 'alias': alias})
        added += 1
    tabs = raw.get('tabs') or []
    if not any(t.get('label') == '居家自重' for t in tabs):
        tabs.append({'key': 'home', 'label': '居家自重', 'field': 'theme', 'value': '居家自重', 'contains': True})
    raw['tabs'] = tabs
    raw['subtitle'] = re.sub(r'^\d+ 个动作 · \d+ 个主题',
                             f'{len(rows)} 个动作 · {len(tabs) - 1} 个主题', raw['subtitle'])
    return raw, added


def check(plan, ex):
    home = [p for p in plan['presets'] if p['id'] == 'home'][0]
    items = sum(len(d.get('items') or []) for d in home['days'])
    rest = sum(len(d.get('recover') or []) for d in home['days'])
    ids = [r['id'] for r in ex['data']]
    assert len(home['days']) == 7, len(home['days'])
    assert items == 52, items
    assert rest == 5, rest
    assert len(plan['themes']) == 4, len(plan['themes'])
    assert sum(len(t['items']) for t in plan['themes']) == 41, sum(len(t['items']) for t in plan['themes'])
    assert len(ids) == len(set(ids)), '库 id 重复'
    assert ids[:72] == ['ex%02d' % i for i in range(1, 73)], '既有 72 条顺序被打乱'
    return items, rest


def main():
    ap = argparse.ArgumentParser(description='slimdown v1.3 数据导入')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    for p in (REF_WEEK, REF_THEME):
        if not p.exists():
            raise SystemExit(f'参考页缺失: {p}')

    old = json.loads(read(DATA_PLAN))
    raw = json.loads(read(DATA_EX))
    days = parse_days(read(REF_WEEK))
    themes = parse_themes(read(REF_THEME))
    plan = build_plan(old, days, themes)
    ex, added = build_ex(raw, plan)
    items, rest = check(plan, ex)

    out_plan = json.dumps(plan, ensure_ascii=False, indent=2) + '\n'
    out_ex = json.dumps(ex, ensure_ascii=False, indent=2) + '\n'
    if args.dry_run:
        print(f'[dry] home: {len(days)} 天 / {items} 条动作 / {rest} 条恢复')
        print(f'[dry] themes: {len(themes)} 套 / {sum(len(t["items"]) for t in themes)} 项')
        print(f'[dry] 库: {len(ex["data"])} 条（新增 {added}）/ tabs {len(ex["tabs"])}')
        print(f'[dry] would write {DATA_PLAN.name} ({len(out_plan.encode("utf-8")):,} B) / '
              f'{DATA_EX.name} ({len(out_ex.encode("utf-8")):,} B)')
        return
    DATA_PLAN.write_text(out_plan, encoding='utf-8')
    DATA_EX.write_text(out_ex, encoding='utf-8')
    print(f'✅ {DATA_PLAN.relative_to(ROOT)} · {len(out_plan.encode("utf-8")):,} B')
    print(f'✅ {DATA_EX.relative_to(ROOT)} · {len(out_ex.encode("utf-8")):,} B')
    print(f'✅ home {len(days)} 天 / {items} 条 / 恢复 {rest} · themes {len(themes)} 套 · 库 +{added}')


if __name__ == '__main__':
    main()
