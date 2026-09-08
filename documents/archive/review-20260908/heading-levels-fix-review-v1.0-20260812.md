# h4-h6 标题渲染支持 — Review 报告

## 版本

v1.1 (2026-08-12, 复检)

## 审查对象

- documents/heading-levels-fix-design-v1.0-20260812.md (commit 19ee648, 复检 c33005f)

## 复检结论

**PASS** — 初版 CONDITIONAL PASS 的 1 处遗漏（D-新增）已在 c33005f 正确闭合。

## 复检验证

| 初版发现 | 修复 | 验证 |
|:---|:---|:--:|
| L376-385 单一循环 conflate TOC 与 anchor 生成 | 新增独立循环（§3 layout-doc.html JS） | ✅ 拆分正确，仅追加 anchor 不进 TOC |
| 设计「复制链接顺带支持」声明不实 | 影响范围表补 JS 拆分 | ✅ layout-doc.html 行已更新 |
| 测试未覆盖 anchor-link | 补 test_doc_h4_anchor_link | ✅ 断言 h4 含 .anchor-link + TOC 仅 h2/h3 |

## 检查项结果

| 检查项 | 结果 |
|:--|:--|
| H1 方案完整性 | ✅ 通过 |
| H2 模板实现正确性 | ✅ 通过 |
| H3 样式一致性 | ✅ 通过（拆分循环补齐 anchor） |
| H4 TOC 决策 | ✅ 通过 |
| H5 测试设计 | ✅ 通过 |
| H6 文档同步 | ✅ 通过 |
| H7 风险 | ✅ 通过 |

## 🟢 观察（非阻塞）

拆分循环的 id fallback 用 `'section-' + h.textContent`，textContent 可能含空格/特殊字符生成非法 id。因 md_to_html 已生成 slug id，该 fallback 为死代码；若保留，建议改用 `'section-' + i`（与原循环一致的索引模式）或复用 `slug()`。

## 修改意见

无阻塞项。🟢 观察 1 条（id fallback 用索引而非 textContent，实施时顺手调整）。

## 结论

**PASS** — 可直接交付 dev 实施。
