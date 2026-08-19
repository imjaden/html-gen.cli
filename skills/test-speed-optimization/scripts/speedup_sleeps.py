#!/usr/bin/env python3
"""speedup_sleeps.py — 测试 sleep 调低脚本.

按映射表将 tests/*.py 中的 time.sleep 大值减半:
  0.3 → 0.15   0.4 → 0.2    0.5 → 0.25
  0.6 → 0.3    0.8 → 0.4    0.9 → 0.45
  0.08 / 0.1 / 0.15 / 0.2 / 0.25 保持不变

用法:
  python3 speedup_sleeps.py --dry-run    # 预览改动
  python3 speedup_sleeps.py --apply      # 应用 (自动 .bak 备份)
  python3 speedup_sleeps.py --restore    # 回滚所有 .bak

幂等: 已改行标记 `# [speedup]`, 二次运行不重复改。
"""
import argparse
import re
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'tests'

# 映射: 原始大值 → 减半值
HALVE = {
    '0.3': '0.15',
    '0.4': '0.2',
    '0.5': '0.25',
    '0.6': '0.3',
    '0.8': '0.4',
    '0.9': '0.45',
}

MARKER = '# [speedup]'

# 匹配 time.sleep(X)，且行内无 MARKER（幂等）
SLEEP_RE = re.compile(r'time\.sleep\((\d+\.\d+)\)')


def is_applied(line: str) -> bool:
    return MARKER in line


def transform(line: str) -> str:
    """单行: 若含未标记的大值 sleep, 减半并打标记."""
    if is_applied(line):
        return line
    m = SLEEP_RE.search(line)
    if not m:
        return line
    val = m.group(1)
    if val not in HALVE:
        return line
    new_val = HALVE[val]
    # 替换第一个匹配的 sleep 值, 并追加标记
    new_line = line.replace(f'time.sleep({val})', f'time.sleep({new_val})', 1)
    return new_line.rstrip() + f'  {MARKER}\n'


def scan() -> list:
    files = sorted(TESTS_DIR.glob('test_*.py'))
    out = []
    for f in files:
        lines = f.read_text(encoding='utf-8').split('\n')
        changed = []
        for i, line in enumerate(lines):
            if is_applied(line):
                continue
            m = SLEEP_RE.search(line)
            if m and m.group(1) in HALVE:
                changed.append((i, line, m.group(1)))
        if changed:
            out.append((f, changed))
    return out


def apply_changes(verbose=True):
    plan = scan()
    if not plan:
        print('无待改 sleep (可能已全部应用)')
        return 0
    for f, changed in plan:
        lines = f.read_text(encoding='utf-8').split('\n')
        # .bak 备份
        bak = f.with_suffix(f.suffix + '.bak')
        if not bak.exists():
            bak.write_text(f.read_text(encoding='utf-8'), encoding='utf-8')
        for i, _line, val in changed:
            lines[i] = transform(lines[i])
        f.write_text('\n'.join(lines), encoding='utf-8')
        if verbose:
            for i, _line, val in changed:
                print(f'  {f.name}:{i+1}  {val}s → {HALVE[val]}s')
    if verbose:
        print(f'\n共改 {len(plan)} 文件, {sum(len(c) for _, c in plan)} 处')
    return len(plan)


def dry_run():
    plan = scan()
    if not plan:
        print('无待改 sleep (可能已全部应用)')
        return
    total = 0
    for f, changed in plan:
        print(f'{f.name}:')
        for i, _line, val in changed:
            print(f'  L{i+1}: {val}s → {HALVE[val]}s')
            total += 1
    print(f'\n共 {len(plan)} 文件, {total} 处')


def restore():
    baks = sorted(TESTS_DIR.glob('test_*.py.bak'))
    if not baks:
        print('无 .bak 可回滚')
        return
    for bak in baks:
        target = bak.with_suffix('')
        target.write_text(bak.read_text(encoding='utf-8'), encoding='utf-8')
        bak.unlink()
        print(f'  回滚 {target.name}')
    print(f'\n回滚 {len(baks)} 文件')


def main():
    ap = argparse.ArgumentParser(description='测试 sleep 调低脚本')
    ap.add_argument('--dry-run', action='store_true', help='预览改动')
    ap.add_argument('--apply', action='store_true', help='应用改动 (.bak 备份)')
    ap.add_argument('--restore', action='store_true', help='回滚所有 .bak')
    args = ap.parse_args()

    if not TESTS_DIR.exists():
        print(f'❌ tests 目录不存在: {TESTS_DIR}', file=sys.stderr)
        sys.exit(1)

    if args.restore:
        restore()
    elif args.apply:
        apply_changes()
    else:
        dry_run()


if __name__ == '__main__':
    main()
