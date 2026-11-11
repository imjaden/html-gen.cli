#!/usr/bin/env python3
"""渲染基线门禁 —— 模板源码与代表产物的 sha256 钉子（HTML-GEN-CL029）。

来源: daily-checker 转交件 ⑥（本仓侧「改了模板却没人发现产物漂移」的守卫）。
设计取舍:
  - 只钉**子集**（4 个模板/样式源 + 5 个代表页），不做全仓哈希 —— 全量会在每次正常重建时全红。
  - 基线文件随仓入库（`data/_render-baseline.json`），改模板后必须**显式** `--update` 重建，
    这样「产物变了但没人说」会变成门禁红，而不是静默漂移。
  - 只依赖标准库；`--root` 供测试在临时副本上跑，不碰真仓。

用法:
  python3 scripts/baseline.py --check            # 校验（rc=0 全绿 / rc=1 有漂移或缺文件）
  python3 scripts/baseline.py --check --json     # 机器可读
  python3 scripts/baseline.py --update           # 重建基线（改完模板并确认产物正确后跑）
  python3 scripts/baseline.py --check --root /tmp/x   # 在指定根上跑（测试用）
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_REL = 'data/_render-baseline.json'

# 子集口径: 模板/样式源（真值层）+ 代表产物（消费层各类型各一）
SUBSET = [
    'layout-table.html',
    'layout-doc.html',
    'layout-knowledge.html',
    'style-guide.css',
    'index.html',
    'demos/index.html',
    'demos/demos-index.html',
    'demos/countries-table.html',
    'demos/provinces-table.html',
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root):
    files = {}
    for rel in SUBSET:
        p = root / rel
        if not p.is_file():
            files[rel] = {'sha256': None, 'bytes': None, 'reason': 'missing'}
            continue
        files[rel] = {'sha256': sha256_of(p), 'bytes': p.stat().st_size}
    return files


def load_baseline(root):
    p = root / BASELINE_REL
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f'❌ 基线文件损坏: {p} ({e})', file=sys.stderr)
        return None


def cmd_update(root, quiet=False):
    data = {
        'version': 1,
        'generated': datetime.now().strftime('%Y-%m-%d'),
        'note': 'CL029 渲染基线：改模板/产物后跑 scripts/baseline.py --update 重建',
        'files': snapshot(root),
    }
    out = root / BASELINE_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not quiet:
        print(f'✅ 已重建基线: {out}（{len(data["files"])} 个文件）')
    return 0


def cmd_check(root, as_json=False):
    base = load_baseline(root)
    if base is None:
        msg = f'未找到基线文件 {root / BASELINE_REL} —— 先跑 --update 建立基线'
        if as_json:
            print(json.dumps({'ok': False, 'error': msg, 'mismatches': []}, ensure_ascii=False))
        else:
            print(f'❌ {msg}', file=sys.stderr)
        return 2

    expected = base.get('files', {})
    actual = snapshot(root)
    mismatches = []
    for rel in SUBSET:
        exp, act = expected.get(rel), actual.get(rel, {})
        if exp is None:
            mismatches.append({'path': rel, 'reason': 'not-in-baseline',
                               'expected': None, 'actual': act.get('sha256')})
        elif act.get('reason') == 'missing':
            if exp.get('sha256') is None:
                # 基线建立时该文件本就不存在（子集里允许缺项）⇒ 仍算一致
                continue
            mismatches.append({'path': rel, 'reason': 'missing',
                               'expected': exp.get('sha256'), 'actual': None})
        elif exp.get('sha256') != act.get('sha256'):
            mismatches.append({'path': rel, 'reason': 'changed',
                               'expected': exp.get('sha256'), 'actual': act.get('sha256'),
                               'bytes_expected': exp.get('bytes'), 'bytes_actual': act.get('bytes')})

    ok = not mismatches
    if as_json:
        print(json.dumps({'ok': ok, 'total': len(SUBSET), 'mismatches': mismatches},
                         ensure_ascii=False, indent=2))
        return 0 if ok else 1

    for rel in SUBSET:
        hit = next((m for m in mismatches if m['path'] == rel), None)
        if hit:
            print(f"❌ {rel}: {hit['reason']}"
                  + (f" （{str(hit['expected'])[:12]} → {str(hit['actual'])[:12]}）" if hit['reason'] == 'changed' else ''))
        else:
            print(f'✅ {rel}')
    if ok:
        print(f'\n基线一致: {len(SUBSET)}/{len(SUBSET)}（{root}）')
        return 0
    print(f'\n漂移 {len(mismatches)}/{len(SUBSET)} —— 确认产物正确后跑 --update 重建基线', file=sys.stderr)
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog='baseline.py',
        description='渲染基线门禁: 模板源码 + 代表产物的 sha256 钉子（HTML-GEN-CL029）')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--check', action='store_true', help='校验当前状态是否与基线一致（rc=0/1）')
    g.add_argument('--update', action='store_true', help='重建基线文件')
    ap.add_argument('--root', default=None, help='仓库根（默认本脚本上一级）')
    ap.add_argument('--json', action='store_true', help='--check 时输出 JSON')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else ROOT
    if not root.is_dir():
        print(f'❌ 根目录不存在: {root}', file=sys.stderr)
        return 2
    if args.update:
        return cmd_update(root, quiet=args.quiet)
    return cmd_check(root, as_json=args.json)


if __name__ == '__main__':
    sys.exit(main())
