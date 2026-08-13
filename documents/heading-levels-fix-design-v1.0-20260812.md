# h4-h6 标题渲染支持 — 功能修正方案

## 版本

v1.0 (2026-08-12)

## 背景与问题来源

`~/Downloads/MyVideos/cache/html-gen/docs/cult-analysis-report-v2.1-20260812.html`（B 型文档）中 `#### 6.1.5 关键寓意`、`##### 剧情 ↔ 历史对位表` 等标题未渲染为 HTML 标题，而是以 `<p>#### 6.1.5 关键寓意</p>` 普通段落形式泄漏。实测该文档共 13 处泄漏（9 个 h4 + 4 个 h5）。

**根因（模板侧）**：`html-gen.py::md_to_html()` L88-93 只识别 `# / ## / ###` 三级标题，h4/h5/h6 不匹配任何规则，落入 else 分支被当作普通文本包成 `<p>`。且 `layout-doc.html` CSS 仅定义 h2/h3 样式（L79-80），TOC 仅收集 h2/h3（L232 `querySelectorAll('h2, h3')`）。

**诱因（prompt 侧）**：生成报告时模型使用了 `####`/`#####` 表达深层级（6.1.x 小节），超出模板支持的语法子集。AGENTS.md 明确 Markdown 规则「h1–h3 标题」。

**结论**：模板能力限制为主责，生成 prompt 违反语法子集为次责。

## 决策

待确认清单（用户超时未回复，按探讨推荐方向 1C 推进）：

| 项 | 决策 |
|:--|:--|
| 1 修复范围 | C=模板加 h4-h6 渲染 + prompt 约束双管齐下 |
| 2 h4-h6 是否进 TOC | 否，TOC 保持 h2/h3（TOC 三层层级已够，避免过深） |
| 3 h4-h6 样式 | 独立 CSS 定义（h4 0.95rem / h5 0.88rem / h6 0.82rem），dark+light 双主题 |
| 4 锚点 | h4-h6 同样加 id + slug（复制链接功能顺带支持） |
| 5 prompt 约束 | 生成 prompt 优先 h1-h3，深层级可用 h4-h6；禁止 h7+ |
| 6 测试 | md_to_html 回归测试 + doc 模板 Selenium 检查渲染 |

## 目标形态

**现状**：h4/h5/h6 → `<p>#### xxx</p>`（泄漏为普通段落，无层级语义、无锚点、无样式）

**目标**：h4/h5/h6 → `<h4 id="...">` / `<h5 id="...">` / `<h6 id="...">`，带独立字号样式与锚点，不进 TOC

## 实现方案

### 1. html-gen.py :: md_to_html()（L88-93 扩展）

```python
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
```

注意顺序：`#` 开头的匹配必须从最长前缀（######）开始，否则 `####` 会被 `# ` 规则误吞（`startswith('# ')` 要求 `#` 后紧跟空格，`#### ` 第 2 字符是 `#` 不匹配 `# `，故现有顺序已安全；但按从长到短排列最稳妥）。

### 2. layout-doc.html CSS（L80 后追加）

```css
.doc-body h4 { font-size: 0.95rem; font-weight: 600; color: #c0c0c0; margin: 0.75rem 0 0.3rem; }
.doc-body h5 { font-size: 0.88rem; font-weight: 600; color: #b0b0b0; margin: 0.6rem 0 0.25rem; }
.doc-body h6 { font-size: 0.82rem; font-weight: 600; color: #a0a0a0; margin: 0.5rem 0 0.2rem; }
```

light 主题对应（L156 后追加）：
```css
::root.light .doc-body h4 { color: #444; }
::root.light .doc-body h5 { color: #555; }
::root.light .doc-body h6 { color: #666; }
```

锚点 hover（L110 扩展）：
```css
h4:hover .anchor-link, h5:hover .anchor-link, h6:hover .anchor-link { opacity: 1; }
```

### 3. layout-doc.html JS — 拆分 anchor 循环（review D-新增）

现状 L376-385 单一 forEach 同时做 anchor-link 追加 + TOC 链接生成，headings 仅 h2/h3，h4-h6 不会获得 ¶ 复制链接锚点。

修复（拆分循环，TOC 保持不变）：
```js
// 原有循环不动: headings (h2/h3) 追加 anchor + TOC 链接
// 新增独立循环: h4-h6 仅追加 anchor-link，不进 TOC
document.querySelectorAll('.doc-body h4, .doc-body h5, .doc-body h6').forEach(function(h) {
  if (!h.id) h.id = 'section-' + h.textContent;
  var anchor = document.createElement('a');
  anchor.className = 'anchor-link';
  anchor.href = '#' + h.id;
  anchor.textContent = '¶';
  h.appendChild(anchor);
});
```

### 3a. layout-slide.html 同步

slide 模板同样使用 md_to_html()，需同步 h4-h6 样式（slide-body 若存在）或确认现有样式覆盖。若 slide 无 h4+ 使用场景，仅保证渲染不泄漏即可（<h4> 标签落入默认样式）。

### 4. TOC 不收录 h4-h6（保持不变）

- L232 `querySelectorAll('h2, h3')` 不动
- 文档说明：TOC 仅 h2/h3

### 5. 生成 prompt 约束

- 文档生成 prompt 增加：支持 h1-h6 标题，**优先使用 h1-h3**（h3 为最深层常规层级），h4-h6 仅用于更细的小节编号，禁止 h7+（会泄漏）
- 迁移 prompt / 相关生成 prompt 同步（news-migration-prompt 等若涉及 doc 生成）

### 6. 测试

**回归测试**（tests/test_templates.py 或新增 test_heading_levels.py）：
- test_md_to_html_h4_h5_h6: md_to_html 输出包含 `<h4 id="...">`、`<h5 id="...">`、`<h6 id="...">`
- test_md_to_html_no_leak: `#### xxx` 不再产生 `<p>####`
- test_slug_anchor: h4 标题 id 与 slug() 一致

**Selenium**（复用 test_doc_sidebar.py 模式或新增）：
- test_doc_h4_h5_render: 生成含 h4/h5 的 doc，检查 DOM 中 h4/h5 存在且 textContent 正确，0 JS errors
- test_doc_toc_excludes_h4: TOC 链接数不含 h4（保证不进 TOC）
- test_doc_h4_anchor_link: h4 元素包含 .anchor-link 子元素（D-新增拆分循环生效），且 TOC 仍仅 h2/h3

### 7. 文档同步

- AGENTS.md「Markdown → HTML 转换规则」：h1–h3 → h1–h6
- features.md：doc 模板标题渲染条目更新（若存在）

## 验证方式

1. `pytest tests/ -q` 全量回归（当前 73 tests → 预期 +2~3）
2. 用含 h4/h5 的样例 md 生成 doc，检查 html 无 `<p>####` 泄漏
3. 重新生成（或局部验证）cult-analysis-report 风格文档确认修复效果
4. 打开生成的 html 确认 h4/h5 样式与锚点正常，0 JS errors

## 影响范围

| 文件 | 改动 |
|:--|:--|
| html-gen.py | md_to_html L88-93 加 3 分支 |
| layout-doc.html | CSS h4/h5/h6 样式 + light 主题 + 锚点 hover；JS 拆分 anchor 循环（D-新增） |
| layout-slide.html | 同步样式（若适用） |
| tests/ | 新增回归 + Selenium 测试（含 anchor-link） |
| AGENTS.md | 标题规则 h1-h6 |
| features.md | 标题渲染条目（若存在） |

## 风险

- 低：h4-h6 渲染为纯增量，不影响现有 h1-h3 路径
- TOC 不含 h4 是有意决策（避免三层以上导航），文档需明确
- 若生成 prompt 仍用 h7+，会继续泄漏（prompt 约束覆盖）
