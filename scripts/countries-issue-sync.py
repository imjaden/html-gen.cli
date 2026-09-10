#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A 型表格「GitHub Issue 反馈通道」同步脚本（HTML-GEN-CL009）。

从 GitHub issue（表单模板 .github/ISSUE_TEMPLATE/data-fix.yml）读取读者提交的
数据纠错，按 scripts/feedback-targets.yaml 的 target 定义校验（页面/数据集/行唯一
定位/字段白名单/类型/保护列），白名单写回 data JSON，并调用 html-gen.py table
重建产物；可选回评/关闭 issue。

用法:
    scripts/countries-issue-sync.py --list                 # 只列待处理 issue
    scripts/countries-issue-sync.py                        # 预览（默认 --dry-run，零写盘）
    scripts/countries-issue-sync.py --apply                # 写回 JSON + 重建产物 + 回评
    scripts/countries-issue-sync.py --apply --close        # 追加关闭已处理 issue
    scripts/countries-issue-sync.py --issue 12 --apply     # 只处理指定 issue
    scripts/countries-issue-sync.py --target countries --config scripts/feedback-targets.yaml

退出码: 0 成功（含无待处理/全部跳过） / 1 校验失败或外部调用失败 / 2 参数错误

设计: documents/solutions/countries-issue-feedback-design-v1.0-20260910.md
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


def gh_issue_list(repo, label, limit, issue_no=None):
    """拉取待处理 issue（gh CLI，shell=False）。返回 (issues, error)。"""
    cmd = ['gh', 'issue', 'list', '--repo', repo, '--label', label, '--state', 'open',
           '--limit', str(limit), '--json', 'number,title,body,url,createdAt']
    if issue_no:
        cmd += ['--search', f'{issue_no} in:number']
    r = run(cmd, cwd=str(PROJECT_ROOT))
    if r.returncode != 0:
        return None, (r.stderr or r.stdout or 'gh 调用失败').strip()
    try:
        issues = json.loads(r.stdout or '[]')
    except json.JSONDecodeError as e:
        return None, f'gh 输出非 JSON: {e}'
    if issue_no:
        issues = [i for i in issues if i.get('number') == issue_no]
    return issues, None


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


def plan_issues(issues, target, rows, index):
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
        field = norm(fields.get('field')).strip()
        if field in (target.get('protected') or []):
            skips.append((no, f'字段 {field} 属保护列（另有专用同步流程）'))
            continue
        if field not in (target.get('editable') or []):
            skips.append((no, f'字段 {field} 不在可写白名单'))
            continue
        suggested = fields.get('suggested')
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


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog='countries-issue-sync.py',
        description='GitHub issue（数据纠错表单）→ 白名单写回 data JSON + 重建产物（HTML-GEN-CL009）')
    ap.add_argument('--config', default=str(DEFAULT_CONFIG), help='目标配置（缺省 scripts/feedback-targets.yaml）')
    ap.add_argument('--target', help='目标名（缺省：配置仅一个 target 时自动选用）')
    ap.add_argument('--limit', type=int, default=100, help='拉取 issue 上限（缺省 100）')
    ap.add_argument('--issue', type=int, help='只处理指定 issue 号（便于实测）')
    ap.add_argument('--repo', help='覆盖配置中的 repo（owner/repo）')
    ap.add_argument('--close', action='store_true', help='apply 后关闭已处理 issue（默认只回评）')
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
    actions, skips = plan_issues(issues, target, rows, index)

    if args.json:
        print(json.dumps({'status': 'ok', 'data': {
            'actions': [{k: v for k, v in a.items() if k != 'row_idx'} | {'row': label_of(target, rows[a['row_idx']])} for a in actions],
            'skipped': [{'issue': n, 'reason': r} for n, r in skips]}}, ensure_ascii=False, indent=2))
    else:
        print(f'[列表] 待处理 {len(issues)} 条 / 可执行 {len(actions)} 条 / 跳过 {len(skips)} 条')
        for a in actions:
            print(f"  #{a['issue']} {label_of(target, rows[a['row_idx']])} · {a['field']}: "
                  f"{norm(a['old']) or '(空)'} → {a['new']}")
        for n, reason in skips:
            print(f'  #{n} [跳过] {reason}')

    if args.list or not actions:
        if not args.list and skips:
            print('[提示] 无可执行条目（见上方跳过原因）')
        return 0

    if not args.apply:
        print('[预览] 将更新 %d 个字段并重建 %s' % (len(actions), target['html']))
        print('[预览] 将回评 %s' % '、'.join(f"#{a['issue']}" for a in actions) + ('（含关闭）' if args.close else ''))
        print('[提示] 使用 --apply 执行（--close 追加关闭 issue）')
        return 0

    # ── apply ──
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
    for a in actions:
        body = (f"✅ 已更新数据：**{label_of(target, rows[a['row_idx']])} · {a['field']}**\n\n"
                f"- 现值：`{norm(a['old']) or '(空)'}` → 建议值：`{a['new']}`\n"
                f"- 来源：{a['source'] or '(未填)'}\n"
                f"- 产物已重建：`{target['html']}`（数据文件已更新，提交由维护者完成）\n\n"
                f"感谢反馈！")
        gh_comment(repo, a['issue'], body, close=args.close)
    return 0


if __name__ == '__main__':
    sys.exit(main())
