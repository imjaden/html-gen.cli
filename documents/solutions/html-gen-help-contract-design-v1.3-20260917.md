# html-gen help 契约治理设计 v1.3（help 单一事实源）

> 日期: 2026-09-17
> 状态: 设计（CL012 已实现并审计 PASS；v1.3 = 审计 finding 直接订正）
> 闭环: HTML-GEN-CL012（契约源 + 渲染 + 守卫）/ HTML-GEN-CL013（四模板补齐 + 文档面）
> 决策（全量，用户定稿）: T1-C T2-A T3-B T4-B T5-A T6-A T7-A · U1-C U2-A U3-A U4-B U5-B
> 基线链: v1.0（`4649053`，CONDITIONAL PASS 80/B）→ v1.1（`ba7b547`，折入 HG-SEC-161..167，复审 CONDITIONAL PASS 85/B）→ v1.2（`a7cdc24`，折入 HG-SEC-168..171）→ **v1.3（折入 HG-SEC-178/179 订正）**
> 评审报告: v1.0 / v1.1 设计评审报告（push 至 `2ed8078`）；**CL012 实现审计** `documents/review/help-contract-impl-audit-v1.0-20260917.md`（`68b7c4b`，PASS 93/100）
> 说明: v1.3 = CL012 实现审计 3 条 finding 的**直接订正**（HG-SEC-178/179 属本档表述订正；HG-SEC-177 属测试侧，
> 已同批修复并验证），按用户指示「直接修正，不走 1A 协议」，不另开评审轮次。
> 开放决策项: 无
> 触发事件: 他项目依 `html-gen help table` 改造前端 → 列默认隐藏不生效 + 被判定「属性名臆造」
> 前置: CL010 实现已落地（`5f447fc`，审计/推送另计）；CL011 ✅

## 0. 变更摘要

### v1.0 → v1.1（首轮评审）

| Finding | 严重度 | v1.0 缺陷 | v1.1 修正 |
|:---|:---|:---|:---|
| HG-SEC-161 | 🟡 | §3.1/§4 键清单三处枚举遗漏（`datetime` 列类型 / `clickMode` 单数选项 / `feedback` 子键），致 B1 在 CL012 即红 | §3.1 补齐三处；§4 订正「列类型 4→6」「options 8→13」；§G 明确 CL012 **仅启用 table 维度**断言 |
| HG-SEC-162 | 🟡 | §D 提取规则只覆盖 table 顶层 `col./c./OPTIONS.`，无列类型取值/`FB_CFG.*`/`tab.*`/嵌套子键，doc/slide/knowledge 无规则 | §D 重写为**分维度规则表**（table 6 维 + doc/slide/knowledge 4 维），并标注各维度的启用阶段 |
| HG-SEC-163 | 🟡 | §E 未知键 warn 作用域未定义 | §E 明确校验对象与**排除项**（data 行字段、简单数组推导列名）；§7 第 5 项改双用例 |
| HG-SEC-164 | 🟡 | §B/§3.2 契约渲染段 vs 手写示例段拼接边界未定义 | 新增 **§B.3 三段式拼接规则** + 键名字面量处理口径 |
| HG-SEC-165 | 🟢 | §1.1 drama「4 处」实为 5 处 | §1.1 订正（含行号） |
| HG-SEC-166 | 🟢 | §7 第 2/3 项断言语义弱、缺期望值 | §7 改为逐键/逐 flag 独立断言 |
| HG-SEC-167 | 🟢 | 断言 #3 探针「分栏模式可见」实为 07-19 | §1.2 订正探针口径（分栏模式可见=07-19；列类型=07-23） |

> 评审确认：§1 的 12 条事实断言除 #7 计数（已由 HG-SEC-161 闭合）外**全部实测成立**；诊断根因与方案方向不变，决策不重开。
> 自查补充（v1.1 内部，超出 finding 范围）：§7 全部命令已在实现前跑过**形态自检**（可执行性 + 期望值语义）；
> 其中第 2 项发现并修正一处假阳性——裸 `grep -q clickMode` 被 `clickModes` **子串**骗过（缺失该键时仍报 OK），
> 已改为词边界 `grep -qE '\b<key>\b'`（macOS BSD grep 实测有效）。属 HG-SEC-166 同源类的又一实例。

### v1.1 → v1.2（复审）

| Finding | 严重度 | v1.1 缺陷 | v1.2 修正 |
|:---|:---|:---|:---|
| HG-SEC-168 | 🟡 | §D CLI 提取规则 `X\.add_argument\('--…'` 在「短形在前」的调用上漏捕（`-i/--input`、`-o/--output`、`-d/--data`、`-g/--groups`）；§D 且缺 table CLI 行 | §D CLI 规则改 `add_argument\([^)]*'(--[a-z-]+)'`（同一调用内扫长形；短形为别名不计键）；补 table CLI 维度行。实测：doc 9 / slide 8 / table 9 / knowledge 10，与 §3 清单逐项吻合 |
| HG-SEC-169 | 🟡 | §D knowledge item 规则 `i?tem\.([a-zA-Z_]\w*)` 误捕模板运行时状态（`item.active` / `item.filtered`）且漏 `icon` | §D 改为**双源提取**：模板 `item\.([a-zA-Z_]\w*)` ∪ 生成器 `item\.get\('icon'\)`（`cmd_knowledge` L571 自动分组推导）；`active`/`filtered` 入白名单（注释理由 + 反断言） |
| HG-SEC-170 | 🟡 | 列类型取值规则只抓显式 `=== '…'` 分支，漏隐式默认 `string`（模板无 `=== 'string'` 分支） | §D 规则改为「显式分支 ∪ {默认 `string`}」（默认值以常量注入测试），断言 == 契约 6 类 |
| HG-SEC-171 | 🟢 | §C/§3.1 引「模板 L471/475/484」行号微瑕（datetime 分支实为 L471/475） | 行号订正为 L471/475 |

### v1.2 → v1.3（CL012 实现审计 finding 订正）

| Finding | 严重度 | v1.2 缺陷 | v1.3 订正 |
|:---|:---|:---|:---|
| HG-SEC-178 | 🟢 | §B.3 写「拼接顺序 `label → ① → ② → ③`，与现状段落顺序一致」自相矛盾（现状实为 ②→①） | §B.3 订正为 `{label/tagline} → ② → ①`；并注明 ③ 语法说明段仅部分主题存在（table 无） |
| HG-SEC-179 | 🟢 | §3.1 低估嵌套 schema：`actions[]` 只列 6 键、`videos` 只写 `{maxShow}` | §3.1 订正为 actions 7 键（补 `class`）、videos 项 5 键（补 `url`/`title`/`duration`/`platform`） |

> HG-SEC-177（🟡，测试侧：`test_08`「契约→help」用**全文词边界**匹配，删段时 8/18 键漏捕）不属本档，
> 已同批直接修复：`test_08` 改为与 `test_09` 共用 `spec_key_tokens()`（`key:` 词元提取，含 `?tab` 等前缀键；
> 并单列 behaviors 的 `key … — 说明` 形态），经变异测试验证 —— `section_order` 删 `options` 段时
> `test_08` 转红并指名全部 18 键，还原后 `14 passed, 7 subtests`。

## 1. 问题

### 1.1 触发事件与事实更正（T7-A / U5-B）

下游页面 `script-miner/efficiency/git-cloner.html:479` 写：

```js
{key: 'path', label: '本地路径', width: '240px', initialHidden: true, preview: true},
```

评审据 `html-gen help table` 的一行「`preview: 分栏模式可见 / hide: 列隐藏`」判定：
「规范是 `hide`，`initialHidden` 是臆造的属性名，规范里没有这个键」。

**事实更正（本条即 U5-B 的留痕）**：

- `initialHidden` **真实存在**，非臆造。实现见 `layout-table.html:373-374`，引入于 `38bdc9f`（2026-08-12
  「table 模板 — pills 斜杠切分 + initialHidden 默认隐藏 + 分栏详情全列渲染 (5 测试)」）。
- 仓库自证在用：`data/_countries-data.json`（6 处）、`data/_drama-table-history-strategy.json`
  （**5 处**：L55/64/74/91/100）、`tests/test_initial_hidden_split.py`（5 用例）、`demos/table-guide.md:100`。
- 结论应为「**未文档化**」而非「臆造」：`html-gen.py` 的 HELP_TABLE、`AGENTS.md`、`features.md`、
  `README.md/.zh.md`、`skills/**` 五处面向人的文档**都没有收录该键**。
- 且该下游页面是**自写表格实现**（自带 `<style>`、994 行、v2.0.0@2026/09/16），`grep colVisibility /
  ⚙ / columnResize` 零命中、`renderHead/renderBody` 对 `COLUMNS` 无任何 hide/initialHidden 过滤
  → 写 `initialHidden` 或 `hide` **都不生效**；其样式亦来自自带 CSS 而非 style-guide。
  两个症状（样式不符预期、配置歧义）**同源**：移植了配置「形状」，未移植模板「能力」。

因此本设计的根因判定是：**help 是使用者唯一可得的键规范，但它既不及时、也不完整，且与其他
文档层互相矛盾**——一次正确的写法会被规范判成错误。

### 1.2 证据链（实测）

时效（help 正文是硬编码字符串，无同步机制）：

- `html-gen.py` L606-835 全为 `HELP_*` 常量；`cmd_help()`（L838）直接 `print`。
- HELP_TABLE 正文最后实质变更 `7297a9c`（2026-07-23, v3.1，以 `-S'列类型'` 为证）；
  `-S'分栏模式可见'` 指向 `dad5629`（2026-07-19, v3.0）——该探针早于最后变更，二者不矛盾。
- HELP_DOC / HELP_SLIDE / HELP_KNOWLEDGE 内容自 `8c67e8b`（2026-07-14）起零更新。
- 同期 banner 已报 `v3.3(2026-08-28)`（`__version__` 来自独立变量）→ 自报版本与正文不同代。
- 模板侧 2026-08-12 起新增：initialHidden、splitFull、videos 类型、pillFilter、format、
  URL 状态（`?tab&q&split`）、favicon 注入、GitHub Issue 反馈通道、CL010 默认转义——**均未进 help**。

完整（模板实际消费 vs help 记录，明细见 §4）：

- table：模板消费 **22** 个列属性、**13** 个 options、**6** 个列类型；help 只记 13 / 8 / 4。
  缺 initialHidden / splitFull / pillFilter / format / videos / datetime（列属性·列类型）与
  searchFields / showIndex / defaultFilter / feedback / clickMode（options）；`feedback` 子键全缺。
- doc：缺 Bare 模式（`?sidebar=0&toolbar=0`）与正文宽度三级（`?width=narrow|medium|wide`）。
- slide：缺侧栏搜索（`.slide-toc-search` / `#tocSearchWrap`）。
- knowledge：条目 schema 基本对齐，缺 CLI 参数（`-g/--groups`、`--welcome`）与 `item.icon`。
- 四模板 help 主题页 **0 覆盖 CLI 参数**：`metadata / welcome / groups / favicon / github-url /
  home-url / quiet / feedback-repo` 在 L604-835 命中数全部为 0。

歧义（语义未区分）：

- `hide` = **永不可见**（`visibleCols()` L397 排除；分栏详情 L1144 也排除；筛选亦不参与）。
- `initialHidden` = **默认收起**（L373-374；⚙️ 可开启；分栏详情仍全列渲染）。
- help 用一行「`hide: 列隐藏`」糊过两者 → 读者无法区分；照 help 改成 `hide` 反而把
  「默认可开启」变成「彻底删除」。
- `escape` 自 CL010（`5f447fc`）起**默认开启**、`escape:false` 才豁免，help 只写「escape: HTML转义」，
  读者会误判为 opt-in。

无兜底：

- 全链路无未知键校验（`html-gen.py` 无 validate / unknown 分支）→ 写错键静默忽略。
  help 事实上是唯一契约，却又是最旧的一份。

### 1.3 多文档层各自持有不同子集（C3 的直接动因）

同一批键/能力散落在 ≥7 处，且互不一致：

| 文档层 | initialHidden | splitFull | 状态 |
|:---|:---:|:---:|:---|
| `html-gen.py` HELP_TABLE | ✗ | ✗ | 最旧（07-23） |
| `AGENTS.md`（模板类型详解） | ✗ | ✗ | 有 `col.hide` |
| `features.md` | ✗ | ✗ | 有 `col.hide`（另有 datetime/clickMode 行） |
| `demos/table-guide.md` / `.html` | ✓ | ✓ | 最新（含 defaultFilter/showIndex） |
| `skills/html-gen-table/SKILL.md` | ✗ | ✗ | 部分列属性 |
| `README.md` / `README.zh.md` | ✗ | ✗ | 基本无键表 |
| `documents/*handbook` | ✗ | ✗ | 无键表 |
| `ops` profile skill 契约 | ✓ | ✓ | 与 help 冲突 |

→ 无单一事实源，任何一方更新都不触发其余方同步。

### 1.4 影响

- 使用者按 help 写配置 → 静默失效或语义走偏（本次事件）。
- 评审以 help 为事实源 → 会把正确写法判成错误（本次事件）。
- 每新增一个模板能力，漂移面 +1；修复成本随层级数量放大。

## 2. 设计决策

### A. 契约源：html-gen.py 内单一 Python 数据结构（U1-C）

新增模块级常量 `TEMPLATE_CONTRACT`（建议置于 Help System 区，L604 前），四个模板各一节点：

```python
TEMPLATE_CONTRACT = {
    'table': {
        'label': 'A 型 · 数据表格 JSON 格式',
        'tagline': 'Cinema 纪律化宽度模型',
        'cli': [ ... ],            # 子命令参数：flag / 取值 / 语义 / 默认
        'data': {                  # 数据契约
            'top_level': [ ... ],
            'columns': [ ... ],    # 列属性：key / 取值 / 语义 / 默认
            'column_types': [ ... ],
            'tabs': [ ... ],
            'options': [ ... ],
            'feedback': [ ... ],   # options.feedback 子键
            'actions': [ ... ],    # 嵌套项
            'videos': [ ... ],     # 嵌套项
        },
        'url_state': [ ... ],      # URL 级状态
        'behaviors': [ ... ],      # 交互能力（不带实现细节）
    },
    'doc': { ... }, 'slide': { ... }, 'knowledge': { ... },
}
```

要点：

- 契约是**唯一**枚举键名的地方（含列类型取值与嵌套子键）；help、测试、文档引用全部指向它。
- `src/html_gen/html-gen.py` 是 `scripts/build-package.py` 的构建产物（`.gitignore:37` 忽略，
  实测 `runpy.run_path('html-gen.py')` 加载 → 契约自动随构建传播，零额外同步动作）。
- 不引入外部依赖、不引入新文件格式（保持零依赖），不新增 yaml 文件。

### B. help 由契约渲染（U2-A）

- 新增 `render_help(topic) -> str`，由契约生成该主题的帮助正文；
  `cmd_help()` 改为 `print(render_help(topic) if topic in TEMPLATE_CONTRACT else HELP_OVERVIEW)`。
- **保持现有输出观感**：同样的 `━━━` 分隔线、同样的缩进与 `key: 说明 / key: 说明` 行式排版，
  仅内容由契约驱动；不改变既有段落顺序。
- 顶部 banner 的 `v{__version__}({__release_date__})` 保持现状（版本号独立演进）。
- 边界：`prompt` / `demo` 两个 help 主题**不进契约**（它们描述 CLI 子命令而非数据契约），
  保持手写；`HELP_OVERVIEW` 保持手写，但主题清单由契约键 + 手写主题合并生成，避免新增模板时漏列。
- `--help`（argparse）不动，与 `help <topic>` 并存。

#### B.3 三段式拼接规则（HG-SEC-164 闭合）

每个主题页明确由三段构成，边界如下：

| 段 | 性质 | 来源 | 含键名字面量? | 处理 |
|:---|:---|:---|:---|:---|
| ① 键规范段 | 结构化 | **契约渲染** | 是（由契约生成） | `render_help` 输出 |
| ② 教程/示例段 | 叙述 | **手写常量**（如 `HELP_TABLE_EXAMPLES`） | 是（JSON 示例块/tab 示例块） | 保留手写，**并在段首标注**「示例，键以键规范段为准」 |
| ③ 语法/说明段 | 叙述 | **手写常量**（如 Markdown 语法沿用 `HELP_DOC`） | 否 | 原样保留 |

- 拼接顺序（**v1.3 订正**，HG-SEC-178）：`{label/tagline} → ② → ①` —— 现状 help 的实际段落顺序是
  **示例段在键规范段之前**（v1.2 原写「① → ② → ③，与现状段落顺序一致」自相矛盾：既称 ①→②→③ 又声称与现状一致，
  而现状实为 ②→①）。③ 语法说明段仅在部分主题存在（如 doc 的 Markdown 语法），table 主题无 ③ 段。
- 键名字面量口径：②中的示例 JSON **允许**出现键名（它是示例而非规范），但由 §7 第 7 项
  grep 核查时**显式排除** `HELP_*_EXAMPLES` 常量区（核查基于契约与键规范段，不扫示例段）；
  ③不含键名。
- `render_help` 的职责边界：只负责 ①；②③由调用方按固定顺序拼接（或由 `render_help` 内部按契约
  的 `examples` 指针拼接，二选一，dev 在 CL012 落地时择一并写入注释）。

### C. 覆盖范围：四模板全量（A2 / T2-A / T3-B）

补齐口径：

- **table（P0）**：
  - 列属性补 `initialHidden`、`splitFull`、`pillFilter`、`format`、`videos`（含 `videos.maxShow`）；
  - 列类型补 `videos` 与 **`datetime`**（日期列专用排序，模板 L471/475 消费，features.md:159 已载）；
  - options 补 `searchFields`、`showIndex`、`defaultFilter`、`feedback`、**`clickMode`**（单数兼容别名，
    模板 L1301-1308 消费，features.md:95 已载）；
  - `feedback` 子键补全：`{repo, dataset, key, altKey, template}`（模板 L357 注释 + `FB_CFG.*` 消费；
    `key`/`altKey` 标注「主键/备用主键字段，默认 name/空」，`template` 标注「Issue 模板名，默认 data-fix.yml」）；
  - 顶层补 title / subtitle / output 与 `data|rows` 别名；
  - 显式写出语义：`hide`（永不可见）vs `initialHidden`（默认收起·可开启·分栏全列）、
    `escape` 默认开启（CL010）、`preview` 的「任一列 preview 则分栏只显 preview 列」规则、
    `width` 默认 120px（actions 100px）、`search` 默认 true、`showIndex` 默认 false、
    `columnResize` 默认 true、`pageSize` 默认 30、`videos.maxShow` 默认 3。
- **doc**：补 Bare 模式（`?sidebar=0&toolbar=0`）与宽度三级（`?width=narrow|medium|wide`，默认 960px）。
- **slide**：补侧栏搜索（T3-B：只记「侧栏支持关键字过滤」，不写防抖/实现细节）。slide 无 URL 状态，如实写明。
- **knowledge**：补 `-g/--groups`、`--welcome`（含默认文案）、`--title` 默认「知识库」、
  `item.icon`、数据源三态（数组 / `{items|data}` / 顶层 `output`）。
- **四模板统一新增「CLI 参数」段**（T2-A）：`-i/-d/-o/--title/--subtitle/--metadata/--welcome/--groups/
  --favicon/--github-url/--home-url/--feedback-repo/--quiet`，逐模板列各自支持项，
  并写明 env 兜底（`HTML_GEN_FAVICON` / `HTML_GEN_GITHUB_URL` / `HTML_GEN_HOME_URL` / `HTML_GEN_FEEDBACK_REPO`）
  与「显式空串禁用」约定。

### D. 守卫测试：双向断言（B1 / T4-B）— 分维度提取规则（HG-SEC-162 闭合）

新增 `tests/test_help_contract.py`。**两类断言**：①模板消费 → ⊆ 契约（template → contract）；
②`render_help(type)` → 含契约全部键名（contract → help）；③契约键名 ⊆ help 输出（help → contract），
三者构成真正的双向闭合。

提取规则**按维度定义**，不得笼统表述为「col./OPTIONS.」：

| 维度 | 来源 | 提取规则（正则） | 启用阶段 |
|:---|:---|:---|:---|
| table 列属性 | `layout-table.html` | `\b(?:col|c)\.([a-zA-Z_]\w*)` | CL012 |
| table options 顶层 | `layout-table.html` | `OPTIONS\.([a-zA-Z_]\w*)` | CL012 |
| table feedback 子键 | `layout-table.html` | `FB_CFG\s*&&\s*FB_CFG\.([a-zA-Z_]\w*)` + `FB_CFG\.([a-zA-Z_]\w*)` | CL012 |
| table 列类型取值 | `layout-table.html` | `\.type\s*===\s*'([a-z]+)'` 得显式分支 **∪ {默认 `string`}**（模板无 `'string'` 分支，默认值以常量注入测试）→ 断言 == 契约 6 类 | CL012 |
| table tabs 键 | `layout-table.html` | `\btab\.([a-zA-Z_]\w*)` + `\bt\.(key\|label\|field\|match\|contains\|value)\b` | CL012 |
| table 嵌套子键 | `layout-table.html` | actions 项字段 / videos 项字段（按模板变量名提取；无法提取时降级为**显式清单 + 存在性断言**） | CL012 |
| table CLI | `html-gen.py` | `add_argument\([^)]*'(--[a-z-]+)'`（`t = sub.add_parser('table')` 块内；短形 `-d/-o` 为别名不计） | CL013 |
| doc CLI | `html-gen.py` | `add_argument\([^)]*'(--[a-z-]+)'`（`d = sub.add_parser('doc')` 块内） | CL013 |
| doc URL | `layout-doc.html` | `params\.get\('([a-z]+)'\)` | CL013 |
| slide 行为项 | `layout-slide.html` | 正则不可提取 → **显式清单 + 模板特征串存在性断言**（如 `.slide-toc-search`） | CL013 |
| slide CLI | `html-gen.py` | `add_argument\([^)]*'(--[a-z-]+)'`（`s = sub.add_parser('slide')` 块内） | CL013 |
| knowledge CLI | `html-gen.py` | `add_argument\([^)]*'(--[a-z-]+)'`（`k = sub.add_parser('knowledge')` 块内） | CL013 |
| knowledge item | `layout-knowledge.html` + `html-gen.py` | **双源**：`item\.([a-zA-Z_]\w*)`（模板）∪ `item\.get\('([a-z]+)'\)`（生成器自动分组推导）；`active`/`filtered` 入白名单 | CL013 |
| knowledge groups | `layout-knowledge.html` | `\bg\.([a-zA-Z_]\w*)` | CL013 |

**白名单纪律**（评审强化要求）：

- 白名单只允许排除「非配置项」（提取正则误捕的原生方法/局部变量），**不得排除真实键**。
- 白名单每项必须在测试内写注释说明理由，并配**反向断言**：`assert 白名单项 not in 契约键集`
  （即白名单项确实不是契约键），双保险。
- 评审实测：layout-table.html 中 `col./c.` 无原生方法调用（`map/find/filter/sort` 均走大写 `COLUMNS.*`），
  白名单实际需求低于 v1.0 预期；白名单长度应趋近于 0，超 3 项需在测试注释说明原因。

**失败信息**必须指名「哪个键 / 来源文件 / 修复动作」，避免只报 `assert failed`。

### E. 未知键 warn（T5-A）— 作用域定义（HG-SEC-163 闭合）

**校验对象（白名单式，只校验配置键）**：

- table：`columns[].key` 属性名、`columns[].type` **取值**、`options` 顶层键、`options.feedback` 子键；
- knowledge：`item` 键、`groups` 键。

**显式排除（不校验）**：

- `data[]` 行内字段名（业务数据列，任意命名，非配置键）；
- 简单数组格式（`[{...}]` 无 `columns`）时由数据键推导出的列名（`{'key': k, 'label': k}`）；
- `render` / `handler` 等指向自定义函数名的值（是值不是键）。

**行为**：未知键写 **stderr**（`⚠️ 未知列属性: xxx（见 html-gen help table）`），
**不阻断、不改退出码**（与既有 `NO_OUTPUT_MSG` 的 stderr 先例一致，不污染 stdout 约定）。
`doc` / `slide` 输入是 Markdown，无键可校验，不适用。不做 `--strict`（T5-A 定档；后续需要再单开）。

### F. 文档面：引用不复制（U3-A）

- 键表**只在契约中存在**；下列文档改为引用并指向 `html-gen help <type>` 与 `TEMPLATE_CONTRACT`：
  `AGENTS.md`（模板类型详解节）、`features.md`、`README.md` / `README.zh.md`、
  `skills/html-gen-cli-spec`、`skills/html-gen-{table,doc,slide,knowledge}`。
- `demos/table-guide.md` / `.html` 是**展示型 demo**，允许保留「功能清单」叙述，
  但其现有键名罗列（如 `列隐藏 (initialHidden/hide)`）改为指向 help，不再单独维护键表；
  与 §B.3 的 ② 段口径统一（示例可含键名，规范只在契约）。
- 常驻自动化只覆盖 help↔模板↔契约（§D）；文档面用一次性 grep 核查（列入 §7 验证清单），
  不写进测试（避免测试随文档风格变化而脆断）。

### G. 闭环拆分（U4-B，HG-SEC-161/162 修正版）

- **CL012｜基础设施**：`TEMPLATE_CONTRACT` + `render_help()` + `cmd_help` 改造 +
  `test_help_contract.py` + 未知键 warn。**断言启用范围 = table 维度**（§D 表中 CL012 行）；
  doc/slide/knowledge 在契约中仅有**骨架节点**（内容 = 现状 help 文案，不新增键模型），
  其断言在 CL013 启用——避免「骨架不全 → B1 即红」。
- **CL013｜四模板补齐 + 文档面**：契约补齐 doc/slide/knowledge 全维度 + 四模板 CLI 参数段 +
  slide 侧栏搜索 + doc Bare/宽度 + knowledge CLI 项；启用 doc/slide/knowledge 维度断言；
  同步文档面引用改造与测试计数。
- 理由：基础设施可独立验证（B1 先绿），文案补齐可分段复核；CL010 仍在跑，串行更稳。

### H. 交付（T6-A）

本会话即 html-gen ops，负责需求沟通与设计编写；实施阶段按项目既有闭环派发（dev → review）。
本轮不涉及跨仓写操作，`script-miner` 侧不触碰（D4）。

## 3. 键清单（契约内容源，四模板）

### 3.1 table

顶层 JSON：`columns` / `data`（别名 `rows`）/ `tabs` / `options` / `title` / `subtitle` / `output`

CLI：`-d --data`（必填）、`--title`、`--subtitle`（纯文本，`\n` → `<br>`；显式空串清空）、
`-o --output`（三态：CLI > JSON `output` > 中断）、`--github-url`、`--home-url`、`--favicon`、
`--feedback-repo`、`--quiet`

列类型（6）：`string`(默认) / `number` / `pills` / `videos` / `actions` / `datetime`

列属性（22）：`key` `label` `type` `width` `sortable` `locale` `freeze` `stickyRight` `preview`
`hide` `initialHidden` `splitFull` `quickFilter` `pillFilter` `onCellClick` `onClick` `escape`
`render` `class` `format` `videos` `actions`

嵌套（**v1.3 订正**，HG-SEC-179 —— 原 v1.2 低估嵌套 schema）：
`actions[]` = `label` `icon` `copyKey` `hrefKey` `handler` `desc` `class`（7 项，`class` 为按钮附加 CSS 类名）；
`videos` 项 = `url` `title` `duration` `platform` `maxShow`（5 项，`maxShow` 默认 3）

tabs（6）：`key` `label` `field` `match` `contains` `value`

options（13）：`pageSize` `exportCSV` `rowSelect` `search` `searchFields` `showIndex` `clickModes`
`clickMode`(单数兼容别名) `columnResize` `columnsSplit` `modalRenderer` `defaultFilter` `feedback`

`options.feedback` 子键（5）：`repo` `dataset` `key` `altKey` `template`

点击模式：`tab` / `modal` / `split` / `expand`

URL 状态：`?tab` `?q` `?split`

### 3.2 doc

CLI：`-i --input`（必填）、`-o --output`、`--title`、`--subtitle`、`--metadata`、
`--github-url`、`--home-url`、`--favicon`、`--quiet`

URL：`?sidebar=0` / `?toolbar=0`（Bare 模式）、`?width=narrow|medium|wide`（默认 medium=960px）

另：Markdown 语法子集沿用现有 `HELP_DOC` 内容（块级/行内/Callout/不支持项）→ 按 §B.3 归入 ③ 段。

### 3.3 slide

CLI：`-i --input`（必填）、`-o --output`、`--title`、`--subtitle`、`--github-url`、`--home-url`、
`--favicon`、`--quiet`（无 `--metadata`）

行为：h2 分页（h1 封面）、←→/Space/Home/End 翻页、F 全屏、底部进度点、localStorage 记忆、
侧栏 H3 开关、侧栏关键字过滤、>50 个 h2 显示性能警告

URL：无

### 3.4 knowledge

CLI：`-d --data`（必填）、`-g --groups`、`--title`（默认「知识库」）、`--subtitle`、
`--welcome`（默认「从上方类目选择，浏览整理的知识内容。」）、`-o --output`、`--github-url`、
`--home-url`、`--favicon`、`--quiet`

数据：数组 或 `{items|data, output}`

item（7）：`title`(必填) `group`(必填) `section` `badge` `desc` `url` `icon`

groups（3）：`key` `label` `icon`

## 4. 键覆盖矩阵（现状 → 目标）

| 模板 | 维度 | 现状 help | 契约目标 | 缺口 |
|:---|:---|---:|---:|:---|
| table | 列属性 | 13 | 22 | initialHidden splitFull pillFilter format videos + actions 嵌套 |
| table | options | 8 | 13 | searchFields showIndex defaultFilter feedback clickMode |
| table | options.feedback 子键 | 0 | 5 | repo dataset key altKey template |
| table | 列类型 | 4 | 6 | videos datetime |
| table | 顶层键 | 2 | 7 | title subtitle rows 别名 |
| table | CLI 参数 | 0 | 9 | 全缺 |
| doc | CLI 参数 | 0 | 9 | 全缺 |
| doc | URL 特性 | 0 | 2 | Bare / 宽度 |
| slide | CLI 参数 | 0 | 8 | 全缺 |
| slide | 行为项 | 7 | 8 | 侧栏搜索 |
| knowledge | CLI 参数 | 0 | 10 | 全缺 |
| knowledge | item / groups | 6 / 3 | 7 / 3 | item.icon |

## 5. 测试影响

- 新增 `tests/test_help_contract.py`：
  - CL012：table 六维度单向断言（template → contract）+ 契约↔help 双向断言 + `render_help` 冒烟；
  - CL013：doc/slide/knowledge 各维度断言接入。
  预计每模板 3-4 例，合计约 12-14 例。
- 现有测试基数 **312 用例 / 30 文件**（`AGENTS.md:299`）→ 需同步为新增后的实测值；
  `test_prompt_site.py` 等对文件数/计数的硬断言按项目既有做法一并核对（prompts/ 内无 help 文本副本，已实测）。
- 现有 help 相关测试：**无**（`grep -rln 'HELP_\|cmd_help' tests/` 零命中）→ 本改动不触发既有断言。
- 回归基线：`.venv/bin/pytest tests/ -q` 全绿（按项目规范跑全量，非仅新文件）。

## 6. 观察项

- O-1：`render_help` 输出与旧文本的 **diff 需人工过目一次**，确认是「补内容」而非「改风格」；
  若风格被迫变化，需在 CL012 提交说明里单独标注。
- O-2：`src/html_gen/` 为构建产物（gitignored），本地副本已过期；CL012 落地后应由
  `scripts/build-package.py` 重建一次，验证契约随构建传播。
- O-3：文档面 grep 核查是一次性的；若后续文档再长出键表，B1 无法自动发现（已知边界，接受）。
- O-4：非契约 help 主题（`prompt` / `demo`）保持手写，其时效性不在本方案覆盖范围。
- O-5：slide 的「行为项」与 ③ 段叙述无法由正则提取，只能靠显式清单 + 特征串断言维持，
  新增 slide 交互能力时需手工登记（B1 无法自动发现）。

## 7. dev 验证清单

```bash
# 1. 契约与渲染存在
python3 -c "import importlib.util; spec=importlib.util.spec_from_file_location('hg','html-gen.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(sorted(m.TEMPLATE_CONTRACT)); print(m.render_help('table')[:200])"

# 2. help 输出含 P0 键（逐键独立断言，期望全部 OK）
#    ⚠️ 必须用词边界 \b：裸 grep 会被子串假阳性骗过（实测 `clickMode` ⊂ `clickModes`，
#    裸 grep -q clickMode 在缺失该键时仍报 OK）。同理适用任何前缀关系键。
for k in initialHidden splitFull pillFilter format videos datetime clickMode searchFields showIndex defaultFilter; do
  html-gen help table | grep -qE "\b$k\b" && echo "OK $k" || echo "MISSING $k"
done

# 3. hide 与 initialHidden 语义并列出现（期望 ≥2 行，且语义可区分）
html-gen help table | grep -n "initialHidden\|hide" | head

# 4. 各模板 CLI 参数段存在（逐 flag 独立断言）
#    table 期望: --data --title --subtitle --output --github-url --home-url --favicon --feedback-repo
for f in --data --feedback-repo; do html-gen help table | grep -q -- "$f" && echo "OK $f" || echo "MISSING $f"; done
for f in --metadata --input; do html-gen help doc | grep -q -- "$f" && echo "OK $f" || echo "MISSING $f"; done
html-gen help doc | grep -q "width=narrow" && echo "OK doc-width" || echo "MISSING doc-width"
html-gen help slide | grep -q "搜索" && echo "OK slide-search" || echo "MISSING slide-search"
for f in --groups --welcome; do html-gen help knowledge | grep -q -- "$f" && echo "OK $f" || echo "MISSING $f"; done

# 5. 未知键 warn 双用例
# (a) 结构化 JSON + 未知列属性 → 期望出现「未知」
printf '{"columns":[{"key":"a","label":"A","bogusKey":1}],"data":[{"a":1}]}' > /tmp/t1.json
html-gen table -d /tmp/t1.json -o /tmp/t1.html 2>&1 | grep -q "未知" && echo "OK 误报-结构化" || echo "MISSING 误报-结构化"
# (b) 简单数组（数据行字段任意命名）→ 期望不出现「未知」（不误报）
printf '[{"任意字段名":1}]' > /tmp/t2.json
html-gen table -d /tmp/t2.json -o /tmp/t2.html 2>&1 | grep -q "未知" && echo "FAIL 简单数组误报" || echo "OK 简单数组不误报"

# 6. 守卫测试
.venv/bin/pytest tests/test_help_contract.py -q

# 7. 全量回归（项目规范）
.venv/bin/pytest tests/ -q

# 8. 文档面残留检查（键表应只在契约；②示例段按 §B.3 排除）
grep -rn "initialHidden" AGENTS.md features.md README.md README.zh.md skills/ | grep -v "html-gen help"
echo "(预期：无裸键表；demos/table-guide.* 允许保留功能叙述但不得再枚举键名)"
```

## 8. 提交计划

```
CL012  feat@cli: help 契约单一事实源 — TEMPLATE_CONTRACT + render_help + 双向守卫测试 + 未知键 warn
CL013  docs@help: 四模板 help 补齐（initialHidden/datetime/CLI 参数/Bare/侧栏搜索）+ 文档面改为引用契约
```

文件变更（预期）：

- CL012：`html-gen.py`、`tests/test_help_contract.py`（新增）、`AGENTS.md`（测试计数）
- CL013：`html-gen.py`（契约补齐）、`AGENTS.md`、`features.md`、`README.md`、`README.zh.md`、
  `demos/table-guide.md` / `.html`、`skills/html-gen-cli-spec` 与四个模板 skill、
  `documents/solutions/html-gen-help-contract-design-v1.1-20260917.md`（本文件）
