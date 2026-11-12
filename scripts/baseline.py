#!/usr/bin/env python3
"""渲染基线门禁 —— 模板源码与代表产物的 sha256 钉子（HTML-GEN-CL029）。

来源: daily-checker 转交件 ⑥（「改了模板却没人发现产物漂移」）。
设计取舍:
  - 只钉**可判定的子集**（模板/样式源 + 全部可重建产物），不做全仓哈希 —— 全量会在每次正常重建时全红。
    v1.2（CL032）：子集从「4 模板 + 6 代表产物」扩到全量可 verify 产物；手写页 / 就地重建 / 生成后注入的页
    进 SKIP_PRODUCTS，`--verify` 逐条标注 skip 与理由，不再静默漏过。
  - `--verify` 把「产物是不是当前模板产出的」变成可判：用**从产物回收的参数集**重渲到临时目录比 sha。
    没有这一条，基线只能证明「文件没被改过」，证明不了「产物与模板同源」（v1.1 修的正是这个缺口）。
  - `--update` 默认先 verify；产物落后于模板时**拒绝**重建基线（需 `--force` 越权），
    避免把「模板已前进、产物没重刷」的漂移一次性拍成绿。
  - 只依赖标准库；`--root` 供测试在临时副本上跑，不碰真仓。

用法:
  python3 scripts/baseline.py --check                 # 校验钉子（0 一致 / 1 漂移 / 2 无基线 / 3 损坏）
  python3 scripts/baseline.py --check --json
  python3 scripts/baseline.py --verify                # 重渲比 sha：产物是否由当前模板产出
  python3 scripts/baseline.py --update                # 重建基线（先 verify；落后则拒，--force 越权）
  python3 scripts/baseline.py --check --root /tmp/x   # 在指定根上跑（测试用）
"""
import argparse
import hashlib
import html as H
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_REL = 'data/_render-baseline.json'

# 钉子子集: 模板/样式源（真值层，含 slide 源）+ 全部「可 verify 的产物」
# v1.2（CL032）: 子集从 10 项扩到全量可重建产物 —— 只钉几个代表页时，别的页停在上古模板也不会红。
SUBSET = [
    'layout-table.html',
    'layout-doc.html',
    'layout-knowledge.html',
    'layout-slide.html',
    'style-guide.css',
    'index.html',
    'demos/index.html',
    'demos/demos-index.html',
    'demos/countries-table.html',
    'demos/provinces-table.html',
    'demos/table-features-demo.html',
    'demos/table-actions-demo.html',
    'demos/hermes-profile-skills-list.html',
    'demos/slide-guide.html',
    'demos/usage-guide.html',
    'demos/doc-guide.html',
    'demos/table-guide.html',
    'demos/knowledge-guide.html',
    'demos/markdown-spec.html',
    'demos/knowledge-demo.html',
    'demos/drama-knowledge.html',
    'demos/chaitin-business-analysis.html',
    'demos/cloudwise-business-analysis.html',
]

# --verify 作业表: 产物 → 数据源。title/subtitle/corner/home 全部从产物回收，
# 不在脚本里维护第二份参数副本（参数漂移是 CL002 FIND-002 的老坑）。
TABLE_PRODUCTS = {
    'demos/countries-table.html': 'data/_countries-data.json',
    'demos/provinces-table.html': 'data/_provinces-data.json',
    'demos/table-features-demo.html': 'data/_table-features-demo.json',
    'demos/table-actions-demo.html': 'data/_table-actions-demo.json',
    'demos/hermes-profile-skills-list.html': 'data/_skills-table-config.json',
}
SLIDE_PRODUCTS = ['demos/slide-guide.html']
# doc 产物没有 md 路径痕迹可回收（产物里只有 basename），走**同目录同名约定**: demos/<name>.html ← demos/<name>.md
DOC_PRODUCTS = [
    'demos/usage-guide.html',
    'demos/doc-guide.html',
    'demos/table-guide.html',
    'demos/knowledge-guide.html',
    'demos/markdown-spec.html',
]
# knowledge 产物 → (kb-data, groups)。groups 缺失的页（the-price-you-choose）走 SKIP：
# 它是生成后注入层产物（rx-patch + canonical + w-note），CLI 直渲 != 产物。
KB_PRODUCTS = {
    'demos/knowledge-demo.html': ('data/_demo-kb-data.json', 'data/_demo-groups.json'),
    'demos/drama-knowledge.html': ('data/_drama-kb-data.json', 'data/_drama-groups.json'),
    'demos/chaitin-business-analysis.html': ('data/_chaitin-kb-data.json', 'data/_chaitin-groups.json'),
    'demos/cloudwise-business-analysis.html': ('data/_cloudwise-kb-data.json', 'data/_cloudwise-groups.json'),
}
# 不可判定型：就地重建 / 手写页 / 生成后注入 ⇒ verify 输出里逐条标注 skip 与理由（不静默漏过）
SKIP_PRODUCTS = {
    'demos/demos-index.html': '就地重建型（demo --rebuild），verify 不判定',
    'demos/index.html': '半手写落地页（demo featured 源），无单源数据可回收',
    'index.html': '手写落地页（仓根），无生成器',
    'demos/slide-demo.html': '手写页（无 .md 源），style/JS 手工同步',
    'demos/the-price-you-choose.html': '生成后注入层产物（rx-patch），CLI 直渲 != 产物',
}

GITHUB_RE = re.compile(r'<a href="([^"]+)" class="github-corner"')
HOME_RE = re.compile(r'<a class="home-link" href="([^"]+)"')
H1_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S)
DESC_RE = re.compile(r'<div class="table-desc">(.*?)</div>', re.S)
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.S)
MD_H1_RE = re.compile(r'^#\s+(.*)$', re.M)
KW_TITLE_RE = re.compile(r'<div class="w-title">📚\s*(.*?)</div>', re.S)
KW_SUB_RE = re.compile(r'<div class="sub">(.*?)</div>', re.S)
KW_WELCOME_RE = re.compile(r'<div class="w-sub">(.*?)</div>', re.S)
KW_WELCOME_DEFAULT = '从上方类目选择，浏览整理的知识内容。'


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
    """返回 (dict|None, err)；err ∈ {None, 'missing', 'corrupt: …'}。"""
    p = root / BASELINE_REL
    if not p.is_file():
        return None, 'missing'
    try:
        return json.loads(p.read_text(encoding='utf-8')), None
    except json.JSONDecodeError as e:
        return None, f'corrupt: {e}'


def _unesc(s):
    return H.unescape(s.replace('<br>', '\n')).strip()


def _plain(s):
    """去标签 + 反转义（产物里回收的标题/欢迎语可能含行内标签）。"""
    return _unesc(re.sub(r'<[^>]+>', '', s))


def _recovered_common(t):
    a = []
    m = GITHUB_RE.search(t)
    if m:
        a += ['--github-url', m.group(1)]
    m = HOME_RE.search(t)
    if m:
        a += ['--home-url', m.group(1)]
    return a


def build_jobs(root):
    """[(rel, argv)]：argv 能把该产物重渲出来（不含 -o）。"""
    jobs = []
    for rel, data in TABLE_PRODUCTS.items():
        target = root / rel
        if not target.is_file():
            continue
        t = target.read_text(encoding='utf-8')
        argv = ['table', '-d', data]
        m = H1_RE.search(t)
        if m:
            argv += ['--title', _unesc(m.group(1))]
        d = DESC_RE.search(t)
        if d and _unesc(d.group(1)):
            argv += ['--subtitle', _unesc(d.group(1))]
        argv += _recovered_common(t)
        jobs.append((rel, argv))
    for rel in SLIDE_PRODUCTS:
        md = root / Path(rel).with_suffix('.md')
        if (root / rel).is_file() and md.is_file():
            jobs.append((rel, ['slide', '-i', str(md.relative_to(root))]))
    for rel in DOC_PRODUCTS:
        target, md = root / rel, root / Path(rel).with_suffix('.md')
        if not target.is_file() or not md.is_file():
            continue
        t = target.read_text(encoding='utf-8')
        argv = ['doc', '-i', str(Path(rel).with_suffix('.md'))]
        # doc 的标题默认取 md 首个 h1；只在产物 <title> 与之不同时才显式传（不存第二份标题表）
        m, h1 = TITLE_RE.search(t), MD_H1_RE.search(md.read_text(encoding='utf-8'))
        if m and h1 and _plain(m.group(1)) != h1.group(1).strip():
            argv += ['--title', _plain(m.group(1))]
        argv += _recovered_common(t)
        jobs.append((rel, argv))
    for rel, (data, groups) in KB_PRODUCTS.items():
        target = root / rel
        if not target.is_file() or not (root / data).is_file():
            continue
        t = target.read_text(encoding='utf-8')
        argv = ['knowledge', '-d', data]
        if groups and (root / groups).is_file():
            argv += ['-g', groups]
        m = KW_TITLE_RE.search(t)
        if m and _plain(m.group(1)):
            argv += ['--title', _plain(m.group(1))]
        m = KW_SUB_RE.search(t)
        if m and _plain(m.group(1)):
            argv += ['--subtitle', _plain(m.group(1))]
        m = KW_WELCOME_RE.search(t)
        if m and _plain(m.group(1)) and _plain(m.group(1)) != KW_WELCOME_DEFAULT:
            argv += ['--welcome', _plain(m.group(1))]
        argv += _recovered_common(t)
        jobs.append((rel, argv))
    return jobs


def cmd_verify(root, as_json=False, quiet=False):
    """重渲比 sha。rc: 0 全部一致 / 1 有落后或渲染失败。"""
    cli = root / 'html-gen.py'
    tmpdir = Path(tempfile.mkdtemp(prefix='baseline-verify-'))
    results = []
    for rel, argv in build_jobs(root):
        out = tmpdir / rel.replace('/', '_')
        r = subprocess.run([sys.executable, str(cli)] + argv + ['-o', str(out)],
                           cwd=str(root), capture_output=True, text=True)
        if r.returncode != 0 or not out.is_file():
            results.append({'path': rel, 'status': 'fail', 'detail': r.stderr.strip()[:200]})
            continue
        same = out.read_text(encoding='utf-8') == (root / rel).read_text(encoding='utf-8')
        results.append({'path': rel, 'status': 'current' if same else 'stale',
                        'detail': f'{sha256_of(root / rel)[:12]} vs {sha256_of(out)[:12]}'})
    for rel, reason in SKIP_PRODUCTS.items():
        if (root / rel).is_file():
            results.append({'path': rel, 'status': 'skip', 'detail': reason})
    bad = [x for x in results if x['status'] in ('stale', 'fail')]
    if as_json:
        print(json.dumps({'ok': not bad, 'results': results}, ensure_ascii=False, indent=2))
    elif not quiet:
        for x in results:
            icon = {'current': '✅', 'stale': '❌ 落后', 'fail': '❌ 失败', 'skip': '⏭ 跳过'}[x['status']]
            print(f'{icon:9} {x["path"]:44} {x["detail"]}')
        print('\n产物与当前模板一致' if not bad else
              f'\n{len(bad)} 个产物落后于当前模板 —— 先重刷产物再 --update')
    return 0 if not bad else 1


def cmd_update(root, quiet=False, force=False):
    if not force:
        if cmd_verify(root, quiet=True) != 0:
            print('❌ 产物落后于当前模板，拒绝重建基线（否则会把漂移拍成绿）。\n'
                  '   先按 --verify 清单重刷产物；确需越权加 --force。', file=sys.stderr)
            return 1
    data = {
        'version': 2,
        'generated': datetime.now().strftime('%Y-%m-%d'),
        'note': 'CL029 渲染基线：改模板/产物后跑 scripts/baseline.py --update（默认先 --verify）',
        'verified': not force,
        'files': snapshot(root),
    }
    out = root / BASELINE_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not quiet:
        print(f'✅ 已重建基线: {out}（{len(data["files"])} 个文件，verified={data["verified"]}）')
    return 0


def cmd_check(root, as_json=False):
    base, err = load_baseline(root)
    if base is None:
        msg = (f'未找到基线文件 {root / BASELINE_REL} —— 先跑 --update 建立基线'
               if err == 'missing' else f'基线文件损坏（{root / BASELINE_REL}）：{err}')
        if as_json:
            print(json.dumps({'ok': False, 'total': len(SUBSET), 'error': msg, 'mismatches': []},
                             ensure_ascii=False))
        else:
            print(f'❌ {msg}', file=sys.stderr)
        return 2 if err == 'missing' else 3

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
                # 基线建立时该文件本就不存在（子集允许缺项）⇒ 仍算一致
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
                  + (f" （{str(hit['expected'])[:12]} → {str(hit['actual'])[:12]}）"
                     if hit['reason'] == 'changed' else ''))
        else:
            print(f'✅ {rel}')
    if ok:
        print(f'\n基线一致: {len(SUBSET)}/{len(SUBSET)}（{root}）')
        return 0
    print(f'\n漂移 {len(mismatches)}/{len(SUBSET)} —— 确认产物正确后跑 --update 重建基线',
          file=sys.stderr)
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog='baseline.py',
        description='渲染基线门禁: 模板源码 + 代表产物的 sha256 钉子（HTML-GEN-CL029）')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--check', action='store_true', help='校验钉子（0/1/2/3）')
    g.add_argument('--verify', action='store_true', help='重渲比 sha：产物是否由当前模板产出')
    g.add_argument('--update', action='store_true', help='重建基线（默认先 verify）')
    ap.add_argument('--root', default=None, help='仓库根（默认本脚本上一级）')
    ap.add_argument('--json', action='store_true', help='机器可读输出')
    ap.add_argument('--force', action='store_true', help='--update 跳过 verify（越权）')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else ROOT
    if not root.is_dir():
        print(f'❌ 根目录不存在: {root}', file=sys.stderr)
        return 2
    if args.update:
        return cmd_update(root, quiet=args.quiet, force=args.force)
    if args.verify:
        return cmd_verify(root, as_json=args.json, quiet=args.quiet)
    return cmd_check(root, as_json=args.json)


if __name__ == '__main__':
    sys.exit(main())
