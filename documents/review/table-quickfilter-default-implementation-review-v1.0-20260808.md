# html-gen table 筛选默认行为调整 — 实现审计报告 v1.0

**文档**: `documents/review/table-quickfilter-default-implementation-review-v1.0-20260808.md`
**审查日期**: 2026-08-08
**审查级别**: L2 (Implementation Audit)
**审查对象**: 65c32c1 (dev 实施) + e0ca95e (ops 核查)

---

## 数据验证

| 验证项 | 方法 | 结果 |
|:---|:---|:---|
| 文件变更 | `git diff --stat` | 14 files, +305/-68 |
| D1 quickFilter | 源码 L525 `=== true` + comment | 确认 |
| D3 firstKeyCol | 源码 L482 `cols.find(c => c.type !== 'actions')` | 动态计算, renderRows 内 |
| D3 优先级链 | L523→L525→L528 | onCellClick>quickFilter>firstKeyCol>none |
| D2 pillFilter | skills ×2, countries ×1 `pillFilter:true` | 确认 |
| D5 test_06 | cells[1] (stars, quickFilter:true) | 适配 |
| D5 test_06b | cells[0] (name) → split-mode 断言 | 新增 |
| D5 select_click_mode | `body.click` → `JS classList.remove` | fix |
| D7 docs | AGENTS.md + features.md + template comments | 三处同步 |
| full tests | `pytest tests/ -q` | **84 passed, 0 failed (121s)** |

---

## 实现与设计一致性

| D# | 设计要点 | 实现 | 评级 |
|:---|:---|:---|:--:|
| D1 | quickFilter `=== true` | L525 单行 + comment | 🟢 |
| D2 | pillFilter 显式声明 ×3 | skills×2, countries×1, L504-505 comment | 🟢 |
| D3 | firstKeyCol 默认分栏 | L482 动态计算, L528-530 priority | 🟢 |
| D5 | test_06 适配 + 06b 新增 | cells[1] + split-mode 断言 | 🟢 |
| D6 | 6 demo 重生成 | drama×3 + skills + phase2 + countries | 🟢 |
| D7 | 文档同步 | AGENTS/features/template comments | 🟢 |

---

## 关键实现亮点

**D3 firstKeyCol 动态计算**（优于设计）:
设计写"模块初始化处"，实施改为 `renderRows()` 内 `var firstKeyCol = cols.find(c => c.type !== 'actions');`，其中 `cols` 来自 `visibleCols()`。好处：列可见性变化后 firstKeyCol 自动跟随更新，无 stale reference 问题。✅

**D5 select_click_mode fix**: `body.click()` 在 clickMode=modal 时误触表格行 → 改为 `classList.remove('show')`，根因修复而非绕过。✅

---

## 安全事项

无安全发现。所有改动为列级配置语义翻转（`!== false`→`=== true`）+ onclick 优先级扩展，不涉及 innerHTML/路径/eval。数据文件仅补布尔属性，无注入风险。

---

## 评分

```
Base: 100  扣分: 0  最终: 100
Rating: A
🔴 0   🟡 0   🟢 0
```

---

## 结论

**PASS** — 授权 push。

D1-D7 全部实施且超越设计质量（firstKeyCol 动态计算 + select_click_mode 根因修复），84 tests 全绿。模板改动保守（1 行判断翻转 + 1 个 else-if 扩展），向后兼容完整（显式配置全保留，默认值仅影响未配置列）。
