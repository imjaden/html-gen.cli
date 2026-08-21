# doc meta 显示 md 路径 — Review 报告 v1.0

## 版本

v1.0 (2026-08-19)

## 审查对象

- documents/doc-meta-path-showmd-design-v1.0-20260819.md (commit 3f456d3 + 5927f97 确认修订)

## 结论

**驳回（🔴 1 项）** — 核心功能（meta 显示路径 + show-md 显隐 + 脱敏）设计正确，但 M4 标题复制逻辑分析错误，会导致既有功能静默退化。修正 M4-1 后复检。

评分: 85/B（Base 100, 🔴×1 = -15）

## 数据验证

| 验证项 | 方法 | 结果 |
|:--|:--|:--|
| cmd_doc 计算 rel 但丢弃 | 源码 L241 rel='~/'+... / L249-250 meta 无路径 | ✅ 确认 |
| 模板路径正则 | 源码 L309 match(/路径:\s*(.+)/) | ✅ 确认 |
| slide 无 URLSearchParams | grep = 0 matches | ✅ 确认（M5 判断正确） |
| meta 组装行号 | 源码 L249-250 / slide 对应处 | ✅ 精确 |

## 🔴 关键发现: 标题点击复制逻辑静默失效 (M4)

设计 M4 声称「路径行恢复后此逻辑自动命中，复制的是脱敏文件名（history-overview.md）」。此断言事实错误，遗漏了 L311 的第二道闸门。

源码 L306-315 完整链路：

```js
var m = metaEl.textContent.match(/路径:\s*(.+)/);   // 命中 → 捕获文件名
var target = m ? m[1].trim() : decodeURI(location.href);
if (/^(https?:|\/|~\/)/.test(target)) {             // ← 第二道闸门！
  navigator.clipboard.writeText(target);            //   filename 不匹配此正则
  showToast('已复制: ' + target);
}
```

问题: 脱敏后的 target = history-overview.md（纯文件名），不匹配 L311 的 `^(https?:|\/|~\/)` 正则 → if 为 false → 复制与 toast 均不执行。

| 场景 | target 值 | L311 闸门 | 实际行为 |
|:--|:--|:--|:--|
| 改前（无路径行） | URL (decodeURI) | 匹配 | 复制 URL ✅ |
| 改后（有路径行） | history-overview.md | 不匹配 | 静默无操作 ❌ |

设计声称「URL fallback → 复制文件名」，实际是「复制 URL → 复制空」，从有功能退化到无功能。

## 修复方案（二选一）

1. **扩展 L311 正则**，允许纯文件名：`/^(https?:|\/|~\/|[\w.-]+$)/`，或直接删掉 L311 闸门（meta 路径行始终有值）
2. 改复制源：title 点击始终复制 URL（location.href），路径行仅作展示，不参与复制逻辑——需同步调整 L309-310 的 target 取值

## 其余维度

| 项 | 评估 | 评级 |
|:--|:--|:--|
| M1 需求覆盖 | meta 路径行 doc+slide 两处，默认隐藏，show-md=1 显示，basename 脱敏 | 🟢 |
| M2 实现正确性 | CSS+JS 与 width/sidebar 模式同构 | 🟢 |
| M3 脱敏与隐私 | basename 无目录泄露，iframe 不自动 show-md | 🟢 |
| M5 slide 处理 | slide 无 URLSearchParams（已实测 0 匹配），生成端统一+默认隐藏合理 | 🟢 |
| M6 测试设计 | 回归 + Selenium 覆盖显隐/复制 | 🟢（复制断言需随 M4 修复调整） |
| M7 影响面 | 仅 html-gen.py + layout-doc.html | 🟢 |

## 修改意见

| 编号 | 问题 | 建议改法 |
|:--|:--|:--|
| M4-1 | L311 闸门 `^(https?:|\/|~\/)` 不匹配脱敏文件名，标题点击复制静默失效 | 扩展正则允许纯文件名，或 title 点击始终复制 URL、路径行仅展示；测试 test_doc_title_click_copy_path 断言需对应修正 |
