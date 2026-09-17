# html-gen help 契约治理设计评审 — review 报告 v1.0

> 日期: 2026-09-17
> 文件: documents/solutions/html-gen-help-contract-design-v1.0-20260917.md（commit 4649053）
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> review 维度: 合理性 / 严格性 / 安全性
> 闭环: HTML-GEN-CL012（契约源 + 渲染 + 守卫）/ CL013（四模板补齐 + 文档面）
> 决策（用户定稿，不再重开）: T1-C T2-A T3-B T4-B T5-A T6-A T7-A · U1-C U2-A U3-A U4-B U5-B

```
┌─ DESIGN REVIEW v1.0 ─────────────────────────────┐
│  Document: html-gen-help-contract-design          │
│  Version : v1.0 (2026-09-17, commit 4649053)      │
│  Baseline: 0 代码改动（设计尚未实施）              │
├──────────────────────────────────────────────────┤
│  合理性   🟡 (诊断根因成立; 键清单三处枚举遗漏)    │
│  严格性   🟡 (B1 提取规则覆盖不完整; 边界未定义)   │
│  安全性   🟢 (纯文档/契约重构, 0 新增风险面)       │
└──────────────────────────────────────────────────┘
```

## 一、逐条断言复核表（12 条，全部实测，非文字接受）

方法：`python3 html-gen.py help <topic>` 实测输出 + `grep`/`git log -S`/`read_file` 逐行对照源码与数据。

| # | 断言 | 实测证据 | 结论 |
|:--|:---|:---|:--|
| 1 | help table 不含 5 键 + 列类型 4 项 + 无 CLI 参数段 | `help table` 输出 grep `initialHidden\|splitFull\|pillFilter\|format\|videos` 仅命中「列类型」「列属性」两个段头；`列类型:` 行 = `string(默认) / number(数值排序) / actions(操作按钮) / pills(标签样式)`（4 项，无 videos）；L604-835 对 `metadata/welcome/groups/favicon/github-url/home-url/quiet/feedback-repo` 命中数全为 0 | ✅ 成立 |
| 2 | help 正文硬编码 HELP_*，cmd_help 直接 print | `HELP_OVERVIEW` L606 / `HELP_DOC` L635 / `HELP_TABLE` L665 / `HELP_KNOWLEDGE` L742 / `HELP_SLIDE` L766 / `HELP_PROMPT` L781 / `HELP_DEMO` L804 / `HELP_MAP` L828 / `def cmd_help` L838 直接 `print(HELP_MAP[...])` | ✅ 成立 |
| 3 | 时效: table 正文 07-23; doc/slide/knowledge 07-14 | `-S'列类型'` → `7297a9c 2026-07-23`（v3.1）；`-S'缩进子列表'`/`-S'底部圆点'`/`-S'条目数据'` → `8c67e8b 2026-07-14`；`-S'分栏模式可见'` → `dad5629 2026-07-19`（v3.0，**非 07-23**，探针本身先于最后变更，不影响结论） | ✅ 成立（附 🟢 微瑕） |
| 4 | initialHidden 真实存在 L373-374, 38bdc9f 08-12, 自证在用 | `layout-table.html:373-374` 实现在用；`git log -1 -S'initialHidden'` = `38bdc9f 2026-08-12`；`data/_countries-data.json` 6 处、`data/_drama-table-history-strategy.json` **5 处**（L55/64/74/91/100，设计 §1.1 写「4 处」少 1）、`tests/test_initial_hidden_split.py` 5 用例、`demos/table-guide.md:100` | ✅ 成立（附 🟢 计数微瑕） |
| 5 | 未文档化: 五处 grep 零命中 | `grep -rn initialHidden AGENTS.md features.md README.md README.zh.md skills/ html-gen.py` → exit 1（零命中） | ✅ 成立 |
| 6 | hide 语义差异: L397 + L1144 双排除, initialHidden 不进 | `visibleCols()` L397 `if (c.hide) return false`；分栏详情 L1144 `!c.hide`；initialHidden 仅 L373-374 置 `colVisibility[key]=false`，不进两处排除 → 默认收起可开启、分栏全列 | ✅ 成立 |
| 7 | 键覆盖对账: 列属性 22 / options 12 | 列属性：实测 `col./c.` 消费 22 键，与 §3.1 清单逐项吻合 ✅；options：实测 `OPTIONS.*` 消费 **13** 键（含 `clickMode` 单数兼容别名，L1301-1308），设计 §3.1 只列 12（漏 `clickMode`）❌；列类型：实测消费 **6** 类（含 `datetime`，L471/475/484），设计 §3.1 只列 5（漏 `datetime`）❌ | ⚠️ 部分成立 |
| 8 | doc/slide/knowledge 缺口 | `layout-doc.html` `URLSearchParams` L261 + `?width` L85-87（narrow/medium/wide）；`layout-slide.html` `.slide-toc-search`/`#tocSearchWrap` L59/237；`html-gen.py` `-g/--groups` L898、`--welcome` L901、默认文案 L581 | ✅ 成立 |
| 9 | 多文档层漂移: table-guide 含, AGENTS/features 只写 hide | `demos/table-guide.md:100`「列隐藏 (initialHidden/hide)」+ L196/L206 亦提 initialHidden/splitFull；`AGENTS.md:158/243`、`features.md:99/164` 仅 `col.hide` | ✅ 成立 |
| 10 | src/html_gen 是构建产物 | `.gitignore:37` = `src/`（忽略）；`scripts/build-package.py` L21 `runpy.run_path('html-gen.py')` + L32 复制 → 模块级常量（含 TEMPLATE_CONTRACT）自动随构建传播 | ✅ 成立 |
| 11 | 测试基数 312 / 30 文件 | `grep -c "def test_" tests/test_*.py` 合计 312；`ls tests/test_*.py` = 30 | ✅ 成立 |
| 12 | 无 help 相关测试 | `grep -rln 'HELP_\|cmd_help' tests/` → exit 1（零命中） | ✅ 成立 |

**复核结论**：12 条断言中 11 条完全成立，1 条（#7 键覆盖对账）部分成立——「列属性 22」精确吻合，但「options 12」「列类型 5」两处数字少算（实为 13 / 6）。诊断根因（help 不及时、不完整、多层漂移、一次正确写法被判臆造）**事实根基完全成立**。

## 二、设计要点评估（A-G + §7）

### A（U1-C 契约作为单一 Python 数据结构）— 🟢 可行

`build-package.py` 用 `runpy.run_path` 加载根 `html-gen.py` 并复制到 `src/html_gen/`，因此 `TEMPLATE_CONTRACT` 作为模块级常量会**自动随构建传播**，零额外同步动作，与零依赖约束、无 yaml 文件约束均不冲突。风险面（契约与代码同文件耦合）是**设计意图**（单一事实源），且契约是纯数据非逻辑，可维护性可接受。无更优载体需评审（已定 U1-C，仅评可行性 → 可行）。

### B（U2-A render_help 由契约渲染 + 保持观感）— 🟡 基本可行，拼接边界未定义

渲染规则（`━━━` 分隔线、两空格缩进、`key: 说明 / key: 说明` 行式排版）足以复刻现状——HELP_TABLE 的分隔线/缩进/行式均可由契约的 label/desc 字段渲染。§3.2 把 Markdown 语法沿用 `HELP_DOC`（半契约半手写）边界本身清晰（键规范 vs 教程示例）。

但存在一处**未定义边界**：HELP_TABLE 的「结构化格式」JSON 示例块（L675-709）、「点击模式」说明块（L736-740）、tab 示例块（L696-700）**含键名字面量**（如示例里的 `"freeze": true`、`"preview": true`）。这些若保留手写，则「键表只在契约中」被破坏，且 §7 第 7 项 grep 核查会误报；若全契约化，则「示例/教程」性质内容（emoji 描述、嵌套 JSON）无法由扁平键表表达。设计未显式定义「契约渲染段 vs 手写示例段」的拼接规则（见 HG-SEC-164）。

### C（四模板全量覆盖）— 🟡 方向正确，键清单三处遗漏

补齐口径覆盖了 P0（initialHidden/splitFull/pillFilter/format/videos/options 四项/顶层别名）与语义区分（hide vs initialHidden / escape 默认开启），方向正确。但键清单本身不完整（HG-SEC-161：漏 `datetime` 列类型、`clickMode` 单数选项、`feedback.template` 子键），§4 覆盖矩阵数字（列类型 4→5、options 8→12）随之对账错误。

### D（B1/T4-B 双向断言提取规则）— 🟡 正则方向正确，覆盖范围不完整

实测模板用小写 `col./c.` 时**无原生方法调用**（`map/find/filter/some/sort` 全部走大写 `COLUMNS.*`，不被 `\b(?:col|c)\.` 正则命中），因此设计所举白名单例子「col.map 原生方法名」在 layout-table.html 中**并不存在**——白名单的实际需求远低于设计预期。白名单「不得排除真实键」可用「白名单项须在测试内反向断言其不在契约键集」强化（每项注释理由 + 反断言双保险）。

但提取规则**只覆盖 table 维度**（列属性 `col./c.` + 顶层 `OPTIONS.`），存在结构性缺口（HG-SEC-162）：① `col.type` 只抓到 `type` 键、抓不到其**取值**（datetime 等列类型枚举）；② `FB_CFG.*`（feedback 子键）不在 `OPTIONS.*` 正则内；③ `tab.*`（field/match/contains/value）不在正则内；④ actions/videos 嵌套子键不在正则内；⑤ doc/slide/knowledge 的「键」维度（CLI 参数/URL 状态/knowledge item/groups/slide 行为项）**完全没有提取规则**，与 §D「逐模板两条断言」的声明不符。

### E（T5-A 未知键 warn 误报面）— 🟡 方向正确，作用域未定义

「stderr 不阻断、不改退出码」与既有 `NO_OUTPUT_MSG`（L588 stderr + exit 1）先例一致，不污染 stdout 约定。但**作用域未定义**（HG-SEC-163）：未明确「warn 只针对 `columns[]` 对象键 + `options` 键（含嵌套 feedback）+ knowledge item/groups 键，**排除** `data` 行字段与简单数组推导列名」。若实现时对数据行字段也 diff，会误报（`data` 行字段是任意数据列，非配置键）。§7 第 5 项测试数据 `[{"a":1}]`（简单数组）与 §E 作用域语义不对应，无法验证「数据行字段不误报」这一关键边界。

### F（U3-A 键表只在契约中 + table-guide 取舍）— 🟢 合理

table-guide 是展示型 demo，价值在「展示能力」而非「键规范」；CL012 已把 table 补齐（P0），故 table-guide 改引用无信息损失。唯一注意：需与 HG-SEC-164（HELP_TABLE 自身示例块边界）统一处理，避免「改 table-guide 引用」却「HELP_TABLE 示例块仍含键名字面量」的自相矛盾。

### G（U4-B CL012/CL013 拆分）— 🟡 拆分合理，但存在「CL012 即红」缺陷

「基建先行 + table 全量 + 三模板骨架保真」的拆分逻辑本身合理（B1 先绿、文案分段复核、CL010 串行更稳）。但 §3.1 键清单遗漏 `clickMode`（OPTIONS 消费但契约无）会**直接导致 B1 断言 1「模板→契约 ⊆」在 CL012 阶段就红**——这正是评审要求识别「拆分缺陷」的场景。修正方向明确（§3.1 options 补 `clickMode` 标注「单数兼容别名」），非拆分结构错误，但设计 v1.1 必须先闭合，否则 dev 在 CL012 撞墙。

### §7 验证清单 — 🟡 命令可执行，3 处断言弱

- 第 1 项：`importlib` 加载 `html-gen.py` 安全（`if __name__=='__main__'` guard 在 L1474，顶层无副作用）→ ✅ 可执行。
- 第 2 项：`grep -c "initialHidden\|splitFull\|pillFilter\|videos"` **无期望值**——grep -c 返回「匹配行数」非「出现次数」，且一行可含多键；应给**下限（≥1）或每键独立断言**，否则脆断（HG-SEC-166）。
- 第 3 项：`grep -c -- '--'` 语义弱——会匹配示例命令里的 `--` 参数，无法精确断言「CLI 参数段存在」；应断言具体 flag（`--feedback-repo`/`--github-url` 等）各出现 ≥1（HG-SEC-166）。
- 第 5 项：测试数据 `[{"a":1}]`（简单数组）与 §E 作用域不对应（HG-SEC-163）。
- 第 6/7 项：可执行且合理。

## 三、发现项汇总

| # | 严重度 | 摘要 |
|:--|:--|:--|
| HG-SEC-161 | 🟡 | §3.1/§4 键清单三处枚举遗漏：`datetime` 列类型（layout-table.html:471/475/484 消费 `col.type==='datetime'` 日期排序，features.md:159 已载）、`clickMode` 单数选项（L1301-1308 消费，features.md:95 已载「兼容单数 clickMode」）、`feedback.template` 子键（L1101 消费，CL009 v1.3 实装）。§4「列类型 4→5」「options 8→12」应为 4→6、8→13。致 B1「模板→契约 ⊆」在 CL012 即红 |
| HG-SEC-162 | 🟡 | §D B1 提取规则覆盖不完整：只抓 `col./c.`/`OPTIONS.` 顶层键，抓不到列类型取值（datetime）、`FB_CFG.*`（feedback 子键）、`tab.*`（tabs 键）、actions/videos 嵌套子键；doc/slide/knowledge 的键维度（CLI 参数/URL 状态/item/groups/行为项）无任何提取规则，与「逐模板两条断言」「键表只在契约中」不符 |
| HG-SEC-163 | 🟡 | §E 未知键 warn 作用域未定义：未明确「warn 仅针对 columns/options/item 配置键，排除 data 行字段与简单数组推导列名」；§7 第 5 项测试数据 `[{"a":1}]`（简单数组）与作用域不对应，无法验证误报规避 |
| HG-SEC-164 | 🟡 | §B/§3.2 契约渲染段 vs 手写示例段（HELP_TABLE JSON 示例块/点击模式/tab 示例块，均含键名字面量）拼接边界未定义，威胁「键表只在契约中」与 §7 第 7 项 grep 核查一致性 |
| HG-SEC-165 | 🟢 | §1.1「data/_drama-table-history-strategy.json（4 处）」实为 5 处（L55/64/74/91/100） |
| HG-SEC-166 | 🟢 | §7 第 2 项 grep -c 缺期望值（应给下限或每键独立断言）；第 3 项 `grep -c '--'` 断言语义弱（应断言具体 flag） |
| HG-SEC-167 | 🟢 | 断言 #3 探针「分栏模式可见」last change 实为 dad5629（2026-07-19 v3.0）非 07-23；§1.2「HELP_TABLE 最后实质变更 07-23」结论仍成立（经「列类型」=7297a9c 证实），仅该 grep 探针本身不指向 07-23 |

## 四、评分

| 项 | 严重度 | 扣分 |
|:---|:---|:---|
| 12 条断言：11 全成立 + 1 部分（键覆盖对账 options/列类型少算） | — | -5 |
| HG-SEC-161 键清单三处枚举遗漏（致 B1 在 CL012 即红） | 🟡 | -8 |
| HG-SEC-162 B1 提取规则覆盖不完整 | 🟡 | -4 |
| HG-SEC-163 未知键 warn 作用域未定义 | 🟡 | -2 |
| HG-SEC-164 契约/手写拼接边界未定义 | 🟡 | -1 |
| HG-SEC-165..167（🟢×3） | 🟢 | 0 |

得分: **80 / 100（B）**

## 五、结论

**CONDITIONAL PASS（80/B）** — 诊断根因（help 不及时/不完整/多层漂移/正确写法被判臆造）的**事实根基 12 条断言全部实测成立**（11 全成立 + 1 部分，仅「options 12」「列类型 5」两处计数少算），方案方向（契约单一事实源 + 渲染 + 双向守卫 + 未知键 warn + 文档面引用 + 拆分）自洽且可落地，安全面无新增风险。

但存在 **4 个 🟡**（键清单三处枚举遗漏 + B1 提取覆盖不完整 + 未知键 warn 作用域未定义 + 契约/手写拼接边界未定义），其中 HG-SEC-161（漏 datetime/clickMode/feedback.template）会**直接导致 B1 双向断言在 CL012 阶段就红**，与设计「契约是唯一完整枚举键名的地方」的核心承诺相抵触，需设计 v1.1 闭合后方可实施。属非阻断（根因不推翻、决策不重开、修正方向明确且局部）。

## 六、最小修正方向（供设计 v1.1，非本轮实施）

1. **§3.1/§4 补 3 键**：列类型补 `datetime`（「列类型 4→6」）；options 补 `clickMode`（标注「单数兼容别名，向后兼容」，「options 8→13」）；`feedback{repo,key,altKey,template,dataset}` 补 `template`（及 key/altKey，或明确标注 key/altKey 为遗留不文档化）。
2. **§D 明确 B1 提取规则分维度**：table 覆盖「列属性键 + options 顶层键 + 列类型取值 + feedback 子键 + tabs 键 + actions/videos 嵌套子键」；doc/slide/knowledge 单独定义「CLI 参数（从 argparse 提取）/ URL 状态（从 URLSearchParams 提取）/ item·groups 键 / slide 行为项」的提取规则，或在 §G 明确「CL013 如何补三模板断言维度」。
3. **§E 明确 warn 作用域**：仅 `columns[]` 对象键 + `options` 键（含嵌套 feedback）+ knowledge `item`/`groups` 键；显式排除 `data` 行字段与简单数组推导列名。
4. **§B 定义拼接规则**：显式列出「契约渲染段」（键规范）与「手写示例段」（JSON 示例块/点击模式/tab 示例块/Markdown 语法）的边界与拼接顺序，并说明手写示例块内的键名字面量如何处理（剥离键名或标注「见契约」）。
5. **§7 修正**：第 2 项给下限或每键独立断言；第 3 项断言具体 flag；第 5 项测试数据改为「带 columns 的结构化 JSON + 未知键」验证 warn 触发，「简单数组」另测不触发。
6. **🟢 随修**：§1.1「4 处」→「5 处」；§1.2 如保留「分栏模式可见」探针则标注其 07-19（或改引「列类型」= 07-23）。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:---|
| — | （无阻塞项；4 🟡 为设计 v1.1 闭合项，3 🟢 随修；非本轮 FAIL 阻断） | — |
