# html-gen 文档模板修正 — 设计文档

## 版本

v1.0 (2026-08-06)

## 背景与问题来源

personal-cinema 项目实践(html-gen-docs skill 生成 `cache/html-gen/docs/male-sexual-energy-management-report-v1.0-20260805.html`)反馈三个问题:

1. **P1 — B 型文档侧边栏随滚动条滑动**: 左侧目录栏(`aside#sidebar`)未固定,页面滚动到底时左侧目录不可见。
2. **P2 — 原因归属判定**: 需确认是 html-gen 项目源码问题、html-gen-docs 规范问题、还是 personal-cinema 实践问题。
3. **P3 — frontmatter 未剥离**: 生成 doc 时 markdown 顶部 YAML frontmatter 被当正文渲染,`title` 泄漏为段落,页面出现 3 次标题。

经分析(结论见下),全部指向 html-gen 项目源码。待确认清单问答(用户回复 1A 2A 3A 4A 5A 6A 7A 8A)定稿。

## 问题分析结论

### P1 — 侧边栏滚动:源码 CSS 覆盖 bug

**根因**: `layout-doc.html` 中 `.doc-sidebar` 被定义两次:
```css
/* L13-19 首次定义 */
.doc-sidebar {
  ...
  position: sticky; top: 0; height: 100vh;
  overflow-y: auto;
  ...
}
/* L21 二次定义 —— 覆盖 sticky */
.doc-sidebar { position: relative; }
```
commit `91626d9`(Phase 4 — sidebar width drag resize)为让 resize handle(`position: absolute`)有定位父级,追加了 `position: relative` 覆盖行。**但 `position: sticky` 元素本身即是 positioned(absolute 子元素同样以其为定位上下文),该覆盖行多余且破坏 sticky 行为。**

**同源 bug**: `layout-slide.html` L35 `.slide-sidebar { position: relative; }` 覆盖 L16 的 `position: sticky; top: 0; height: 100vh;`。

**排除**: `layout-knowledge.html` 的 `.kw-sidebar` 无 sticky 定义(仅 overflow-y:auto),C 型知识库不涉及此问题。

**结论归属**: html-gen 项目源码问题(layout-doc.html / layout-slide.html)。html-gen-docs 规范(调用 `html-gen doc -i --title`)参数正确;personal-cinema 实践无误。

### P3 — frontmatter 泄漏:cmd_doc 未处理 YAML 头

**根因**: `cmd_doc()` 将 md 全文直接交给 `md_to_html()`,对开头 `---` 块无识别:
- `title: 男性性能量管理…` → 渲染为 `<p>title: 男性性能量管理…</p>`(泄漏)
- `---` → 渲染为 `<hr>`(doc-body 顶部出现多余横线)
- 标题 3 次: 侧边栏 sidebar-title + doc-header `<h1>`(均来自 `--title`,即 html-gen-docs 传入的 frontmatter title)+ 正文 `<h1>`(md 正文首个 `#`)

**连带**: 因 frontmatter 泄漏产生的 `<hr>` 在正文最前,`cmd_doc`/`cmd_slide` 的 h1 提取逻辑(`if content.startswith('<h1')`)失效,正文首个 `<h1>` 未被剥除,与 doc-header 标题重复显示。

**结论归属**: html-gen 项目源码问题(html-gen.py cmd_doc/cmd_slide)。

## 设计决策 (D)

### D1 — 删除 sticky 覆盖行,恢复固定侧边栏 (1A)

**改动文件**: `layout-doc.html`、`layout-slide.html`

删除以下覆盖行:
```css
/* layout-doc.html L21 */
.doc-sidebar { position: relative; }
/* layout-slide.html L35 */
.slide-sidebar { position: relative; }
```

**理由**: sticky 元素本身是 positioned,resize handle 的 `position: absolute; right: -4px; top: 0; bottom: 0` 仍相对 sidebar 定位,拖拽功能不受影响。删除后 `position: sticky; top: 0; height: 100vh` 生效,侧边栏随页面滚动固定。

**验证方式**: 生成含长内容的 doc/slide HTML,浏览器滚动检查 sidebar 保持视口内。

### D2 — cmd_doc/cmd_slide frontmatter 自动剥离 (3A)

**改动文件**: `html-gen.py`

新增函数:
```python
def strip_frontmatter(text):
    """剥离 markdown 顶部 YAML frontmatter（--- 开头 --- 结束）。"""
    if text.startswith('---'):
        m = re.match(r'^---\n.*?\n---\n?', text, re.DOTALL)
        if m:
            return text[m.end():], m.group(0)
    return text, ''
```

在 `cmd_doc` / `cmd_slide` 中,`md_to_html(text)` 前调用:
```python
text, _fm = strip_frontmatter(text)
```

**规则**:
- 仅剥离**文件开头**的 `---` 块(零配置自动)
- 无 frontmatter 的文件不受影响(向后兼容)
- 剥离后正文首个 `<h1>` 提取逻辑恢复生效(见 D3)
- 字数统计 `wc` 基于剥离后 text(更准确);meta 路径/时间不变

### D3 — h1 提取逻辑生效,正文标题去重 (4A)

frontmatter 剥离后,`content.startswith('<h1')` 恢复匹配,cmd_doc/cmd_slide 现有提取逻辑将正文首个 h1 剥除:

- **doc**: 标题显示为 侧边栏 sidebar-title + doc-header h1(2 处),正文不再重复 h1
- **slide**: 正文 h1 提取为封面 `cover=h1_html`(原有设计),行为不变

**无需新增代码** — 仅 D2 剥离使既有逻辑恢复工作。

### D4 — extract_title 优先 frontmatter title (5A)

**改动**: `extract_title()` 或调用处

当前 `extract_title` 只匹配正文 `# `。改为优先读 frontmatter `title:` 字段:
```python
def extract_title(md_text):
    m = re.search(r'^title:\s*(.+)$', md_text, re.MULTILINE)
    return m.group(1).strip() if m else ''
```
(frontmatter 已剥离的 text 不含 title 行,故需在剥离**前**调用,或直接读 `_fm`)

**调用顺序调整**:
```python
text = md.read_text(encoding='utf-8')
text, fm = strip_frontmatter(text)
fm_title = re.search(r'^title:\s*(.+)$', fm, re.MULTILINE)
title = args.title or (fm_title.group(1).strip() if fm_title else '') or extract_title(text) or md.stem
```

与 html-gen-docs 的 `--title` 传参一致(frontmatter title),无冲突。

### D5 — 回归测试 (6A)

**改动文件**: `tests/test_templates.py`(扩展)

新增测试:
1. **test_doc_frontmatter_stripped**: 构造含 frontmatter 的 md → `run_gen('doc', ...)` → 断言:
   - HTML 不含 `<p>title:`(无泄漏)
   - 正文 doc-body 内 h1 唯一(不与 doc-header 重复;剥离后 doc-body 内 `<h1` 计数为 0)
   - `<title>` / sidebar-title 来自 frontmatter title
2. **test_slide_frontmatter_stripped**: slide 模式同样断言无泄漏、封面 h1 正常
3. **test_doc_no_frontmatter_regression**: 无 frontmatter 的 md 生成行为不变(标题/正文完整)

**sidebar sticky 测试**: CSS 静态断言(生成 HTML 中 `.doc-sidebar` 后定义处不再有 `position: relative`;或 Selenium 验证 offsetTop 滚动后不变)。倾向 Selenium:生成长文档,`window.scrollTo(0, document.body.scrollHeight)`,断言 `#sidebar.getBoundingClientRect().top === 0`。

### D6 — 文档同步 (7A)

**改动文件**:
- `skills/html-gen/SKILL.md`: doc 命令说明补充 "自动剥离 YAML frontmatter" 一句话 + 版本 bump(当前 2.2.0 → 2.3.0,附变更记录)
- `features.md`: CLI doc/slide 行补 frontmatter 剥离;模板功能补 sidebar sticky 修复
- `AGENTS.md`(如触及 Markdown 转换规则处):frontmatter 剥离说明

### D7 — html-gen-docs 侧 (8A)

**结论**: generate.py **无需改**(已传 `--title`,frontmatter 剥离由 html-gen 自动完成)。`script-miner/skills/html-gen-docs/SKILL.md` 变更记录补一行:"html-gen 现自动剥离 frontmatter,单文档 HTML 不再泄漏 YAML 头"。

## 影响范围

| 类型 | 文件 | 改动 |
|:---|:---|:---|
| 直接功能 | `html-gen.py` | strip_frontmatter() + cmd_doc/cmd_slide 调用 + extract_title 顺序 |
| 直接功能 | `layout-doc.html` | 删除 `.doc-sidebar { position: relative; }` 覆盖行 |
| 直接功能 | `layout-slide.html` | 删除 `.slide-sidebar { position: relative; }` 覆盖行 |
| 说明性指令 | `skills/html-gen/SKILL.md` | frontmatter 剥离说明 + bump 2.3.0 |
| 说明性文档 | `features.md` | CLI/模板功能补 frontmatter 剥离 + sidebar sticky |
| 测试用例 | `tests/test_templates.py` | 新增 frontmatter 剥离测试(≥3)+ sidebar sticky 测试 |
| 外部说明 | `script-miner/skills/html-gen-docs/SKILL.md` | 变更记录补一行(可选,非 html-gen 仓库) |
| 无改动 | `layout-knowledge.html` | C 型无 sticky 定义,不涉及 |

## 修改步骤

1. dev 实施 `html-gen.py`: strip_frontmatter + cmd_doc/cmd_slide 接线 + extract_title 顺序
2. dev 实施 `layout-doc.html` / `layout-slide.html`: 删除覆盖行
3. dev 实施 `tests/test_templates.py`: 新增回归测试
4. 运行全部测试(当前 57 → 预期 60+ 全绿)
5. 手动验证: 重新生成该报告 HTML,浏览器确认侧边栏固定、标题 2 处、无 frontmatter 泄漏
6. dev 实施文档同步(SKILL.md / features.md)
7. ops 核查(对照 TC/SC)
8. review 审计后 push

## 验收清单 (TC)

- TC1: 生成 doc,页面滚动到底侧边栏保持视口内(`#sidebar` top 恒为 0)
- TC2: 生成 slide 同理(sticky 恢复)
- TC3: 含 frontmatter md → HTML 无 `<p>title:` 泄漏、无多余 `<hr>` 开头
- TC4: doc-body 内 `<h1` 计数为 0(正文标题不重复)
- TC5: frontmatter title 生效(侧边栏 + doc-header 显示正确标题)
- TC6: 无 frontmatter 文件生成行为不变(回归)
- TC7: resize 拖拽仍可用(sticky 不影响 absolute handle)
- TC8: 测试全绿(57 → 60+,无回归)
- TC9: SKILL.md/features.md 同步,bump 版本正确

## 自检清单 (SC)

- SC1: strip_frontmatter 仅匹配文件开头,不误伤正文 `---` 分隔线
- SC2: 剥离后 h1 提取在 doc(剥除)与 slide(封面)行为均正确
- SC3: extract_title 优先级: --title > frontmatter title > 正文 h1 > stem
- SC4: 删除覆盖行后 resize handle 仍正确吸附(absolute 相对 sticky 父级)
- SC5: 文档与实现一致(不写无实现的功能)
