# html-gen table 筛选默认行为调整 — review报告 v1.0

**文档**: `documents/solutions/table-quickfilter-default-design-v1.0-20260806.md`
**审查日期**: 2026-08-08
**审查级别**: L2 (Design Document Review)

---

## 数据验证

| 验证项 | 方法 | 结果 |
|:---|:---|:---|
| D1 判断点 | 源码 L525 `col.quickFilter !== false` | 确认，改 `=== true` |
| D2 pillFilter | 源码 L504-505 `col.pillFilter !== false` | 确认保持 |
| D3 决策链 | 源码 L523-526 onCellClick → quickFilter → (end) | D3 新增 firstKeyCol 最低优先级 |
| drama 3 表零配置 | Python 遍历 3 个 data JSON columns | 0 onClick/onCellClick/preview/quickFilter |
| skills/countries/phase2 | `ls -la` 3 文件均存在 | skills 58KB, countries 103KB, phase2 2.4KB |
| 需求覆盖 | 对照 1A-7A | 7/7 全覆盖 |

---

## 模板改动安全性

### D1 — quickFilter `!== false` → `=== true`

受影响的 6 个引用点（L337/416/418-423/525-526/601-604/611-624）均通过 `quickFilter` 运行时变量 gate，不受列级配置变更影响。无遗漏路径。

### D3 — 第 1 列默认分栏

4 级优先级链: `onCellClick:split` > `quickFilter:true` > `firstKeyCol` > 无操作。向后兼容：countries/skills 第 1 列已显式 split（不受影响），drama 第 1 列获新增分栏能力（非破坏）。

---

## 评分

```
Base: 100  扣分: 0  最终: 100  Rating: A
🔴 0   🟡 0   🟢 1 (firstKeyCol 建议按 colVisibility 动态计算)
```

---

## 结论

**通过** — 改动最小（1 行判断 + firstKeyCol 计算），向后兼容完整。源码交叉验证确认 drama 3 表零配置。7 项需求全覆盖。
