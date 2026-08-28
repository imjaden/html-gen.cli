#!/usr/bin/env python3
"""
html-gen — HTML 模板 CLI 生成器
Layer 3: 将 JSON/Markdown 注入模板，输出单文件 HTML

用法:
  html-gen doc --input report.md --output report.html [--title "xxx"]
  html-gen slide --input report.md --output report.html [--title "xxx"]
  html-gen table --data data.json [--title "xxx"] [--output index.html]
  html-gen knowledge --data data.json [--groups groups.json] --title "xxx" [--output kb.html]

版本: 3.2(2026-08-28)
"""
import html, json, re, sys, os, time, argparse, types
from pathlib import Path

__version__ = "3.2"              # CL016: 版本号 (格式 \d+\.\d+)
__release_date__ = "2026-08-28"  # CL016: 发版日期 (格式 YYYY-MM-DD, 与版本同步)

SKILLS_DIR = Path(__file__).resolve().parent
TEMPLATE_DOC   = SKILLS_DIR / 'layout-doc.html'
TEMPLATE_SLIDE = SKILLS_DIR / 'layout-slide.html'
TEMPLATE_TABLE = SKILLS_DIR / 'layout-table.html'
TEMPLATE_KNOWLEDGE = SKILLS_DIR / 'layout-knowledge.html'
STYLE_GUIDE    = SKILLS_DIR / 'style-guide.css'


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
    result = inject(tmpl, title=title, subtitle=args.subtitle or '', metadata=meta, content=content)
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
    result = inject(tmpl, title=title, subtitle=args.subtitle or '', metadata=meta, content=content,
                    cover=h1_html, h2_count=str(h2_count), perf_warning=perf_warning)
    out = args.output or md.with_suffix('.slide.html')
    Path(out).write_text(result, encoding='utf-8')
    if not getattr(args, 'quiet', False):
        pages = h2_count + (1 if h1_html else 0)
        print_summary(out, args.input, stat.st_size, Path(out).stat().st_size,
                      time.perf_counter() - t0, [f"🖥 页面: {pages} 页"])
    else:
        print(f"✅ 已生成: {out}")


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
    else:
        # Structured object: {columns?, data?, rows?, tabs?, options?, title?, subtitle?}
        data = raw.get('data') or raw.get('rows') or []
        if 'columns' in raw:
            columns = raw['columns']
        else:
            columns = [{'key': k, 'label': k, 'sortable': True} for k in (data[0] if data else {}).keys()]
        tabs = raw.get('tabs', [])
        options = raw.get('options', {})
        json_title = raw.get('title')
        json_subtitle = raw.get('subtitle')

    # title/subtitle 优先级: CLI 显式入参 > JSON 顶层字段 > 默认值
    title = args.title if args.title is not None else (json_title or '数据表格')
    if args.subtitle is not None:
        subtitle = args.subtitle  # 显式传入（含空串）→ 覆盖 JSON
    else:
        subtitle = json_subtitle or ''
    # 段落描述: 纯文本安全转义, \n → <br> 换行
    description = html.escape(subtitle, quote=False).replace('\n', '<br>')

    tmpl = inline_style(read_template(TEMPLATE_TABLE))
    result = inject(tmpl, title=title, description=description,
                    columns=json.dumps(columns, ensure_ascii=False),
                    data=json.dumps(data, ensure_ascii=False),
                    tabs=json.dumps(tabs, ensure_ascii=False),
                    options=json.dumps(options, ensure_ascii=False),
                    filters='', search_placeholder='搜索...')
    out = args.output or 'index.html'
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
    tmpl = inline_style(read_template(TEMPLATE_KNOWLEDGE))
    result = inject(tmpl, title=args.title or '知识库',
                    subtitle=args.subtitle or '',
                    welcome_text=args.welcome or '从上方类目选择，浏览整理的知识内容。',
                    groups=json.dumps(groups, ensure_ascii=False),
                    items=json.dumps(items, ensure_ascii=False))
    out = args.output or 'kb.html'
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


# ═══ Help System ═══

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
  html-gen help doc        Markdown 语法规范 (B/D 型)
  html-gen help table      JSON 数据格式 (A 型)
  html-gen help knowledge  JSON 数据格式 (C 型)
  html-gen help slide      slide 特有功能说明
  html-gen help prompt     prompt 指令说明
  html-gen help demo       demo 指令与 demo 规范

零外部依赖，输出自包含单文件 HTML。"""

HELP_DOC = """\
B/D 型 · Markdown 语法规范
━━━━━━━━━━━━━━━━━━━━━━━━

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

HELP_TABLE = """\
A 型 · 数据表格 JSON 格式 (Cinema 纪律化宽度模型)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

简单格式 (JSON 数组):
  [{"名称": "A", "数量": 10}, {"名称": "B", "数量": 20}]

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
  "options": {
    "pageSize": 30, "exportCSV": true, "rowSelect": true,
    "clickModes": ["tab", "modal", "split", "expand"],
    "columnResize": false,       // 禁用列宽拖拽
    "columnsSplit": ["name", "actions"],  // 分栏专用列集
    "modalRenderer": "skills"   // 自定义模态框渲染器
  }
}

列类型:
  string(默认) / number(数值排序) / actions(操作按钮) / pills(标签样式)

列属性:
  width:     列宽 (Cinema 模型下必设, 默认 120px, actions 100px)
  sortable:  是否可排序 / locale: 排序语言(zh)
  freeze:    列冻结 (sticky, left 偏移基于 col.width 动态计算)
  stickyRight: 右侧固定列 (水平滚动时粘在视口右侧)
  preview:   分栏模式可见 / hide: 列隐藏
  quickFilter: false 禁用点击筛选
  onCellClick: "split" 单元格点击直接打开分栏
  onClick:   "url" 行点击跳转
  escape:    HTML转义 / render: 自定义渲染 / class: CSS类

Tab 属性:
  field: 匹配字段 / match: 精确匹配字段 / contains: 逗号分隔包含匹配

选项:
  pageSize:      分页大小(默认30) / exportCSV: 导出按钮
  rowSelect:     行选择复选框 / search: 搜索框显隐(默认true)
  clickModes:    允许的点击模式 ["tab","modal","split","expand"]
  columnResize:  列宽拖拽 (默认true, false时隐藏 resize handle)
  columnsSplit:  分栏模式专用列集 (如 ["name","actions"])
  modalRenderer: 自定义模态框渲染器 (如 "skills" 结构化详情)

点击模式:
  tab      — 🔗 新标签页打开 (window.open, noopener)
  modal    — 📋 居中弹出面板 (键值列表/Esc关闭/自定义渲染器)
  split    — 📑 分栏预览 (表格+详情, 拖拽分栏线, ▦ 比例预设, ▲▼ 导航)
  expand   — 📂 行内手风琴展开 (网格布局)"""

HELP_KNOWLEDGE = """\
C 型 · 知识库 JSON 格式
━━━━━━━━━━━━━━━━━━━━

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

类目分组 (可选, 不提供时从 group 自动推导):
[
  {"key": "类目", "label": "🤖 显示名", "icon": "🤖"}
]"""

HELP_SLIDE = """\
D 型 · 幻灯片功能说明
━━━━━━━━━━━━━━━━━━━

分页: 每个 ## h2 为一页, h1 为封面页
导航: ← → Space Home End 翻页
全屏: F 键
进度: 底部圆点 (已读/当前/未读)
记忆: localStorage 恢复上次阅读位置
侧栏: H3 子标题默认隐藏, 点击 H3 开关显示
性能: >50 h2 时显示加载警告

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

说明:
  skills/ 每子目录一个 skill (含 SKILL.md), 支持 references/*.md 拼接。"""

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

HELP_MAP = {
    'doc': HELP_DOC,
    'slide': HELP_SLIDE,
    'table': HELP_TABLE,
    'knowledge': HELP_KNOWLEDGE,
    'prompt': HELP_PROMPT,
    'demo': HELP_DEMO,
}


def cmd_help(args):
    if args.topic and args.topic in HELP_MAP:
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

    s = sub.add_parser('slide', help='Markdown → 幻灯片')
    s.add_argument('--quiet', action='store_true', default=argparse.SUPPRESS, help='仅打印生成路径，抑制统计信息')
    s.add_argument('-i', '--input', required=True)
    s.add_argument('-o', '--output')
    s.add_argument('--title')
    s.add_argument('--subtitle')

    t = sub.add_parser('table', help='JSON → A 型数据表格')
    t.add_argument('--quiet', action='store_true', default=argparse.SUPPRESS, help='仅打印生成路径，抑制统计信息')
    t.add_argument('-d', '--data', required=True)
    t.add_argument('--title')  # 优先级: CLI > JSON 顶层 title > '数据表格'
    t.add_argument('--subtitle', help='页面级段落描述(纯文本, \\n 换行); JSON 顶层 subtitle 兜底, 显式传空串清空')
    t.add_argument('-o', '--output', default='index.html')

    k = sub.add_parser('knowledge', help='JSON → C 型知识库')
    k.add_argument('--quiet', action='store_true', default=argparse.SUPPRESS, help='仅打印生成路径，抑制统计信息')
    k.add_argument('-d', '--data', required=True)
    k.add_argument('-g', '--groups')
    k.add_argument('--title', default='知识库')
    k.add_argument('--subtitle', default='')
    k.add_argument('--welcome', default='')
    k.add_argument('-o', '--output', default='kb.html')

    pr = sub.add_parser('prompt', help='输出项目 skills (html-gen prompt <skill>)')
    pr.add_argument('skill', nargs='?', help='skill 名称 (可选)')
    pr.add_argument('--brief', action='store_true', help='仅输出摘要')
    pr.add_argument('--json', action='store_true', help='JSON 输出 (checkpoint 信封 {status,data,error})')

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
    import subprocess as _sp
    import json as _json
    SKILLS_DIR = Path(__file__).resolve().parent / 'skills'
    if not SKILLS_DIR.is_dir():
        print("❌ skills/ 目录不存在", file=sys.stderr); sys.exit(1)

    def _skill_desc(skill_path):
        try:
            with open(skill_path) as _f:
                for _line in _f:
                    if _line.startswith('description:'):
                        return _line.split(':', 1)[1].strip()
        except Exception:
            pass
        return ''

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
            {'key': '文档链接', 'label': '文档链接', 'sortable': True, 'locale': 'zh', 'width': '260px', 'preview': True},
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
