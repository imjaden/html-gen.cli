# 表格文本列 XSS 转义设计评审 v1.0（HG-SEC-134，HTML-GEN-CL010）

> 日期: 2026-09-17
> 闭环: HTML-GEN-CL010（1A 闭环 2/6 设计评审，**补做**）
> 评审对象: `documents/solutions/table-text-xss-escape-design-v1.0-20260911.md`（决策 A2+B1+C1+D1+E1+F2；commit `5f447fc`）
> 基线: 本地 HEAD = `github/main` = `72e76f4`，工作区干净；设计父提交 `5f447fc^` = `2e4dce9`
> 口径: 本轮聚焦「设计本身是否成立、是否会在设计阶段正确设闸」；不重复实现审计（`72e76f4` PASS 100/100）与 ops 核查（`741a7f2` PASS）结论，事实性证据由 review 独立实测（`git show 5f447fc^` 对照 + 全仓扫描 + 源码行号）

## 0. 结论

**CONDITIONAL PASS（非阻断）— 90/100（2 🟡 + 3 🟢，0 🔴）**

设计的安全机制本身成立且最小完备：A2（默认转义 + `escape===false` 豁免）是正确且唯一的设闸方式，
B1 扫描、C1 入库防护、D1 列级豁免、E1 解耦、F2 验收均自洽；问题陈述与四条渲染路径矩阵事实准确。

但设计存在 1 处**会让实现者走错**的表述（HG-SEC-172 🟡）：§6 文件清单把 `data/_demos-data.json` 当作
demos-index「文档链接」列的修复目标，实为 `html-gen demo --rebuild` 的**生成物**，真正的生成源是
`html-gen.py cmd_demo idx_columns`（line 1366）。按设计字面执行 → 修复不持久，下次 `--rebuild` 静默回退。
实现已正确补上 `html-gen.py:1366`（属「设计漏列 + 实现多做」），故为**非阻断**，且设计 §5.3「重建后链接仍可点」
验收项提供兜底闸门。

其余 1 🟡（HG-SEC-173 测试计划四路径 overclaim）+ 3 🟢 均为精度/完备性瑕疵，不影响安全设闸方向。
设计已冻结于 `5f447fc`（不改写历史），本轮 findings 留痕备查，不触发再评审循环。

## 1. 逐项评审表

| # | 评审任务 | 判定 | 关键证据 |
|:--|:--|:--|:--|
| 1 | 问题陈述事实性（§1） | ✅ 准确 | §2 事实对照：opt-in / 18 列未设 / 三路径已转义 / 唯一 HTML 列，四项全部核实成立 |
| 2 | 决策自洽性（§2 A2/B1/C1/D1/E1/F2） | ✅ 成立 | §3 判定表：六项决策自洽，B1/D1 各带 1 处精度瑕疵（🟢） |
| 3 | 安全矩阵（§3 四路径） | ✅ 一致 | §4 行号对照：四路径修复前后判定与当前代码吻合 |
| 4 | 影响面与回归（§4） | ⚠️ 有遗漏 | §5：`html-gen.py cmd_demo idx_columns` 亦为生成源，§6 漏列 → HG-SEC-172 |
| 5 | 测试计划（§5 六用例 + 假阳性） | ⚠️ overclaim | §6：expand 未直接测（test_06 等效论证）→ HG-SEC-173；断言无假阳性 |
| 6 | 设计↔实现偏差 | ⚠️ 有偏差 | §7：实现多做 html-gen.py + 计数/产物文件；无实现少做 |
| 7 | 方法论（是否让实现者走错） | ⚠️ 1 处 | §8：§6 文件清单根因定位错（生成物当修复目标）；其余表述清晰 |

## 2. 事实性核实证据（`git show 5f447fc^` 对照，review 独立实测）

### 2.1 问题陈述 §1 四项事实

| 设计声称 | 父提交 `2e4dce9`（`5f447fc^`）实测 | 判定 |
|:--|:--|:--|
| 「`col.escape: true` 显式标记才转义（opt-in）」 | `layout-table.html:588` `else if (col.escape) val = escapeHtml(String(val));`（真值才转义，默认不转） | ✅ |
| 「countries 18 列全部未设」 | `_countries-data.json` columns 18 项，`escape` 键全部为 `None`（无一处声明） | ✅ |
| 「modal / split preview / expand 三条路径已 escapeHtml」 | modal `L878`、split `L1152`、expand `L621` 三处均 `escapeHtml(String(v))` | ✅ |
| 「唯一依赖 HTML 的 text 列: _demos-data.json 文档链接」 | 全仓 `data/*.json` 扫描：A 型 table text 列含 `<` 标签仅 `_demos-data.json`「文档链接」18 条 `<a>` | ✅ |

补充核实（设计未明言但隐含成立）：

- 攻击路径（反馈 Issue → `--apply` 写回 → 重建 → 访客触发）与 countries editable string 字段（note/capital_zh/ethnic_groups 等）对应，威胁模型成立。
- `escapeHtml`（`layout-table.html:385-389`）为 `textContent → innerHTML` 标准语义，`<`/`>`/`&` 全转义、无二次解析旁路。

### 2.2 父提交主单元格渲染分支（修改前，opt-in）

```
588:  else if (col.escape) val = escapeHtml(String(val));
589:  else if (val === undefined || val === null) val = '';
```

设计 §1「opt-in」表述与父提交逐字一致；`escape: undefined`（未声明）→ 落入「不转义」分支 → raw innerHTML，确为 stored XSS 隐患。

## 3. 决策自洽性判定（§2 A2..F2）

| 决策 | 设计语义 | 自洽性判定 |
|:--|:--|:--|
| A2 | 默认转义 + `escape===false` 豁免 | ✅ 最小且完备。分支顺序（render→thousands→escape===false→null→默认）保证唯一 raw-HTML 逃逸口仅 `col.render`（已废弃、全仓零使用）与 `escape===false`（显式）。`escape:true` 兼容落入默认分支（冗余无害） |
| B1 | 全局覆盖 + 唯一 HTML 列豁免 | ✅ 扫描依据正确（`<` 为标签起始，全 A 型 text 列除文档链接外 `<=0`）。🟢 瑕疵：未注记 `_skills/_user-skills` description 含孤立 `>`（`>-`），转义后视觉不变（见 HG-SEC-176） |
| C1 | 入库防护（`<`/`>` 拒绝） | ✅ 不漏拦。string 分支全覆盖（含 `--value`/`override_value` 路径）；数值列走 `to_number()`（`float()` 失败→None→拒绝）；实体编码绕过（`&lt;script&gt;`）由 `escapeHtml` 的 `&` 转义兜底（`&amp;lt;` 呈字面文本） |
| D1 | 列级 `escape:false` 豁免 | ✅ 唯一且充分。全仓唯一 HTML 列已豁免；无 `col.render` 列。🟢 瑕疵：未声明 `escape:false` 仅作用于主单元格，不传导 split/modal/expand（见 HG-SEC-174） |
| E1 | 与 `--feedback-repo` 解耦 | ✅ 成立。默认转义在 `render()` 模板层，无反馈通道页面同样受保护 |
| F2 | 验收（六用例 + 全量回归 + 链接可点） | ✅ 够。六用例覆盖主格/split/modal/expand/链接豁免/无 JS 错误 + 全量回归 + demos-index 链接可点。⚠️ expand 仅等效覆盖（见 HG-SEC-173） |

## 4. 安全矩阵对照（§3 四条渲染路径，给行号）

| 路径 | 设计引用 | 父提交行号（修复前） | 当前 HEAD 行号（修复后） | 修复前→后判定 | 实测 |
|:--|:--|:--|:--|:--|:--|
| 主表格单元格 | render() 529-605 | `504`（函数），转义分支 `588` | `504`，豁免 `588` / 默认转义 `590` | ❌ raw → ✅ 默认 escapeHtml | 吻合 |
| 分栏预览 | renderSplitPreview() 1118-1156 | `1118`（函数），escape `1152` | `1119`，escape `1153` | ✅ 已 escape → ✅ 不变 | 吻合 |
| 弹窗 modal | showModal() 872-883 | `872`（函数），escape `878` | `873`，escape `879` | ✅ 已 escape → ✅ 不变 | 吻合 |
| 行内展开 | expand grid 610-626 | escape `621` | escape `622` | ✅ 已 escape → ✅ 不变 | 吻合 |

注：设计行号引用**父提交（pre-change）**状态；`render()` 函数声明实际起点为 `504`（非 `529`，`529` 约为 tbody 渲染块起点），
为近似引用（见 HG-SEC-175 🟢）。修复后行号因 +1 行新增整体后移 1（588→589 区间）。四路径「修复前/后」判定与当前代码全部吻合。

## 5. 影响面与回归评估（§4）

受影响页面清单**完整**：countries / provinces / hermes-profile-skills-list / table-features-demo / table-actions-demo / drama 策略与时间轴，均为 A 型 table，数据侧 text 列 `<`/`>` 数 = 0，转义后视觉零变化（设计 §4 论断成立）。

「唯一需数据侧修复 = demos-index 文档链接」**不成立（不完整）**——这正是 HG-SEC-172 的核心：

- `demos-index.html` 的 COLUMNS 由 `html-gen.py cmd_demo idx_columns`（`html-gen.py:1366`）生成，`--rebuild` 时**重写** `data/_demos-data.json`（`html-gen.py:1380`）再调 `cmd_table` 重建。
- 设计 §6 仅列 `data/_demos-data.json（escape:false）`，未列生成源 `html-gen.py`。字面执行 → 改生成物 → 下次 `--rebuild` 被 `idx_columns`（无 `escape:false`）覆盖回退 → 文档链接列被转义为 `&lt;a…&gt;` 纯文本、链接失效。
- 实现已正确做「多做」：`html-gen.py:1366` 补 `'escape': False`（源头）+ `data/_demos-data.json`（生成物）+ `demos/demos-index.html`（产物）三者同步。
- 设计 §5.3「重建后文档链接仍可点」验收项构成兜底闸门：若实现者真跑 `--rebuild` 并验链接，可捕获此遗漏（但需实现者「先怀疑生成源」而非按 §6 字面改生成物）。

## 6. 测试计划评估（§5 六用例 + 假阳性风险）

`tests/test_xss_escape.py` 6 用例与设计 §5 对应关系：

| 用例 | 设计声称覆盖 | 实测 | 判定 |
|:--|:--|:--|:--|
| test_01 | 主表格单元格转义 | 断言 `&lt;img` 存在 + 剥离后无真实 `<img` | ✅ 直接 |
| test_02 | escape:false 链接列可点 | 断言 `<a href>` 渲染 | ✅ 直接 |
| test_03 | 无 JS 错误 | `window.__testErrors` 空 | ✅ 直接 |
| test_04 | 分栏预览转义 | 点击首格开 split，断言 `&lt;img` | ✅ 直接 |
| test_05 | modal 转义 | `showModal(XSS row)` 直接调，断言 `&lt;img` | ✅ 直接 |
| test_06 | **行内展开** | **未触发 expand**（IIFE 闭包无法外部触发），仅断言无 JS 错误 + 「split 同款 kv-list 逻辑等效覆盖」 | ⚠️ 等效，非直接 |

**假阳性风险判定：低。** `_assert_escaped` 以「`&lt;img` 存在 + 剥离实体后无真实 `<img`」为判据，
非巧合形态——若转义失效，`<img` 会真实出现、`&lt;img` 缺失，断言必失败（正确捕获）；若只转义 `<` 不转义 `>`，
则 `<img` 无法成标签、无脚本执行，断言仍成立且安全成立（`<` 是成标签的必要条件）。故无「漏洞存在但测试通过」的假阴性，亦无「测试通过却未测所述主题」之外的真假阳性。

设计 §5.1「四路径**均**断言」为 **overclaim**（HG-SEC-173 🟡）：expand 路径未直接断言 payload 转义，
仅依赖 split 等效 + 无 JS 错误。等效论证技术成立（expand `L622` 与 split `L1152` 同用 `escapeHtml(String(v))`），
但设计应在测试计划中预先声明 expand 的 Selenium 不可触发性与等效覆盖策略，而非让实现者自行降级。

## 7. 设计↔实现偏差

| 偏差 | 方向 | 详情 | 判定 |
|:--|:--|:--|:--|
| `html-gen.py:1366` idx_columns 补 `escape:false` | 实现多做 | 设计 §6 未列；demos-index 文档链接列的真正生成源，属「设计漏列」 | 可接受且**必要**（HG-SEC-172） |
| `AGENTS.md` / `features.md` 计数 305→311 | 实现多做 | 文档/计数同步，设计 §6 未列（常规约定） | 可接受（惯例） |
| `demos/countries-table.html` / `demos/demos-index.html` 重建 | 实现多做 | 产物重建，设计 §6 未列（产物不入设计文件清单惯例） | 可接受（惯例） |
| expand 路径测试降级为等效覆盖 | 实现少做（相对 §5.1 overclaim） | 设计声称四路径直接断言，实现 test_06 仅等效 | 可接受（等效论证成立；设计应预先声明） |

无「实现少做安全项」的偏差：A2/C1/D1/E1 四决策逐字落地，四路径转义全部生效（实现审计 `72e76f4` 已独立 PASS）。

## 8. 方法论审查（是否让实现者不产生歧义）

总体清晰：威胁模型、四路径矩阵、决策 A2..F2 的语义边界、提交计划均表达到位。

**1 处会让实现者走错的表述**（HG-SEC-172）：§4/§6 把 `data/_demos-data.json` 当修复目标，
未点破其「`html-gen demo --rebuild` 生成物」性质与「真正生成源 = `html-gen.py cmd_demo idx_columns`」。
实现者若按字面只改 `_demos-data.json`，修复不持久且 demos-index 链接静默回归。这是本次设计唯一的
实质性方法论缺陷。

**2 处建议（非走错，属精度）**：

- D1 应明确 `escape:false` 是「主单元格 only」豁免，split/modal/expand 恒转义（保守安全，但读者易误解「列级豁免」为全路径）。
- §5.1 应预先声明 expand 的 Selenium 触发限制与等效覆盖策略，避免测试计划与实际用例降级脱节。

## 9. Finding 清单

- 🔴 0 / 🟡 2 / 🟢 3（全部非阻断；设计已冻结于 `5f447fc`，留痕备查，不触发再评审）

| ID | 级别 | 位置 | 说明 | 处置 |
|:--|:--|:--|:--|:--|
| HG-SEC-172 | 🟡 | §4/§6 | 影响面与文件清单漏列生成源 `html-gen.py cmd_demo idx_columns`（demos-index「文档链接」列真正来源），误把生成物 `_demos-data.json` 当修复目标；字面执行→修复不持久（`--rebuild` 覆盖回退）。实现已正确补 `html-gen.py:1366` | 记录（非阻断，实现已 PASS） |
| HG-SEC-173 | 🟡 | §5.1 | 「四路径均断言」overclaim：expand 路径（test_06）未直接触发（IIFE 闭包），仅 no-JS-error + split 等效论证；等效成立但设计未预先声明 | 记录（非阻断） |
| HG-SEC-174 | 🟢 | §D1 | 未声明 `escape:false` 仅作用于主表格单元格，不传导 split/modal/expand（恒转义，保守安全） | 记录 |
| HG-SEC-175 | 🟢 | §1/§3 | 行号引用父提交（pre-change）状态，`render()` 起点 529 与实际 504 不符（529≈tbody 渲染块起点）；修复后行号整体 +1 | 记录 |
| HG-SEC-176 | 🟢 | §B1 | 「均不含 `<` 字符」准确，但未注记 `_skills/_user-skills` description 含孤立 `>`（`>-`），转义后视觉不变、非安全 | 记录 |

## 10. 评分

| 维度 | 得分 |
|:--|:--|
| 问题陈述事实性（§1） | 100 |
| 决策自洽性（§2 A2/B1/C1/D1/E1/F2） | 95 |
| 安全矩阵（§3 四路径） | 100 |
| 影响面与回归（§4 + §6 文件清单） | 75 |
| 测试计划（§5 覆盖与假阳性） | 85 |
| 设计↔实现一致性（§7） | 95 |
| 方法论清晰度（§8） | 85 |
| **综合** | **90 / 100 — CONDITIONAL PASS（非阻断）** |

## 11. 处理

- ✅ 非阻断 CONDITIONAL PASS → 写报告 + `review-log.md` + `.review-level.yaml`，按任务约定一次性提交并推送：
  commit `audit@review: XSS 转义设计评审 PASS (HTML-GEN-CL010)` → `git push github main`（ff-only）。
- 禁止推 gitee（origin）；仅 `github`。不改源码/数据/产物，不改写历史。
