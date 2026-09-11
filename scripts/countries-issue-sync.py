#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A 型表格「GitHub Issue 反馈通道」同步脚本（HTML-GEN-CL009）。

从 GitHub issue（表单模板 .github/ISSUE_TEMPLATE/data-fix-countries.yml）读取读者提交的
数据反馈，按 scripts/feedback-targets.yaml 的 target 定义校验（页面/数据集/行唯一
定位/字段白名单/类型/保护列），白名单写回 data JSON，并调用 html-gen.py table
重建产物；可选回评/关闭 issue。

用法:
    python3 scripts/countries-issue-sync.py --list          # 只列待处理 issue（每条附 --issue N --dry-run 引导）
    python3 scripts/countries-issue-sync.py                 # 预览（默认 --dry-run，零写盘）
    python3 scripts/countries-issue-sync.py --apply         # 写回 JSON + 重建产物 + 提交 + 回评
    python3 scripts/countries-issue-sync.py --apply --close # 追加关闭已处理 issue
    python3 scripts/countries-issue-sync.py --apply --no-commit   # 只写盘重建，不自动提交
    python3 scripts/countries-issue-sync.py --issue 12 --apply    # 只处理指定 issue
    python3 scripts/countries-issue-sync.py --issue 12 --field note --value-file body.txt --apply  # 人工裁决：指定字段与值
    python3 scripts/countries-issue-sync.py --check-template      # 模板 ↔ 配置一致性校验
    python3 scripts/countries-issue-sync.py --target countries --config scripts/feedback-targets.yaml

提交: `--apply` 默认自动 `git commit`（显式 pathspec：数据文件 + 产物；只提交不推送；--no-commit 关闭）

退出码: 0 成功（含无待处理/全部跳过） / 1 校验失败、外部调用失败或提交失败 / 2 参数错误

设计: documents/solutions/countries-issue-feedback-design-v1.4-20260911.md
依赖: PyYAML（dev 依赖 requirements-dev.txt）+ 本机 gh CLI（已登录）; 运行时 html-gen 零依赖不受影响
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

# scripts/ 的上级 = 项目根；data / html / html-gen.py 相对路径一律以项目根为基准
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / 'scripts' / 'feedback-targets.yaml'
NO_RESPONSE = '_No response_'


# ── 工具 ─────────────────────────────────────────────────────────────
def die(msg, code=2):
    print(f'[错误] {msg}', file=sys.stderr)
    return code


def run(cmd, **kw):
    return subprocess.run(cmd, shell=False, capture_output=True, text=True, **kw)


def gh_issue_by_number(repo, number, label):
    """按编号直查单个 issue（HG-SEC-119：GitHub 搜索无 in:number 限定符，故用 gh issue view）。

    仅返回 open 且带目标 label 的 issue，其余返回 []（与 --list 口径一致）。
    """
    cmd = ['gh', 'issue', 'view', str(number), '--repo', repo,
           '--json', 'number,title,body,url,createdAt,state,labels']
    r = run(cmd, cwd=str(PROJECT_ROOT))
    if r.returncode != 0:
        return [], (r.stderr or r.stdout or 'gh 调用失败').strip()
    try:
        issue = json.loads(r.stdout or '{}')
    except json.JSONDecodeError as e:
        return [], f'gh 输出非 JSON: {e}'
    if (issue.get('state') or '').upper() != 'OPEN':
        return [], None
    if label and label not in [(l or {}).get('name') for l in (issue.get('labels') or [])]:
        return [], None
    return [issue], None


def gh_issue_list(repo, label, limit, issue_no=None):
    """拉取待处理 issue（gh CLI，shell=False）。返回 (issues, error)。"""
    if issue_no:
        return gh_issue_by_number(repo, issue_no, label)
    cmd = ['gh', 'issue', 'list', '--repo', repo, '--label', label, '--state', 'open',
           '--limit', str(limit), '--json', 'number,title,body,url,createdAt']
    r = run(cmd, cwd=str(PROJECT_ROOT))
    if r.returncode != 0:
        return None, (r.stderr or r.stdout or 'gh 调用失败').strip()
    try:
        return json.loads(r.stdout or '[]'), None
    except json.JSONDecodeError as e:
        return None, f'gh 输出非 JSON: {e}'


def parse_issue_body(body, parse_fields):
    """GitHub Issue Form 渲染体 → {field_id: value}。

    body 形如 '### 页面\n\ndemos/...\n\n### 数据集\n\ncountries\n\n...'
    （空回答渲染为 _No response_）。按 parse_fields 的 label 精确匹配段落标题。
    """
    fields = {}
    if not body:
        return fields
    # HG-SEC-115: GitHub 渲染的段头前必有空行 → 以「空行 + ### 」为界，值内偶发 '###' 行不产生错位段
    text = body.replace('\r\n', '\n')
    chunks = re.split(r'\n\s*\n### ', text)
    by_label = {label: fid for fid, label in parse_fields.items()}
    last_fid = None
    for i, chunk in enumerate(chunks):
        if i == 0 and not chunk.lstrip().startswith('### '):
            # 表单首部 markdown 块（说明文字）不参与解析
            continue
        lines = chunk.split('\n')
        head = lines[0].strip().lstrip('#').strip()
        value = '\n'.join(lines[1:]).strip()
        if value == NO_RESPONSE:
            value = ''
        fid = by_label.get(head)
        if fid is None:
            # 未知段：并入上一字段值（不丢弃、不新建字段）
            if last_fid:
                merged = fields.get(last_fid, '')
                fields[last_fid] = (merged + '\n' + chunk.strip()).strip()
            continue
        if fid not in fields:          # 同名字段首次生效
            fields[fid] = value
            last_fid = fid
    return fields


def to_number(text):
    """数值列解析：接受 '1,234' / '33.5' / '79' 等。失败返回 None。"""
    if text is None:
        return None
    s = str(text).replace(',', '').replace('，', '').strip()
    if not s:
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    if f.is_integer():
        return int(f)
    return f


def norm(v):
    """比较用归一化：None → ''，其余 str。"""
    return '' if v is None else str(v)


def load_target(cfg, name):
    targets = (cfg or {}).get('targets') or {}
    if not targets:
        return None, '配置无 targets'
    if name:
        if name not in targets:
            return None, f'未知 target: {name}（可用: {", ".join(targets)}）'
        return targets[name], None
    if len(targets) == 1:
        return next(iter(targets.values())), None
    return None, f'配置含多个 target，需 --target 指定（可用: {", ".join(targets)}）'


def build_row_index(rows, target):
    """key_field / alt_key 双索引（值 → 行下标列表，检测歧义）。"""
    idx = {}
    for field in (target.get('key_field'), target.get('alt_key')):
        if not field:
            continue
        bucket = idx.setdefault(field, {})
        for i, row in enumerate(rows):
            v = norm(row.get(field)).strip()
            if v:
                bucket.setdefault(v, []).append(i)
    return idx


def resolve_row(fields, index, target):
    """行唯一定位：key_field 精确 → alt_key 退化。返回 (row_idx, err)。"""
    for field in (target.get('key_field'), target.get('alt_key')):
        if not field:
            continue
        v = norm(fields.get('row' if field == target.get('key_field') else 'row_en')).strip()
        if not v:
            continue
        hits = (index.get(field) or {}).get(v) or []
        if len(hits) == 1:
            return hits[0], None
        if len(hits) > 1:
            return None, f'{field}={v} 命中 {len(hits)} 行（歧义）'
    key = target.get('key_field')
    return None, f'{key}={fields.get("row", "")!r} 未找到匹配行'


def resolve_field(raw, target, override=None):
    """字段解析（K1/O1/N1）：--field 覆盖 → `标签｜key` 取末段 → 裸 key（旧 issue 兼容）。

    返回 (key, err)；无法识别返回 (None, 原因)。
    """
    if override:
        return str(override).strip(), None
    v = norm(raw).strip()
    if not v:
        return None, '字段为空'
    editable = target.get('editable') or []
    key = v.split('｜')[-1].strip() if '｜' in v else v
    if key in editable:
        return key, None
    if v in editable:                       # 兜底：整串即 key
        return v, None
    return None, f'字段值无法识别（{v!r} 不在可写列中）'


def guarded_fields(target):
    """受保护字段集合（A1）：key_field / alt_key / key_guard / protected。"""
    guard = set(target.get('key_guard') or [])
    guard |= {target.get('key_field'), target.get('alt_key')}
    guard |= set(target.get('protected') or [])
    return {g for g in guard if g}


def plan_issues(issues, target, rows, index, override_field=None, override_value=None):
    """逐条校验 → (actions, skips)。actions: dict(row_idx, field, old, new, issue)。"""
    actions, skips = [], []
    t_page = norm(target.get('page'))
    t_base = Path(t_page).name
    for issue in issues:
        no = issue.get('number')
        fields = parse_issue_body(issue.get('body'), target.get('parse_fields') or {})
        page = norm(fields.get('page')).strip()
        pages_ok = page in (t_page, t_base) or Path(page).name == t_base
        if not pages_ok:
            skips.append((no, f'page 不匹配（{page!r} ≠ {t_page}）'))
            continue
        if norm(fields.get('dataset')).strip() != norm(target.get('dataset')):
            skips.append((no, f'dataset 不匹配（{fields.get("dataset")!r}）'))
            continue
        field, ferr = resolve_field(fields.get('field'), target, override_field)
        if ferr:
            skips.append((no, ferr))
            continue
        if field in guarded_fields(target):
            # A1: 主键 / 匹配键 / 保护列 一律拒绝（配置误列也在代码层拦截）
            skips.append((no, f'字段 {field} 属受保护列（主键/匹配键/视频列不可修改）'))
            continue
        if field not in (target.get('editable') or []):
            skips.append((no, f'字段 {field} 不在可写白名单'))
            continue
        suggested = override_value if override_value is not None else fields.get('suggested')
        if not suggested or not str(suggested).strip():
            skips.append((no, '建议值为空'))
            continue
        row_idx, err = resolve_row(fields, index, target)
        if err:
            skips.append((no, err))
            continue
        row = rows[row_idx]
        old = row.get(field)
        if (target.get('types') or {}).get(field) == 'number':
            new = to_number(suggested)
            if new is None:
                skips.append((no, f'数值列 {field} 无法解析建议值 {suggested!r}'))
                continue
        else:
            new = str(suggested).strip()
        if norm(old) == norm(new):
            skips.append((no, f'{field} 建议值与现值一致，无变化'))
            continue
        actions.append({'issue': no, 'row_idx': row_idx, 'field': field,
                        'old': old, 'new': new, 'source': norm(fields.get('source')).strip(),
                        'created': norm(issue.get('createdAt'))})

    # 冲突：同一 (行, 字段) 多条 → 只取最新（createdAt 大者，同则 issue 号大者）
    best = {}
    for a in actions:
        k = (a['row_idx'], a['field'])
        if k not in best or (a['created'], a['issue']) > (best[k]['created'], best[k]['issue']):
            if k in best:
                skips.append((best[k]['issue'], f"{a['field']} 与 #{a['issue']} 冲突，取最新"))
            best[k] = a
        else:
            skips.append((a['issue'], f"{a['field']} 与 #{best[k]['issue']} 冲突，取最新"))
    return sorted(best.values(), key=lambda x: x['issue']), sorted(skips)


def load_rows(target):
    data_path = PROJECT_ROOT / target['data']
    raw = data_path.read_text(encoding='utf-8')
    return data_path, raw, json.loads(raw)


def dump_rows(doc, raw_len_guard=True):
    """与现文件逐字一致的回写格式：indent=2 + ensure_ascii=False + 无尾换行。"""
    return json.dumps(doc, ensure_ascii=False, indent=2)


def label_of(target, row):
    key = target.get('key_field')
    return norm(row.get(key)) or f"#{row}"


HINT = 'python3 scripts/countries-issue-sync.py'


def git_paths(target):
    """本次提交涉及的仓库相对路径（B1：显式 pathspec，禁用 git add -A）。

    仅数据文件 + 产物；本仓存在并行会话 WIP，-A 会裹走非本次改动（CL002 FIND-002 教训）。
    """
    return [str(target['data']), str(target['html'])]


def git_dirty(paths):
    """目标文件的未提交改动（porcelain 行列表；空 = 干净）。返回 (lines, err)。"""
    r = run(['git', '-C', str(PROJECT_ROOT), 'status', '--porcelain', '--'] + [str(x) for x in paths])
    if r.returncode != 0:
        return None, (r.stderr or '').strip() or f'exit {r.returncode}'
    return [ln for ln in (r.stdout or '').splitlines() if ln.strip()], None


def git_commit(target, title, body, paths):
    """H1/G1: 显式 pathspec 提交。返回 (short_sha | None, err | None)；无变化返回 ('no-change')。"""
    dirty, err = git_dirty(paths)
    if err:
        return None, f'git status 失败: {err}'
    if not dirty:
        return None, 'no-change'
    r = run(['git', '-C', str(PROJECT_ROOT), 'add', '--'] + [str(x) for x in paths])
    if r.returncode != 0:
        return None, f'git add 失败: {(r.stderr or "").strip()}'
    # HG-SEC-140: commit 亦带 pathspec —— 否则会提交整个已暂存索引（并行会话已 git add 的无关文件会被裹走）
    c = run(['git', '-C', str(PROJECT_ROOT), 'commit', '-m', title, '-m', body, '--']
            + [str(x) for x in paths])
    if c.returncode != 0:
        return None, f'git commit 失败: {(c.stderr or c.stdout or "").strip()}'
    v = run(['git', '-C', str(PROJECT_ROOT), 'rev-parse', '--short', 'HEAD'])
    short = (v.stdout or '').strip()
    if v.returncode != 0 or not short:          # HG-SEC-141: 提交已产生但 sha 读取失败
        print('[警告] 提交已产生，但 rev-parse 读取 sha 失败', file=sys.stderr)
        return None, 'sha-unknown'
    return short, None


def rebuild(target):
    """调 html-gen.py table 重建产物（列表参数 + shell=False，打印 [执行]）。"""
    args = ((target.get('rebuild') or {}).get('args')) or []
    cmd = [sys.executable, str(PROJECT_ROOT / 'html-gen.py'), 'table',
           '-d', str(PROJECT_ROOT / target['data']), '-o', str(PROJECT_ROOT / target['html'])]
    cmd += [str(a) for a in args]
    print('[执行] ' + ' '.join(cmd))
    r = run(cmd, cwd=str(PROJECT_ROOT))
    if r.returncode != 0:
        print(f'[错误] html 重建失败（exit {r.returncode}）', file=sys.stderr)
        print((r.stderr or r.stdout or '').strip(), file=sys.stderr)
        return 1
    print(f"[重建] {target['html']}")
    return 0


def gh_comment(repo, no, body, close=False):
    r = run(['gh', 'issue', 'comment', str(no), '--repo', repo, '--body', body])
    if r.returncode != 0:
        print(f'[警告] #{no} 回评失败: {(r.stderr or "").strip()}', file=sys.stderr)
        return False
    print(f'[回评] #{no}')
    if close:
        rc = run(['gh', 'issue', 'close', str(no), '--repo', repo])
        if rc.returncode != 0:
            print(f'[警告] #{no} 关闭失败: {(rc.stderr or "").strip()}', file=sys.stderr)
            return False
        print(f'[关闭] #{no}')
    return True


def check_template(target):
    """L1: 模板 dropdown 选项 ↔ config.editable / 数据 columns[].label 一致性校验。返回退出码。"""
    tmpl_rel = target.get('template') or 'data-fix.yml'
    tmpl = PROJECT_ROOT / '.github' / 'ISSUE_TEMPLATE' / tmpl_rel
    if not tmpl.is_file():
        print(f'[错误] 模板不存在: {tmpl}', file=sys.stderr)
        return 1
    try:
        doc = yaml.safe_load(tmpl.read_text(encoding='utf-8')) or {}
    except yaml.YAMLError as e:
        print(f'[错误] 模板解析失败: {e}', file=sys.stderr)
        return 1
    options = []
    for blk in (doc.get('body') or []):
        if blk.get('type') == 'dropdown' and blk.get('id') == 'field':
            options = [str(o) for o in ((blk.get('attributes') or {}).get('options') or [])]
    if not options:
        print('[错误] 模板未找到 id=field 的 dropdown 选项', file=sys.stderr)
        return 1
    keys, labels = [], {}
    for o in options:
        if '｜' in o:
            lab, _, k = o.rpartition('｜')
            labels[k.strip()] = lab.strip()
            keys.append(k.strip())
        else:
            keys.append(o.strip())
    editable = list(target.get('editable') or [])
    guard = guarded_fields(target)
    problems = []
    if set(keys) != set(editable):
        problems.append(f'选项 key 集合 ≠ editable（模板多 {sorted(set(keys) - set(editable))} / '
                        f'少 {sorted(set(editable) - set(keys))}）')
    bad = [k for k in keys if k in guard]
    if bad:
        problems.append(f'选项含受保护列: {sorted(set(bad))}')
    if len(keys) != len(set(keys)):
        problems.append('选项 key 重复')
    try:
        cols = {c.get('key'): c.get('label') for c in
                (json.loads((PROJECT_ROOT / target['data']).read_text(encoding='utf-8')).get('columns') or [])}
        for k, lab in labels.items():
            if k in cols and lab and cols.get(k) and str(cols[k]) != lab:
                problems.append(f'标签不一致: {k} 模板={lab!r} 数据={cols[k]!r}')
    except (OSError, json.JSONDecodeError) as e:
        problems.append(f'数据列标签无法比对: {e}')
    if problems:
        print('[校验] 模板与配置不一致:')
        for x in problems:
            print('  - ' + x)
        return 1
    print(f'[校验] 模板 {tmpl_rel} 与 config.editable / 数据列标签 一致（{len(keys)} 项）')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog='countries-issue-sync.py',
        description='GitHub issue（数据反馈表单）→ 白名单写回 data JSON + 重建产物（HTML-GEN-CL009）')
    ap.add_argument('--config', default=str(DEFAULT_CONFIG), help='目标配置（缺省 scripts/feedback-targets.yaml）')
    ap.add_argument('--target', help='目标名（缺省：配置仅一个 target 时自动选用）')
    ap.add_argument('--limit', type=int, default=100, help='拉取 issue 上限（缺省 100）')
    ap.add_argument('--issue', type=int, help='只处理指定 issue 号（便于实测；与 --field 联用可人工指定目标字段）')
    ap.add_argument('--field', help='显式指定目标字段 key（仅与 --issue 联用；人工裁决入口，N1）')
    ap.add_argument('--value', help='显式指定建议值（仅与 --issue 联用；人工裁决入口）')
    ap.add_argument('--value-file', help='从文件读取建议值（仅与 --issue 联用；适合多行长文本）')
    ap.add_argument('--check-template', action='store_true',
                    help='只读校验：表单 dropdown 选项 ↔ config.editable / 数据列标签（L1）')
    ap.add_argument('--repo', help='覆盖配置中的 repo（owner/repo）')
    ap.add_argument('--close', action='store_true', help='apply 后关闭已处理 issue（默认只回评）')
    ap.add_argument('--no-commit', action='store_true',
                    help='apply 时不自动提交（默认提交数据文件与产物；显式 pathspec，只提交不推送，A1）')
    ap.add_argument('--json', action='store_true', help='机器可读输出 {status,data,error}')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--list', action='store_true', help='只列待处理 issue（零写盘）')
    g.add_argument('--dry-run', action='store_true', help='预览（默认；零写盘）')
    g.add_argument('--apply', action='store_true', help='执行写盘 + 重建 + 回评')
    args = ap.parse_args(argv)

    cfg_path = Path(args.config)
    if not cfg_path.is_absolute():
        cfg_path = PROJECT_ROOT / cfg_path
    if not cfg_path.is_file():
        return die(f'配置不存在: {cfg_path}')
    try:
        cfg = yaml.safe_load(cfg_path.read_text(encoding='utf-8'))
    except yaml.YAMLError as e:
        return die(f'配置解析失败: {e}')

    target, err = load_target(cfg, args.target)
    if err:
        return die(err)
    if args.check_template:
        return check_template(target)
    if (args.field or args.value is not None or args.value_file) and not args.issue:
        return die('--field / --value / --value-file 仅可与 --issue 联用（人工裁决入口）', 2)
    override_value = None
    if args.value_file:
        try:
            override_value = Path(args.value_file).read_text(encoding='utf-8')
        except OSError as e:
            return die(f'读取 --value-file 失败: {e}')
    elif args.value is not None:
        override_value = args.value
    repo = args.repo or target.get('repo')
    label = target.get('label') or 'data-fix'
    if not repo:
        return die('未指定 repo（配置 target.repo 或 --repo）')

    # 一致性提示：数据 JSON options.feedback ↔ config
    data_path, raw, doc = load_rows(target)
    rows = doc.get('data') or doc.get('rows') or []
    fb = (doc.get('options') or {}).get('feedback') or {}
    for cfg_key, fb_key in (('dataset', 'dataset'), ('key_field', 'key'), ('alt_key', 'altKey')):
        if fb.get(fb_key) and norm(fb.get(fb_key)) != norm(target.get(cfg_key)):
            print(f'[警告] options.feedback.{fb_key}={fb.get(fb_key)!r} 与 config.{cfg_key}='
                  f'{target.get(cfg_key)!r} 不一致（按钮预填的 dataset/key 与脚本解析口径需一致）')

    issues, err = gh_issue_list(repo, label, args.limit, args.issue)
    if err:
        return die(f'拉取 issue 失败: {err}', 1)
    if not issues:
        msg = f'无待处理 issue（repo={repo}, label={label}）'
        print(msg if not args.json else json.dumps({'status': 'ok', 'data': {'actions': [], 'skipped': [], 'note': msg}}, ensure_ascii=False))
        return 0

    index = build_row_index(rows, target)
    actions, skips = plan_issues(issues, target, rows, index,
                                 override_field=args.field, override_value=override_value)

    if args.json:
        print(json.dumps({'status': 'ok', 'data': {
            'actions': [{k: v for k, v in a.items() if k != 'row_idx'} | {'row': label_of(target, rows[a['row_idx']])} for a in actions],
            'skipped': [{'issue': n, 'reason': r} for n, r in skips]}}, ensure_ascii=False, indent=2))
    else:
        print(f'[列表] 待处理 {len(issues)} 条 / 可执行 {len(actions)} 条 / 跳过 {len(skips)} 条')
        for a in actions:
            print(f"  #{a['issue']} {label_of(target, rows[a['row_idx']])} · {a['field']}: "
                  f"{norm(a['old']) or '(空)'} → {a['new']}")
            print(f'     → {HINT} --issue {a["issue"]} --dry-run')
        for n, reason in skips:
            print(f'  #{n} [跳过] {reason}')
            print(f'     → {HINT} --issue {n} --dry-run')

    if args.list or not actions:
        if not args.list and skips:
            print('[提示] 无可执行条目（见上方跳过原因）')
        return 0

    if not args.apply:
        print('[预览] 将更新 %d 个字段并重建 %s' % (len(actions), target['html']))
        if not args.no_commit:
            print('[预览] 将提交 %s（本地，不推送）' % '、'.join(git_paths(target)))
        print('[预览] 将回评 %s' % '、'.join(f"#{a['issue']}" for a in actions) + ('（含关闭）' if args.close else ''))
        print(f'[提示] 使用 {HINT} --apply 执行（--close 追加关闭；--no-commit 不提交）')
        return 0

    # ── apply ──
    paths = git_paths(target)
    if not args.no_commit:
        dirty, gerr = git_dirty(paths)
        if gerr:
            return die(f'提交预检失败: {gerr}', 1)
        if dirty:
            return die('目标文件存在未提交改动，请先提交或回滚（C1 预检）：\n  ' + '\n  '.join(dirty), 1)
    for a in actions:
        row = rows[a['row_idx']]
        print(f"[更新] {label_of(target, row)}.{a['field']}: {norm(a['old']) or '(空)'} → {a['new']}")
        row[a['field']] = a['new']
    new_raw = dump_rows(doc)
    if len(new_raw) == 0:
        return die('序列化失败', 1)
    data_path.write_text(new_raw, encoding='utf-8')
    print(f"[写回] {target['data']}（{len(actions)} 处字段）")

    rc = rebuild(target)
    if rc:
        return rc

    # ── 提交（A1/B1/D1/E1/F1/G1/H1） ──
    sha, commit_err, sha_unknown = None, None, False
    if not args.no_commit:
        scope = ((target.get('commit') or {}).get('scope')) or target.get('dataset') or 'data'
        nums = '#' + ',#'.join(str(a['issue']) for a in actions)
        fields = ','.join(dict.fromkeys(a['field'] for a in actions))
        title = f'data@{scope}: apply {nums} {fields} 更新 (HTML-GEN-CL009)'
        cbody = ('issue 反馈自动处置：\n' + '\n'.join(
            f"- #{a['issue']} {label_of(target, rows[a['row_idx']])}.{a['field']}: "
            f"{norm(a['old']) or '(空)'} → {a['new']}" for a in actions)
            + f"\n\n产物重建：{target['html']}")
        sha, commit_err = git_commit(target, title, cbody, paths)
        if commit_err == 'no-change':
            print('[提交] 无变化，跳过')
            commit_err = None
        elif commit_err == 'sha-unknown':
            print(f'[提交] 已提交（sha 读取失败）{title}')
            commit_err = None
            sha_unknown = True
        elif commit_err:
            print(f'[错误] {commit_err}', file=sys.stderr)
        else:
            print(f'[提交] {sha} {title}')

    if args.no_commit:
        commit_txt = '提交由维护者完成（--no-commit）'
    elif sha_unknown:
        commit_txt = '本地提交已产生（sha 读取失败，待维护者确认）'
    elif sha:
        commit_txt = f'本地提交 `{sha}`（待推送）'
    elif commit_err:
        commit_txt = '提交失败，待维护者处理'
    else:
        commit_txt = '本次无文件变化，未产生提交'

    for a in actions:
        body = (f"✅ 已更新数据：**{label_of(target, rows[a['row_idx']])} · {a['field']}**\n\n"
                f"- 现值：`{norm(a['old']) or '(空)'}` → 建议值：`{a['new']}`\n"
                f"- 来源：{a['source'] or '(未填)'}\n"
                f"- 产物已重建：`{target['html']}`；{commit_txt}\n\n"
                f"感谢反馈！")
        gh_comment(repo, a['issue'], body, close=args.close)
    return 1 if commit_err else 0


if __name__ == '__main__':
    sys.exit(main())
