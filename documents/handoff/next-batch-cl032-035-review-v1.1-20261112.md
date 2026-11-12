---
title: next-batch CL032/CL035（基线扩面 + 夹具临时路径） — 复核报告 v1.1
topic: html-gen-cl032-035
type: review
version: 1.1
date: 2026-11-12
author: Security Reviewer (review profile)
profile: review
tags: [review, recheck, html-gen, baseline-gate, test-fixtures]
loop: HTML-GEN-CL035
tracking: HG-SEC-237..248
---

[HTML-GEN-CL035] [2/6] 设计评审复审 @ 2026-11-12 22:52:40

# next-batch CL032/CL035 — 复核报告 v1.1（round-2：只判上轮 🔴/🟡 是否闭合）

> 角色: review（1A 口径：独立复算，不采信 commit body 自述）
> 受审区间: `github/main..HEAD` **5 笔** —— `87f2369`(CL032 主体) / `4393e03`(CL035) / `76e0a5d`(上轮 audit) / `d978c97`(本轮修复) / `488af5e`(AGENTS 计数)
> 基线: `git status --short` 空 · ahead 5 / behind 0 · HEAD=`488af5e`
> **结论: ✅ PASS — 90/100 · 上轮 2 🔴 + 3 🟡 全部闭合（5/5），新增 2 🟡 / 2 🟢 均非阻断**
> 一句话：5 页角标复原（95 页回归面全一致）、`param-lost` 钉子实测会红、两处 `/tmp` 夹具已迁、21 passed 且 `/tmp` 残留 0、`addClassCleanup` 在「setUpClass 中途抛错」实证下不泄漏、`_BASE_SUBSET` 与旧版**集合/顺序/jobs/skip 全等**。仍留两个尾巴：`--update` 会把 `corner:false` 写进基线（洗白）、守卫判据漏 `/private/tmp` 与 `/var/tmp`。

---

## ① 逐条复核（每条均独立复跑，命令可复跑）

| # | 上轮项 | 期望 | 实测（本轮） | 判定 |
|:--|:--|:--|:--|:--|
| 1 | **HG-SEC-237 🔴 ①** 5 件产物 corner 复原 | 7/7/7/7/5 = 父提交同值 | daming/history/yongzheng/zhuyuanzhang overview = **7,7,7,7**；history-strategy-table = **5**；逐笔与 `87f2369^` 完全相同 | ✅ |
| 2 | **HG-SEC-237 🔴 ①** 回归面是否还有别页丢角标 | 无 | `87f2369^` vs HEAD 逐页比 `<a class="github-corner"` 存在性：**95 页全一致（丢 0 / 增 0）** | ✅ |
| 3 | **HG-SEC-237 🔴 ②** 基线记 corner/home 存在性 | 字段落库 | `data/_render-baseline.json` v2 / 47 条：**46 条带 `corner`+`home`**，1 条为 `style-guide.css`（非 html，按 `p.suffix=='.html'` 跳过，合理）；`corner:true` 20 条、`home:true` 2 条 | ✅ |
| 4 | **HG-SEC-237 🔴 ②** `param-lost` 实测会红 | 1 条 | 故意漏 `--github-url` 重生成 daming-overview → `--check --json` 得 `param-lost:corner` **1 条**（另有 1 条 `changed`，属同一变更的第二证据）；还原后 **47/47** | ✅ |
| 5 | **HG-SEC-238 🔴** 两处夹具迁移 | 已改 | `test_datetime_clickmode.py:45` `cls.demo = cls.tmpdir / '_test_datetime_clickmode.html'`（`TmpDirMixin`）+ `generate_html(out_path=…)`；`test_templates.py:34` `out = self.tmpdir / f'test-doc-…'` | ✅ |
| 6 | **HG-SEC-238 🔴** test_05 判据覆盖三写法 | 覆盖 | `test_selenium_infra.py:92` `re.compile(r'''['\"]/tmp(/|['\"])''')`；变异探针 5 行→**命中 4 行**（`'/tmp/x'`、`Path('/tmp')/'x'`、纯 `'/tmp'`、f-string `f'/tmp/{1}'`），仅 `'/private/tmp/q.md'` 漏（见 HG-SEC-246） | ✅（三形态达标的；第四形态见 ②） |
| 7 | **HG-SEC-238 🔴** 两文件用例 + `/tmp` 残留 | 21 passed；残留 0 | `pytest tests/test_datetime_clickmode.py tests/test_templates.py -q -n 0` → **21 passed (7.79s)**；跑前跑后 `/tmp/_test_datetime_clickmode.html` + `/tmp/test-doc-*.html` 均 **0** | ✅ |
| 8 | **HG-SEC-239 🟡** test_27 清理 | `addCleanup(shutil.rmtree, …)` | `test_issue_feedback.py:403-404` 已落；跑 `test_issue_feedback.py`（37 passed）前后 `$TMPDIR/hg-nope-*` **3 → 3**（3 个是 21:55–22:00 修复前遗留，近 10 分钟新建 `hg-*` = **0**） | ✅ |
| 9 | **HG-SEC-240 🟡** `addClassCleanup` | 已落、无 tearDownClass | `conftest.py:61` `cls.addClassCleanup(shutil.rmtree, str(cls.tmpdir), ignore_errors=True)`；`grep tearDownClass conftest.py` 仅剩**注释**两处。实证：构造 `setUpClass` 在 `super().setUpClass()` 之后抛错的子类 → 运行后 `hg-boom-*` = **0/0**（旧写法此处必留目录） | ✅ |
| 10 | **HG-SEC-241 🟡** CL035 台账翻转 | `[x]` DONE | `cache/draft/TODO-20261109.md:23` = `- [x] … 状态: DONE; 闭环: HTML-GEN-CL035`，尾部实证段含「25 处清零 + 守卫 test_05（三种写法）+ TmpDirMixin addClassCleanup；review HG-SEC-238 补漏 2 处」；`git check-ignore` 确认 `cache/` 不入库（按本地留存审） | ✅ |
| 11 | **HG-SEC-243 🟡** AGENTS 计数 | `:6` 473 / `:44` 473·47 文件 / ≤4,000B | `:6`「期望 473 passed」、`:44`「473 tests（47 文件，含 102 subtests）」；文件 **3,660B**；`grep -c 472` = **0**、`grep -c 473` = 2 | ✅ |
| 12 | **HG-SEC-243** 计数口径实测 | 473 / 102 / 47 | py3.12+pytest 9.1.0 `pytest tests/ -q -n 4` → **473 passed, 102 subtests passed (62.88s)**；`ls tests/test_*.py` = **47** | ✅（口径依赖解释器，见 HG-SEC-248） |
| 13 | **HG-SEC-244 🟡** SUBSET 二次拼接 | `_BASE_SUBSET` 单次 | `scripts/baseline.py:157-158` 单表达式；`_BASE_SUBSET` 出现 3 次（赋值/列表推导/无残留自引用）；`SUBSET` 47 项**无重复**；与 `4393e03` 版逐项比：**集合相等 / 顺序相等 / build_jobs 39==39 / case_skip_files 相等** ⇒ 重构语义无损 | ✅ |

复跑命令（关键几条，与上表一一对应）：

```bash
# 1-2 角标复原 + 全量回归面
for f in demos/drama/{daming,history,yongzheng,zhuyuanzhang}-overview.html demos/drama/history-strategy-table.html; do echo -n "$f "; grep -c 'github-corner' $f; done
for f in $(git ls-tree -r --name-only 87f2369^ | grep '\.html$'); do \
  o=$(git show 87f2369^:$f | grep -c 'class="github-corner"'); n=$(grep -c 'class="github-corner"' $f); \
  [ "$o" != "$n" ] && echo "DIFF $f $o -> $n"; done   # 期望无输出
# 3-4 参数钉子
python3 scripts/baseline.py --check                                   # 期望 47/47
./html-gen.py doc -i demos/drama/daming-overview.md -o demos/drama/daming-overview.html --quiet
python3 scripts/baseline.py --check --json | grep -c param-lost      # 期望 1
git checkout -- demos/drama/daming-overview.html
# 7 夹具
python3 -m pytest tests/test_datetime_clickmode.py tests/test_templates.py -q -n 0   # 期望 21 passed
ls /tmp/_test_datetime_clickmode.html /tmp/test-doc-*.html 2>/dev/null | wc -l        # 期望 0
# 13 语义等价
python3 -c "import sys;sys.path.insert(0,'scripts');import baseline as b;print(len(b.SUBSET),len(set(b.SUBSET)))"   # 期望 47 47
```

**对来件复核指令的一处勘误**：第 6 条给的 `grep -rn "tmp" tests/*.py | grep -v tmp-path-guard | grep -v "^tests/test_selenium_infra.py:9[0-9]"` 期望「空」不可满足 —— 它会命中所有 `tmpdir`/`mkdtemp`/`mkstemp`/`tmp_md`，实测 **355 行**。等价于守卫正则的判据是：

```bash
grep -rnE "[\"']/tmp(/|[\"'])" tests/ | grep -v "noqa: tmp-path-guard"   # 判据：期望空（实测 0 行）
grep -rnE "[\"']/tmp(/|[\"'])" tests/                                     # 全量：现存 2 行，均为 test_02 的 CHROMEDRIVER env 字符串（:48/:50，带 noqa）
```

---

## ② 本轮新发现（2 🟡 / 2 🟢，全部非阻断）

### 🟡 HG-SEC-245 — `--update` 会把 `corner:false` 洗进基线，`param-lost` 钉子对「重建 + update 同批」无效

新增的存在性钉子只在「基线有、产物没有」时报警，而 `--update` 是**照产物重建基线**：漏参 → 产物无 corner → 基线登记 `corner:false` → 此后 `--check` 恒绿。**这正是 CL032 的事故路径**（`demo --rebuild` 之后 `baseline --update`）。实证（本轮实跑，已还原）：

```
step1 ./html-gen.py doc -i demos/drama/daming-overview.md -o … --quiet   → corner_after_regen=5（只剩 CSS 死规则）
step2 python3 scripts/baseline.py --update                               → exit 0，✅ 已重建基线（47 个文件，verified=True）
step3 基线登记值                                                        → baseline_corner = False
step4 python3 scripts/baseline.py --check                                → exit 0，基线一致 47/47   ← 洗白
```

⇒ `d978c97` commit body 的「结构上 **堵住**「参数丢失」这类盲区」为**过头表述**：钉子堵的是「产物在基线之后漂移」，不堵「漂移与 update 同批」。`documents/testing.md:67-70` 的措辞（只描述 `--update` 记存在性 + `--check` 报 `param-lost`）与实际行为一致，未越界。

**修复建议（二选一，均 < 20 行）:**
1. `--update` 覆写前读旧基线：`old.get(flag) is True and rec[flag] is False` ⇒ 打印 `param-lost-warning:<path>:<flag>` 并 `return 1`（`--force` 才继续）；
2. 存在性做「黏性」：`rec[flag] = 新产物有 or 旧基线有`，把「曾经有」作为不变量，降低只由 `--force` 显式重置。
另建议在 `tests/test_baseline_gate.py` 补一条用例（现无任何自动化覆盖 `param-lost`：`grep -rn "param-lost" tests/` 为 0，本轮 473 绿不含该路径）。

### 🟡 HG-SEC-246 — 守卫判据仍漏 `/private/tmp`、`/var/tmp` 两种 macOS 合法形态

`test_selenium_infra.py:92` 的 `['\"]/tmp(/|['\"])` 要求引号**紧邻** `/tmp`，`'/private/tmp/q.md'`、`'/var/tmp/q.md'` 均不命中（变异探针实测：5 行探针命中 4 行，`/private/tmp` 那行漏）。macOS 上 `/tmp` 是 `/private/tmp` 的软链，同机脚本两种写法都常见 —— 与上轮 238 属同一「形态盲区」病。

**修复建议:** `re.compile(r'''['\"]/(?:private/|var/)?tmp(?:/|['\"])''')`，并把 `tempfile.mktemp(` 一并纳入（该 API 只是「不安全」而非「固定名」，可判 warning 级）。

### 🟢 HG-SEC-247 — 两处文档仍在说 `tearDownClass` 清理（与实现自相矛盾）

`tests/conftest.py:52` docstring「`tearDownClass` 负责清理」、`documents/testing.md:34`「`setUpClass` 建 `mkdtemp`、`tearDownClass` 清」—— 同一段落往下两行（conftest `:59-61`、testing.md `:37`）已正确写 `addClassCleanup`。读懂代码不受影响，但会被后来者当规范抄。建议两处一并改「`addClassCleanup` 注册清理」。

### 🟢 HG-SEC-248 — 上轮 HG-SEC-242 的一处记录有误 + 计数口径依赖解释器

- 上轮写「`documents/testing.md` 按设计不写计数，`grep 473` 无命中 ⇒ 无面可同步」：该文件**确有计数位**——`documents/testing.md:42`「组成：46 文件，共 102 subtests（下表为旧快照…）」，其中 **46 与实测 47 不符**（该行自我声明为旧快照，不构成阻断，但「无计数位」结论应撤回）。
- 「473 passed / 102 subtests」**依赖解释器**：`/usr/bin/python3`（pytest 8.4.2）不记 subtests、输出 `473 passed, 5 warnings`；py3.12 + pytest 9.1.0 才输出 `473 passed, 102 subtests passed`。AGENTS.md 只写 `python3 -m pytest`，同机 `python3` 指向 3.9.6 ⇒ 口径随 PATH 漂移。建议在 `documents/testing.md` 注明「subtests 计数需 pytest ≥9」，或在 AGENTS 计数行去掉 subtests 数。

---

## ③ 全量复跑（本轮实测）

| 门 | 命令 | 实测 |
|:--|:--|:--|
| 全量测试 | `pytest tests/ -q -n 4`（py3.12 / pytest 9.1.0） | **473 passed, 102 subtests passed, 62.88s** |
| 同上（系统解释器交叉验证） | `/usr/bin/python3 -m pytest tests/ -q -n 4` | **473 passed, 5 warnings, 70.75s** |
| 产物一致性 | `python3 scripts/baseline.py --verify` | **产物与当前模板一致**；skip 逐条带理由（slimdown 3 条自建构建链 / the-price 17 条 md 源不在本仓 / 3 个 strategy 表 → CL038） |
| 基线 | `python3 scripts/baseline.py --check` | **基线一致: 47/47**，exit 0 |
| 工作区 | `git status --short` | **空**；ahead **5** / behind **0** |
| `/tmp` 卫生 | `ls /tmp/_test_datetime_clickmode.html /tmp/test-doc-*.html \| wc -l` | **0** |
| 新笔攻击面 | `git diff 76e0a5d..HEAD -- '*.py' '*.sh' \| grep -E "shell=True\|os\.system\|eval\(\|exec\(\|pickle\|verify=False\|requests\.\|urllib"` | **0 命中**（新增仅 `read_text` 取两段正则匹配 + 临时目录清理，`subprocess` 无新增） |

---

## ④ 维度评分与结论

| 维度 | 评分 | 依据 |
|:--|:--|:--|
| 合理性 | 90 | 修复路径与 finding 一一对应（重渲走父提交 corner URL、判据三形态、addClassCleanup、台账翻转）；扣分在参数钉子的设计未覆盖 `--update` 同批路径（HG-SEC-245） |
| 严格性 | 93 | 每条判据独立复跑 + 双向变异（`param-lost` 红/绿、探针 4 形态、`setUpClass` 抛错不泄漏、新旧 SUBSET 四项全等）；commit 自述与实测无冲突（除「结构上堵住」的措辞） |
| 安全性 | 95 | 无新增攻击面；无新增外部资源；`--update` 洗白属完整性回归而非可利用漏洞 |
| 覆盖度 | 85 | 角标 95 页全回归面 + 全量 473 绿；扣分在 `param-lost` 零自动化测试、守卫仍有形态缺口 |
| **总分** | **90** | **PASS** |

**结论: ✅ PASS（90/100）** —— 上轮 5 项（2 🔴 / 3 🟡）全部闭合且均有可复跑证据；本轮 2 🟡 / 2 🟢 非阻断，建议并入下一批（HG-SEC-245 优先，因其决定这道门是否真能防复发）。

### 处理约定

- 本报告 + `review-log.md` + `.review-level.yaml` 本地 path-scoped 提交（`audit@review`）。
- **未 push**：沿用上轮裁定「按『推送』口令放行」；本批 `github/main..HEAD` 已 5 笔（含修复笔 `d978c97`），待口令。
- 不属本批（不重复记账）：CL038（3 个 strategy 表 JSON 回填）、CL037（`b0f4b4f` slimdown 笔）、跨仓 hermes-manager 重生成转交件。
