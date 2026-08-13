# h4-h6 标题渲染支持 — Review 报告

## 版本

v1.0 (2026-08-12)

## 审查对象

- documents/heading-levels-fix-design-v1.0-20260812.md (commit 19ee648)

## 结论

**CONDITIONAL PASS** — 核心修复（h4-h6 渲染为 `<h4>/<h5>/<h6>` + id + 样式）方案正确。1 处遗漏需在 D 待办清单补充。

## 检查项结果

| 检查项 | 结果 |
|:--|:--|
| H1 方案完整性 | ✅ 通过 |
| H2 模板实现正确性 | ✅ 通过 |
| H3 样式一致性 | ⚠️ 见遗漏风险点 |
| H4 TOC 决策 | ✅ 通过 |
| H5 测试设计 | ✅ 通过 |
| H6 文档同步 | ✅ 通过 |
| H7 风险 | ✅ 通过 |

## 🔴 遗漏风险点 (1 处)

### anchor-link JS 循环与 TOC 共用 headings 数组

源码 L376-385 是单一 forEach 循环，同时完成两件事：

```js
// L232: var headings = body.querySelectorAll('h2, h3');
headings.forEach(function(h, i) {
  if (!h.id) h.id = 'section-' + i;
  var anchor = document.createElement('a');       // ← ① 复制链接锚点
  anchor.className = 'anchor-link'; ...
  h.appendChild(anchor);
  var link = document.createElement('a');          // ← ② TOC 链接
  link.href = '#' + h.id; ...
  toc.appendChild(link);                           // ← ② 加入 TOC
});
```

设计声称「h4-h6 同样加 id + slug（复制链接功能顺带支持）」，但：

| 能力 | 实现方式 | h4-h6 是否获得 |
|:--|:--|:--|
| id + slug | 服务端 md_to_html | ✅ 自动获得（修复后） |
| 复制链接 ¶ 锚点 | 客户端 JS L376-380 | ❌ 不会获得（headings 仅 h2/h3） |
| TOC 链接 | 客户端 JS L382-384 | ✅ 正确排除（设计意图） |

**矛盾点**: 设计 H3 检查项要求「锚点 hover 扩展 h4:hover .anchor-link」，但若 JS 不给 h4 追加 .anchor-link 元素，这条 CSS hover 是死代码。设计「影响范围」表和「实现方案」均未提及需拆分 L376 循环。

**修复方案（二选一）**:

1. **拆分循环（推荐）**: L376 后新增独立循环 `document.querySelectorAll('.doc-body h4, .doc-body h5, .doc-body h6').forEach(...)`，仅追加 .anchor-link（不加入 TOC）。TOC 循环保持 headings (h2/h3)。
2. 收缩声明: 删去「复制链接功能顺带支持」，明确「h4-h6 仅获 id 语义，¶ 复制链接仍限 h2/h3」。

## 修改意见

| 编号 | 问题 | 建议改法 |
|:--|:--|:--|
| D-新增 | L376-385 单一循环 conflate TOC 与 anchor 生成，h4-h6 复制链接功能不会生效 | 拆分循环：新增 h4-h6 独立 anchor 循环（不加入 TOC）；或删去「复制链接顺带支持」声明 |
