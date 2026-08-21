# doc meta 显示 md 文件路径（show-md 入参 + 脱敏）— 设计文档

## 版本

v1.0 (2026-08-19)

## 背景与问题来源

用户在 `demos/drama/history-overview.html`（B 型文档）中观察到：文档头部 meta 区（创建/编辑/字数/阅读时间）不展示 markdown 源文件路径。

**现状分析**：
- `cmd_doc`（html-gen.py L241-250）已计算 `rel` 变量（`~/` 相对主目录的完整路径），但组装 meta 字符串时**丢弃**了它——只输出 `创建/编辑/字数/阅读约`
- 模板 JS（layout-doc.html L306-311）仍保留 `metaEl.textContent.match(/路径:\s*(.+)/)` 逻辑（侧边栏标题点击复制路径的 fallback），说明模板预期 meta 含"路径:"行，但生成端已不再输出
- 历史原因：B 型 guide 曾有过路径行，v2.1 修订时"meta 去路径行"主动移除（隐私/整洁考虑）

需求：
1. meta 区展示 markdown 源文件路径
2. 默认不展示（隐私保障）
3. URL 入参控制展示：`?show-md=1` 显示
4. 路径脱敏：只显示文件名（basename），不显示完整路径

待确认清单（用户回复）定稿：

| 项 | 确认 |
|:--|:--|
| 1 方案 | A=meta 输出路径行 + 运行时 URL 入参显隐 |
| 2 参数名 | `show-md=1` 显示；缺省隐藏 |
| 3 脱敏 | 只显示文件名（basename），不显示完整路径 |
| 4 默认 | 不展示（隐私） |

## 目标形态

**现状**：
- meta 仅 `创建: xxx · 编辑: xxx<br>字数: N · 阅读约 M 分钟`
- 无路径信息；标题点击复制 fallback 到 URL

**目标**：
- meta 增加路径行：`路径: <code>history-overview.md</code>`（仅文件名）
- 默认 CSS 隐藏（`.meta-path { display: none }`）
- `?show-md=1` 时显示路径行
- 标题点击复制行为恢复为复制脱敏路径（或保留原逻辑，按实现细节定）

## 实现方案

### 1. html-gen.py :: cmd_doc / cmd_slide（meta 组装，L249-250 / L308-309）

```python
import os
md_name = os.path.basename(str(md))          # 脱敏: 仅文件名
meta = (f"创建: {ct} · 编辑: {et}<br>"
        f"字数: {wc:,} · 阅读约 {rt} 分钟"
        f"<span class=\"meta-path\"> · 路径: <code>{md_name}</code></span>")
```

- 路径行包在 `<span class="meta-path">` 内（供 CSS/JS 显隐控制）
- 脱敏: `os.path.basename()` 只取文件名，不含目录
- 两处（doc + slide）同步修改

### 2. layout-doc.html CSS（L80 后追加）

```css
/* ── md 路径行: 默认隐藏, ?show-md=1 显示 (隐私) ── */
.meta-path { display: none; }
body.show-md .meta-path { display: inline; }
```

### 3. layout-doc.html JS（L269 width 处理后追加）

```js
// ── md 路径: ?show-md=1 显示 (默认隐藏, 隐私) ──
if (params.get('show-md') === '1') document.body.classList.add('show-md');
```

与 sidebar/toolbar/width 同一解析处，body class 驱动 CSS。

### 4. 标题点击复制逻辑（L306-311）确认

现状：`match(/路径:\s*(.+)/)` → 找到则复制路径，否则 fallback URL。
路径行恢复后此逻辑自动命中，复制的是脱敏文件名（`history-overview.md`）。
- 决策：保持模板逻辑不变（复制脱敏文件名合理）；若希望复制完整路径需另议（违背脱敏意图，不采用）

### 5. layout-slide.html

- slide 模板无 URL 参数解析机制（grep 确认无 URLSearchParams）
- 决策：slide 同步 meta 输出（生成端统一），但不做 show-md 运行时显隐（slide 无此机制，保持默认隐藏即可；如需支持可后续扩展）

### 6. 重新生成产物

- 重新生成 demos/ 下 B 型文档（history-overview.html 等）使 meta 含路径行
- slide demo 同理

## 测试

### 回归测试（tests/test_templates.py 或 test_doc_md_path.py）

- test_doc_meta_has_path: 生成 doc 的 meta 含 `路径:` 且为文件名（不含 `/`）
- test_doc_meta_path_hidden_by_default: meta-path span 存在但默认 CSS display:none（无 show-md 时）
- test_slide_meta_has_path: slide meta 同样含脱敏路径

### Selenium

- test_doc_show_md_param: ?show-md=1 → .meta-path 计算样式 display:inline
- test_doc_no_param_hidden: 无参数 → .meta-path display:none
- test_doc_title_click_copy_path: 点击侧边栏标题复制的是文件名（非 URL）
- 0 JS errors

## 影响范围

| 文件 | 改动 |
|:--|:--|
| html-gen.py | cmd_doc + cmd_slide meta 加脱敏路径行（各 2-3 行） |
| layout-doc.html | CSS 2 条 + JS 3 行（show-md body class） |
| demos/*.html | 重新生成 B 型文档 |
| features.md | B 型 URL 入参节补 show-md |
| AGENTS.md | 可选：B 型功能清单补充 |

## 风险

- 低：纯增量，默认行为不变（路径行默认隐藏）
- 隐私：HTML 源码仍含文件名（非完整路径）——脱敏后不泄露目录结构；完整路径不出现在产物中
- 标题点击复制行为变化：从复制 URL fallback 变为复制脱敏文件名——需确认符合预期（用户已知悉，合理）
- 与知识库嵌入联动：layout-knowledge 的 iframe 不自动追加 show-md（默认隐私），用户手动 ?show-md=1 才显示

## 待确认

- slide 是否需要 show-md 运行时显隐（当前建议：生成端统一输出，slide 不做运行时控制）
- 测试文件命名：并入 test_templates.py vs 新建 test_doc_md_path.py
