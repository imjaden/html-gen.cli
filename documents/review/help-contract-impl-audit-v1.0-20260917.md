# help 契约基础设施实现审计 v1.0（HTML-GEN-CL012）

> 日期: 2026-09-17
> 闭环: HTML-GEN-CL012（1A 闭环 5/6 实现审计）
> 设计: `documents/solutions/html-gen-help-contract-design-v1.2-20260917.md`（§A 契约源 / §B 渲染 / §D 守卫 / §E warn / §G 拆分）
> 实现: `92ff7d9`（`feat@cli: help 契约基础设施 — TEMPLATE_CONTRACT + render_help + table 双向守卫 + 未知键 warn`）
> ops 核查: `documents/review/help-contract-ops-verify-v1.0-20260917.md`（`0e85fd0`，12 项实测）
> 待审三笔（本地领先 github/main）：`92ff7d9` / `0e85fd0` / `21c9569`（`github/main` = `0645a29`）
> 口径: 不采信 ops/dev 自报，本轮由 review 独立实测（契约计数 + 渲染随动 + 3 项变异测试 + 全量回归 + 产物字节比对 + 模板消费路径逐行核实）

## 0. 结论

**PASS — 93/100（🟡 1 + 🟢 2，全部非阻断）**

契约基础设施按设计 §A/§B/§D(table)/§E/§G 完整落地且独立复核成立：契约 7 维度计数与 §3.1 逐项吻合、
`render_help('table')` 由契约驱动（渲染随动实证）、三类守卫断言基本闭合（①模板⊆契约 airtight；②③有 1 处盲区，见 HG-SEC-177）、
未知键 warn 严格限 §E 四项且 stderr + 不改退出码、`videos`/`actions` 扩展键经模板消费路径核实为真实 schema、
`test_help_contract` 14 passed + 7 subtests、全量 326 passed + 7 subtests、countries 重建字节一致、工作区零残留。

3 条 findings 均非阻断（见 §4）：1 🟡 守卫 test_08 词边界盲区（折 CL013 加固）+ 2 🟢 设计文档待订正（videos/actions 键模型欠详 / §B.3 拼接顺序表述自相矛盾）。

## 1. 逐项复核表

| # | 审计项 | 实测证据 | 判定 |
|:--|:--|:--|:--|
| 1 | 契约完整性（§3.1 全键） | 程序化计数：top_level 7 / column_types 6 / columns 22 / tabs 6 / options 13 / feedback 5 / url_state 3 全吻合；actions=7（补 `class`）、videos=5（补 url/title/duration/platform）为模板真实消费 | ✅ |
| 2 | doc/slide/knowledge 骨架 | `TEMPLATE_CONTRACT` L770-790 `legacy` 指向 HELP_DOC/HELP_SLIDE/HELP_KNOWLEDGE，无键模型；`render_help` 原样输出常量 | ✅ |
| 3 | 渲染真实性（契约驱动） | 实证：改契约 `hide` 描述 → 输出随动（§2.2）；删一键/删段 → 测试红（§2.3） | ✅ |
| 4 | 观感判定 | `━━━`(37 字符) + 两空格缩进 + `key: 说明` 行式 + 既有段序全保留；新增段/默认标注/78 列折行属补内容必然重排 | ✅(a) |
| 5 | 三段式边界（§B.3） | ① render_help_spec（契约）/ ② HELP_TABLE_EXAMPLES（段首「以下为示例…」标注）/ ③ legacy 常量；prompt/demo 手写；HELP_OVERVIEW 合并生成 | ✅ |
| 6 | 守卫三类断言 + 变异 | 3 项变异测试全红且指名键/来源/修复（§2.3）；六维度分维度正则（DIMENSIONS 表）；白名单 0 项 + test_10 反向断言 | ⚠️ 见 HG-SEC-177 |
| 7 | warn 作用域（§E） | L508-521 仅列属性/列类型/options 顶层/feedback 子键；L497-498 排除简单数组；data 行字段不迭代；stderr + exit 0 | ✅ |
| 8 | videos 4 键扩展 | L669-699 videoPillLabel/renderVideoPill/renderVideoListHtml 消费 url/title/duration/platform；L568 maxShow | ✅ 属模板固定 schema |
| 9 | 回归与产物 | 14 passed + 7 subtests / 326 passed + 7 subtests / countries 字节一致(231082B, sha 同) / git 空 | ✅ |
| 10 | 边界 | stdlib-only（html/json/re/sys/os/time/argparse/types/pathlib）；未改 src/；未触 script-miner；warn→stderr | ✅ |

## 2. 独立复跑证据

### 2.1 契约计数（程序化，非手数）

以 `importlib` 加载真实 `html-gen.py`，遍历 `TEMPLATE_CONTRACT['table']['data']`：

```
top_level   7 (columns/data/tabs/options/title/subtitle/output)   == §3.1 7   OK
column_types 6 (string/number/pills/videos/actions/datetime)     == §3.1 6   OK
columns    22                                                      == §3.1 22  OK
tabs        6 (key/label/field/match/contains/value)              == §3.1 6   OK
options    13                                                      == §3.1 13  OK
feedback    5 (repo/dataset/key/altKey/template)                  == §3.1 5   OK
url_state   3 (?tab/?q/?split)                                     == §3.1 3   OK
actions     7 (…+class)    §3.1 写 6  → 实现扩展
videos      5 (url/title/duration/platform/maxShow)  §3.1 写 {maxShow} → 实现扩展
```

actions/videos 两处扩展经模板消费路径核实（§2.4），非「为让断言变绿而塞进契约」。

### 2.2 渲染真实性（契约驱动，正向实证）

改契约 `columns` 中 `hide` 条目的说明文本为探针串 → `render_help('table')` 输出即时包含探针串：

```
改前含原 hide 描述: True
改前不含探针: True
改后含探针: True
输出随契约描述随动(渲染真实性): True
```

即 render 不保留任何旧硬编码键文本（旧 `HELP_TABLE` 已删除，`HELP_TABLE_EXAMPLES` 仅保留②示例段），键规范段完全由 `render_help_spec` 从契约 `data` + `section_order` 生成。

### 2.3 变异测试（3 项，改后立即还原，git 状态确认干净）

| # | 变异 | 预期 | 实测 | 还原 |
|:--|:--|:--|:--|:--|
| M1 | 模板加 `col.zzProbe` 消费 | test_02 红，指名键/来源/修复 | `AssertionError: {'zzProbe'}… 来源 layout-table.html; 修复: 在 TEMPLATE_CONTRACT["table"]["data"]["columns"] 补该键` | ✅ git clean |
| M2 | 契约删 `format` 键 | test_02 红 | `AssertionError: {'format'}… 来源 layout-table.html; 修复: …补该键` | ✅ git clean |
| M3 | `section_order` 删 `options` 段 | test_08 红 | `契约键未出现在 html-gen help table 输出: [options.search, searchFields, showIndex, clickMode, defaultFilter, feedback, feedback.repo, dataset, altKey, template]` | ✅ git clean |

M3 的失败清单**暴露 HG-SEC-177**：options 维度共 13 键 + feedback 5 键 = 18 键，test_08 只捕获 10 键，**8 键漏捕**（pageSize/exportCSV/rowSelect/clickModes/columnResize/columnsSplit/modalRenderer 因出现在②示例 JSON；feedback.key 因「key」为通用词在顶层段出现）。见 §4。

### 2.4 videos/actions 扩展键 = 模板固定 schema（逐行核实）

`layout-table.html` 视频渲染路径：

```
L669-675 videoPillLabel(v):  v.platform / v.title / v.duration  (title 缺省→platform)
L677-681 renderVideoPill(v):  v.url (undefined/null 返回空)
L693-699 renderVideoListHtml: v.url
L568        col.videos.maxShow (折叠阈值, 缺省 3)
```

`url`=必填、`title`/`duration`/`platform`=pill 文案字段、`maxShow`=折叠配置 —— 是视频项**固定 schema**，非任意业务字段，亦非白名单兜底。`actions.class` 消费于 L646 `'<button class="action-btn ' + (act.class||'') + …'`。**判定：合理扩展**，设计 §3.1 欠详（见 HG-SEC-179）。

### 2.5 warn 作用域 + stderr + 退出码（本轮实测）

```
$ printf '{"columns":[{"key":"a","label":"A","bogusKey":1}],"data":[{"a":1}]}' > /tmp/uk.json
$ python3 html-gen.py table -d /tmp/uk.json -o /tmp/uk.html
exit=0
stderr: ⚠️ 未知列属性: bogusKey (columns[0])（见 html-gen help table）
stdout: ✅ 已生成: /tmp/uk.html  …（无「未知」污染）
```

countries 真实数据（195 行 × 18 列）重建 stderr **零 warn**，确认不误伤生产数据。

### 2.6 回归与产物

```
pytest tests/test_help_contract.py -q -n 0  → 14 passed, 7 subtests passed (0.24s)
pytest tests/ -q -n 0                        → 326 passed, 7 subtests passed (131.77s)
countries 重建 cmp 字节一致 (231082 B), sha256 两文件一致:
  556d58839fe0c000cc7553d4db9d5e83545ca1600078d623c5313888c572cbba
git status --short                            → 空
```

### 2.7 AGENTS.md 同步 + 边界

- L299 `326 tests（31 文件，含 test_help_contract 14 + 7 subtests`；L326 `(326 tests)`；清单含 `test_help_contract 14`。
- 全仓无 `312 tests`/`30 文件` 残留（仅 `cache/review-prep/` 审计提示缓存 + `review-log.md:2183` 设计期历史留痕，均非应同步文档）。
- imports 仅标准库；`92ff7d9` 文件面仅 `html-gen.py` + `tests/test_help_contract.py`，未触 `src/`、未触 script-miner。

## 3. 观感判定（§B.2「保持现有输出观感」）

**判定：(a) 属「只换内容来源的必然重排」，可接受。**

事实依据（旧 `HELP_TABLE`@`0645a29` 74 行 vs 新 `help table` 118 行逐行对照）：

| 观感要素 | 旧 | 新 | 判定 |
|:--|:--|:--|:--|
| `━━━` 分隔线 | 37 字符 | 37 字符（`rule: 37`） | ✅ 不变 |
| 条目缩进 | 两空格 | 两空格 | ✅ 不变 |
| 行式排版 | `key: 说明 / key: 说明` | `key: 说明 (默认: x) / key: 说明`（78 列折行） | ✅ 同构 + 默认标注 |
| 既有段序 | 示例→列类型→列属性→Tab→选项→点击模式 | 同序（新增段插入） | ✅ 不重排 |

新增内容（属「补内容」而非「改风格」，设计 §C 与 O-1 明确预期）：
① 段首「以下为示例…」标注行（§B.3 强制）；② 顶层键段（7 键）；③ actions[]/videos/options.feedback 嵌套子段；
④ URL 状态段（3 键）；⑤ 每个键补 `(默认: x)` 标注；⑥ 列属性 13→22、选项 8→13、列类型 4→6（§4 覆盖矩阵的目标缺口）。

唯一「风格」差异：旧版列属性/选项用空格对齐 padding（`width:     列宽`），新版为单空格 + `/` 分隔流式折行。
这是程序化渲染（`_fmt_entries` 78 列折行）的机械必然，§B.2 承诺的「同样缩进 + `key: 说明 / key: 说明` 行式排版」
在实质上保留；对齐 padding 属手工排版痕迹，非 §B.2 保护对象。

> 附注（非 finding）：ops OV-10 描述「列属性段改为『一键一行 + (默认: x)』」措辞不准确 —— 实测为「多键挤一行（78 列折行）+ (默认: x) 标注」，非一键一行。不影响判定结论。

## 4. Finding 清单

| 编号 | 严重度 | 位置 | 问题 | 处置建议 |
|:--|:--|:--|:--|:--|
| HG-SEC-177 | 🟡 | `tests/test_help_contract.py:276-279` `_key_in_help` | ②契约→help 方向用 `\b key \b` 词边界匹配，对「键名出现在②示例 JSON」或「通用英文词」的键产生假阴性，未达设计 §D「真正双向闭合」。M3 删 options 段时 8/18 键漏捕（7 options 键在示例 JSON + feedback.key 通用词） | 折 CL013：`_key_in_help` 改为对 `render_help_spec('table')` 输出匹配 `key:` 词元形式（同 test_09 提取逻辑的反向），锚定真实渲染键而非全文词出现 |
| HG-SEC-178 | 🟢 | 设计 §B.3「拼接顺序：label→①→②→③，与现状段落顺序一致」 | 表述自相矛盾：现状（旧 help）段落顺序实为 ②(示例)→①(键规范)，非 ①→②→③。实现选择遵从 §B.2「不改变既有段落顺序」，渲染 ②→①，正确。ops 澄清「拼接顺序=内容来源归属，不重排段落」**成立** | 设计 v1.3 订正 §B.3 措辞，明确 ①②③ 为内容来源标签、字面顺序以 §B.2 现状顺序为准 |
| HG-SEC-179 | 🟢 | 设计 §3.1 `videos={maxShow}` / `actions[]=6 键` | §3.1 低估嵌套 schema：模板实消费 `videos.url/title/duration/platform`（4 键）+ `actions.class`（1 键）。实现已据模板消费路径正确补全契约，非塞键变绿 | 设计 v1.3 订正 §3.1 嵌套键清单（或标注「模板消费为准」） |

- 🔴 0 / 🟡 1 / 🟢 2（新增 HG-SEC-177..179，全部非阻断，留痕备查，折 CL013/v1.3 处置）。

## 5. 三段式边界 + 设计澄清判定

| 段 | 归属 | 实现 | 判定 |
|:--|:--|:--|:--|
| ① 键规范段 | 契约渲染 | `render_help_spec`（table 维度） | ✅ |
| ② 教程/示例段 | 手写常量 | `HELP_TABLE_EXAMPLES`，段首「以下为示例, 键名以键规范段 (顶层键/列类型/列属性/选项) 为准。」 | ✅ |
| ③ 语法/说明段 | 手写常量 | doc/slide/knowledge `legacy`（HELP_DOC/HELP_SLIDE/HELP_KNOWLEDGE）；table 无 ③ 段（与旧 help 一致） | ✅ |
| prompt/demo | 手写 | `HELP_MAP`，`cmd_help` 路由 | ✅ |
| HELP_OVERVIEW 主题清单 | 合并生成 | `_help_topics()` = 契约键（既定序+兜底）+ 手写主题 | ✅ |

**ops 设计澄清判定：成立。** §B.3「拼接顺序 = label → ① → ② → ③」按字面执行会把键规范段提到示例段之前，直接违反 §B.2「不改变既有段落顺序」与「与现状段落顺序一致」的原文自述。实现渲染 `label → ② → ①`（示例在前、键规范在后）与旧 help 实序一致，正确。该澄清将 §B.3 的 ①②③ 视为「内容来源标签」而非「字面输出顺序」，与 §B.3 表格三列「性质/来源/处理」的语义自洽。残缺点在 §B.3 那一行文字本身（见 HG-SEC-178），建议 v1.3 订正措辞。

## 6. 评分

| 维度 | 得分 |
|:--|:--|
| 契约完整性（§3.1） | 100 |
| 渲染真实性 / 观感（§B） | 100 |
| 守卫闭合（§D） | 88（②方向词边界盲区，见 HG-SEC-177） |
| warn 作用域（§E） | 100 |
| 回归与产物（§7/§8） | 100 |
| 边界与治理 | 100 |
| **综合** | **93 / 100 — PASS** |

## 7. 处理

- ✅ PASS（非阻断）→ 提交审计产出并推送本轮全部产出：审计报告 + `review-log.md` + `.review-level.yaml`，
  commit `audit@review: help 契约基础设施实现审计 PASS (HTML-GEN-CL012)` → `git push github main`（ff-only，含本地领先 `92ff7d9`/`0e85fd0`/`21c9569`）。
- 3 条 findings（1 🟡 + 2 🟢）非阻断：HG-SEC-177 折 CL013 加固守卫，HG-SEC-178/179 折设计 v1.3 订正，留痕备查，不触发再评审循环。
- 禁止推 gitee（origin）；仅 `github`。
