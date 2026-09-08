# doc meta 显示 md 路径 — review报告 v1.0

**文档**: `documents/doc-meta-path-showmd-design-v1.0-20260819.md`
**审查日期**: 2026-08-19
**审查级别**: L2 (Design Document Review)

---

## 数据验证

| 验证项 | 方法 | 结果 |
|:---|:---|:---|
| cmd_doc 计算 rel 但丢弃 | 源码 L241 `rel = '~/'+...` / L249-250 meta 无路径 | ✅ 确认 |
| 模板路径正则 | 源码 L309 `match(/路径:\s*(.+)/)` | ✅ 确认 |
| slide 无 URLSearchParams | `grep` = 0 matches | ✅ 确认 |
| meta 组装行号 | 源码 L249-250 / slide 对应处 | ✅ 精确 |

---

## 🔴 关键发现: 标题点击复制逻辑静默失效 (M4)

设计 M4 声称「路径行恢复后此逻辑自动命中，复制的是脱敏文件名」。此断言事实错误，遗漏了 L311 第二道闸门。

```javascript
var m = metaEl.textContent.match(/路径:\s*(.+)/);   // 命中 → 捕获文件名
var target = m ? m[1].trim() : decodeURI(location.href);
if (/^(https?:|\/|~\/)/.test(target)) {             // ← 第二道闸门
  navigator.clipboard.writeText(target);
  showToast('已复制: ' + target);
}
```

脱敏后 `target` = `history-overview.md`（纯文件名），不匹配 L311 `^(https?:|\/|~\/)` → 复制与 toast 均不执行。

| 场景 | target 值 | L311 闸门 | 实际行为 |
|:---|:---|:---|:---|
| 改前（无路径行） | URL | 匹配 | 复制 URL ✅ |
| 改后（有路径行） | `history-overview.md` | 不匹配 | **静默无操作** ❌ |

**修复方案（二选一）**:
1. 扩展 L311 正则允许纯文件名：`if (/^(https?:|\/|~\/|[\w.-]+$)/.test(target))`，或删除闸门（meta 路径行始终有值）
2. title 点击始终复制 URL（`location.href`），路径行仅作展示不参与复制

---

## 其余维度

| 项 | 评估 | 评级 |
|:---|:---|:--:|
| M1 需求覆盖 | 路径行 doc+slide、默认隐藏、show-md=1、basename 脱敏 | 🟢 |
| M2 实现正确性 | CSS+JS 与 width/sidebar 同构 | 🟢 |
| M3 脱敏与隐私 | basename 无目录泄露，iframe 不自动 show-md | 🟢 |
| M5 slide 处理 | slide 无 URLSearchParams（实测 0 匹配），默认隐藏合理 | 🟢 |
| M6 测试设计 | 回归 + Selenium，复制断言需随 M4 修复调整 | 🟢 |
| M7 影响面 | 仅 html-gen.py + layout-doc.html | 🟢 |

---

## 评分

```
Base: 100  扣分: 🔴×1 = -15  最终: 85  Rating: B
🔴 1   🟡 0   🟢 6
```

---

## 修改意见

| 编号 | 问题 | 建议改法 |
|:---|:---|:---|
| M4-1 | L311 闸门 `/^(https?:|\/|~\/)/` 不匹配脱敏文件名，标题点击复制静默失效 | 扩展正则允许纯文件名，或 title 点击始终复制 URL、路径行仅展示 |

---

## 结论

**驳回**（🔴 1 项）— 核心功能设计正确，但 M4 标题复制逻辑分析错误导致既有功能静默退化。修正 M4-1 后复检。
