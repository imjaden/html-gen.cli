# html-gen help 契约治理设计 v1.0（help 单一事实源）

> 日期: 2026-09-17
> 状态: 设计（待评审）
> 闭环: HTML-GEN-CL012（契约源 + 渲染 + 守卫）/ HTML-GEN-CL013（四模板补齐 + 文档面）
> 决策（全量，用户定稿）: T1-C T2-A T3-B T4-B T5-A T6-A T7-A · U1-C U2-A U3-A U4-B U5-B
> 开放决策项: 无
> 触发事件: 他项目依 `html-gen help table` 改造前端 → 列默认隐藏不生效 + 被判定「属性名臆造」
> 前置: CL010 实现已落地（`5f447fc`，审计/推送另计）；CL011 ✅

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
- 仓库自证在用：`data/_countries-data.json`（6 处）、`data/_drama-table-history-strategy.json`（4 处）、
  `tests/test_initial_hidden_split.py`（5 用例）、`demos/table-guide.md:100`。
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
- HELP_TABLE 正文最后实质变更 `7297a9c`（2026-07-23, v3.1）；HELP_DOC / HELP_SLIDE / HELP_KNOWLEDGE
  内容自 `8c67e8b`（2026-07-14）起零更新。
- 同期 banner 已报 `v3.3(2026-08-28)`（`__version__` 来自独立变量）→ 自报版本与正文不同代。
- 模板侧 2026-08-12 起新增：initialHidden、splitFull、videos 类型、pillFilter、format、
  URL 状态（`?tab&q&split`）、favicon 注入、GitHub Issue 反馈通道、CL010 默认转义——**均未进 help**。

完整（模板实际消费 vs help 记录，明细见 §4）：

- table：模板消费 **22** 个列属性、**12** 个 options；help 只记 13 / 8。
  缺 initialHidden / splitFull / pillFilter / format / videos（列属性）与
  searchFields / showIndex / defaultFilter / feedback（options）；列类型清单漏 `videos`。
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
| `features.md` | ✗ | ✗ | 有 `col.hide` |
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
            'actions': [ ... ],    # 嵌套项
        },
        'url_state': [ ... ],      # URL 级状态
        'behaviors': [ ... ],      # 交互能力（不带实现细节）
    },
    'doc': { ... }, 'slide': { ... }, 'knowledge': { ... },
}
```

要点：

- 契约是**唯一**枚举键名的地方；help、测试、文档引用全部指向它。
- `src/html_gen/html-gen.py` 是 `scripts/build-package.py` 的构建产物（`.gitignore:37` 忽略），
  契约自动随构建传播，无额外同步动作。
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

### C. 覆盖范围：四模板全量（A2 / T2-A / T3-B）

补齐口径：

- **table（P0）**：补 initialHidden、splitFull、pillFilter、format、videos（含 `videos.maxShow`）；
  列类型补 `videos`；
  options 补 searchFields、showIndex、defaultFilter、feedback（`{repo,dataset}`）；
  顶层补 title / subtitle / output 与 `data|rows` 别名；
  显式写出语义：`hide`（永不可见）vs `initialHidden`（默认收起·可开启·分栏全列）、
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

### D. 守卫测试：双向断言（B1 / T4-B）

新增 `tests/test_help_contract.py`，逐模板两条断言：

1. **模板 → 契约**：`layout-{type}.html` 中消费的键集合 ⊆ 契约键集合。
   提取规则需显式定义并写进测试注释（避免脆弱）：
   - 列属性：正则 `\b(?:col|c)\.([a-zA-Z_]\w*)` 取模板 JS 中的属性读取；
   - options：`OPTIONS\.([a-zA-Z_]\w*)`；
   - 维护一份**非契约白名单**（如 `c.key` 的循环变量、`col.map` 等原生方法名），
     白名单仅允许排除「非配置项」，不得排除真实键（白名单本身要在测试里注释逐项理由）。
2. **help → 契约**：`render_help(type)` 的输出包含契约中的**全部**键名（逐键 `assertIn`），
   且不含契约外的键名（用同一份白名单做反向扫描）。

失败信息必须指名「哪个键 / 来源文件 / 修复动作」，避免只报 `assert failed`。

### E. 未知键 warn（T5-A）

- `cmd_table` / `cmd_knowledge` 载入数据后，将 columns 的键、options 的键、item 的键与契约 diff，
  未知键写 **stderr**（`⚠️ 未知列属性: xxx（见 html-gen help table）`），**不阻断、不改退出码**。
- `doc` / `slide` 输入是 Markdown，无键可校验，不适用。
- 不做 `--strict`（T5-A 定档；后续需要再单开）。

### F. 文档面：引用不复制（U3-A）

- 键表**只在契约中存在**；下列文档改为引用并指向 `html-gen help <type>` 与 `TEMPLATE_CONTRACT`：
  `AGENTS.md`（模板类型详解节）、`features.md`、`README.md` / `README.zh.md`、
  `skills/html-gen-cli-spec`、`skills/html-gen-{table,doc,slide,knowledge}`。
- `demos/table-guide.md` / `.html` 是**展示型 demo**，允许保留「功能清单」叙述，
  但其现有键名罗列（如 `列隐藏 (initialHidden/hide)`）改为指向 help，不再单独维护键表。
- 常驻自动化只覆盖 help↔模板↔契约（§D）；文档面用一次性 grep 核查（列入 §7 验证清单），
  不写进测试（避免测试随文档风格变化而脆断）。

### G. 闭环拆分（U4-B）

- **CL012｜基础设施**：`TEMPLATE_CONTRACT` + `render_help()` + `cmd_help` 改造 + `test_help_contract.py`
  （双向断言）+ 未知键 warn；契约内容**先覆盖 table**（P0：initialHidden 等），
  doc/slide/knowledge 节点先建骨架保真（内容 = 现状 help 文案，不新增）。
- **CL013｜四模板补齐 + 文档面**：契约补齐 doc/slide/knowledge 与四模板 CLI 参数段、
  slide 侧栏搜索、doc Bare/宽度、knowledge CLI 项；同步文档面引用改造与测试计数。
- 理由：基础设施可独立验证（B1 双向断言先绿），文案补齐可分段复核；CL010 仍在跑，串行更稳。

### H. 交付（T6-A）

本会话即 html-gen ops，负责需求沟通与设计编写；实施阶段按项目既有闭环派发（dev → review）。
本轮不涉及跨仓写操作，`script-miner` 侧不触碰（D4）。

## 3. 键清单（契约内容源，四模板）

### 3.1 table

顶层 JSON：`columns` / `data`（别名 `rows`）/ `tabs` / `options` / `title` / `subtitle` / `output`

CLI：`-d --data`（必填）、`--title`、`--subtitle`（纯文本，`\n` → `<br>`；显式空串清空）、
`-o --output`（三态：CLI > JSON `output` > 中断）、`--github-url`、`--home-url`、`--favicon`、
`--feedback-repo`、`--quiet`

列类型：`string`(默认) / `number` / `pills` / `videos` / `actions`

列属性（22）：`key` `label` `type` `width` `sortable` `locale` `freeze` `stickyRight` `preview`
`hide` `initialHidden` `splitFull` `quickFilter` `pillFilter` `onCellClick` `onClick` `escape`
`render` `class` `format` `videos` `actions`

嵌套：`actions[]` = `label` `icon` `copyKey` `hrefKey` `handler` `desc`；`videos` = `{maxShow}`

tabs：`key` `label` `field` `match` `contains` `value`

options（12）：`pageSize` `exportCSV` `rowSelect` `search` `searchFields` `showIndex` `clickModes`
`columnResize` `columnsSplit` `modalRenderer` `defaultFilter` `feedback{repo,dataset}`

点击模式：`tab` / `modal` / `split` / `expand`

URL 状态：`?tab` `?q` `?split`

### 3.2 doc

CLI：`-i --input`（必填）、`-o --output`、`--title`、`--subtitle`、`--metadata`、
`--github-url`、`--home-url`、`--favicon`、`--quiet`

URL：`?sidebar=0` / `?toolbar=0`（Bare 模式）、`?width=narrow|medium|wide`（默认 medium=960px）

另：Markdown 语法子集沿用现有 `HELP_DOC` 内容（块级/行内/Callout/不支持项）。

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

item：`title`(必填) `group`(必填) `section` `badge` `desc` `url` `icon`

groups：`key` `label` `icon`

## 4. 键覆盖矩阵（现状 → 目标）

| 模板 | 维度 | 现状 help | 契约目标 | 缺口 |
|:---|:---|---:|---:|:---|
| table | 列属性 | 13 | 22 | initialHidden splitFull pillFilter format videos + actions 嵌套 |
| table | options | 8 | 12 | searchFields showIndex defaultFilter feedback |
| table | 列类型 | 4 | 5 | videos |
| table | 顶层键 | 2 | 7 | title subtitle rows 别名 |
| table | CLI 参数 | 0 | 9 | 全缺 |
| doc | CLI 参数 | 0 | 9 | 全缺 |
| doc | URL 特性 | 0 | 2 | Bare / 宽度 |
| slide | CLI 参数 | 0 | 8 | 全缺 |
| slide | 行为项 | 7 | 8 | 侧栏搜索 |
| knowledge | CLI 参数 | 0 | 10 | 全缺 |
| knowledge | item/ groups | 6 / 3 | 7 / 3 | item.icon |

## 5. 测试影响

- 新增 `tests/test_help_contract.py`（CL012：table 双向断言 + 渲染冒烟；CL013：四模板全量）。
  预计每模板 2-3 例，合计约 10 例。
- 现有测试基数 **312 用例 / 30 文件**（`AGENTS.md:299`）→ 需同步为新增后的实测值；
  `test_prompt_site.py` 等对文件数/计数的硬断言按项目既有做法一并核对（prompts/ 内无 help 文本副本，已实测）。
- 现有 help 相关测试：**无**（`grep -rln "HELP_\|cmd_help" tests/` 零命中）→ 本改动不触发既有断言。
- 回归基线：`.venv/bin/pytest tests/ -q` 全绿（按项目规范跑全量，非仅新文件）。

## 6. 观察项

- O-1：`render_help` 输出与旧文本的 **diff 需人工过目一次**，确认是「补内容」而非「改风格」；
  若风格被迫变化，需在 CL012 提交说明里单独标注。
- O-2：`src/html_gen/` 为构建产物（gitignored），本地副本已过期；CL012 落地后应由
  `scripts/build-package.py` 重建一次，验证契约随构建传播。
- O-3：文档面 grep 核查是一次性的；若后续文档再长出键表，B1 无法自动发现（已知边界，接受）。
- O-4：非契约 help 主题（`prompt` / `demo`）保持手写，其时效性不在本方案覆盖范围。

## 7. dev 验证清单

```bash
# 1. 契约与渲染存在
python3 -c "import importlib.util,sys; spec=importlib.util.spec_from_file_location('hg','html-gen.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(sorted(m.TEMPLATE_CONTRACT)); print(m.render_help('table')[:200])"

# 2. help 输出含关键键（P0 回归锚点）
html-gen help table | grep -c "initialHidden\|splitFull\|pillFilter\|videos"
html-gen help table | grep -n "hide"        # 必须与 initialHidden 语义并列出现
html-gen help doc   | grep -c "width=narrow\|sidebar=0"
html-gen help slide | grep -c "搜索"
html-gen help knowledge | grep -c "welcome\|groups"

# 3. 四模板 help 均含 CLI 参数段
for t in table doc slide knowledge; do echo "== $t"; html-gen help $t | grep -c -- '--'; done

# 4. 守卫测试
.venv/bin/pytest tests/test_help_contract.py -q

# 5. 未知键 warn（不阻断）
printf '[{"a":1}]' > /tmp/t.json && html-gen table -d /tmp/t.json -o /tmp/t.html 2>&1 | grep -i "未知"

# 6. 全量回归（项目规范）
.venv/bin/pytest tests/ -q

# 7. 文档面残留检查（应仅剩契约与引用）
grep -rn "initialHidden" AGENTS.md features.md README.md README.zh.md skills/ \
  | grep -v "html-gen help" ; echo "(预期：无裸键表)"
```

## 8. 提交计划

```
CL012  feat@cli: help 契约单一事实源 — TEMPLATE_CONTRACT + render_help + 双向守卫测试 + 未知键 warn
CL013  docs@help: 四模板 help 补齐（initialHidden/CLI 参数/Bare/侧栏搜索）+ 文档面改为引用契约
```

文件变更（预期）：

- CL012：`html-gen.py`、`tests/test_help_contract.py`（新增）、`AGENTS.md`（测试计数）
- CL013：`html-gen.py`（契约补齐）、`AGENTS.md`、`features.md`、`README.md`、`README.zh.md`、
  `demos/table-guide.md` / `.html`、`skills/html-gen-cli-spec` 与四个模板 skill、
  `documents/solutions/html-gen-help-contract-design-v1.0-20260917.md`（本文件）
