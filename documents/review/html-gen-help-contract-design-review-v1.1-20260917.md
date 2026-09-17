# html-gen help 契约治理设计复审 — review 报告 v1.1

> 日期: 2026-09-17
> 文件: documents/solutions/html-gen-help-contract-design-v1.1-20260917.md（commit ba7b547）
> 基线: v1.0（commit 4649053）评审 CONDITIONAL PASS 80/B；v1.1 折入 HG-SEC-161..167
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> review 维度: 合理性 / 严格性 / 安全性
> 闭环: HTML-GEN-CL012（契约源+渲染+守卫）/ CL013（四模板补齐+文档面）
> 决策（用户定稿，不再重开）: T1-C T2-A T3-B T4-B T5-A T6-A T7-A · U1-C U2-A U3-A U4-B U5-B

```
┌─ DESIGN REVIEW v1.1 (复审) ─────────────────────┐
│  Document: html-gen-help-contract-design          │
│  Version : v1.1 (2026-09-17, commit ba7b547)      │
│  Baseline: 0 代码改动（设计尚未实施）              │
├──────────────────────────────────────────────────┤
│  合理性   🟢 (键清单补全已实测对账吻合)            │
│  严格性   🟡 (§D 提取正则三处不可靠)               │
│  安全性   🟢 (纯文档/契约重构, 0 新增风险面)       │
└──────────────────────────────────────────────────┘
```

## 一、v1.0 4🟡+3🟢 闭合清单（逐条核销）

| Finding | 状态 | 证据（本轮实测） |
|:--|:--|:--|
| HG-SEC-161 键清单三处枚举遗漏 | ✅ 已闭合 | §3.1 列类型=6（含 datetime，实测 `col.type === 'datetime'` L471/475）；options=13（实测 `OPTIONS.*` 13 键与 §3.1 逐项吻合，含 `clickMode`）；`options.feedback` 子键=5（实测 `FB_CFG.*` = {repo,dataset,key,altKey,template}，L357 注释吻合）。§4「列类型 4→6」「options 8→13」已订正 |
| HG-SEC-162 提取规则覆盖不完整 | ⚠️ 部分闭合 | §D 重写为分维度表，覆盖 table 6 维 + doc 2 + slide 2 + knowledge 3（v1.0 缺失的列类型取值/FB_CFG/tab/嵌套/doc/slide/knowledge 均已补）。但「列类型取值」正则仍漏捕默认类型 `string`（详见 HG-SEC-170） |
| HG-SEC-163 warn 作用域未定义 | ✅ 已闭合 | §E 明确校验对象（table columns/options/feedback 子键 + knowledge item/groups）+ 排除项（data 行字段、简单数组推导列名、render/handler 值）；§7 第 5 项改双用例 (a) 结构化含未知键→报「未知」、(b) 简单数组→不报 |
| HG-SEC-164 契约/手写拼接边界未定义 | ✅ 已闭合 | 新增 §B.3 三段式（①契约渲染段 / ②手写示例段 / ③语法说明段）+ 键名字面量口径 + §7 第 8 项 grep 显式排除 `HELP_*_EXAMPLES` |
| HG-SEC-165 drama「4 处」实为 5 处 | ✅ 已闭合 | §1.1 订正「5 处 L55/64/74/91/100」；实测 `grep -n initialHidden data/_drama-table-history-strategy.json` = 5 处（L55/64/74/91/100）吻合 |
| HG-SEC-166 §7 断言弱 | ✅ 已闭合 | §7 第 2 项改逐键独立断言 `grep -qE "\b$k\b"`；第 4 项改逐 flag 独立断言；§0 附注补记词边界假阳性（`clickMode` ⊂ `clickModes`） |
| HG-SEC-167 探针口径 | ✅ 已闭合 | §1.2 订正「分栏模式可见=dad5629(07-19 v3.0)；列类型=7297a9c(07-23 v3.1)，二者不矛盾」 |

## 二、v1.1 断言实测复核表（7 项 must-test）

| # | 断言 | 实测结果 | 结论 |
|:--|:--|:--|:--|
| 1 | §3.1 列类型=6 / options=13 / feedback 子键=5 | `grep -n "type === 'datetime'"` = L471/475（**无 484**，见 HG-SEC-171）；`OPTIONS.*` sort -u = 13 键；`FB_CFG.*` = 5 子键；L357 注释 `{repo,dataset,key,altKey,template}` | ✅ 成立（行号微瑕另计） |
| 2 | §G 分期避免 B1 在 CL012 即红 | §G 明确 CL012 仅启用 table 维度、doc/slide/knowledge 走骨架节点（断言 CL013 启用）。§3.1 键清单已补全（无缺失键），B1「模板→契约 ⊆」在 CL012 不会因键缺失而红 | ✅ 成立 |
| 3 | §D 分维度正则实跑 | 详见「三」：列属性 22✓ / options 13✓ / feedback 5✓ / tabs 6✓ / doc URL 3✓ / groups 3✓；**列类型取值 5（漏 string）/ CLI 漏 short-form 别名 / item 误捕+漏捕** | ⚠️ 3 处正则不可靠 |
| 4 | §E 作用域 + 双用例 | §E 明确校验对象与排除项；§7 第 5 项 (a) 结构化未知键→报 / (b) 简单数组→不报，覆盖误报面 | ✅ 成立 |
| 5 | §B.3 三段式 + 键名字面量 + §7 第 8 项 | §B.3 三段边界明确（①契约渲染含键名 / ②示例段含键名但段首标注 / ③语法段不含键名）；§7 第 8 项 `grep -v "html-gen help"` + 排除示例段 | ✅ 自洽可落地 |
| 6 | §1.1「5 处」/ §7 逐键断言 / §1.2 探针口径 | 均已订正（见闭合清单 165/166/167） | ✅ 到位 |
| 7 | §0 附注词边界自查 | `printf 'clickModes\n' \| grep -qE '\bclickMode\b'` → 无匹配（正确）；`printf 'clickMode / clickModes\n' \| grep -qE '\bclickMode\b'` → 匹配（正确）；§7 第 2 项已改 `grep -qE "\b$k\b"` | ✅ 成立 |

## 三、§D 分维度正则实跑结果（高价值动作）

方法：Python `re.findall` 逐正则跑在对应文件，提取唯一键集合，与设计 §3 键清单对账。

| 维度 | 设计正则 | 实跑唯一键数 | 设计 §3 声称 | 吻合 | 判定 |
|:--|:--|:--|:--|:--|:--|
| table 列属性 | `\b(?:col\|c)\.([a-zA-Z_]\w*)` | 22 | 22 | ✅ 逐项一致 | 可靠 |
| table options | `OPTIONS\.([a-zA-Z_]\w*)` | 13 | 13 | ✅ | 可靠 |
| table feedback | `FB_CFG\s*&&\s*FB_CFG\.(…)` + `FB_CFG\.(…)` | 5 | 5 | ✅ | 可靠 |
| table 列类型取值 | `(?:col\|c\|col2)\.type === '…'` 与 `type === '…'` | 5 | 6 | ❌ 漏 `string` | **不可靠** |
| table tabs | `\btab\.(…)` + `\bt\.(key\|label\|field\|match\|contains\|value)` | 6（并集） | 6 | ✅ | 可靠 |
| doc URL | `params\.get\('…'\)` | 3 | sidebar/toolbar/width | ✅ | 可靠 |
| doc CLI | `d\.add_argument\('--…'` | 7 | 9 | ❌ 漏 input/output | **不可靠** |
| slide CLI | `s\.add_argument\('--…'` | 6 | 8 | ❌ 漏 input/output | **不可靠** |
| knowledge CLI | `k\.add_argument\('--…'` | 7 | 10 | ❌ 漏 data/groups/output | **不可靠** |
| knowledge item | `i?tem\.([a-zA-Z_]\w*)` | 8（含 2 误捕） | 7 | ❌ 误捕 active/filtered + 漏 icon | **不可靠** |
| knowledge groups | `\bg\.([a-zA-Z_]\w*)` | 3 | 3 | ✅ | 可靠 |

详细证据：

- **列类型取值（漏 string）**：模板对 `string` 无 `=== 'string'` 分支（string 为隐式默认，走 `else` 落 `String(va).localeCompare`）；`type === '…'` 仅得 {actions, datetime, number, pills, videos}。§3.1 已标注 `string(默认)`，但 §D 未注明「string 为默认、不入模板提取断言、由契约手工登记」。
- **CLI（漏 short-form 别名）**：`-i/--input`、`-o/--output`、`-d/--data`、`-g/--groups` 均以 `add_argument('-x', '--long', …)` 短形式在前定义（html-gen.py L865-866/876-877/886/889/897-898/902），`add_argument\('--([a-z-]+)'` 只匹配首字面量以 `--` 开头者，故漏捕。改进正则 `X\.add_argument\([^)]*'--([a-z-]+)'` 实跑 = doc 9 / slide 8 / table 9 / knowledge 10，与 §3 各 CLI 清单逐项吻合。
- **knowledge item（误捕 + 漏捕）**：`i?tem\.` 误捕 CSS 类名 `.kw-item.active` / `.kw-item.filtered-out`（→ active/filtered，非 JSON 键）；漏捕 `icon`（CL013 新增，当前模板无 `item.icon`）；实际 JS 循环变量用 `i.`/`it.`（`i.group`/`i.section`/`i.title`），`i?tem\.` 正则仅能覆盖 `item.*` 形态。改进方向：改「显式清单 + 存在性断言」（设计已对 slide 行为/table 嵌套用此降级），或精确正则 `(?<!-)\bitem\.` + 显式列循环变量。

## 四、新发现问题（v1.1 引入）

| # | 严重度 | 摘要 |
|:--|:--|:--|
| HG-SEC-168 | 🟡 | §D CLI 提取正则漏捕 short-form 别名（`-i/--input`/`-o/--output`/`-d/--data`/`-g/--groups`），实测 doc=7/slide=6/knowledge=7（各少 2-3 项，vs §3 清单 9/8/10）；且 §D 缺 table CLI 行（§3.1 table CLI 9 项在 §D 无对应提取规则，只有 doc/slide/knowledge CLI 三行）。致「source→contract ⊆」断言对 CLI 维度弱化，未达「真正双向闭合」 |
| HG-SEC-169 | 🟡 | §D knowledge item 提取正则 `i?tem\.(…)` 误捕 CSS 类名（active/filtered）+ 漏捕 icon（CL013 新增未实现），实测 8 键 vs 设计 7；需白名单排除 2 项 CSS 误捕（违反「白名单趋近 0」预期且 §D 未注明），且 icon 在 CL013 补入模板前无法被该正则捕获 |
| HG-SEC-170 | 🟡 | §D 列类型取值正则漏捕默认类型 `string`（`type === '…'` 仅得 5 项），为 HG-SEC-162 的残留缺口；§3.1 已列 `string(默认)` 但 §D 未注明其提取口径 |
| HG-SEC-171 | 🟢 | §3.1「模板 L471/475/484 消费」行号微瑕：datetime 实际 `type === 'datetime'` 在 L471/475，isDate 使用分支在 L485，L484 为 `var cmp;`。不影响结论 |

## 五、评估项

- **§B.3 三段式是否过度设计 / 是否与「键表只在契约中」一致**：三段式（①契约渲染含键名 / ②示例段含键名但段首标注「示例，键以键规范段为准」/ ③语法段不含键名）结构合理、不过度——它正是调和「键表唯一」与「教程示例需键名」的最小边界定义；§7 第 8 项 grep 排除示例段使核查与 §B.3 口径一致。②/③拼接顺序二选一（`render_help` 内部 vs 调用方拼接）留给 dev 落地时择一并写注释，可接受。
- **§D 白名单纪律是否足以自约束**：注释理由 + 反向断言 `白名单项 not in 契约键集` 双保险，方向正确；但 HG-SEC-169 表明 knowledge item 正则实际需要 ≥2 项白名单（active/filtered 为 CSS 误捕），而 §D 未预记——建议 §D 对 item 维度直接降级「显式清单」，消除白名单需求。
- **§G CL012/CL013 边界是否清晰、CL013 是否有隐含未定义项**：边界清晰（CL012=table 6 维 + 基建；CL013=doc/slide/knowledge 7 维 + 文档面）。CL013 隐含未定义项：knowledge item `icon` 为 CL013 新增键，但 §D item 提取规则无法捕获它（HG-SEC-169 的漏捕侧）；且 table CLI（§3.1 9 项）在 §D 无启用阶段归属（HG-SEC-168 的 coverage 侧）。两处需在 §D/§G 明示。
- **§5 测试影响（12-14 例 / 计数同步 312）是否与 §D 维度数匹配**：§D 维度 table 6 + doc 2 + slide 2 + knowledge 3 = 13 维（部分可合并断言），加契约↔help 双向 + render_help 冒烟 ≈ 12-14 例，量级匹配。计数同步 312 的承诺在 §5 已明确，可实施。
- **§7 全部命令可执行性与断言强度**：第 1 项 importlib 加载安全（顶层无副作用 guard，v1.0 已核）；第 2/4 项已改逐键/逐 flag 独立断言（HG-SEC-166 闭合）；第 3 项语义并列、第 5 项双用例、第 6/7 项 pytest、第 8 项文档面 grep 排除示例段——均无残留子串/弱断言类问题。唯 §7 第 2 项与第 4 项的「CLI flag 断言」是「contract→help 方向」（grep help 输出），不覆盖「source→contract 方向」的 CLI 提取（即 HG-SEC-168 的正则缺陷），二者互补而非替代。

## 六、评分

| 项 | 严重度 | 扣分 |
|:---|:---|:---|
| 4 🟡 v1.0 findings 闭合：161/163/164 全闭合 + 162 部分闭合（残留 string 漏捕） | — | 0（净修复） |
| 3 🟢 v1.0 findings（165/166/167）闭合 | — | 0 |
| HG-SEC-168 §D CLI 正则漏捕 + 缺 table CLI 行 | 🟡 | -3 |
| HG-SEC-169 §D knowledge item 正则误捕+漏捕 | 🟡 | -2 |
| HG-SEC-170 §D 列类型取值漏捕 string（162 残留） | 🟡 | -1 |
| HG-SEC-171 §3.1 行号微瑕 | 🟢 | 0 |

得分: **85 / 100（B）**（较 v1.0 的 80 净修复 +5）

## 七、结论

**CONDITIONAL PASS（非阻断，85/B）** — v1.0 的 4 🟡 + 3 🟢 **7 条 findings 全部闭合或部分闭合**：HG-SEC-161/163/164/165/166/167 六条完全闭合，HG-SEC-162 部分闭合（维度覆盖已补齐，仅「列类型取值」正则残留 `string` 漏捕）。v1.1 的键清单（§3.1-3.4）经本轮源码实测对账**完整且正确**（列属性 22 / options 13 / feedback 5 / tabs 6 / doc URL 3 / groups 3 / 各模板 CLI 9/8/9/10 逐项吻合），§B.3 三段式 / §E 作用域 / §G 分期边界均已明确定义，安全面无新增风险。

但 v1.1 的 §D 重写**引入 3 个 🟡 提取正则可靠性缺陷**（HG-SEC-168 CLI 漏捕 short-form 别名 / HG-SEC-169 item 误捕 CSS+漏捕 icon / HG-SEC-170 列类型漏捕 string）+ 1 🟢 行号微瑕。三处均为非阻断（测试配方细节，修正方向明确且极小，正则改进版已在本报告实测给出 9/8/9/10 吻合），可折入 CL012/CL013 实施（dev 落地时直接用改进正则）或设计 v1.2 微调。属非阻断 CONDITIONAL PASS，按任务约定提交并推送本轮审计产物。

## 八、最小修正方向（供 dev 折入 / 设计 v1.2）

1. **CLI 正则改为 `X\.add_argument\([^)]*'--([a-z-]+)'`**（跨过短形式 `-x`, 实测 doc 9 / slide 8 / table 9 / knowledge 10 与 §3 清单逐项吻合），并在 §D 补 table CLI 行（`t\.add_argument`，CL012 或 CL013 明示归属）。
2. **列类型取值维度**：§D 注明 `string` 为隐式默认（`type === 'string'` 不存在），由契约手工登记、不入模板提取断言；或改「5 项显式取值 + string 契约常量」。
3. **knowledge item 维度**：改「显式清单 + 存在性断言」（7 键：title/group/section/badge/desc/url/icon），与 slide 行为/table 嵌套的降级口径统一；消除 `i?tem\.` 对 CSS 类名的误捕与对 icon/循环变量 `i.`/`it.` 的漏捕。
4. **🟢 随修**：§3.1「L471/475/484」→「L471/475」（isDate 使用分支 L485）。
5. **§D/§G 补明**：table 顶层键（7）/点击模式取值（4）/URL 状态键（3）三者的断言维度与启用阶段（可由「契约→help」断言兜底，但需明说，避免与「逐维度提取」承诺不一致）。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:---|
| — | （无阻断项；HG-SEC-168/169/170 为 🟡 非阻断，折入 CL012/CL013 实施或设计 v1.2 微调；HG-SEC-171 🟢 随修） | — |
