# 表格文本列 XSS 转义实现审计 v1.0（HG-SEC-134，HTML-GEN-CL010）

> 日期: 2026-09-17
> 闭环: HTML-GEN-CL010（1A 闭环 5/6 实现审计）
> 设计: `documents/solutions/table-text-xss-escape-design-v1.0-20260911.md`（决策 A2+B1+C1+D1+E1+F2）
> 实现: `5f447fc`（`feat@table: default HTML escape for text cells`，已在 github/main）
> ops 核查: `documents/review/table-text-xss-escape-ops-verify-v1.0-20260917.md`（commit `741a7f2`）
> 口径: 不采信 ops/dev 自报，本轮由 review 独立实测（源码逐行 + 独立扫描 + 最小复现 + 全量回归 + 产物字节比对）

## 0. 结论

**PASS — 100/100（0 finding）**

设计 §2 六项决策（A2/B1/C1/D1/E1/F2）与 §5 测试计划逐项落地且独立复核成立：主表格单元格默认转义生效、
唯一 HTML 依赖列（demos-index「文档链接」）经 `escape:false` 正确豁免、反馈入库路径 C1 拒绝分支实测触发、
四渲染路径无脚本执行、全量 312 passed、countries 产物重建字节一致、工作区零残留。

非阻断说明 2 项（见 §7，均非安全缺陷，不留 HG-SEC 号）：设计评审缺步（随实现同一 commit 落地）+ expand 路径测试覆盖粒度。

## 1. 逐项复核表

| # | 审计项 | 实测证据 | 判定 |
|:--|:--|:--|:--|
| 1 | A2 默认转义 + 分支顺序 | `layout-table.html:586-590`（豁免先于默认；render/thousands 优先级未破坏） | ✅ |
| 2 | B1 覆盖范围（独立扫描） | 见 §2 全仓扫描结果；唯一 HTML 列已豁免 | ✅ |
| 3 | C1 入库防护（最小复现） | 见 §3 四用例复现，拒绝分支均触发 | ✅ |
| 4 | D1 列级豁免唯一口 | `escape:false` 唯一豁免；全仓无「既无 escape 又需 HTML」遗漏列 | ✅ |
| 5 | E1 防御性（与反馈通道无关） | 默认转义在模板 render() 内，与 `--feedback-repo` 解耦 | ✅ |
| 6 | F2 全量回归 + demos-index 链接可点 | 312 passed；demos-index 文档链接 `escape:false` + 数据 `<a>` 完整 | ✅ |
| 7 | 回归与产物 | 6 passed / 312 passed / countries 重建字节一致 / git 零残留 | ✅ |
| 8 | 安全面无新增 | escapeHtml 无旁路；无新 innerHTML 注入面/依赖/凭证/外部资源 | ✅ |

## 2. 独立复跑证据

### 2.1 A2 — 主单元格渲染分支顺序（静态，layout-table.html）

```
586:  if (col.render) val = col.render(val, row);
587:  else if (col.format === 'thousands' && typeof val === 'number') val = val.toLocaleString('en-US');
588:  else if (col.escape === false) { /* 显式豁免: raw HTML（如 <a> 链接列） */ }
589:  else if (val === undefined || val === null) val = '';
590:  else val = escapeHtml(String(val));  // HG-SEC-134: 默认转义，防止 stored XSS
```

分支顺序 = 设计 A2 逐字一致：`col.render`（最高）→ `thousands` → `escape === false`（豁免先于默认）
→ null/undefined → 默认 `escapeHtml`。既有 `col.render` / `thousands` 优先级未破坏。
语义变化精确收敛：`escape: undefined` 由「raw」→「转义」，`escape: true` 仍转义（落默认分支），`escape: false` 新豁免口。

### 2.2 B1 — 全仓「HTML 依赖 text 列」独立扫描（本轮自跑，非引用 ops）

对 `data/*.json` 全量 25 文件做 `<`/`>` 字符串扫描 + `escape` 标志枚举，结果：

- `escape` 标志仅 2 处：`_demos-data.json:28`「文档链接」`escape:false`（type 未设 = string）；`_skills-table-config.json:25`「profiles」`escape:true`（type=pills，走 pills 分支 `escapeHtml(s)` 单独转义，不受本次改动影响）。
- 含 HTML（`<` 标签）的 A 型 text 列仅 1 处：`_demos-data.json`「文档链接」18 条 `<a href=...>`，已 `escape:false` 豁免。✅
- 其余 A 型 text 列（countries/provinces/drama-* 策略与时间轴/table-features/table-actions）字符串含 `<`/`>` 数 = **0**，转义后视觉零变化（设计 §4 论断成立）。✅
- 含 `<p>` HTML 的 `desc` 字段出现在 `_cloudwise-kb-data.json`（13 处）/ `_demo-kb-data.json`（98 处）—— 属 **C 型知识库内联 HTML**（layout-knowledge.html 按设计渲染 `desc`），非 A 型表格 text 列，不在本次转义范围，无回归。✅
- `_skills-table-config.json` / `_user-skills.json` 的 `description` 值含 `>`（如 `>-`）—— 仅孤立 `>` 字符，非 HTML 标签，默认转义为 `&gt;-` 后视觉不变，无回归。✅
- `html-gen.py:1366` `cmd_demo` `idx_columns` 同列补 `'escape': False`，与数据侧 `_demos-data.json` 双源一致；`demos/demos-index.html:581` 产物 COLUMNS 同步 `"escape": false`。✅

### 2.3 C1 — 入库防护最小复现（本轮自跑，零写盘）

以 `importlib` 加载真实 `scripts/countries-issue-sync.py`，加载 `feedback-targets.yaml` + `_countries-data.json`，直接调用 `plan_issues()`（不触发 gh 网络、不写盘），四用例结果：

```
[CASE 1 issue-body 路径] note=<script>alert(1)</script>
  actions=0  skips=1  → skip #999: 字段 note 建议值含 HTML 标签字符（< 或 >），安全策略拒绝
[CASE 2 --value 人工裁决路径] override note=<img src=x onerror=alert(1)>
  actions=0  skips=1  → skip #998: 字段 note 建议值含 HTML 标签字符（< 或 >），安全策略拒绝
[CASE 3 数值列 to_number 路径] area_km2=<script>
  actions=0  skips=1  → skip #997: 数值列 area_km2 无法解析建议值 '<script>'
[CASE 4 正常值放行] capital_zh=北京
  actions=1  skips=0   （正常值零误拦）
```

C1 判定成立：`scripts/countries-issue-sync.py:262-265` 的 `if '<' in new or '>' in new:` 拒绝分支在
issue-body 路径与 `--value` 覆盖路径（`override_value` 经 `plan_issues` 第 245 行 `suggested` 统一流入）均生效；
数值列走 `to_number()`（第 256-259 行，`float()` 失败 → None → 拒绝），不含 `<`/`>` 额外检查且同样安全；正常值零误拦。

### 2.4 D1 — 列级豁免唯一口

`escape:false` 为唯一「raw HTML」豁免口。全仓 data JSON 无任何 `render` 列定义（`col.render` 自定义渲染已废弃、数据侧零使用），
故不存在「依赖 HTML 但未显式豁免」的旁路列。profiles 列 `escape:true` 为 pills 路径的遗留冗余声明，无害（pills 分支独立转义）。

### 2.5 E1 — 防御性与反馈通道解耦

默认转义位于模板 `render()` 主单元格分支（layout-table.html:590），对所有 A 型表格生效，
与 `options.feedback.repo` / `--feedback-repo` 注入无关；无反馈通道的页面（如 table-features-demo）同样受保护。✅

### 2.6 F2 — 全量回归 + demos-index 链接可点

- 设计 §5 第 2 项（全量回归）：`/usr/bin/python3 -m pytest tests/ -q -n 0` → **312 passed**（132.34s，串行权威）。
- 设计 §5 第 3 项（demos-index 重建后链接仍可点）：`demos/demos-index.html:581` COLUMNS 含 `"escape": false`，
  DATA 段 18 条 `<a href=... target=_blank rel=noopener>` 完整保留；`tests/test_xss_escape.py::test_02_html_link_column_not_escaped`
  实测 `escape:false` 列仍渲染为可点 `<a>`（`href="https://example.com"` 命中）。✅

### 2.7 回归与产物（本轮实测）

```
/usr/bin/python3 -m pytest tests/test_xss_escape.py -q -n 0   → 6 passed (3.32s)
/usr/bin/python3 -m pytest tests/ -q -n 0                     → 312 passed (132.34s)
git status --short                                            → 空（测试零残留）
```

countries 重建字节比对（按 `scripts/feedback-targets.yaml` `rebuild.args` 复跑至 /tmp，不触碰产物）：

```
python3 html-gen.py table -d data/_countries-data.json -o /tmp/countries-rebuild.html \
  --github-url https://github.com/imjaden/html-gen.cli \
  --home-url https://html-gen.cli.jaden.tech/ \
  --favicon https://www.jaden.tech/static/img/favicon.png \
  --feedback-repo imjaden/html-gen.cli
cmp /tmp/countries-rebuild.html demos/countries-table.html   → 字节一致 (exit 0)
sha256 两文件一致: 556d58839fe0c000cc7553d4db9d5e83545ca1600078d623c5313888c572cbba
```

### 2.8 安全面无新增

- `escapeHtml`（layout-table.html:385-389）用 `textContent → innerHTML` 标准语义，`<`/`>`/`&` 全转义、无旁路；
  输出落点均在 `<td>` 文本上下文（非属性上下文），无需引号转义，无二次解析风险。
- 本次变更最小化：仅 render() 主单元格分支新增默认转义 + C1 脚本侧 4 行 + 数据/生成器侧 `escape:false` 声明 + 测试；
  无新增外部资源、无凭证面、无新增依赖（PyYAML 为既有 dev 依赖）。
- 四渲染路径矩阵复核：主单元格（L590 默认转义）/ 分栏预览（L1152-1153 `escapeHtml`）/ 弹窗 modal（L879 `escapeHtml`）/ 行内展开（L622 `escapeHtml`），均转义。

## 3. 设计决策 A2..F2 落地判定

| 决策 | 设计语义 | 落地位置 | 判定 |
|:--|:--|:--|:--|
| A2 | 模板侧默认转义，`escape===false` 显式豁免 | layout-table.html:586-590 | ✅ 逐字一致 |
| B1 | 全局覆盖，唯一 HTML 列加 `escape:false` | `_demos-data.json:28` + `html-gen.py:1366` | ✅ 双源一致 |
| C1 | 反馈脚本 string 字段含 `<`/`>` 拒绝 | countries-issue-sync.py:262-265 | ✅ 复现触发 |
| D1 | 列级 `escape:false` 唯一豁免口 | 全仓仅文档链接 1 处，无 render 列 | ✅ 无遗漏 |
| E1 | 默认转义与 `--feedback-repo` 无关 | render() 模板层，全 A 型页面生效 | ✅ |
| F2 | 全量回归 + demos-index 链接可点 | 312 passed + test_02 链接可点 | ✅ |

## 4. Finding 清单

- 🔴 0 / 🟡 0 / 🟢 0 —— 无新增安全 finding，无 HG-SEC 续号。
- 历史 finding 闭合：HG-SEC-134（stored XSS，A 型表 text 列 raw innerHTML）即本次 CL010 目标漏洞，
  由 `5f447fc` 的默认转义（layout-table.html:590）+ `escape:false` 豁免 + C1 入库防护（countries-issue-sync.py:262-265）闭合。

## 5. 非阻断说明（非安全缺陷，留痕不编号）

| # | 项 | 说明 |
|:--|:--|:--|
| N-1 | 设计评审缺步（流程偏差） | CL010 设计随实现同一 commit（`5f447fc`）落地，无独立 `docs@design` 提交、无设计评审报告。本轮实现审计已一并复核设计决策 A2/B1/C1/D1/E1/F2 的落地与自洽（§3），六项均成立。留痕：后续闭环应在 `dev 实施` 前独立完成 `docs@design` 评审，避免设计-实现同 commit。 |
| N-2 | expand 路径测试覆盖粒度 | `test_06` 因 expand/expandedIdx 在 IIFE 闭包内，Selenium 无法外部触发，以 split 等效 kv-list 路径（同一 `escapeHtml` 逻辑）间接覆盖 + 断言无 JS 错误。expand 路径转义已静态核实（layout-table.html:622 `escapeHtml(String(v))`），非安全缺口，仅测试粒度可后续增强。 |

## 6. 评分

| 维度 | 得分 |
|:--|:--|
| 转义机制正确性（A2/D1） | 100 |
| 覆盖范围（B1） | 100 |
| 入库防护（C1） | 100 |
| 回归完整性（F2/§7） | 100 |
| 安全面（§2.8） | 100 |
| **综合** | **100 / 100 — PASS** |

## 7. 处理

- ✅ PASS（无阻断、无 finding）→ 一次性提交并推送本轮全部产出：审计报告 + `review-log.md` + `.review-level.yaml`，
  commit `audit@review: XSS 转义实现审计 PASS (HTML-GEN-CL010)` → `git push github main`（ff-only，含本地领先 `741a7f2` / `a7cdc24`）。
- 禁止推 gitee（origin）；仅 `github`。
