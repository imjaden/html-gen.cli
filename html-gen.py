#!/usr/bin/env python3
"""
html-gen — HTML 模板 CLI 生成器
Layer 3: 将 JSON/Markdown 注入模板，输出单文件 HTML

用法:
  html-gen doc --input report.md --output report.html [--title "xxx"]
  html-gen slide --input report.md --output report.html [--title "xxx"]
  html-gen table --data data.json [-o out.html]  # 输出: CLI -o 或 JSON 顶层 output 必填其一
  html-gen knowledge --data data.json [--groups groups.json] --title "xxx" [-o out.html]

版本: 3.3(2026-08-28)
"""
import html, json, re, sys, os, time, argparse, types, unicodedata
from pathlib import Path

__version__ = "3.3"              # CL016: 版本号 (格式 \d+\.\d+)
__release_date__ = "2026-08-28"  # CL016: 发版日期 (格式 YYYY-MM-DD, 与版本同步)

SKILLS_DIR = Path(__file__).resolve().parent
TEMPLATE_DOC   = SKILLS_DIR / 'layout-doc.html'
TEMPLATE_SLIDE = SKILLS_DIR / 'layout-slide.html'
TEMPLATE_TABLE = SKILLS_DIR / 'layout-table.html'
TEMPLATE_KNOWLEDGE = SKILLS_DIR / 'layout-knowledge.html'
STYLE_GUIDE    = SKILLS_DIR / 'style-guide.css'

# CL003: table/knowledge 无输出目标时的中断文案 (两处共用, stderr + exit 1)
NO_OUTPUT_MSG = '❌ 未指定输出文件: 请补充 -o <output.html>，或 JSON 顶层加 "output": "demos/xxx.html"'


def read_template(path):
    if not path.exists():
        print(f"❌ 模板不存在: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding='utf-8')


# Keys injected into <script> context — need </ → <\/ escaping
_SCRIPT_KEYS = {'columns', 'data', 'tabs', 'options', 'groups', 'items'}


def inject(template, **kwargs):
    for key, value in kwargs.items():
        s = str(value)
        # SECURITY: prevent </script> injection in <script>-context values only
        if key in _SCRIPT_KEYS:
            s = s.replace('</', '<\\/')
        template = template.replace(f'<!--{key.upper()}-->', s)
    return template


def inline_style(template):
    """Replace external style-guide link with inlined CSS."""
    css = STYLE_GUIDE.read_text(encoding='utf-8') if STYLE_GUIDE.exists() else ''
    if not css:
        return template
    return template.replace(
        '<link rel="stylesheet" href="style-guide.css">',
        f'<style>\n{css}\n</style>'
    )


# ═══ Render Summary ═══
def human_size(n):
    """人类可读文件大小: <1KB 显示 B, 否则 KB 保留 1 位小数."""
    return f"{n/1024:.1f} KB" if n >= 1024 else f"{n} B"


def print_summary(out, src_path, src_size, out_size, elapsed, stats):
    """渲染完成后打印统计信息卡（--quiet 时不调用）."""
    print(f"✅ 已生成: {out}")
    print(f"   📄 源文件: {src_path} · {human_size(src_size)}")
    print(f"   📦 产物: {human_size(out_size)}")
    for line in stats:
        print(f"   {line}")
    print(f"   ⏱ 耗时: {elapsed:.2f}s")


# ═══ Opt-in GitHub Corner & Home Link (隐私: 默认不带, 显式入参才注入) ═══
GITHUB_CORNER_TMPL = """<a href="{url}" class="github-corner" target="_blank" rel="noopener" aria-label="View source on Github">
  <svg width="72" height="72" viewBox="0 0 250 250" aria-hidden="true">
    <path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z" fill="rgba(0,0,0,0.41)"></path>
    <path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path>
    <path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path>
  </svg>
</a>
<a class="github-corner-hit" href="{url}" target="_blank" rel="noopener" aria-label="GitHub"></a>"""


def github_corner_html(url):
    return GITHUB_CORNER_TMPL.format(url=url)


def home_link_html(url):
    return f'<a class="home-link" href="{url}" aria-label="Demo 首页">🏠</a>'


def corner_args(args):
    """--github-url/--home-url 入参 + env 兜底 (CLI 优先; 显式空串禁用, 同 favicon HG-SEC-073).

    None(未传) → env 兜底; 显式 '' → 禁用(不落 env) — cmd_prompt_site 直调传空串防
    HTML_GEN_GITHUB_URL 环境覆盖 (HG-SEC-090)."""
    gh = getattr(args, 'github_url', None)
    if gh is None:
        gh = os.environ.get('HTML_GEN_GITHUB_URL', '')
    home = getattr(args, 'home_url', None)
    if home is None:
        home = os.environ.get('HTML_GEN_HOME_URL', '')
    return (github_corner_html(gh) if gh else ''), (home_link_html(home) if home else '')


# ═══ Favicon (CL004: 默认注入 DEFAULT_FAVICON; --favicon 覆盖; 显式空串禁用) ═══
DEFAULT_FAVICON = "https://www.jaden.tech/static/img/favicon.png"


def favicon_link_html(url):
    """favicon link 注入串；空 → 空串（禁用, 与 --github-url 空语义对齐）。"""
    if not url:
        return ''
    return f'<link rel="icon" href="{url}" type="image/png">'


def favicon_args(args):
    """--favicon 入参 + env 兜底 (HG-SEC-073: 勿用 or 链, 否则空串禁用失效).

    优先级: CLI --favicon > env HTML_GEN_FAVICON > DEFAULT_FAVICON。
    显式传空串 → 空串 → favicon_link_html 返回 '' → 不注入。
    """
    favicon = args.favicon if getattr(args, 'favicon', None) is not None \
        else (os.environ.get('HTML_GEN_FAVICON') or DEFAULT_FAVICON)
    return favicon_link_html(favicon)


# ═══ GitHub Issue 反馈通道 (CL009: --feedback-repo; 默认不注入, 隐私同 --github-url) ═══
def feedback_repo_args(args, options):
    """反馈仓库三级取值并合并进 options.feedback（CL009 K1）。

    优先级: CLI --feedback-repo > env HTML_GEN_FEEDBACK_REPO > JSON options.feedback.repo。
    显式空串 → 禁用（不渲染反馈按钮, 与 --favicon/--github-url 空语义对齐）。
    仅 table 子命令调用；未配置且无 dataset → 不新增 feedback 键（产物与既有逐字一致）。
    """
    repo = getattr(args, 'feedback_repo', None)
    if repo is None:
        env = os.environ.get('HTML_GEN_FEEDBACK_REPO')
        repo = env if env is not None else (options.get('feedback') or {}).get('repo', '')
    fb = dict(options.get('feedback') or {})
    fb['repo'] = '' if repo is None else str(repo)
    if fb['repo'] or fb.get('dataset'):
        options['feedback'] = fb
    return options


# ═══ Markdown → HTML (minimal, no deps) ═══
def md_to_html(text):
    lines = text.split('\n')
    html = []
    i, in_code, code_buf, fence_len = 0, False, [], 0
    RE_FENCE = re.compile(r'^(```+)(.*)$')
    while i < len(lines):
        line = lines[i]
        m = RE_FENCE.match(line)
        if m:
            ticks, rest = m.group(1), m.group(2).strip()
            num = len(ticks)
            if in_code:
                # Close: same/more backticks, no extra text on line
                if num >= fence_len and not rest:
                    lang = code_buf[0][fence_len:].strip()
                    content = '\n'.join(code_buf[1:])
                    html.append(
                        f'<pre><code class="language-{lang}">'
                        f'{content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}'
                        f'</code></pre>')
                    code_buf, in_code, fence_len = [], False, 0
                else:
                    code_buf.append(line)
            else:
                code_buf = [line]
                in_code, fence_len = True, num
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.startswith('###### '):
            html.append(f'<h6 id="{slug(line[7:])}">{_md_escape(line[7:])}</h6>')
        elif line.startswith('##### '):
            html.append(f'<h5 id="{slug(line[6:])}">{_md_escape(line[6:])}</h5>')
        elif line.startswith('#### '):
            html.append(f'<h4 id="{slug(line[5:])}">{_md_escape(line[5:])}</h4>')
        elif line.startswith('### '):
            html.append(f'<h3 id="{slug(line[4:])}">{_md_escape(line[4:])}</h3>')
        elif line.startswith('## '):
            html.append(f'<h2 id="{slug(line[3:])}">{_md_escape(line[3:])}</h2>')
        elif line.startswith('# '):
            html.append(f'<h1 id="{slug(line[2:])}">{_md_escape(line[2:])}</h1>')
        elif line.startswith('|'):
            tbl = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                tbl.append(lines[i])
                i += 1
            html.append(parse_table(tbl))
            continue
        elif re.match(r'^[-*] ', line):
            html.append(f'<li>{inline_format(_md_escape(line[2:]))}</li>')
        elif re.match(r'^\d+\.\s', line):
            html.append(f'<li>{inline_format(_md_escape(line.split(". ",1)[1]))}</li>')
        elif re.match(r'^-{3,}$', line.strip()):
            html.append('<hr>')
        elif line.startswith('> '):
            cm = re.match(r'>\s*\*\*(注意|Note|提示|Tip|警告|Warning|危险|Danger|Caution)[：:]?\*\*[：:]?\s*(.*)', line)
            if cm:
                ct_map = {'注意': 'note', 'Note': 'note', '提示': 'tip', 'Tip': 'tip',
                          '警告': 'warning', 'Warning': 'warning', 'Caution': 'caution',
                          '危险': 'danger', 'Danger': 'danger'}
                cls = 'callout ' + ct_map.get(cm.group(1), 'note')
                label = cm.group(1).rstrip(':')
                html.append(
                    f'<blockquote class="{cls}"><strong>{label}:</strong>'
                    f'{inline_format(_md_escape(cm.group(2)))}</blockquote>')
            else:
                html.append(f'<blockquote>{inline_format(_md_escape(line[2:]))}</blockquote>')
        elif line.strip() == '':
            pass
        else:
            t = inline_format(_md_escape(line))
            if t.strip():
                html.append(f'<p>{t}</p>')
        i += 1
    result = []
    in_ul = False
    for h in html:
        if h.startswith('<li>'):
            if not in_ul:
                result.append('<ul>')
                in_ul = True
            result.append(h)
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            result.append(h)
    if in_ul:
        result.append('</ul>')
    html_text = '\n'.join(result)
    return html_text


def parse_table(lines):
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    if not rows:
        return ''
    body_start = 2 if len(rows) > 1 and all(re.match(r'^[-:\s]+$', c) for c in rows[1]) else 1
    html = ['<table><thead><tr>']
    for c in rows[0]:
        html.append(f'<th>{c}</th>')
    html.append('</tr></thead><tbody>')
    for row in rows[body_start:]:
        html.append('<tr>')
        for c in row:
            html.append(f'<td>{inline_format(c)}</td>')
        html.append('</tr>')
    html.append('</tbody></table>')
    return '\n'.join(html)


def slug(text):
    t = text.lower()
    t = re.sub(r'[^\w\u4e00-\u9fff]+', '-', t)
    return t.strip('-') or 'section'


def strip_frontmatter(text):
    """剥离 markdown 顶部 YAML frontmatter（--- 开头 --- 结束）。"""
    if text.startswith('---'):
        m = re.match(r'^---\n.*?\n---\n?', text, re.DOTALL)
        if m:
            return text[m.end():], m.group(0)
    return text, ''


def _skill_desc(skill_path):
    """读取 SKILL.md frontmatter description 首行 (缺失返回 '')."""
    try:
        with open(skill_path) as _f:
            for _line in _f:
                if _line.startswith('description:'):
                    return _line.split(':', 1)[1].strip()
    except Exception:
        pass
    return ''


RE_FENCE = re.compile(r'^(```+)(.*)$')


def _fence_top_h1_indices(lines):
    """fence-aware: 返回顶层(围栏外) `# ` 标题行索引 (复用 md_to_html 围栏解析语义, HG-SEC-087).

    3 个 skill 正文的代码围栏内含 `# ` 注释行 (html-gen 7 / html-gen-table 3 /
    test-speed-optimization 2)，不得计入——删除/h1 计数均须 fence-aware。
    """
    idxs, in_code, fence_len = [], False, 0
    for i, line in enumerate(lines):
        m = RE_FENCE.match(line)
        if m:
            ticks, rest = m.group(1), m.group(2).strip()
            num = len(ticks)
            if in_code:
                # 闭合: 同/更多 backticks 且行内无附加文本
                if num >= fence_len and not rest:
                    in_code, fence_len = False, 0
            else:
                in_code, fence_len = True, num
            continue
        if not in_code and line.startswith('# '):
            idxs.append(i)
    return idxs


def _md_escape(text):
    """Escape HTML in plain text content of markdown."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def inline_format(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text


def extract_title(md_text):
    m = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    return m.group(1).strip() if m else ''


# ═══ Commands ═══
def cmd_doc(args):
    from datetime import datetime
    t0 = time.perf_counter()
    md = Path(args.input)
    if not md.exists():
        print(f"❌ 文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)
    text = md.read_text(encoding='utf-8')
    # ── D2: frontmatter 自动剥离 ──
    text, fm = strip_frontmatter(text)
    # ── D4: title 优先级: --title > fm title > body # > stem ──
    fm_title = re.search(r'^title:\s*(.+)$', fm, re.MULTILINE)
    title = args.title or (fm_title.group(1).strip() if fm_title else '') or extract_title(text) or md.stem
    content = md_to_html(text)

    # ── Extract h1 for slide cover page BEFORE stripping ──
    h1_html = ''
    if content.startswith('<h1'):
        idx = content.index('</h1>') + 5
        h1_html = content[:idx]
        content = content[idx:].lstrip()

    # ── Count h2s for slide mode performance warning ──
    h2_count = len(re.findall(r'<h2\b', content))
    perf_warning = ''
    if h2_count > 50:
        perf_warning = (f'<div class="perf-warning">'
                        f'⚠️ 本文档共 {h2_count} 节，幻灯片模式下可能加载较慢'
                        f'</div>')

    # 计算元信息
    try:
        rel = '~/' + str(md.resolve().relative_to(Path.home()))
    except ValueError:
        rel = str(md.resolve())
    stat = md.stat()
    wc = len(text.split())
    rt = max(1, round(wc / 200))
    ct = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M')
    et = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
    md_name = os.path.basename(str(md))
    meta = (f"创建: {ct} · 编辑: {et}<br>"
            f"字数: {wc:,} · 阅读约 {rt} 分钟"
            f"<span class=\"meta-path\"> · 路径: <code>{md_name}</code></span>")

    # External link archive at document bottom
    ext_links = sorted(set(re.findall(r'href="(https?://[^"]+)"', content)))
    if ext_links:
        ref_html = '\n<h2>🔗 参考链接</h2>\n<ol>\n'
        for link in ext_links:
            ref_html += f'<li><a href="{link}" target="_blank" rel="noopener">{link}</a></li>\n'
        ref_html += '</ol>\n'
        content += ref_html

    tmpl = inline_style(read_template(TEMPLATE_DOC))
    gc, hl = corner_args(args)
    result = inject(tmpl, title=title, subtitle=args.subtitle or '', metadata=meta, content=content,
                    github_corner=gc, home_link=hl, favicon=favicon_args(args))
    out = args.output or md.with_suffix('.html')
    Path(out).write_text(result, encoding='utf-8')
    if not getattr(args, 'quiet', False):
        h3_count = len(re.findall(r'<h3\b', content))
        stats = [f"📑 章节: {h2_count} 节" + (f" · {h3_count} 子节" if h3_count else '')]
        print_summary(out, args.input, stat.st_size, Path(out).stat().st_size,
                      time.perf_counter() - t0, stats)
    else:
        print(f"✅ 已生成: {out}")


def cmd_slide(args):
    """Markdown → slide 幻灯片（h2 分页）"""
    from datetime import datetime
    t0 = time.perf_counter()
    md = Path(args.input)
    if not md.exists():
        print(f"❌ 文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)
    text = md.read_text(encoding='utf-8')
    # ── D2: frontmatter 自动剥离 ──
    text, fm = strip_frontmatter(text)
    # ── D4: title 优先级 ──
    fm_title = re.search(r'^title:\s*(.+)$', fm, re.MULTILINE)
    title = args.title or (fm_title.group(1).strip() if fm_title else '') or extract_title(text) or md.stem
    content = md_to_html(text)

    # Extract h1 for cover page
    h1_html = ''
    if content.startswith('<h1'):
        idx = content.index('</h1>') + 5
        h1_html = content[:idx]
        content = content[idx:].lstrip()

    # Count h2s for performance warning
    h2_count = len(re.findall(r'<h2\b', content))
    perf_warning = ''
    if h2_count > 50:
        perf_warning = (f'<div class="perf-warning">'
                        f'⚠️ 本文档共 {h2_count} 节，幻灯片模式下可能加载较慢'
                        f'</div>')

    # Metadata
    try:
        rel = '~/' + str(md.resolve().relative_to(Path.home()))
    except ValueError:
        rel = str(md.resolve())
    stat = md.stat()
    wc = len(text.split())
    rt = max(1, round(wc / 200))
    ct = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M')
    et = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
    md_name = os.path.basename(str(md))
    meta = (f"创建: {ct} · 编辑: {et}<br>"
            f"字数: {wc:,} · 阅读约 {rt} 分钟"
            f"<span class=\"meta-path\"> · 路径: <code>{md_name}</code></span>")

    # External link archive
    ext_links = sorted(set(re.findall(r'href="(https?://[^\"]+)"', content)))
    if ext_links:
        ref_html = '\n<h2>🔗 参考链接</h2>\n<ol>\n'
        for link in ext_links:
            ref_html += f'<li><a href="{link}" target="_blank" rel="noopener">{link}</a></li>\n'
        ref_html += '</ol>\n'
        content += ref_html

    tmpl = inline_style(read_template(TEMPLATE_SLIDE))
    gc, hl = corner_args(args)
    result = inject(tmpl, title=title, subtitle=args.subtitle or '', metadata=meta, content=content,
                    cover=h1_html, h2_count=str(h2_count), perf_warning=perf_warning,
                    github_corner=gc, home_link=hl, favicon=favicon_args(args))
    out = args.output or md.with_suffix('.slide.html')
    Path(out).write_text(result, encoding='utf-8')
    if not getattr(args, 'quiet', False):
        pages = h2_count + (1 if h1_html else 0)
        print_summary(out, args.input, stat.st_size, Path(out).stat().st_size,
                      time.perf_counter() - t0, [f"🖥 页面: {pages} 页"])
    else:
        print(f"✅ 已生成: {out}")


def _contract_keys(dim):
    """table 契约某维度的键清单 (校验复用契约源, 避免第二份键表)。"""
    return [e[0] for e in TEMPLATE_CONTRACT['table']['data'][dim]]


def warn_unknown_table_keys(raw):
    """CL012: 未知配置键提示 — 仅写 stderr, 不阻断、不改退出码。

    校验对象 (仅配置键): columns[] 属性名 / columns[].type 取值 / options 顶层键 /
    options.feedback 子键。显式不校验: data[] 行内字段名 (业务字段任意命名)、简单数组
    推导出的列名、render/handler 等指向函数名的值 (是值不是键); col.actions[] 与
    col.videos 嵌套项不在本 CL 校验范围 (设计 §E 四项之外)。
    """
    if not isinstance(raw, dict):
        return  # 简单数组: 列名由数据字段推导, 非配置键, 不校验
    cols = _contract_keys('columns')
    types = _contract_keys('column_types')
    opts = _contract_keys('options')
    fbs = _contract_keys('feedback')
    found = []
    for i, col in enumerate(raw.get('columns') or []):
        if not isinstance(col, dict):
            continue
        for k in col:
            if k not in cols:
                found.append(('未知列属性', k, f'columns[{i}]'))
        if 'type' in col and col['type'] not in types:
            found.append(('未知列类型', col['type'], f'columns[{i}].type'))
    options = raw.get('options')
    if isinstance(options, dict):
        for k in options:
            if k not in opts:
                found.append(('未知选项', k, 'options'))
        fb = options.get('feedback')
        if isinstance(fb, dict):
            for k in fb:
                if k not in fbs:
                    found.append(('未知反馈子键', k, 'options.feedback'))
    seen = set()
    for kind, key, loc in found:                   # 同一键只提示一次 (保留首个位置)
        if (kind, key) in seen:
            continue
        seen.add((kind, key))
        print(f'⚠️ {kind}: {key} ({loc})（见 html-gen help table）', file=sys.stderr)


def cmd_table(args):
    t0 = time.perf_counter()
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ 数据文件不存在: {args.data}", file=sys.stderr)
        sys.exit(1)
    with open(data_path) as f:
        raw = json.load(f)

    # ── Parse data: supports plain array OR structured object ──
    if isinstance(raw, list):
        data = raw
        columns = [{'key': k, 'label': k, 'sortable': True} for k in (data[0] if data else {}).keys()]
        tabs = []
        options = {}
        json_title = None
        json_subtitle = None
        json_output = None  # 简单数组无元数据能力, CLI-only
    else:
        # Structured object: {columns?, data?, rows?, tabs?, options?, title?, subtitle?, output?}
        data = raw.get('data') or raw.get('rows') or []
        if 'columns' in raw:
            columns = raw['columns']
        else:
            columns = [{'key': k, 'label': k, 'sortable': True} for k in (data[0] if data else {}).keys()]
        tabs = raw.get('tabs', [])
        options = raw.get('options', {})
        json_title = raw.get('title')
        json_subtitle = raw.get('subtitle')
        json_output = raw.get('output')

    # CL012: 未知配置键提示 (仅 stderr, 不阻断不改退出码)
    warn_unknown_table_keys(raw)

    # title/subtitle 优先级: CLI 显式入参 > JSON 顶层字段 > 默认值
    title = args.title if args.title is not None else (json_title or '数据表格')
    if args.subtitle is not None:
        subtitle = args.subtitle  # 显式传入（含空串）→ 覆盖 JSON
    else:
        subtitle = json_subtitle or ''
    # 段落描述: 纯文本安全转义, \n → <br> 换行
    description = html.escape(subtitle, quote=False).replace('\n', '<br>')

    # CL009: --feedback-repo / env / JSON options.feedback.repo 三级取值合并
    options = feedback_repo_args(args, options)

    tmpl = inline_style(read_template(TEMPLATE_TABLE))
    gc, hl = corner_args(args)
    result = inject(tmpl, title=title, description=description,
                    columns=json.dumps(columns, ensure_ascii=False),
                    data=json.dumps(data, ensure_ascii=False),
                    tabs=json.dumps(tabs, ensure_ascii=False),
                    options=json.dumps(options, ensure_ascii=False),
                    filters='', search_placeholder='搜索...',
                    github_corner=gc, home_link=hl, favicon=favicon_args(args))
    # CL003: 输出目标三态 — CLI -o 非空 > JSON 顶层 output > 中断 (写盘前)
    out = args.output or json_output
    if not out:
        print(NO_OUTPUT_MSG, file=sys.stderr)
        sys.exit(1)
    Path(out).write_text(result, encoding='utf-8')
    if not getattr(args, 'quiet', False):
        tabs_n = len(tabs)
        stats = [f"📊 数据: {len(data)} 行 × {len(columns)} 列" + (f" · {tabs_n} 标签页" if tabs_n else '')]
        print_summary(out, args.data, data_path.stat().st_size, Path(out).stat().st_size,
                      time.perf_counter() - t0, stats)
    else:
        print(f"✅ 已生成: {out}")


def cmd_knowledge(args):
    """从 JSON 数据生成 C 型知识库 HTML（顶部类目 + 左侧章节）"""
    t0 = time.perf_counter()
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ 数据文件不存在: {args.data}", file=sys.stderr)
        sys.exit(1)
    groups = []
    if args.groups:
        with open(args.groups) as f:
            groups = json.load(f)
    else:
        with open(data_path) as f:
            raw = json.load(f)
        items = raw if isinstance(raw, list) else (raw.get('items') or raw.get('data') or raw)
        seen = []
        for item in items:
            g = item.get('group', '其他')
            if g not in seen:
                seen.append(g)
                groups.append({'key': g, 'label': g, 'icon': item.get('icon', '')})
    with open(data_path) as f:
        raw = json.load(f)
    items = raw if isinstance(raw, list) else (raw.get('items') or raw.get('data') or raw)
    # CL003: knowledge 只认 data 文件的 output (groups 文件不带); 结构化键 items/data, 简单数组 None
    json_output = raw.get('output') if isinstance(raw, dict) else None
    tmpl = inline_style(read_template(TEMPLATE_KNOWLEDGE))
    gc, hl = corner_args(args)
    result = inject(tmpl, title=args.title or '知识库',
                    subtitle=args.subtitle or '',
                    welcome_text=args.welcome or '从上方类目选择，浏览整理的知识内容。',
                    groups=json.dumps(groups, ensure_ascii=False),
                    items=json.dumps(items, ensure_ascii=False),
                    github_corner=gc, home_link=hl, favicon=favicon_args(args))
    # CL003: 输出目标三态 — CLI -o 非空 > JSON 顶层 output > 中断 (写盘前)
    out = args.output or json_output
    if not out:
        print(NO_OUTPUT_MSG, file=sys.stderr)
        sys.exit(1)
    Path(out).write_text(result, encoding='utf-8')
    if not getattr(args, 'quiet', False):
        if isinstance(items, list):
            sections_n = len({i.get('section') for i in items if isinstance(i, dict) and i.get('section')})
            items_n = len(items)
        else:
            sections_n = items_n = 0
        stats = [f"🏷 类目 {len(groups)} · 章节 {sections_n} · 条目 {items_n}"]
        print_summary(out, args.data, data_path.stat().st_size, Path(out).stat().st_size,
                      time.perf_counter() - t0, stats)
    else:
        print(f"✅ 已生成: {out}")


# ═══ 模板契约 (CL012) ═══
# help 契约的单一事实源: help 渲染 / 守卫测试 (tests/test_help_contract.py) / 文档引用
# 均以本结构为准 (help 文本 = 本契约的渲染结果, 不再手抄键清单)。
# 条目格式: (键名, 语义说明, 默认值) —— 默认值 '' 表示无默认; 说明文本不得含「词元:」片段
# (ASCII 或中文均不可: 会污染 spec_key_tokens() 的 key: 提取口径)。
# CL012 建 table 维度全量 + doc/slide/knowledge 骨架; CL013 补齐三模板维度模型 + 四模板 CLI 参数段
# (三模板骨架 'legacy' 指针已在 CL013 删除)。
# 四渲染子命令通用 flag 条目 (共用一份, 防四模板文案漂移; 语义含 env 兜底与「显式空串禁用」约定)
_CLI_GITHUB_URL = ('--github-url', '右上角 GitHub corner 链接 (默认不带, 隐私; 显式空串禁用; 环境变量 HTML_GEN_GITHUB_URL)', '')
_CLI_HOME_URL = ('--home-url', 'demo 首页入口链接 (默认不带, 隐私; 显式空串禁用; 环境变量 HTML_GEN_HOME_URL)', '')
_CLI_FAVICON = ('--favicon', 'favicon 图标 URL (默认注入默认图标; 显式空串禁用; 环境变量 HTML_GEN_FAVICON)', '')
_CLI_QUIET = ('--quiet', '仅打印生成路径, 抑制统计信息', 'false')

TEMPLATE_CONTRACT = {
    'table': {
        'label': 'A 型 · 数据表格 JSON 格式',
        'tagline': 'Cinema 纪律化宽度模型',
        'overview': 'JSON 数据格式 (A 型)',
        'rule': 37,                      # 标题下 ━ 分隔线长度 (沿用现状观感)
        'examples': 'HELP_TABLE_EXAMPLES',   # ② 手写示例段常量名 (见 §B.3 三段式)
        'behaviors_title': '点击模式',        # behaviors 段标题 (CL013: 按节点区分, table 渲染逐字不变)
        'cli': [
            ('--data', 'JSON 数据文件 (必填; 短形 -d)', ''),
            ('--title', '页面标题 (优先级 CLI > JSON 顶层 title > 数据表格)', '数据表格'),
            ('--subtitle', '页面级段落描述, 纯文本, 换行用换行符 (JSON 顶层 subtitle 兜底, 显式空串清空)', ''),
            ('--output', '输出 HTML 路径 (短形 -o; 三态 CLI > JSON 顶层 output > 均无则中断 exit 1)', ''),
            _CLI_GITHUB_URL,
            _CLI_HOME_URL,
            _CLI_FAVICON,
            ('--feedback-repo', 'GitHub Issue 反馈通道仓库 owner/repo (默认不注入, 隐私; 显式空串禁用; 环境变量 HTML_GEN_FEEDBACK_REPO)', ''),
            _CLI_QUIET,
        ],
        'data': {
            'top_level': [
                ('columns', '列定义数组 (列属性见下)', ''),
                ('data', '数据行数组 (别名 rows, 二选一)', ''),
                ('tabs', '标签页数组 (属性见下)', ''),
                ('options', '选项开关对象 (键见下)', ''),
                ('title', '页面标题 (CLI --title > 顶层 title > 默认)', ''),
                ('subtitle', '标题下段落描述, 纯文本, 换行用换行符 (显式空串清空)', ''),
                ('output', '渲染目标 (CLI -o > 顶层 output > 均无则中断 exit 1)', ''),
            ],
            'column_types': [
                ('string', '文本列 (列类型缺省值)', ''),
                ('number', '数值列 (按数值排序)', ''),
                ('pills', '标签列 (逗号/顿号分隔值渲染为 pill)', ''),
                ('videos', '视频列 (字段为对象数组, 每视频一个 pill)', ''),
                ('actions', '操作按钮列 (按钮由 col.actions 定义)', ''),
                ('datetime', '日期列 (按 Date.parse 排序)', ''),
            ],
            'columns': [
                ('key', '数据字段名 (必填)', ''),
                ('label', '表头显示名 (缺省用 key)', ''),
                ('type', '列类型 (取值见列类型段)', 'string'),
                ('width', '列宽 (Cinema 模型下必设; actions 列为 100px)', '120px'),
                ('sortable', '是否可排序', 'true'),
                ('locale', '排序语言 (如 zh 按中文排序)', ''),
                ('freeze', '列冻结 (sticky, left 偏移按前列宽累计)', ''),
                ('stickyRight', '右侧固定列 (水平滚动时贴视口右侧)', ''),
                ('preview', '分栏模式可见; 任一列 preview 为 true 时, 分栏表只显 preview 列', ''),
                ('hide', '永不可见 (表格/筛选/分栏详情 全部排除)', ''),
                ('initialHidden', '默认收起, ⚙️ 面板可开启; 分栏详情仍全列渲染 (与 hide 语义不同)', ''),
                ('splitFull', '分栏详情中该字段独占整行并可换行', ''),
                ('quickFilter', '单元格值点击即按该列筛选', 'false'),
                ('pillFilter', '标签点击筛选 (false 关闭)', 'true'),
                ('onCellClick', '单元格点击行为 (split 直接打开分栏预览)', ''),
                ('onClick', '整行点击行为 (url 点击行跳转 row.url)', ''),
                ('escape', 'HTML 转义 (自 CL010 起默认开启, escape 显式 false 是唯一豁免口)', 'true'),
                ('render', '自定义渲染函数名 (是值不是键; 新配置优先用 type)', ''),
                ('class', '单元格附加 CSS 类名', ''),
                ('format', '数值格式化 (thousands 千分位)', ''),
                ('videos', '视频列配置对象 (子键见 videos 段; type 为 videos 时生效)', ''),
                ('actions', '操作按钮数组 (子键见 actions 段; type 为 actions 时生效)', ''),
            ],
            'tabs': [
                ('key', '标签唯一标识 (匹配基准值)', ''),
                ('label', '标签显示名 (可含 emoji)', ''),
                ('field', '匹配字段 (row[field] 与 key 全等)', ''),
                ('match', '精确匹配字段 (优先于 field)', ''),
                ('contains', '逗号分隔包含匹配 (true 时按分隔符切分 field 值查找)', ''),
                ('value', '匹配目标值 (缺省取 key)', ''),
            ],
            'options': [
                ('pageSize', '每页条数', '30'),
                ('exportCSV', '导出 CSV 按钮', 'false'),
                ('rowSelect', '行选择复选框与批量操作栏', 'false'),
                ('search', '搜索框显隐', 'true'),
                ('searchFields', '限定搜索字段 (列 key 数组; 缺省全部文本列, videos 列始终排除)', ''),
                ('showIndex', '显示序号列', 'false'),
                ('clickModes', '允许的点击模式数组 ["tab","modal","split","expand"]', "['tab']"),
                ('clickMode', '单数兼容别名 (clickModes 优先, 缺 clickModes 时等价单元素数组)', ''),
                ('columnResize', '列宽拖拽 (false 时隐藏 resize handle)', 'true'),
                ('columnsSplit', '分栏模式专用列集 (如 ["name","actions"]; 缺省按 preview 过滤)', ''),
                ('modalRenderer', '自定义模态框渲染器 (如 skills 结构化详情)', ''),
                ('defaultFilter', '初始筛选 {key,value,mode} 加载后自动按该列筛选', ''),
                ('feedback', 'GitHub Issue 反馈通道配置对象 (子键见下)', ''),
            ],
            'feedback': [
                ('repo', '目标仓 owner/repo (缺失则整条反馈通道不渲染)', ''),
                ('dataset', '数据集标识 (随 issue 回传)', ''),
                ('key', '主键字段名', 'name'),
                ('altKey', '备用主键字段名 (主键为空时兜底)', ''),
                ('template', 'Issue 模板名', 'data-fix.yml'),
            ],
            'actions': [
                ('label', '按钮文案', ''),
                ('icon', '按钮图标 (emoji)', ''),
                ('copyKey', '点击复制该字段值', ''),
                ('hrefKey', '点击新标签页打开该字段 URL', ''),
                ('handler', '自定义 JS 函数名, 模板调 window.{handler}(event,row)', ''),
                ('desc', '兜底提示文案 (无其他动作时点击弹出)', ''),
                ('class', '按钮附加 CSS 类名', ''),
            ],
            'videos': [
                ('url', '视频地址 (videos 列行值对象数组的必填字段)', ''),
                ('title', '视频标题 (pill 文案, 缺省用 platform)', ''),
                ('duration', '时长 (渲染在标题后的小括号内)', ''),
                ('platform', '平台 (douyin/抖音/bilibili/B站/youtube, 其他用默认图标)', ''),
                ('maxShow', '折叠前最多显示条数, 超出折叠 +N (点击展开不收回)', '3'),
            ],
        },
        'section_order': ['top_level', 'column_types', 'columns', 'tabs', 'options', 'url_state', 'cli'],
        'url_state': [
            ('?tab', '当前标签页 key (白名单校验, 非法忽略)', ''),
            ('?q', '搜索关键字 (仅恢复输入框值)', ''),
            ('?split', '分栏预览行下标 (越界忽略)', ''),
        ],
        'behaviors': [
            ('tab', '🔗 新标签页打开 (window.open, noopener)'),
            ('modal', '📋 居中弹出面板 (键值列表/Esc关闭/自定义渲染器)'),
            ('split', '📑 分栏预览 (表格+详情, 拖拽分栏线, ▦ 比例预设, ▲▼ 导航)'),
            ('expand', '📂 行内手风琴展开 (网格布局)'),
        ],
    },
    # ── CL013: 三模板真实维度模型 (骨架 legacy 指针已删, 见 §3.2/§3.3/§3.4) ──
    #    url_state 口径: table 沿用节点顶层 (CL012 既有断言不动); doc/slide 按 R1 置于 data 分区,
    #    并在契约定义后统一别名为节点顶层键 (见下方「口径调和」; 渲染/断言经 _spec_entries 单次取用)。
    'doc': {
        'label': 'B/D 型 · Markdown 语法规范',
        'tagline': '',
        'overview': 'Markdown 语法规范 (B/D 型)',
        'rule': 24,
        'notes': 'HELP_DOC_SYNTAX',      # ③ 语法说明段 (手写常量, 不含键名; §B.3)
        'cli': [
            ('--input', 'Markdown 输入文件 (必填; 短形 -i)', ''),
            ('--output', '输出 HTML 路径 (短形 -o; 缺省与输入同名的 .html)', ''),
            ('--title', '页面标题 (优先级 CLI > frontmatter title > 正文 h1 > 文件名)', ''),
            ('--subtitle', '页面副标题', ''),
            ('--metadata', 'meta 区补充信息 (缺省自动生成创建/编辑时间与字数)', ''),
            _CLI_GITHUB_URL,
            _CLI_HOME_URL,
            _CLI_FAVICON,
            _CLI_QUIET,
        ],
        'data': {
            'url_state': [
                ('?sidebar', 'Bare 模式: sidebar=0 隐藏侧边栏 (默认隐藏, 知识库嵌入自动降级)', ''),
                ('?toolbar', 'Bare 模式: toolbar=0 隐藏工具栏 (默认隐藏)', ''),
                ('?width', '正文宽度三级 width=narrow|medium|wide (默认 medium 即 960px; 不持久化)', ''),
            ],
        },
        'section_order': ['url_state', 'cli'],
    },
    'slide': {
        'label': 'D 型 · 幻灯片功能说明',
        'tagline': '',
        'overview': 'slide 特有功能说明',
        'rule': 19,
        'notes': 'HELP_SLIDE_USAGE',     # ③ 用法说明段 (手写常量, 不含键名)
        'behaviors_title': '交互行为',    # CL013: behaviors 段标题按节点区分 (table 为「点击模式」)
        'cli': [
            ('--input', 'Markdown 输入文件 (必填; 短形 -i)', ''),
            ('--output', '输出 HTML 路径 (短形 -o; 缺省与输入同名的 .html)', ''),
            ('--title', '页面标题 (优先级 CLI > frontmatter title > 正文 h1 > 文件名)', ''),
            ('--subtitle', '页面副标题', ''),
            _CLI_GITHUB_URL,
            _CLI_HOME_URL,
            _CLI_FAVICON,
            _CLI_QUIET,
        ],
        'data': {
            'url_state': [],             # slide 无 URL 状态 (如实留空; 说明见 url_state_note)
        },
        'url_state_note': '无 —— slide 不使用 URL 参数; 阅读位置只由 localStorage 记忆',
        'section_order': ['url_state', 'behaviors', 'cli'],
        'behaviors': [
            ('分页', '每个 ## h2 为一页, h1 为封面页'),
            ('导航', '← → Space Home End 翻页'),
            ('全屏', 'F 键切换全屏'),
            ('进度点', '底部圆点 (已读/当前/未读)'),
            ('记忆', 'localStorage 恢复上次阅读位置'),
            ('侧栏H3', 'H3 子标题默认隐藏, 点击开关显示'),
            ('侧栏搜索', '支持按关键字过滤侧栏章节'),
            ('性能警告', '>50 个 h2 时显示加载警告'),
        ],
    },
    'knowledge': {
        'label': 'C 型 · 知识库 JSON 格式',
        'tagline': '',
        'overview': 'JSON 数据格式 (C 型)',
        'rule': 20,
        'examples': 'HELP_KNOWLEDGE_EXAMPLES',   # ② 手写示例段常量名 (§B.3)
        'cli': [
            ('--data', 'JSON 数据文件 (必填; 短形 -d)', ''),
            ('--groups', '类目分组文件 (短形 -g; 缺省从条目 group 自动推导)', ''),
            ('--title', '页面标题', '知识库'),
            ('--subtitle', '页面副标题', ''),
            ('--welcome', '空状态欢迎语', '从上方类目选择，浏览整理的知识内容。'),
            ('--output', '输出 HTML 路径 (短形 -o; 三态 CLI > 顶层 output > 均无则中断 exit 1)', ''),
            _CLI_GITHUB_URL,
            _CLI_HOME_URL,
            _CLI_FAVICON,
            _CLI_QUIET,
        ],
        'data': {
            'item': [
                ('title', '条目名称 (必填)', ''),
                ('group', '所属类目 (必填, 对应顶部 Tab)', ''),
                ('section', '子分类 (可选, 侧栏分组)', ''),
                ('badge', '标记文本 (可选, 侧栏条目右侧徽标)', ''),
                ('desc', '条目正文 HTML (内联渲染; 与 url 二选一)', ''),
                ('url', '详情页地址 (iframe 加载; 与 desc 二选一)', ''),
                ('icon', '条目图标 emoji (缺省无 groups 文件时用于推导类目图标)', ''),
            ],
            'groups': [
                ('key', '类目 key (与条目 group 全等匹配)', ''),
                ('label', '类目显示名 (可含 emoji, 即顶部 Tab 文案)', ''),
                ('icon', '类目图标 emoji', ''),
            ],
            'data_source': [
                ('数组', '简单格式 顶层 JSON 数组即条目列表, 类目与章节自动推导', ''),
                ('{items|data}', '结构化对象 条目取 items 或 data 字段 (二选一)', ''),
                ('output', '顶层渲染目标 (仅 data 文件识别, groups 文件忽略; 三态 CLI -o > 顶层 output > 均无则中断 exit 1)', ''),
            ],
        },
        'section_order': ['item', 'groups', 'data_source', 'cli'],
    },
}

# CL013 口径调和: 任务书 R1 要求 doc/slide 的 url_state 置于 `data` 分区, 而设计 §A 的契约结构与
# 项目核查脚本 (HTML-GEN-CL013-verify T12: 读 `TEMPLATE_CONTRACT['doc']['url_state']`) 取**节点顶层** ——
# 此处让两处指向**同一个 list 对象** (单一真源, 无内容漂移; 渲染只走一次, 见 _spec_entries)。
# table 保持 CL012 既有形态 (仅节点顶层, 不设 data 别名)。
for _t in ('doc', 'slide'):
    TEMPLATE_CONTRACT[_t]['url_state'] = TEMPLATE_CONTRACT[_t]['data']['url_state']
del _t

# 键规范段的小节标题 (节点 data 顺序 = section_order 顺序, 不在此表内的维度不渲染)
# ⚠️ 标题文本同样不得构成「词元:」形态 (标题 `X:` 中的 X 会被 spec_key_tokens() 当作键)
_SPEC_TITLES = {
    'top_level': '顶层键 (JSON 对象)',
    'column_types': '列类型',
    'columns': '列属性',
    'tabs': 'Tab 属性',
    'options': '选项',
    'url_state': 'URL 状态',
    'feedback': 'options.feedback 子键',
    'actions': 'actions[] 操作按钮子键',
    'videos': 'videos 子键',
    'cli': 'CLI 参数',
    'item': 'item 条目键 (数据源)',
    'groups': 'groups 类目键',
    'data_source': '数据源与输出目标',
}
# 嵌套维度: 父维度 → 紧随其后的子维度 (缩进渲染)
_SPEC_NESTED = {'columns': ['actions', 'videos'], 'options': ['feedback']}

# ═══ Help System ═══

# 主题清单顺序 (契约键 + 手写主题合并生成, 防新增模板漏列); 未列出者按契约顺序兜底追加
_HELP_TOPIC_ORDER = ['doc', 'table', 'knowledge', 'slide']
_HELP_MANUAL_TOPICS = [('prompt', 'prompt 指令说明'), ('demo', 'demo 指令与 demo 规范')]


def _help_topics():
    """(topic, 一句话说明) 列表: 契约键按既定顺序 + 契约新增兜底 + 手写主题。"""
    rows = [(k, TEMPLATE_CONTRACT[k]['overview']) for k in _HELP_TOPIC_ORDER if k in TEMPLATE_CONTRACT]
    rows += [(k, n['overview']) for k, n in TEMPLATE_CONTRACT.items() if k not in _HELP_TOPIC_ORDER]
    return rows + _HELP_MANUAL_TOPICS


def _help_detail_lines():
    rows = _help_topics()
    w = max(len(k) for k, _ in rows) + 1      # 与既有观感一致: 最长主题名后留 2 空格
    return '\n'.join(f"  html-gen help {k.ljust(w)} {d}" for k, d in rows)


HELP_OVERVIEW = f"""\
html-gen — HTML 模板 CLI 生成器 v{__version__}({__release_date__})

四型模板:
  doc       Markdown → B 型文档 (侧边栏 TOC + 阅读)
  slide     Markdown → D 型幻灯片 (h2 分页 + 键盘翻页)
  table     JSON     → A 型数据表格 (搜索/排序/分页)
  knowledge JSON     → C 型知识库 (标签栏 + 章节)

工具指令:
  prompt    skills/ 项目 skill 摘要与全文 (html-gen prompt <skill>)
  demo      demo 清单与详情 (html-gen demo list|<name>)

快速开始:
  html-gen doc   -i report.md  -o report.html
  html-gen slide -i slides.md  -o slides.html
  html-gen table -d data.json  -o index.html
  html-gen knowledge -d data.json -o kb.html

详细帮助:
{_help_detail_lines()}

零外部依赖，输出自包含单文件 HTML。"""

# ③ 语法/说明段 (手写常量, 不含键名; §B.3) —— 正文与 CL012 前 HELP_DOC 的语法叙述逐字一致
HELP_DOC_SYNTAX = """\
块级元素:
  # 标题            h1 (全文唯一)
  ## 标题           h2 (TOC + slide 分页)
  ### 标题          h3 (TOC 子项)
  - 列表项          无序列表 (连续自动合并)
  1. 列表项         有序列表 (连续自动合并)
  | A | B |         表格 (第二行 |:---|:---| 为分隔)
  ```lang ... ```   围栏代码块 (变长 fence 嵌套)
  > 文字            引用 (单行)
  ---               分隔线 (3+ 短横)

行内元素:
  **加粗**  *斜体*  `代码`  [文字](url)

Callout 提示框:
  > **Note:** ...     > **注意**：...
  > **Tip:** ...      > **提示**：...
  > **Warning:** ...  > **警告**：...
  > **Danger:** ...   > **危险**：...
  > **Caution:** ...

不支持:
  ✗ 缩进子列表 (平铺即可)
  ✗ ![图片](url) (用 <img> 标签)
  ✗ HTML 标签 (会被转义)"""

# ② 教程/示例段 (手写, §B.3): 示例允许含键名, 但键名以契约渲染的键规范段为准
HELP_TABLE_EXAMPLES = """\
以下为示例, 键名以键规范段 (顶层键/列类型/列属性/选项) 为准。

简单格式 (JSON 数组):
  [{"名称": "A", "数量": 10}, {"名称": "B", "数量": 20}]

输出目标 (-o 必填二选一):
  CLI -o/--output  >  JSON 顶层 "output"  >  均无 → 提示中断 (exit 1)

结构化格式:
{
  "columns": [
    {"key": "name", "label": "名称", "sortable": true, "locale": "zh",
     "width": "120px",          // 列宽 (必设, 默认 120px)
     "freeze": true,            // 列冻结 (sticky)
     "preview": true,           // 分栏模式可见
     "quickFilter": false,      // 禁用点击筛选
     "onCellClick": "split"},  // 单元格点击 → 分栏
    {"key": "count", "label": "数量", "type": "number"},
    {"key": "tags", "label": "标签", "type": "pills"},
    {"key": "actions", "label": "操作", "type": "actions",
     "stickyRight": true,       // 右侧固定列
     "actions": [
      {"icon": "📋", "label": "复制", "copyKey": "name"},
      {"icon": "🔗", "label": "打开", "hrefKey": "url"},
      {"icon": "📋", "label": "弹窗", "handler": "skillModal"},
      {"icon": "📑", "label": "分栏", "handler": "skillSplit"}
    ]}
  ],
  "data": [...],
  "tabs": [
    {"key": "all", "label": "全部"},
    {"key": "Python", "label": "🐍 Python", "field": "lang"},
    {"key": "dev", "label": "🧑‍💻 dev", "field": "profiles", "contains": true}
  ],
  "output": "demos/xxx.html",   // 可选: 渲染目标 (无 CLI -o 时生效; 均无则中断)
  "options": {
    "pageSize": 30, "exportCSV": true, "rowSelect": true,
    "clickModes": ["tab", "modal", "split", "expand"],
    "columnResize": false,       // 禁用列宽拖拽
    "columnsSplit": ["name", "actions"],  // 分栏专用列集
    "modalRenderer": "skills"   // 自定义模态框渲染器
  }
}

"""

# ② 教程/示例段 (手写常量, §B.3): 示例允许含键名, 键名以契约渲染的键规范段为准
# 三块 (条目数据 / 输出目标 / 类目分组) 与 CL012 前 HELP_KNOWLEDGE 正文逐字一致, 仅按 §B.3 补段首注记
HELP_KNOWLEDGE_EXAMPLES = """\
以下为示例, 键名以键规范段 (item/groups/数据源与输出目标) 为准。

条目数据:
[
  {
    "title": "条目名称",    // 必填
    "group": "所属类目",    // 必填, 对应顶部 Tab
    "section": "子分类",    // 可选, 侧栏分组
    "badge": "标记",        // 可选
    "desc": "<p>HTML</p>", // 内联渲染 (与 url 二选一)
    "url": "detail.html"    // iframe 加载 (与 desc 二选一)
  }
]

输出目标 (-o 必填二选一):
  CLI -o/--output  >  JSON 顶层 "output" (仅 data 文件)  >  均无 → 提示中断 (exit 1)

类目分组 (可选, 不提供时从 group 自动推导):
[
  {"key": "类目", "label": "🤖 显示名", "icon": "🤖"}
]"""

# ③ 用法说明段 (手写常量, 不含键名; §B.3) —— 与 CL012 前 HELP_SLIDE 的「用法」块逐字一致
HELP_SLIDE_USAGE = """\
用法:
  html-gen slide -i slides.md -o slides.html --title "标题\""""

HELP_PROMPT = """\
prompt — 输出项目 skills 内容
━━━━━━━━━━━━━━━━━━━━━━━━━━

用途:
  展示 skills/ 目录下项目 skill 的摘要或全文 (供 agent 参考)

用法:
  html-gen prompt                列出全部 skill (名称 + 摘要)
  html-gen prompt <skill>        输出该 skill 摘要 + 章节
  html-gen prompt <skill> --brief  仅输出摘要 (不打印章节/全文)
  html-gen prompt <skill> --json  JSON 输出 (checkpoint 信封 {status,data,error})
  html-gen prompt --site         生成 prompts/ 在线阅读站点 (31 文件)
  html-gen prompt --site --dir <path>  站点输出目录覆盖 (默认 仓库根/prompts/)

说明:
  skills/ 每子目录一个 skill (含 SKILL.md), 支持 references/*.md 拼接。
  --site: 产物一律剥离 YAML frontmatter (GitHub Pages 原样服务, curl 可得纯 md /
  json 信封 / all.md 全量; index.html 为 C 型 knowledge 门户 (5 tab: A 表格/B 文档/
  C 知识库/D 幻灯片/通用 CLI; 纵向 指令 CLI/模板语法/使用案例), kb/{skill}.html
  为 skill detail 页)。--site 与 skill/--brief/--json 互斥。产物勿手改,
  由 --site 重新生成。"""

HELP_DEMO = """\
demo — demo 清单与详情
━━━━━━━━━━━━━━━━━━━━━━━━━━

用途:
  按模板类型列出 demos/ 目录的 demo, 或查看单个 demo 的文件结构与预览地址

用法:
  html-gen demo list             按类型分组列出独立 demo (过滤被引用子页)
  html-gen demo list --all       含被引用子页 (knowledge 主库引用的内容页)
  html-gen demo list --json      JSON 输出
  html-gen demo <name>           查看详情: entry / 源文件 / 预览 URL
  html-gen demo <name> --open    浏览器打开预览 (需 hs 服务)
  html-gen demo --rebuild        重新扫描 demos/ 生成 _registry.json

demo 规范:
  demos/_registry.json           清单数据源 {version,count,demos[]}
  demos[] 字段: name/title/type/entry/featured/referenced/referenced_by
  type: knowledge(C) / table(A) / doc(B) / html(独立页) —— 按模板特征自动识别
  featured: 首页精选 (index.html 链接项)
  referenced: 被 knowledge 主库引用 → 默认 list 不单列 (--all 查看)
  name 唯一: 根级=文件名; 子目录页={子目录}-{文件名} (避免跨主题撞名)
  目录约定: 根级=独立案例 (URL 扁平 /demos/{name}.html); 子目录=知识库引用子页/主题分组"""

# 手写主题 (不进契约: 描述 CLI 子命令而非数据契约)
HELP_MAP = {
    'prompt': HELP_PROMPT,
    'demo': HELP_DEMO,
}


def _help_const(name):
    """按名取手写 help 文案常量 (契约节点以常量名引用, 规避前向定义)。"""
    text = globals().get(name)
    if not isinstance(text, str):
        raise RuntimeError(f'help 契约引用的常量不存在: {name}')
    return text


def _fmt_entries(entries, indent='  ', width=78):
    """键规范条目 → `key: 说明 (默认: x)` 行式排版 (同小节按宽度折行, 条目间 ' / ' 分隔)。"""
    parts = []
    for key, desc, default in entries:
        text = f'{key}: {desc}' if desc else key
        if default:
            text += f' (默认: {default})'
        parts.append(text)
    lines, cur = [], ''
    for part in parts:
        if not cur:
            cur = part
        elif len(indent) + len(cur) + 3 + len(part) <= width:
            cur += ' / ' + part
        else:
            lines.append(indent + cur)
            cur = part
    if cur:
        lines.append(indent + cur)
    return lines


def _spec_block(title, entries, indent=0):
    """单小节: 标题 (顶格/嵌套缩进) + 条目行 (条目恒缩进两级于标题)。"""
    return [f'{" " * indent}{title}:'] + _fmt_entries(entries, indent=' ' * (indent + 2))


def _disp_width(text):
    """显示宽度 (东亚宽/全角字符按 2 列计): behaviors 段中文键对齐用; ASCII 键与 len() 等价。"""
    return sum(2 if unicodedata.east_asian_width(ch) in 'WF' else 1 for ch in text)


def _spec_entries(node, dim):
    """维度条目取用口径: node['data'][dim] 优先, 其次节点顶层 (table.url_state / 四模板 cli)。"""
    data = node.get('data') or {}
    if dim in data:
        return data[dim]
    return node.get(dim) or []


def _behaviors_block(node):
    """behaviors 段: 标题按节点区分 (behaviors_title, 缺省「点击模式」), 行式 `key … — 说明`。"""
    rows = node['behaviors']
    w = max(_disp_width(k) for k, _ in rows) + 3
    body = [f'  {k}{" " * (w - _disp_width(k))}— {d}' for k, d in rows]
    return [f'{node.get("behaviors_title", "点击模式")}:'] + body


def render_help_spec(topic):
    """① 键规范段 (契约渲染): help 中键清单的唯一来源 (§B.3)。"""
    node = TEMPLATE_CONTRACT[topic]
    data = node.get('data') or {}
    order = node.get('section_order') or list(data)
    blocks = []
    for dim in order:
        if dim == 'behaviors':                    # 行为段 (非键表): 按 section_order 位置就地渲染
            if node.get('behaviors'):
                blocks.append(_behaviors_block(node))
            continue
        entries = _spec_entries(node, dim)
        if dim == 'url_state' and not entries:
            if node.get('url_state_note'):        # 如实写明「无 URL 状态」(slide, §3.3)
                blocks.append([f'{_SPEC_TITLES[dim]}:', f'  {node["url_state_note"]}'])
            continue
        if not entries:
            continue
        blocks.append(_spec_block(_SPEC_TITLES[dim], entries))
        for sub in _SPEC_NESTED.get(dim, []):     # 嵌套子键紧随父小节 (缩进一级)
            sub_entries = data.get(sub) or []
            if sub_entries:
                blocks.append(_spec_block(_SPEC_TITLES[sub], sub_entries, indent=4))
    if node.get('behaviors') and 'behaviors' not in order:
        blocks.append(_behaviors_block(node))     # table: 行为段恒在末尾 (沿用既有观感, 逐字不变)
    return '\n\n'.join('\n'.join(b) for b in blocks)


def render_help(topic):
    """主题 help 正文: label/tagline → ② 示例段 → ③ 语法/说明段 → ① 契约键规范段 (§B.3)。"""
    node = TEMPLATE_CONTRACT[topic]
    header = node['label'] + (f" ({node['tagline']})" if node.get('tagline') else '')
    lines = [header, '━' * node['rule'], '']
    for slot in ('examples', 'notes'):            # ② 示例段 / ③ 语法说明段 (手写常量)
        if node.get(slot):
            lines.append(_help_const(node[slot]).rstrip('\n'))
    spec = render_help_spec(topic)
    if spec:
        lines.append('')
        lines.append(spec)
    return '\n'.join(lines)


def cmd_help(args):
    if args.topic in TEMPLATE_CONTRACT:           # 契约主题 → 契约渲染
        print(render_help(args.topic))
    elif args.topic in HELP_MAP:                  # prompt/demo → 手写
        print(HELP_MAP[args.topic])
    else:
        print(HELP_OVERVIEW)


def cmd_version(args):
    """CL016: version 子指令, 输出 {name} v{ver} ({date}) 空格分隔."""
    print(f'html-gen v{__version__} ({__release_date__})')


# ═══ CLI ═══
def main():
    p = argparse.ArgumentParser(description=f'html-gen v{__version__}({__release_date__}) — HTML 模板生成器')
    p.add_argument('--version', action='version', version=f'html-gen v{__version__} ({__release_date__})')
    p.add_argument('--quiet', action='store_true', help='仅打印生成路径，抑制统计信息')
    sub = p.add_subparsers(dest='command', required=True)

    h = sub.add_parser('help', help='显示帮助')
    h.add_argument('topic', nargs='?', choices=['doc', 'slide', 'table', 'knowledge', 'prompt', 'demo'],
                   help='帮助主题 (doc/slide/table/knowledge/prompt/demo)')

    v = sub.add_parser('version', help='显示版本')

    d = sub.add_parser('doc', help='Markdown → B 型文档')
    d.add_argument('--quiet', action='store_true', default=argparse.SUPPRESS, help='仅打印生成路径，抑制统计信息')
    d.add_argument('-i', '--input', required=True)
    d.add_argument('-o', '--output')
    d.add_argument('--title')
    d.add_argument('--subtitle')
    d.add_argument('--metadata')
    d.add_argument('--github-url', help='右上角 GitHub corner 链接 (默认不带, 隐私; 显式空串禁用; env: HTML_GEN_GITHUB_URL)')
    d.add_argument('--home-url', help='demo 首页入口链接 (默认不带, 隐私; 显式空串禁用; env: HTML_GEN_HOME_URL)')
    d.add_argument('--favicon', help='favicon URL (默认注入默认图标; 显式空串禁用; env: HTML_GEN_FAVICON)')

    s = sub.add_parser('slide', help='Markdown → 幻灯片')
    s.add_argument('--quiet', action='store_true', default=argparse.SUPPRESS, help='仅打印生成路径，抑制统计信息')
    s.add_argument('-i', '--input', required=True)
    s.add_argument('-o', '--output')
    s.add_argument('--title')
    s.add_argument('--subtitle')
    s.add_argument('--github-url', help='右上角 GitHub corner 链接 (默认不带, 隐私; 显式空串禁用; env: HTML_GEN_GITHUB_URL)')
    s.add_argument('--home-url', help='demo 首页入口链接 (默认不带, 隐私; 显式空串禁用; env: HTML_GEN_HOME_URL)')
    s.add_argument('--favicon', help='favicon URL (默认注入默认图标; 显式空串禁用; env: HTML_GEN_FAVICON)')

    t = sub.add_parser('table', help='JSON → A 型数据表格')
    t.add_argument('--quiet', action='store_true', default=argparse.SUPPRESS, help='仅打印生成路径，抑制统计信息')
    t.add_argument('-d', '--data', required=True)
    t.add_argument('--title')  # 优先级: CLI > JSON 顶层 title > '数据表格'
    t.add_argument('--subtitle', help='页面级段落描述(纯文本, \\n 换行); JSON 顶层 subtitle 兜底, 显式传空串清空')
    t.add_argument('-o', '--output', help='输出 HTML 路径 (必填: CLI -o 或 JSON 顶层 output 二选一)')
    t.add_argument('--github-url', help='右上角 GitHub corner 链接 (默认不带, 隐私; 显式空串禁用; env: HTML_GEN_GITHUB_URL)')
    t.add_argument('--home-url', help='demo 首页入口链接 (默认不带, 隐私; 显式空串禁用; env: HTML_GEN_HOME_URL)')
    t.add_argument('--favicon', help='favicon URL (默认注入默认图标; 显式空串禁用; env: HTML_GEN_FAVICON)')
    t.add_argument('--feedback-repo', help='GitHub Issue 反馈通道仓库 owner/repo (默认不注入, 隐私; 显式空串禁用; env: HTML_GEN_FEEDBACK_REPO)')

    k = sub.add_parser('knowledge', help='JSON → C 型知识库')
    k.add_argument('--quiet', action='store_true', default=argparse.SUPPRESS, help='仅打印生成路径，抑制统计信息')
    k.add_argument('-d', '--data', required=True)
    k.add_argument('-g', '--groups')
    k.add_argument('--title', default='知识库')
    k.add_argument('--subtitle', default='')
    k.add_argument('--welcome', default='')
    k.add_argument('-o', '--output', help='输出 HTML 路径 (必填: CLI -o 或 JSON 顶层 output 二选一)')
    k.add_argument('--github-url', help='右上角 GitHub corner 链接 (默认不带, 隐私; 显式空串禁用; env: HTML_GEN_GITHUB_URL)')
    k.add_argument('--home-url', help='demo 首页入口链接 (默认不带, 隐私; 显式空串禁用; env: HTML_GEN_HOME_URL)')
    k.add_argument('--favicon', help='favicon URL (默认注入默认图标; 显式空串禁用; env: HTML_GEN_FAVICON)')

    pr = sub.add_parser('prompt', help='输出项目 skills (html-gen prompt <skill>; --site 生成在线阅读站点)')
    pr.add_argument('skill', nargs='?', help='skill 名称 (可选)')
    pr.add_argument('--brief', action='store_true', help='仅输出摘要')
    pr.add_argument('--json', action='store_true', help='JSON 输出 (checkpoint 信封 {status,data,error})')
    pr.add_argument('--site', action='store_true', help='生成 prompts/ 在线阅读站点 (31 文件: C 型门户 + kb detail)')
    pr.add_argument('--dir', help='站点输出目录覆盖 (默认 仓库根/prompts/)')
    pr.add_argument('--quiet', action='store_true', default=argparse.SUPPRESS, help='仅打印生成路径，抑制统计信息')

    dm = sub.add_parser('demo', help='demo 列表与详情 (html-gen demo list|<name>)')
    dm.add_argument('name', nargs='?', help='demo 名称 (可选; 缺省=list)')
    dm.add_argument('--json', action='store_true', help='JSON 输出')
    dm.add_argument('--all', action='store_true', help='list 含被引用子页')
    dm.add_argument('--open', action='store_true', help='打开浏览器预览')
    dm.add_argument('--rebuild', action='store_true', help='重新扫描 demos/ 生成 _registry.json')

    args = p.parse_args()
    {'help': cmd_help, 'version': cmd_version, 'doc': cmd_doc, 'slide': cmd_slide,
     'table': cmd_table, 'knowledge': cmd_knowledge, 'prompt': cmd_prompt,
     'demo': cmd_demo}[args.command](args)


def cmd_prompt(args):
    """输出项目 skills prompt 内容."""
    # HTML-GEN-CL007: --site 生成 prompts/ 在线阅读站点 (互斥校验 → cmd_prompt_site)
    if getattr(args, 'site', False):
        if args.skill or args.brief or args.json:
            print('❌ --site 与 skill/--brief/--json 互斥（--site 独立生成 prompts/ 站点）',
                  file=sys.stderr)
            sys.exit(1)
        cmd_prompt_site(args)
        return

    import subprocess as _sp
    import json as _json
    SKILLS_DIR = Path(__file__).resolve().parent / 'skills'
    if not SKILLS_DIR.is_dir():
        print("❌ skills/ 目录不存在", file=sys.stderr); sys.exit(1)

    # 收集所有 skill
    skills = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir():
            smd = d / 'SKILL.md'
            if smd.exists():
                skills.append({'name': d.name, 'path': smd, 'dir': d})

    if not skills:
        print("❌ 无可用 skill", file=sys.stderr); sys.exit(1)

    # 无参: 列出所有
    if not args.skill:
        if getattr(args, 'json', False):
            print(_json.dumps({'status': 'ok', 'error': '', 'data': [
                {'name': s['name'],
                 'description': _skill_desc(s['path']),
                 'references': [r.name for r in s['dir'].glob('references/*.md')]}
                for s in skills]}, ensure_ascii=False, indent=2))
            return
        print("可用 skills:\n")
        for s in skills:
            desc = ''
            try:
                with open(s['path']) as _f:
                    for _line in _f:
                        if _line.startswith('description:'):
                            desc = _line.split(':',1)[1].strip(); break
            except: pass
            refs = [r.name for r in s['dir'].glob('references/*.md')]
            print(f"  {s['name']}")
            if desc: print(f"    {desc}")
            if refs: print(f"    references: {', '.join(refs)}")
            print(f"    用法: html-gen prompt {s['name']}")
            print()
        return

    # 带参: 查找 skill
    target = next((s for s in skills if s['name'] == args.skill), None)
    if not target:
        if getattr(args, 'json', False):
            print(_json.dumps({'status': 'error', 'data': None,
                               'error': f"skill '{args.skill}' 不存在"},
                              ensure_ascii=False, indent=2))
            sys.exit(1)
        print(f"❌ skill '{args.skill}' 不存在", file=sys.stderr)
        print(f"可用: {', '.join(s['name'] for s in skills)}")
        sys.exit(1)

    # 输出 SKILL.md 全文
    content_text = Path(target['path']).read_text(encoding='utf-8')

    if getattr(args, 'json', False):
        refs = sorted(target['dir'].glob('references/*.md'))
        print(_json.dumps({'status': 'ok', 'error': '', 'data': {
            'name': target['name'],
            'content': content_text,
            'references': {r.stem: r.read_text(encoding='utf-8') for r in refs},
        }}, ensure_ascii=False, indent=2))
        return

    if args.brief:
        # 仅摘要: description + 章节标题 + references
        lines = content_text.split('\n')
        desc = next((l.split(':',1)[1].strip() for l in lines if l.startswith('description:')), '')
        headings = [l for l in lines if l.startswith('## ')]
        refs = [r.name for r in target['dir'].glob('references/*.md')]
        if desc: print(desc); print()
        if headings:
            print('章节:')
            for h in headings: print(f"  {h[3:]}")
            print()
        if refs: print(f"references: {', '.join(refs)}")
        return

    # 全文
    print(content_text)

    # 拼接 references
    refs = sorted(target['dir'].glob('references/*.md'))
    if refs:
        print('\n---\n')
        for r in refs:
            print(f'## {r.stem}')
            print(r.read_text(encoding='utf-8'))
            print()


# ── prompt --site v2 门户注册表 (HTML-GEN-CL008, 设计 §4) ──
# groups: 横向 5 tab; SKILL_TO_GROUP/GUIDE_MAP/CASE_MAP: _kb-data 条目 append 序
# = SKILL_TO_GROUP → GUIDE_MAP → CASE_MAP (HG-SEC-102: layout-knowledge 侧栏按
# 数据数组内 section 首现顺序渲染, 保证组内 指令 CLI → 模板语法 → 使用案例)。

SITE_GROUPS = [
    {'key': 'table',     'label': 'A 表格',   'icon': '📊'},
    {'key': 'doc',       'label': 'B 文档',   'icon': '📄'},
    {'key': 'knowledge', 'label': 'C 知识库', 'icon': '📚'},
    {'key': 'slide',     'label': 'D 幻灯片', 'icon': '🎞️'},
    {'key': 'cli',       'label': '通用 CLI', 'icon': '🛠️'},
]

SKILL_TO_GROUP = {
    'html-gen-table':          ('table',     '指令 CLI'),
    'html-gen-doc':            ('doc',       '指令 CLI'),
    'html-gen-knowledge':      ('knowledge', '指令 CLI'),
    'html-gen-slide':          ('slide',     '指令 CLI'),
    'html-gen':                ('cli',       '指令 CLI'),
    'html-gen-cli-spec':       ('cli',       '指令 CLI'),
    'github-issue-feedback':   ('table',     '指令 CLI'),
    'pages-index':             ('cli',       '页面规范'),
    'test-speed-optimization': ('cli',       '测试规范'),
}

# demos/ 指南页 (badge 指南; file 相对 demos/, group/section 门户归属, desc 一句)
GUIDE_MAP = [
    {'file': 'table-guide.html',      'group': 'table',     'section': '模板语法',
     'title': 'A 型 · 数据表格方案',  'desc': 'table 模板方案指南 (列配置/交互/案例)'},
    {'file': 'doc-guide.html',        'group': 'doc',       'section': '模板语法',
     'title': 'B 型 · 文档阅读方案',  'desc': 'doc 模板方案指南 (Markdown/阅读)'},
    {'file': 'knowledge-guide.html',  'group': 'knowledge', 'section': '模板语法',
     'title': 'C 型 · 知识库方案',    'desc': 'knowledge 模板方案指南 (条目/分组)'},
    {'file': 'slide-guide.html',      'group': 'slide',     'section': '模板语法',
     'title': 'D 型 · 幻灯片方案',    'desc': 'slide 模板方案指南 (分页/演示)'},
    {'file': 'usage-guide.html',      'group': 'cli',       'section': '指令 CLI',
     'title': 'CLI 使用说明',         'desc': 'html-gen CLI 命令总览'},
    {'file': 'markdown-spec.html',    'group': 'doc',       'section': '模板语法',
     'title': 'Markdown 语法规范',    'desc': 'md_to_html 支持的语法子集 (随 doc 组)'},
]

# demos/ 使用案例 (badge 案例; cli 组无案例维, G1b-1)
CASE_MAP = [
    # table
    {'file': 'countries-table.html',          'group': 'table',     'section': '使用案例',
     'title': '全球国家速查表',               'desc': '全球 195 国速查表 (A 型)'},
    {'file': 'provinces-table.html',          'group': 'table',     'section': '使用案例',
     'title': '中国省份速查表',               'desc': '中国 34 省速查表 (A 型)'},
    {'file': 'table-features-demo.html',      'group': 'table',     'section': '使用案例',
     'title': '表格功能全演示',               'desc': '表格功能全演示 (A 型)'},
    {'file': 'hermes-profile-skills-list.html', 'group': 'table',   'section': '使用案例',
     'title': 'Hermes Skills 列表',           'desc': 'Hermes Skills 列表 (A 型)'},
    # doc (内容子页)
    {'file': 'chaitin/company-profile.html',  'group': 'doc',       'section': '使用案例',
     'title': '长亭公司档案',                 'desc': '长亭公司档案 (B 型内容页)'},
    {'file': 'cloudwise/company-profile.html', 'group': 'doc',      'section': '使用案例',
     'title': '云智慧公司档案',               'desc': '云智慧公司档案 (B 型内容页)'},
    {'file': 'chaitin/business-model.html',   'group': 'doc',       'section': '使用案例',
     'title': '长亭商业模式',                 'desc': '长亭商业模式 (B 型内容页)'},
    # knowledge
    {'file': 'drama-knowledge.html',          'group': 'knowledge', 'section': '使用案例',
     'title': '以剧读史知识库',               'desc': '以剧读史影视历史知识库 (C 型)'},
    {'file': 'chaitin-business-analysis.html', 'group': 'knowledge', 'section': '使用案例',
     'title': '长亭商业分析',                 'desc': '长亭科技商业分析知识库 (C 型)'},
    {'file': 'cloudwise-business-analysis.html', 'group': 'knowledge', 'section': '使用案例',
     'title': '云智慧商业分析',               'desc': '云智慧商业分析知识库 (C 型)'},
    {'file': 'knowledge-demo.html',           'group': 'knowledge', 'section': '使用案例',
     'title': '知识库功能演示',               'desc': '知识库功能演示 (C 型)'},
    # slide
    {'file': 'slide-demo.html',               'group': 'slide',     'section': '使用案例',
     'title': '幻灯片演示',                   'desc': 'D 型幻灯片演示'},
]


def _site_kb_items(skills):
    """构建 _kb-data.json 条目列表 (kind ∈ skill/guide/case).

    desc: skill = SKILL.md frontmatter description 首行 (HG-SEC-095);
    guide/case = 注册表一句。url 为门户相对路径: kb/{skill}.html (detail) 或
    ../demos/*.html (guide/case)。全条目带 url → layout-knowledge url 优先,
    desc 不参与门户 UI 渲染, 仅注册表元数据 (HG-SEC-101)。"""
    by_name = {s['name']: s for s in skills}
    items = []
    for name, (group, section) in SKILL_TO_GROUP.items():
        s = by_name.get(name)
        if not s:
            continue
        items.append({'title': name, 'group': group, 'section': section,
                      'badge': 'Prompt', 'desc': _skill_desc(s['path']),
                      'url': f'kb/{name}.html', 'kind': 'skill'})
    for g in GUIDE_MAP:
        items.append({'title': g['title'], 'group': g['group'], 'section': g['section'],
                      'badge': '指南', 'desc': g['desc'],
                      'url': '../demos/' + g['file'], 'kind': 'guide'})
    for c in CASE_MAP:
        items.append({'title': c['title'], 'group': c['group'], 'section': c['section'],
                      'badge': '案例', 'desc': c['desc'],
                      'url': '../demos/' + c['file'], 'kind': 'case'})
    return items


def cmd_prompt_site(args):
    """生成 prompts/ 在线阅读站点 (31 文件): C 型知识库门户 + kb/{skill}.html ×9.

    HTML-GEN-CL008 (v2)。流程: 内存全量构建(fail-fast, 零写盘) → 清理已知产物名
    (顶层 22 + kb/ 9, HG-SEC-088 containment) → 写 18 md/json + all.md +
    _kb-groups/_kb-data json → cmd_doc 渲染 9 个 kb/{skill}.html (stdout 抑制)
    → cmd_knowledge 渲染 index.html 门户 (stdout 抑制)。
    产物一律剥离 frontmatter (Jekyll 原样服务依据, 设计 §3/§6)。
    """
    import json as _json
    import contextlib
    import io
    SKILLS_DIR = Path(__file__).resolve().parent / 'skills'
    if not SKILLS_DIR.is_dir():
        print("❌ skills/ 目录不存在", file=sys.stderr)
        sys.exit(1)
    default_out = Path(__file__).resolve().parent / 'prompts'
    raw_dir = getattr(args, 'dir', None)
    if raw_dir is not None and str(raw_dir).strip() == '':
        print('❌ --dir 不能为空串 (站点输出目录)', file=sys.stderr)
        sys.exit(1)
    out_dir = Path(raw_dir) if raw_dir else default_out
    if out_dir.exists() and not out_dir.is_dir():
        print(f'❌ --dir 输出路径不是目录: {out_dir}', file=sys.stderr)
        sys.exit(1)
    if out_dir.resolve() == Path(__file__).resolve().parent.resolve():
        # HG-SEC-098: 仓库根含 index.html/all.md 同名产物在 known 清理集 → 防误删
        print('❌ --dir 不能为仓库根目录 (含 index.html/all.md 同名产物, 防误删)',
              file=sys.stderr)
        sys.exit(1)

    # 收集 skills (sorted, 与 cmd_prompt 一致)
    skills = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir():
            smd = d / 'SKILL.md'
            if smd.exists():
                skills.append({'name': d.name, 'path': smd, 'dir': d})
    if not skills:
        print("❌ 无可用 skill", file=sys.stderr)
        sys.exit(1)

    # ── 内存构建全部产物 (fail-fast: 任一读失败 → stderr + exit 1, 零写盘) ──
    md_texts, json_docs, site_sections = {}, {}, []
    try:
        for s in skills:
            raw = Path(s['path']).read_text(encoding='utf-8')
            stripped, _fm = strip_frontmatter(raw)
            refs = sorted(Path(s['dir']).glob('references/*.md'))
            ref_contents, md_tail, site_refs = {}, [], []
            for r in refs:
                rtext = r.read_text(encoding='utf-8')
                ref_contents[r.stem] = rtext
                # §6.1: 每 reference 前 \n\n---\n\n## {stem}\n + 原文 (CLI prompt 全文一致)
                md_tail.append(f'\n\n---\n\n## {r.stem}\n{rtext}')
                # all.md 内: 段标题 ## {stem} 已承载 → 剥离 reference 自身首个顶层 h1
                site_refs.append((r.stem, _strip_leading_h1(rtext)))
            md_texts[s['name']] = stripped + ''.join(md_tail)
            json_docs[s['name']] = {'status': 'ok', 'error': '', 'data': {
                'name': s['name'],
                'content': stripped,
                'references': ref_contents,
            }}
            site_sections.append(_site_skill_section(s, stripped, site_refs))
    except OSError as e:
        print(f"❌ 读取失败: {e}", file=sys.stderr)
        sys.exit(1)

    # ── 清理已知产物名 (HG-SEC-088: 仅删已知产物名, 其他文件保留; containment) ──
    # 顶层 22 = index.html + all.md + _kb-groups/_kb-data json + 18 md/json
    top_known = {'index.html', 'all.md', '_kb-groups.json', '_kb-data.json'}
    for s in skills:
        top_known.add(f'{s["name"]}.md')
        top_known.add(f'{s["name"]}.json')
    # kb/ 9 个 detail (顶层 iterdir 扫不到子目录 → 对 kb/ 内已知名再循环, HG-SEC-103)
    kb_known = {f'{s["name"]}.html' for s in skills}
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.iterdir():
        if f.is_file() and f.name in top_known:
            f.unlink()
    kb_dir = out_dir / 'kb'
    kb_dir.mkdir(parents=True, exist_ok=True)   # cmd_doc/cmd_knowledge 均不建父目录
    for f in kb_dir.iterdir():
        if f.is_file() and f.name in kb_known:
            f.unlink()

    # ── 写 18 md/json + all.md + _kb-groups/_kb-data json ──
    for s in skills:
        (out_dir / f'{s["name"]}.md').write_text(md_texts[s['name']], encoding='utf-8')
        (out_dir / f'{s["name"]}.json').write_text(
            _json.dumps(json_docs[s['name']], ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8')
    all_md = _site_all_md(skills, site_sections)
    (out_dir / 'all.md').write_text(all_md, encoding='utf-8')
    (out_dir / '_kb-groups.json').write_text(
        _json.dumps(SITE_GROUPS, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8')
    (out_dir / '_kb-data.json').write_text(
        _json.dumps(_site_kb_items(skills), ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8')

    # ── kb/{skill}.html ×9: cmd_doc 渲染 detail (Namespace 全字段 HG-SEC-100) ──
    for s in skills:
        a = types.SimpleNamespace(
            input=str(out_dir / f'{s["name"]}.md'),
            output=str(kb_dir / f'{s["name"]}.html'),
            title=s['name'],
            subtitle=None,
            quiet=True,
            github_url='',                                       # 空串: 防 env 覆盖 (HG-SEC-090)
            home_url='',                                         # detail 无首页入口
        )
        with contextlib.redirect_stdout(io.StringIO()):          # 抑制 cmd_doc 内部输出
            cmd_doc(a)

    # ── index.html: cmd_knowledge 渲染 C 型门户 (Namespace 全字段 HG-SEC-100) ──
    p = types.SimpleNamespace(
        data=str(out_dir / '_kb-data.json'),
        groups=str(out_dir / '_kb-groups.json'),
        output=str(out_dir / 'index.html'),
        title='html-gen Prompt 站点',
        welcome='从上方类目选择: 每模板维度下 指令 CLI / 模板语法 / 使用案例',
        subtitle=None,
        quiet=True,
        github_url='',
        home_url='https://html-gen.cli.jaden.tech/',
    )
    with contextlib.redirect_stdout(io.StringIO()):              # HG-SEC-103: quiet 非「仅打印路径」
        cmd_knowledge(p)

    # 统计「31 文件」与清理集解耦 (HG-SEC-103): 每 skill 3 文件 (md/json/kb) + 顶层 4
    n_total = len(skills) * 3 + 4
    if getattr(args, 'quiet', False):
        print(str(out_dir))
    else:
        print(f"[站点] {out_dir} 已生成: {len(skills)} skills "
              f"({n_total} 文件: 门户 + kb×{len(skills)} + md/json×{len(skills) * 2} + all.md)")


def _strip_leading_h1(text):
    """删除 markdown 文本首个顶层(围栏外) `# ` 标题行 (fence-aware, HG-SEC-087)."""
    lines = text.split('\n')
    idxs = _fence_top_h1_indices(lines)
    if idxs:
        del lines[idxs[0]]
    return '\n'.join(lines).strip('\n')


def _site_skill_section(skill, stripped, site_refs):
    """all.md 单 skill 段: ## {name} + > description + 正文(删 h1) + references."""
    desc = _skill_desc(skill['path'])
    parts = [f"## {skill['name']}"]
    if desc:
        parts.append(f"> {desc}")
    parts.append(_strip_leading_h1(stripped))
    for stem, rtext in site_refs:
        parts.append(f"---\n\n## {stem}\n\n{rtext}")
    return '\n\n'.join(parts)


def _site_all_md(skills, site_sections):
    """all.md 组装: 唯一顶层 h1 + 说明引用块 + 9 skill 段."""
    header = ("# html-gen Prompt 合集\n\n"
              "> 在线阅读: html-gen 项目 9 个 skills prompt 全文（含 references）。\n"
              "> 单篇获取: prompts/{skill}.md（纯 markdown）· prompts/{skill}.json（JSON 信封）· all.md（全量）。\n"
              "> 重新生成: html-gen prompt --site（产物勿手改，由生成器产出）。\n")
    return header + '\n\n' + '\n\n'.join(site_sections) + '\n'


def cmd_demo(args):
    """demo 列表与详情：html-gen demo list|<name> [--json] [--all] [--open] [--rebuild]."""
    import json as _json
    import urllib.request as _ur
    DEMOS_DIR = Path(__file__).resolve().parent / 'demos'
    DATA_DIR = Path(__file__).resolve().parent / 'data'
    reg_file = DEMOS_DIR / '_registry.json'

    # --rebuild: 重新扫描 demos/ 生成 registry
    if getattr(args, 'rebuild', False):
        import re as _re
        refs = {}
        for kb in DATA_DIR.glob('*kb-data.json'):
            try:
                items = _json.loads(kb.read_text(encoding='utf-8'))
            except Exception:
                continue
            for it in items:
                u = it.get('url')
                if u:
                    refs.setdefault(u, []).append(kb.stem)
        featured = set()
        try:
            idx = (DEMOS_DIR / 'index.html').read_text(encoding='utf-8')
            featured = {m for m in _re.findall(r'href="([^"#]+\.html)"', idx)}
        except Exception:
            pass

        def detect_type(h):
            if 'doc-header' in h:
                return 'doc'
            if 'kw-tab' in h or 'kwSidebar' in h:
                return 'knowledge'
            if 'data-table' in h or 'kv-list' in h:
                return 'table'
            return 'html'

        demos = []
        for f in sorted(DEMOS_DIR.rglob('*.html')):
            if f.name in ('index.html', '_registry.json'):
                continue
            rel = f.relative_to(DEMOS_DIR).as_posix()
            # name 唯一化: 根级=stem; 子目录页={topic}-{stem} (防 chaitin/cloudwise 等跨主题撞名)
            name = f.stem if f.parent == DEMOS_DIR else f.parent.name + '-' + f.stem
            h = f.read_text(encoding='utf-8', errors='ignore')
            t = _re.search(r'<title>(.*?)</title>', h, _re.S)
            demos.append({
                'name': name, 'title': t.group(1).strip() if t else f.stem,
                'type': detect_type(h), 'entry': rel, 'featured': rel in featured,
                'referenced': rel in refs, 'referenced_by': refs.get(rel, []),
            })
        reg = {'version': 3, 'count': len(demos), 'demos': demos}
        reg_file.write_text(_json.dumps(reg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f"✅ registry 重建: {len(demos)} demos (featured {len(featured)} / "
              f"引用子页 {len(refs)})")

        # 顺带重建独立案例索引 (data/_demos-data.json + demos-index.html)
        type_icons = {'knowledge': '📚 C 型', 'table': '🗂 A 型', 'doc': '📄 B 型', 'html': '🌐 独立页'}
        indep = [d for d in demos if not d.get('referenced')]
        indep.sort(key=lambda d: (not d.get('featured'), d['entry']))
        idx_columns = [
            {'key': '标题', 'label': '标题', 'sortable': True, 'locale': 'zh', 'width': '200px', 'freeze': True, 'preview': True},
            {'key': '模板', 'label': '模板', 'type': 'pills', 'sortable': True, 'locale': 'zh', 'width': '120px', 'preview': True},
            {'key': '文档链接', 'label': '文档链接', 'sortable': True, 'locale': 'zh', 'width': '260px', 'preview': True, 'escape': False},
        ]
        idx_rows = []
        for d in indep:
            title_txt = ('★ ' if d.get('featured') else '') + d['title']
            fname = d['entry'].rsplit('/', 1)[-1]
            idx_rows.append({
                '标题': title_txt,
                '模板': type_icons.get(d['type'], '🌐 独立页'),
                '文档链接': f'<a href="{d["entry"]}" target="_blank" rel="noopener">{fname} ↗</a>',
            })
        idx_data = {'columns': idx_columns, 'data': idx_rows, 'tabs': [],
                    'options': {'pageSize': 30, 'exportCSV': True, 'search': True, 'showIndex': True}}
        idx_file = DATA_DIR / '_demos-data.json'
        idx_file.write_text(_json.dumps(idx_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        a = types.SimpleNamespace(data=str(idx_file), title='DEMO 案例索引',
                                  subtitle=None,
                                  github_url=None,
                                  home_url='https://html-gen.cli.jaden.tech/',  # G1(CL005): demo 首页入口, 与 syncer rebuild 缺省一致
                                  output=str(DEMOS_DIR / 'demos-index.html'))
        cmd_table(a)
        print(f"📇 索引重建: {len(idx_rows)} 独立案例 → demos-index.html")
        return

    if not reg_file.exists():
        print('❌ demos/_registry.json 不存在（html-gen demo --rebuild 生成）', file=sys.stderr)
        sys.exit(1)
    reg = _json.loads(reg_file.read_text(encoding='utf-8'))
    demos = reg.get('demos', [])

    # list（无参或缺省）——按模板类型分组，过滤被引用子页
    if not args.name or args.name == 'list':
        if args.json:
            print(_json.dumps({'status': 'ok', 'data': demos, 'error': ''},
                              ensure_ascii=False))
            return
        groups = [('knowledge', '📚 知识库（C 型）'), ('table', '🗂 表格（A 型）'),
                  ('doc', '📄 文档（B 型）'), ('html', '🌐 独立页')]
        show_all = getattr(args, 'all', False)
        indep = [d for d in demos if not d.get('referenced')]
        total = len(demos) if show_all else len(indep)
        hidden = len(demos) - len(indep)
        print(f"共 {total} 个 demo（按模板分组{'；--all 查看引用子页 ' + str(hidden) + ' 个' if hidden else ''}）")
        for key, label in groups:
            items = [d for d in (demos if show_all else indep) if d['type'] == key]
            if not items:
                continue
            print(f"\n  {label}（{len(items)}）")
            for d in sorted(items, key=lambda x: (not x.get('featured'), x['entry'])):
                star = '★' if d.get('featured') else ' '
                stale = ' ⚠️过期' if d.get('stale') else ''
                tag = f"  → {d['entry'].split('/')[0]}" if d.get('referenced') else ''
                print(f"    {star}{d['name']:40s} {d['entry']}{stale}{tag}")
        return

    hit = next((d for d in demos if d['name'] == args.name), None)
    if not hit:
        if args.json:
            print(_json.dumps({'status': 'error', 'data': None,
                               'error': f"demo '{args.name}' 不存在"}, ensure_ascii=False))
        else:
            print(f"❌ demo '{args.name}' 不存在（html-gen demo list 查看）", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(_json.dumps({'status': 'ok', 'data': hit, 'error': ''},
                          ensure_ascii=False))
        return

    print(f"📌 {hit['title']}  [{hit['type']}]" + (' ★精选' if hit.get('featured') else ''))
    print(f"   entry: demos/{hit['entry']}")
    # 关联文件：同名 md/json（demos 内）+ data/ 下同名 json
    src = DEMOS_DIR / hit['entry']
    related = []
    if src.exists():
        for ext in ('.md', '.json'):
            f = src.with_suffix(ext)
            if f.exists():
                related.append(f.relative_to(DEMOS_DIR.parent).as_posix())
        data_f = Path(__file__).resolve().parent / 'data' / (src.stem + '.json')
        if data_f.exists():
            related.append(data_f.relative_to(Path(__file__).resolve().parent).as_posix())
        for prefix in ('_drama-table-', '_drama-kb-', '_countries-', '_chaitin-'):
            df2 = Path(__file__).resolve().parent / 'data' / (prefix + src.stem + '.json')
            if df2.exists():
                related.append(df2.relative_to(Path(__file__).resolve().parent).as_posix())
        # 同目录同名但不同子目录（如 drama/history-overview.html ← demos/drama/history-overview.md）
        if src.parent.name != 'demos':
            parent_md = DEMOS_DIR / src.parent.name / (src.stem + '.md')
            if parent_md.exists():
                related.append(parent_md.relative_to(DEMOS_DIR.parent).as_posix())
    if related:
        print('   源文件:')
        for r in sorted(set(related)):
            print(f"     {r}")
    url = f'http://localhost:8081/demos/{hit["entry"]}'
    print(f"   预览: {url}")
    if args.open:
        try:
            _ur.urlopen(url, timeout=2)
            import subprocess as _sp
            _sp.run(['open', url])
            print('   已在浏览器打开')
        except Exception:
            print('   服务未就绪，请先启动: hs <html-gen/demos> --url', file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
