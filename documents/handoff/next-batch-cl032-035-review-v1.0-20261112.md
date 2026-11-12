---
title: next-batch CL032/CL035（基线扩面 + 夹具临时路径） — review报告 v1.0
topic: html-gen-cl032-035
type: review
version: 1.0
date: 2026-11-12
author: Security Reviewer (review profile)
profile: review
tags: [review, html-gen, baseline-gate, test-fixtures, design-review]
loop: HTML-GEN-CL035
tracking: HG-SEC-237..244
---

[HTML-GEN-CL035] [2/6] 设计评审 @ 2026-11-12 22:06:17

# next-batch CL032/CL035 — review报告 v1.0

> 日期: 2026-11-12 · 闭环: **HTML-GEN-CL035**（本批实跨 CL032/CL035；`loop:` 取聚焦笔，CL032 侧以 `tracking` + 标题含号兜底）· 角色: review（1A 口径：独立复算，不采信转述）
> 受审区间: `github/main..HEAD` **2 笔**（覆盖会话开场模板的「聚焦 HEAD 1 笔」）—— `87f2369 chore@baseline`(CL032, 29 文件) / `4393e03 chore@tests`(CL035, 9 文件)
> 基线: `git status --short` 空 · ahead 2 / behind 0 · HEAD=`4393e03`
> **结论: ⚠️ CONDITIONAL PASS — 80/100 · 2 🔴 / 3 🟡 / 3 🟢**
> 两条 🔴 都是**小面可修**：① 5 个重建产物丢 github-corner（产物可见回归 + 门禁结构性盲区）；② CL035「25 处清零」不成立（2 处存活，守卫判据天生看不见这种写法）。CL032 的扩面、拒刷判断、确定性重建**逐条复算成立**。

---

## ① 复算判据（逐条独立重跑，命令可复跑）

### CL032（`87f2369`）

| # | 主张 | 复跑方式 | 实测 | 判定 |
|:--|:--|:--|:--|:--|
| 1 | `demos/` 下 59 个子目录产物 | 枚举 `demos/**/*.html` | 总 78 = 顶层 19 + 子目录 59（cloudwise 14 / chaitin 13 / drama 12 / slimdown 3 / the-price 17） | ✅ |
| 2 | 子集 47 / 可 verify 39 / skip 带理由 | `import baseline` 复算 `build_jobs`、`SUBSET`、`case_skip_files` | jobs=**39**、SUBSET=**47**、skip=**40**（8 单条 + 3 目录型展开 32）；`uncovered=∅`、`jobs ∩ skip=∅` | ✅ |
| 3 | 19 件 doc 页「docBody 逐字一致」 | 逐页取 `<div class="doc-body" id="docBody">` 平衡切片，比 `87f2369^` vs `87f2369` | **19/19 长度与内容全等**（7203/702/562/… 逐页相等） | ✅ |
| 4 | 5 件 table 页 `COLUMNS/DATA/OPTIONS` 逐字一致 | 块级 JSON 解析后比对 | `COLUMNS`/`DATA` 全等；`OPTIONS` 对象字面量全等（pageSize 30/30/15/30/40）；壳内 JS 多出 CL009/CL021 新块 = 模板前进，与声明一致 | ✅ |
| 5 | 3 个 strategy 表「产物 10 列 / 源 JSON 7 列」⇒ 拒绝重刷 | 解析产物 `const COLUMNS` + `data/_drama-table-*-strategy.json` 的 `columns` | 三表均 **10 vs 7**：产物独有 `derivative/homology/synonym/antonym`；**反向还有 JSON 独有 `idiom`（产物根本没这列）**；另有 5/2/2 处 `(label,width)` 不等；行数 22/26/17 两边相等 ⇒ **拒刷判断成立，且实际差异比 commit 声明更大**（方向保守，安全） | ✅ |
| 6 | slimdown 三页「重跑逐字节可复现」 | `python3 scripts/build-slimdown.py --apply` 后看工作区 | 三页重写后 `git status --short` **空**（exercises 24,054→ 同、plan/archive 同字节） | ✅ 确定性实证 |
| 7 | `test_08` 扩到 `rglob` 后确有判别力 | 造 `demos/_probe_case/orphan.html` 跑 test_08 | 红：`未进门禁的页面: ['demos/_probe_case/orphan.html']`（探针已删，工作区仍空） | ✅ |
| 8 | `--check` 47/47、`--verify` 全一致 | `python3 scripts/baseline.py --check / --verify` | `基线一致: 47/47`；`产物与当前模板一致`，skip 逐条带理由（含 3 个 strategy 表指向 CL038） | ✅ |
| 9 | `demos/chaitin/` 目录型 skip 不吞 `menu-design.html` | `jobs ∩ skip` | 空集；chaitin skip 实测 12 = 13 − menu-design（可 verify） | ✅ 排除逻辑生效 |
| 10 | 基线文件结构 | `data/_render-baseline.json` | `version: 2` · `verified: true` · `files` 47 条 | ✅ |

### CL035（`4393e03`）

| # | 主张 | 复跑方式 | 实测 | 判定 |
|:--|:--|:--|:--|:--|
| 11 | 473 passed / 102 subtests / 47 文件 | `/usr/bin/python3 -m pytest tests/ -q -n 4` | **473 passed**, 5 warnings, 72.11s；`ls tests/test_*.py` = 47 | ✅ |
| 12 | gate 9 + selenium_infra 5 | 两文件 `-n 0` | 14 passed（9+5） | ✅ |
| 13 | **「25 处固定 `/tmp` 清零」** | `grep -rn "/tmp" tests/`（去掉尾斜杠）+ 跑完全量后看 `/tmp` | ❌ **存活 2 处真夹具**：`tests/test_datetime_clickmode.py:13` `Path('/tmp') / '_test_datetime_clickmode.html'`（:39 写盘、Selenium `file://` 读）、`tests/test_templates.py:34` `Path('/tmp') / f'test-doc-{...}'`（循环 5 个固定名）；跑完全量后 `/tmp` 留 **6 个固定名文件**（`_test_datetime_clickmode.html` 118KB + `test-doc-{usage-guide,doc-guide,table-guide,knowledge-guide,markdown-spec}.html`） | ❌ |
| 14 | 守卫 `test_05` 判别力 | 探针：同一临时测试文件写 `'/tmp/probe.md'` 与 `Path('/tmp') / 'probe.md'` 两行后跑 test_05 | 只抓前者（`:4` 命中），后者**漏网**——判据是 `/tmp/` 子串，`Path('/tmp') / '名'` 天然不含该子串 | ⚠️ 部分判别力 |
| 15 | `TmpDirMixin` 清理生效 | 跑完查 `$TMPDIR` | `hg-{testdoc,testslide,testbackwardcompat,testdocslidefrontmatter,testdocwidthregression,h4h6}-*` 残留 **0** | ✅ |
| 16 | 无临时目录泄漏 | 查 `$TMPDIR` | `hg-nope-*` **3 个空目录**（test_27 每次跑留 1，从不清理） | ⚠️ |
| 17 | `git status --short` 空 | 复跑 + 探针后复查 | 空 | ✅ |

### 安全面（区间静态扫，两条 commit 全覆）

`git diff 87f2369^..HEAD -- '*.py' '*.sh' | grep -E 'shell=True|os.system|eval\(|exec\(|pickle|verify=False|requests\.|urllib'` → **0 命中**；`scripts/baseline.py:284` 为列表式 `subprocess.run`（无 shell）+ `mkdtemp` 临时目录 + `rmtree(ignore_errors=True)`；24 页重刷产物外部资源集合与 prev **相同**（无新增 host，存量 github/文档外链为既有约定）；无凭据、无新增外部资源、无 `--force` 类旁路。**新增攻击面 0**。

---

## ② 三维检查

| 面 | 结论 | 依据 |
|:--|:--|:--|
| **评审规范（§6 报告结构）** | ✅ 合规 | 首行 `[HTML-GEN-CL035] [2/6] 设计评审 @ …`；frontmatter 六字段 + `loop:`/`tracking:`；结论/vs 发现项/维度评分齐备；落点 `documents/handoff/`（G-2） |
| **commit 规范** | ✅ 合规（1 处建议） | 两笔均 `{type}@{scope}: {subject}`、type/scope 小写、subject 全英文、编号 `(HTML-GEN-CL0NN)` 原样保留；`chore`↔治理表 `test`(测试变更) 的映射存在偏差但仓内先例 chore 7 / test 1，不判违规（见 HG-SEC-242） |
| **命名规范** | ✅ 合规 | `CASE_DOC_DIRS`/`CASE_TABLE_PRODUCTS`/`CASE_SKIP` 与既有 `*_PRODUCTS` 同构；私有 `_CASE_DOC`；`case_doc_products()`/`case_skip_files()` 动宾清晰；mkdtemp 前缀 `hg-{class}` 与既有 `hg-showmd-`/`hg-cl036-` 同族；`test_05_no_fixed_temp_paths_in_tests` 序号接 `test_01..test_04`；CL 编号与台账一致 |

---

## ③ 发现项

### 🔴 必须修复（2）

**HG-SEC-237 — CL032 重建使 5 个产物丢掉 `github-corner`，且 `--verify` 结构上看不见**

`87f2369` 重刷的 24 页里，下列 5 页把整块 GitHub 角标（`<a class="github-corner">` + octocat SVG + `.github-corner-hit`）**整段删除**，只留 CSS 死规则：

- `demos/drama/daming-overview.html`
- `demos/drama/history-overview.html`
- `demos/drama/yongzheng-overview.html`
- `demos/drama/zhuyuanzhang-overview.html`
- `demos/drama/history-strategy-table.html`

prev 5/5 均为 `<a href="https://github.com/imjaden/html-gen.cli" class="github-corner"`，cur 5/5 为 `[]`（`grep -c github-corner` 仍 ≥5，命中的全是 `:437-447` 的 CSS 选择器 = 死代码）。commit 声明「壳差异仅 generator 戳 / `--hl-*` 新样式 / meta 字数口径」**未含此项**；其余 19 页不受影响（cloudwise 14 / 4 个 timeline / slimdown 原本无角标；`chaitin/menu-design` 角标保留）。

**门禁为什么没红（这是本批真正该修的洞）**：`scripts/baseline.py:210-216 _recovered_common()` 从**产物自身**回收 `--github-url/--home-url`。产物丢了角标 ⇒ 回收不到 ⇒ 重渲出来的也是无角标版 ⇒ 与产物逐字节相同 ⇒ `--verify` 报 `current`；`--update` 之后 `--check` 同样恒绿。实证：

```
demos/drama/daming-overview.html      => ['doc', '-i', 'demos/drama/daming-overview.md']            # 无 --github-url
demos/drama/history-strategy-table.html => ['table', '-d', 'data/_drama-table-history-strategy.json', '--title=…', '--subtitle=…']  # 无 corner/home
demos/chaitin/menu-design.html        => ['doc', '-i', 'demos/chaitin/menu-design.md', '--github-url=https://github.com/imjaden/html-gen.cli']   # 保留
```

即 CL002 FIND-002「参数从产物回收」设计在**参数丢失**方向上的镜像失效：丢参数后的产物是自洽不动点。仓内已有明训 `scripts/tool-table-videos-syncer.py:207`「旧 html 含 corner（HG-SEC-014 demo 页规范）时透传 `--github-url`，避免重建丢失」——本批重建未走该约定；测试面亦无产物级角标断言（`tests/test_corner_privacy.py` 只断言 `--github-url` 的注入/不注入行为，覆盖不到「产物被重刷掉」）。

**修复建议:**
1. 用 prev 产物回收的参数重渲这 5 页（`--github-url https://github.com/imjaden/html-gen.cli`，走 `build_jobs` 的 argv，勿手敲），再 `python3 scripts/baseline.py --update`。
2. 门禁补「参数丢失」面：`--update` 时把每项回收到的 `(github_url, home_url, favicon)` 写进 `data/_render-baseline.json`，`--verify` 用**基线登记值**渲染（缺登记才回退产物回收）；或在 `test_08` 加一条「SUBSET 内产物 corner/home 与基线登记一致」的断言。否则这一类回归永久绿。

---

**HG-SEC-238 — CL035「25 处固定临时路径清零」在 HEAD 不成立，守卫判据对 `Path('/tmp') /` 形式天生盲**

两处**真夹具**仍写固定名到 `/tmp`（不是 env 字符串、确实落盘）：

- `tests/test_datetime_clickmode.py:13` `DEMO = Path('/tmp') / '_test_datetime_clickmode.html'`（`:39` `DEMO.write_text`，Selenium 用 `file://` 读）
- `tests/test_templates.py:34` `out = Path('/tmp') / f'test-doc-{md_name.replace(".md", ".html")}'`（`TestDoc.test_gen_all_demos` 循环写 5 个固定名）

实测跑完全量后 `/tmp` 留下 **6 个固定名文件**（`_test_datetime_clickmode.html` 118,746B + 5 个 `test-doc-*.html`）。而守卫 `tests/test_selenium_infra.py:88-92` 的判据是 `'/tmp/' in line`——`Path('/tmp') / '名'` 这段**不含** `/tmp/` 子串，故恒绿。探针实证（临时文件两行，跑 test_05 后删除）：`'/tmp/probe.md'` 在 `:4` 被抓，`Path('/tmp') / 'probe.md'` 在 `:5` **漏网**。

⇒ commit body「25 处清零」、`documents/testing.md:33-38`（「存量已清零」）、台账验收「无 `/tmp` 残留」三处口径与 HEAD 实测冲突；而症状正是本批要消灭的「并行 worker / 同机他进程把同名文件顶掉」——`test_gen_all_demos` 的 5 个固定名正是最容易被别会话顶掉的一组。

**修复建议:** 判据放宽到「路径字面量含 tmp 目录」而非「含 `/tmp/`」：`re.search(r"""['"]/tmp\b""", line)` + `/private/tmp` + `tempfile.mktemp(`；把上述 2 处迁到 `TmpDirMixin`（`test_templates.py:34` 类已继承）与类内 `mkdtemp`；`documents/testing.md` 改为「存量清零（守卫口径内可判）」并把口径写清，别写绝对清零。

### 🟡 建议修复（3）

**HG-SEC-239 — test_27 的 `mkdtemp` 只造目录不清理**

`tests/test_issue_feedback.py:403` `missing = str(Path(tempfile.mkdtemp(prefix='hg-nope-')) / 'nope.md')` —— 每次跑留 1 个空目录（实测 `$TMPDIR` 已有 3 个 `hg-nope-*`），与台账「全部 mkdtemp + **tearDown 清理**」不符。
**修复建议:** 这里要的是「唯一且不存在」而非「真目录」：`Path(tempfile.gettempdir()) / f'hg-nope-{uuid4().hex}.md'`（不落盘）；或 `d = Path(tempfile.mkdtemp(...)); self.addCleanup(shutil.rmtree, d, True)`。

**HG-SEC-240 — `TmpDirMixin` 未用 `addClassCleanup`，`setUpClass` 中途失败即泄漏**

`tests/conftest.py:56-64`：`setUpClass` 建目录、`tearDownClass` 清。unittest 语义是「`setUpClass` 抛错 ⇒ **不调用** `tearDownClass`」⇒ `test_doc_width.py:27-34`（`super().setUpClass()` 之后才 `run_gen`）一旦 `run_gen` 失败就留下 `hg-testdocwidthregression-*`。同坑 HG-SEC-221（CL034 批）已建议 `addClassCleanup`，本批新建 mixin 未吸收。
**修复建议:** mixin 内 `cls.addClassCleanup(shutil.rmtree, cls.tmpdir, ignore_errors=True)`，删掉 `tearDownClass` 覆写；子类无需再关心清理顺序。

**HG-SEC-241 — CL035 台账未翻转，且其验收条款已被本报告证伪**

`cache/draft/TODO-20261109.md:23` 仍 `- [ ] … 状态: READY`（同批 CL032 的 `:27` 已 `[x] DONE` + 实证段），本 commit 9 文件未触台账；其验收「`-n 4` ×2 全绿 + 无 `/tmp` 残留」— 后半条被 HG-SEC-238 证伪。
**修复建议:** 翻转 `[x]` + 在实证段写清「2 处尾项（test_datetime_clickmode / test_templates）+ 守卫口径收窄为 `/tmp/` 字面」，并链本报告；尾项修完再改「清零」。

### 🟢 记录（3）

**HG-SEC-242 — 记录集（不阻塞）**

- commit 类型：`chore@tests` 与治理表 `test`=「测试变更」的映射有偏差（仓内先例 chore 7 / test 1）；格式本身合规，建议纯测试笔起用 `test@tests`。
- 台账 `:27` 写「24 件子目录产物按当前模板重刷（19 doc + 5 table + slimdown/exercises）」——19+5+1=**25**，与 `git show --stat` 的 25 个 demo html 一致，括号内算术少 1。
- 判据 `grep -rn "/tmp/" tests/*.py` 实得 **3 行**（多出守卫自身 `:90`，同行 noqa 自豁免），非「仅 47/49 两行」。
- 来件称「`documents/testing.md` 已同步 473」：该文件按设计不写计数（「以 AGENTS.md 为唯一权威」），`grep 473` 无命中——即无面可同步，非缺陷。
- 守卫可用 `'/t'+'mp/'` 绕过（docstring 已声明属打回范式）；属约定级守卫可接受，但别把它当「清零证明」。

**HG-SEC-243 — `AGENTS.md` 计数仍 472/47（实测 473），被指向的权威反而旧**

`:6` 期望 472 passed、`:44` 472 tests/47 文件；`README.md:137`/`README.zh.md:135` 已 473 且注「权威见 AGENTS.md」⇒ 指针反向。**按来件说明不计本批缺陷**（受保护文件审批未获同意），登记待审批（连续第 4 批同款）。

**HG-SEC-244 — `SUBSET` 计算口径双源（方向安全，建议收敛）**

`scripts/baseline.py:181` `_CASE_DOC = case_doc_products()` 在**导入期**以脚本父目录为 base 拼进 `SUBSET`，而 `build_jobs(root)`/`case_skip_files(root, …)` 用实参 `root`。跑 `--root` 副本时两者基准不同；方向由 `test_08` 的 `jobs ⊆ SUBSET` 与 `uncovered` 双向断言兜住（副本多出来的产物会红），**无静默漏网**，故只列记录。建议 `case_doc_products(root)` 在构造 jobs 时算，或在 `main()` 断言 `root == Path(__file__).parent.parent`。

---

## ④ 优先处理顺序

| 序 | 项 | 理由 | 预估 |
|:--|:--|:--|:--|
| 1 | HG-SEC-237：5 页重渲 + `--verify` 改用基线登记参数 | 产物可见回归；不补门禁则「参数丢失」类永久绿，会复发 | 30 min |
| 2 | HG-SEC-238：2 处迁移 + 守卫判据放宽 + 文档回填 | 本批核心交付物的声明为假 | 20 min |
| 3 | HG-SEC-239 / 240：临时目录卫生（各 3 行） | 与「tearDown 清理」验收条款一致性 | 10 min |
| 4 | HG-SEC-241：台账翻转 + 实测偏差回写 | 追溯链闭合 | 5 min |
| 5 | HG-SEC-242 / 243 / 244 | 记录与待审批项 | 不阻塞 |

---

## 附录：维度评估

| 维度 | 评分 | 备注 |
|:--|:--|:--|
| 合理性 | 82 | 扩面思路（先试渲染 + 内容级 diff 分类、拒刷 3 表、排除已判定文件）可复算且保守；扣分在「重刷未走 recovered argv」导致 5 页丢角标 |
| 严格性 | 88 | 19/19 docBody、5/5 table 块级全等、3 表列集拒绝判断、slimdown 逐字节可复现、test_08 探针转红——判据都可复跑且命中 |
| 安全性 | 90 | 无新增攻击面（shell/eval/外部资源 0 新增），列表式 subprocess + mkdtemp；扣分在守卫判据形式化不足（`/tmp/` 子串） |
| 覆盖度 | 78 | 门禁自回收参数的循环性使「参数丢失」不可见；固定路径守卫漏 `Path('/tmp') /` 写法 |
| **总分** | **80** | CONDITIONAL PASS |

---

> **处理约定**：CONDITIONAL PASS ⇒ 本报告 + `review-log.md` + `.review-level.yaml` 本地提交（`audit@review`），**不 push**；待 HG-SEC-237/238 修后按「推送」口令重审。
