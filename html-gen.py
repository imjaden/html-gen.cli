#!/usr/bin/env python3
"""
html-gen — HTML 模板 CLI 生成器
Layer 3: 将 JSON/Markdown 注入模板，输出单文件 HTML

用法:
  html-gen doc --input report.md --output report.html [--title "xxx"]
  html-gen slide --input report.md --output report.html [--title "xxx"]
  html-gen table --data data.json [--title "xxx"] [--output index.html]
  html-gen knowledge --data data.json [--groups groups.json] --title "xxx" [--output kb.html]

版本: 3.1(2026-07-23)
"""
import json, re, sys, os, argparse
from pathlib import Path

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
                    html.append(f'<pre><code class="language-{lang}">{content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</code></pre>')
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

        if line.startswith('### '):
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
                ct_map = {'注意':'note','Note':'note','提示':'tip','Tip':'tip','警告':'warning','Warning':'warning','Caution':'caution','危险':'danger','Danger':'danger'}
                cls = 'callout ' + ct_map.get(cm.group(1), 'note')
                label = cm.group(1).rstrip(':')
                html.append(f'<blockquote class="{cls}"><strong>{label}:</strong>{inline_format(_md_escape(cm.group(2)))}</blockquote>')
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
    meta = (f"路径: <code>{rel}</code><br>"
            f"创建: {ct} · 编辑: {et}<br>"
            f"字数: {wc:,} · 阅读约 {rt} 分钟")

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
    print(f"✅ 已生成: {out}")


def cmd_slide(args):
    """Markdown → slide 幻灯片（h2 分页）"""
    from datetime import datetime
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
    meta = (f"路径: <code>{rel}</code><br>"
            f"创建: {ct} · 编辑: {et}<br>"
            f"字数: {wc:,} · 阅读约 {rt} 分钟")

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
    print(f"✅ 已生成: {out}")


def cmd_table(args):
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
    else:
        # Structured object: {columns?, data?, rows?, tabs?, options?}
        data = raw.get('data') or raw.get('rows') or []
        if 'columns' in raw:
            columns = raw['columns']
        else:
            columns = [{'key': k, 'label': k, 'sortable': True} for k in (data[0] if data else {}).keys()]
        tabs = raw.get('tabs', [])
        options = raw.get('options', {})

    tmpl = inline_style(read_template(TEMPLATE_TABLE))
    result = inject(tmpl, title=args.title or '数据表格',
                    columns=json.dumps(columns, ensure_ascii=False),
                    data=json.dumps(data, ensure_ascii=False),
                    tabs=json.dumps(tabs, ensure_ascii=False),
                    options=json.dumps(options, ensure_ascii=False),
                    filters='', search_placeholder='搜索...')
    out = args.output or 'index.html'
    Path(out).write_text(result, encoding='utf-8')
    print(f"✅ 已生成: {out}")


def cmd_knowledge(args):
    """从 JSON 数据生成 C 型知识库 HTML（顶部类目 + 左侧章节）"""
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
    print(f"✅ 已生成: {out}")


# ═══ Help System ═══

HELP_OVERVIEW = """\
html-gen — HTML 模板 CLI 生成器 v3.0

四型模板:
  doc       Markdown → B 型文档 (侧边栏 TOC + 阅读)
  slide     Markdown → D 型幻灯片 (h2 分页 + 键盘翻页)
  table     JSON     → A 型数据表格 (搜索/排序/分页)
  knowledge JSON     → C 型知识库 (标签栏 + 章节)

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

HELP_MAP = {
    'doc': HELP_DOC,
    'slide': HELP_SLIDE,
    'table': HELP_TABLE,
    'knowledge': HELP_KNOWLEDGE,
}


def cmd_help(args):
    if args.topic and args.topic in HELP_MAP:
        print(HELP_MAP[args.topic])
    else:
        print(HELP_OVERVIEW)


# ═══ CLI ═══
def main():
    p = argparse.ArgumentParser(description='HTML 模板生成器')
    sub = p.add_subparsers(dest='command', required=True)

    h = sub.add_parser('help', help='显示帮助')
    h.add_argument('topic', nargs='?', choices=['doc', 'slide', 'table', 'knowledge'],
                   help='帮助主题 (doc/slide/table/knowledge)')

    d = sub.add_parser('doc', help='Markdown → B 型文档')
    d.add_argument('-i', '--input', required=True)
    d.add_argument('-o', '--output')
    d.add_argument('--title')
    d.add_argument('--subtitle')
    d.add_argument('--metadata')

    s = sub.add_parser('slide', help='Markdown → 幻灯片')
    s.add_argument('-i', '--input', required=True)
    s.add_argument('-o', '--output')
    s.add_argument('--title')
    s.add_argument('--subtitle')

    t = sub.add_parser('table', help='JSON → A 型数据表格')
    t.add_argument('-d', '--data', required=True)
    t.add_argument('--title', default='数据表格')
    t.add_argument('-o', '--output', default='index.html')

    k = sub.add_parser('knowledge', help='JSON → C 型知识库')
    k.add_argument('-d', '--data', required=True)
    k.add_argument('-g', '--groups')
    k.add_argument('--title', default='知识库')
    k.add_argument('--subtitle', default='')
    k.add_argument('--welcome', default='')
    k.add_argument('-o', '--output', default='kb.html')

    args = p.parse_args()
    {'help': cmd_help, 'doc': cmd_doc, 'slide': cmd_slide,
     'table': cmd_table, 'knowledge': cmd_knowledge}[args.command](args)


if __name__ == '__main__':
    main()
