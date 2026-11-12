---
title: CL038 数据回填 + CL039 基线抗洗白 — review 报告 v1.0
topic: drama-backfill-cl038-cl039
type: review
version: 1.0
date: 2026-11-12
author: Security Reviewer (review profile)
profile: review
tags: [review, html-gen, baseline-gate, data-backfill, security]
loop: HTML-GEN-CL038
tracking: HG-SEC-245..255
---

[HTML-GEN-CL038] [2/6] 实现审计 @ 2026-11-12 22:55

# CL038 / CL039 — review 报告 v1.0

> 角色: review（独立复算，不采信 commit body 自述；每条结论附可复跑命令）
> 受审区间: `github/main..HEAD` **2 笔** —— `8bd4840`(CL039 3 文件 +35/-4) / `7b09b1f`(CL038 10 文件 +2732/-1351)
> 现场: `git status --short` 空 · ahead 2 / behind 0 · HEAD=`7b09b1f`
> **结论: ✅ PASS — 86/100 · 病人主张逐条复算成立（无一伪造）；新 5 🟡 / 4 🟢，无 🔴（编号 249–258，251 未分配）**
> 一句话：CL039 的 `--update` 拦截在真仓实证（rc=1、基线 sha 不动、`--force` 才写 `corner:false`），但**两步洗白仍开**（`--force` 之后一次普通 `--update` 就把 `verified` 翻回 true）且该门零自动化覆盖；CL038 数据迁移**零丢失**（22/3/17 全等、产物逐字节可复现），但 `legacy` 有 **5 条键挂在改名后的旧行名上**（yongzheng 3 条全 dangling），回填工具的孤儿提取在「重复行键 / 行数不等」两种输入下会静默丢数据。

---

## ① 病人主张逐条复算

### CL039（`8bd4840`）

| # | 主张 | 实测 | 判定 |
|:--|:--|:--|:--|
| 1 | 漏 `--github-url` 重生成后 `--verify` 仍绿（参数回收盲区） | 真仓重生成 daming 表 → `baseline.py --verify` rc=**0** | ✅ |
| 2 | 此时 `--update` 应被拒（rc=1、基线不动） | `❌ demos/drama/daming-strategy-table.html: 基线有 corner、新快照没有` → rc=**1**；`data/_render-baseline.json` sha256 **前后同值**，`corner=True`/`verified=True` 未动 | ✅ |
| 3 | `--update --force` 才写 `corner=False / verified=false` | force → `corner: False`、`verified: False`；`--check` 转 50/50 绿 | ✅ |
| 4 | 守卫判据补 `/private/tmp`、`/var/tmp` | `tests/test_selenium_infra.py:92` `['\"](?:/private|/var)?/tmp(/|['\"])`；注入两行 ⇒ `test_05` **FAILED**，删除后 5 passed | ✅ |
| 5 | 判据放宽未漂移 | 旧/新判据对 `tests/**/*.py` 逐行比对：old 0 命中 / new 0 命中，**丢失命中 0 / 新增命中 0** | ✅ |
| 6 | `documents/testing.md` 两处 `tearDownClass` → `addClassCleanup`/`addCleanup` | `:33`/`:38` 已改，与 `tests/conftest.py:61` `cls.addClassCleanup(...)` 一致 | ✅（另一处见 ③-247） |
| 7 | 全量回归 | `/usr/bin/python3 -m pytest tests/ -q -n 4` → **473 passed**（62.13s）；`baseline.py --check` → **50/50**；`--verify` → 「产物与当前模板一致」 | ✅ |

### CL038（`7b09b1f`）

| # | 主张 | 实测 | 判定 |
|:--|:--|:--|:--|
| 8 | 产物 `const DATA` 不再含 `idiom` | 3 表 COLUMNS 均 10 列、DATA 行键并集 10 个，`idiom` **不存在** | ✅ |
| 9 | `legacy.idiom` 条数 = 旧源 idiom 非空条数（22/3/17） | daming **22/22**、yongzheng **3/3**、zhuyuanzhang **17/17**；键集合相等 3/3、**值逐条全等 3/3** | ✅ |
| 10 | 孤儿字段无遗漏（不只 idiom） | 旧行∪−新行∪ = `{idiom}`；`idiom` 之外**零孤儿**；`tabs`/`options` 与旧源逐字相同；未进 legacy 的孤儿值 **0** | ✅ |
| 11 | 回填后按新源重刷，COLUMNS/DATA/title/corner 逐字相等 | 渲到临时目录比对：3/3 四项全等，且**整页逐字节相同**（119892 / 120589 / 119294 B）；真仓 `git status` 空 | ✅（强于主张「仅壳前进」） |
| 12 | 与回填前（`7b09b1f^`）产物比：只壳变化 | COLUMNS/DATA/title/corner 四项 **3/3 全等**；字节 89–90KB → 119–121KB（模板 CL036 密度变量等） | ✅ |
| 13 | baseline 3 表入 `CASE_TABLE_PRODUCTS` | `scripts/baseline.py:110-112` 新增 3 条、`CASE_SKIP` 对应 3 条摘除；`--check` **50/50**；`--verify` 判定数实测 **42 ✅ + 37 ⏭ = 79 行** | ✅ |
| 14 | 零依赖铁律（产物自包含） | 新产物外链仅 `github.com/imjaden/html-gen.cli`（角标 a 标签）与 favicon `<link rel=icon>`（`7b09b1f^` 已有 1 处，同款）；**无外链 stylesheet / @font-face / 外链 script** | ✅ |
| 15 | 全量回归 | 同 #7（473 passed / 50-50 / verify 一致） | ✅ |

---

## ② 安全维度

- **权限/门禁模型**：`--verify`（模板↔产物）+ `--check`（sha + 参数存在性）+ `--update`（新增参数回归拦截）三层方向正确；新增拦截点在**写盘之前**返回，基线零残留（sha 实证）。
- **数据流**：`产物 → 源` 是**反向**数据流（页面权威）。这一类迁移的典型风险是「把页面里的错误固化成源权威」，本轮确有 1 处（③-255 待确认）。
- **供应链**：新脚本 `scripts/backfill-table-json.py` 仅用标准库（argparse/json/pathlib/re/sys），无网络、无 eval、无 shell 调用；`--pair` 路径由调用者显式给，属本机 CLI 工具面。
- **密钥/凭据**：两笔 diff 内无 token/key/URL 凭据（`git show` 全量扫过）。

---

## ③ 发现

- 🟡 **HG-SEC-249（新 · MEDIUM）** `verified=false` 不黏滞 ⇒ **两步洗白**：`--update --force` 写完 `corner:false / verified:false` 后，紧接着一次**普通** `--update` 就写回 `corner:false / verified:true`，`--check` 当场 50/50 绿（实测日志 `二次 update 后 corner: False verified: True`）。全程 `verified` 字段**无任何读者**（`grep -rn verified scripts/ tests/` 只命中写入点 `baseline.py:356` 与注释），故该标记只是被动注释、洗白后无审计痕迹。建议：`cmd_update` 读到旧基线 `verified is False` 时，普通 `--update` 直接拒（同样提示「确属产品决策再加 --force」），把二段洗白抬成「两次显式 --force」；或让 `--check` 在 `verified is False` 时打 ⚠️。
- 🟡 **HG-SEC-250（新 · MEDIUM）** 新门**零自动化覆盖**：`tests/test_baseline_gate.py` 9 例中 test_07 只测「产物落后 → 拒 / force 标 verified=false」，**没有一例**走「verify 绿但 corner True→False」这条被修路径（`grep -n "param_regression\|param-lost" tests/` 空）。本轮正确性靠我手工复跑保证；下一轮重构删掉 `_param_regressions` 调用也不会红。建议补 1 例（临时根放一个无 corner 标记的产物 + 基线记 `corner:true`，断言 `--update` rc=1、基线 sha 未变、`--force` 后 `verified=False`），并把 AGENTS.md 计数同步到 474。
- 🟡 **HG-SEC-252（新 · MEDIUM · 数据归属）** `legacy` 的行标识取**旧行** `strategy` 名，而 3 表共 **5 处** strategy 在产物里被改名：daming 行 21 `走为上计→走为上`、zhuyuanzhang 行 16 同款、yongzheng 行 21 `离间计→反间计` / 23 `将计就计→连环计` / 24 `杀鸡儆猴→指桑骂槐`。结果 `legacy.idiom` 有 **5 条键在实际数据行里找不到**（daming 1 / zhuyuanzhang 1 / **yongzheng 3，全部 dangling，可按名 join 0 条**）。值没丢、值与旧行自身配对错配 **0 处**，但「按行名恢复」这一卖点对这 5 条不成立。建议：legacy 值改存 `{行名: {idx, value}}` 或在键上带 `#idx`，让改名不割断归属；回填工具同步报「dangling legacy 键」。
- 🟡 **HG-SEC-253（新 · MEDIUM · 工具健壮性）** 回填脚本孤儿提取的三个静默面（均实测）：
  (a) 行键 `strategy` 不唯一 ⇒ `legacy.setdefault(k, {})[rid]` **静默覆盖**：造两行同 `strategy`、idiom 不同 → 结果只剩 `{'离间计': '另一个不同值'}`，rc=**0**、无告警；
  (b) `zip(old_rows, new_rows)` **按索引截断** ⇒ 行数不等时尾部旧行的孤儿字段全部消失：旧源 2 行 vs 产物 17 行 → `保留未渲染字段 {'idiom': 2}`，其余 15 行旧数据静默丢（rc=0，仅打 `行 rows: count: 2→17`）；
  (c) `--drop-orphans` 只在「本次从旧行提取」时生效，**不清理已存在的 `legacy` 段**：对已回填文件加 `--drop-orphans` 再跑，`legacy.idiom` 仍 22 条 —— 与文档「`--drop-orphans` 才丢」的暗示不符。
  建议：`--apply` 前校验行数相等且行键唯一（否则 rc≠0 并拒写，`--drop-orphans` 才放行）；`--drop-orphans` 时 `raw.pop('legacy', None)`。
- 🟡 **HG-SEC-254（新 · LOW · 报告正确性）** `field_diff` 的 added/dropped 标签**反转**：`scripts/backfill-table-json.py:40-43` 中 `extra`（旧有新增无）被标 `('<none>', None)`、`gone`（新增有旧无）被标 `(None, '<dropped>')`。实测输出把**新增的** `derivative/homology/synonym/antonym` 印成 `→'<dropped>'`，而真正被摘的 `idiom` **一次都没出现在差异行里**（也不显示其值）——「字段级差异」是 CL038 的核心卖点，这条误导会让复核者判反方向。另 `SKIP_KEYS`（:24）定义后**从未使用**（死代码）。建议：正名 + `gone` 带旧值、新增带新值。
- 🟢 **HG-SEC-255（新 · 待确认 · 内容）** yongzheng 现数据 `strategy` **重复**：`反间计` 出现于行 8 与行 21（origin/event 内容不同：周瑜版 vs 陈平+抬旗纳秋月版）。该重复在 `7b09b1f^` 产物里已存在（DATA 本轮逐字未变），本轮回填把它**固化为源权威**。`离间计/将计就计/杀鸡儆猴 → 反间计/连环计/指桑骂槐` 是「换成另一个三十六计条目」而非同计简称，疑早期页面录入错位。**请 data owner 确认页面这 4 处是对的**；若为误编辑，应改产物 + 重跑回填（工具已就绪）。
- 🟢 **HG-SEC-256（新 · LOW）** `documents/testing.md:57` **算术自相矛盾**：改为「5 模板 + 2 手写 + demos-index + **39 个可 verify 产物** = **50 项**」，但 5+2+1+39=**47**；实测判定数是 **42**（42+8=50）。同文件 `:71`「补回 ⇒ **47/47** 一致」本轮也已过时（现 50/50）。这是 HG-SEC-248「testing.md 计数位」的同款复发（见 ④）。
- 🟢 **HG-SEC-257（新 · LOW）** 判据仍属**枚举**，漏 macOS realpath 复合形态：`/private/var/tmp/x`（`/var/tmp` 的 realpath）与 `/var/folders/…`（真实 `TMPDIR` 形态）都不命中（实测 11 形态探针表）。建议并成 `['\"]/(?:private/)?(?:var/)?tmp(?:/|['\"])|['\"]/var/folders/`。属加固项，非复发。
- 🟢 **HG-SEC-258（新 · NIT）** `--help` 文案未随行为更新：`--update` 仍写「默认先 verify」、`--force` 仍写「跳过 verify」，均未提参数回归拦截；`scripts/backfill-table-json.py` 权限 `644`（同类 `baseline.py` 为 `755`）、且只登记在 `documents/testing.md`，未进 `documents/cli-reference.md` 的脚本索引。

---

## ④ 上轮开放项状态（HG-SEC-245..248）

| 项 | 上轮结论 | 本轮实测 | 状态 |
|:--|:--|:--|:--|
| 245 `--update` 洗白 | 🟡 开 | 直连路径已封（#2/#3 实证）；**二段路径仍开** → 转 HG-SEC-249 | **部分闭合** |
| 246 守卫漏 `/private/tmp`、`/var/tmp` | 🟡 开 | 两形态已命中（#4），无漂移（#5）；realpath 复合形态仍漏 → HG-SEC-257 | **闭合（主项）** |
| 247 `conftest.py:52` + `testing.md:34` 的 `tearDownClass` 措辞 | 🟢 开 | `testing.md` 已改；**`tests/conftest.py:52` docstring 仍写「`tearDownClass` 负责清理」**（与 :61 `addClassCleanup` 自相矛盾） | **未闭合** |
| 248 `testing.md` 计数位失真 | 🟢 开 | 本轮改同一段又引入新算术错（39 vs 42）→ HG-SEC-256 | **未闭合（复发）** |

---

## ⑤ 可复跑验证

```bash
# 门禁三连（期望：473 passed / 50-50 / 产物一致 / 工作区空）
/usr/bin/python3 -m pytest tests/ -q -n 4
python3 scripts/baseline.py --check | tail -1     # 基线一致: 50/50
python3 scripts/baseline.py --verify | tail -1    # 产物与当前模板一致
git status --short                                # 空

# CL038 判断点 1：legacy 与旧源 idiom 全等（期望 22/22、3/3、17/17，值全等 True）
python3 - <<'E'
import json,subprocess,pathlib
for s in ('daming','yongzheng','zhuyuanzhang'):
    old=json.loads(subprocess.run(['git','show',f'7b09b1f^:data/_drama-table-{s}-strategy.json'],capture_output=True,text=True).stdout)
    new=json.loads(pathlib.Path(f'data/_drama-table-{s}-strategy.json').read_text(encoding='utf-8'))
    exp={str(r['strategy']):r.get('idiom') for r in old['data'] if str(r.get('idiom') or '').strip()}
    got=new['legacy']['idiom']
    print(s,len(exp),len(got),set(got)==set(exp),all(got.get(k)==v for k,v in exp.items()))
E

# CL038 判断点 2：按新源重刷四项逐字相等（渲到临时目录，零写盘）
#   见本报告 #11；等价做法是把 -o 指向 $TMPDIR 后比 COLUMNS/DATA/title/corner

# CL039 ①：漏参 → --update 拒；--force 才写（会改真仓，跑完 git checkout -- <两个文件>）
PG=demos/drama/daming-strategy-table.html
python3 html-gen.py table -d data/_drama-table-daming-strategy.json -o $PG --title "$(grep -o '<title>.*</title>' $PG | head -1 | sed 's/<[^>]*>//g')" --quiet
python3 scripts/baseline.py --update ; echo rc=$?          # 期望 rc=1 + 基线 sha 不变
python3 scripts/baseline.py --update --force; echo rc=$?   # 期望 corner=False / verified=False

# CL039 ②/257：判据覆盖面
python3 - <<'E'
import re
P=re.compile(r'''['\"](?:/private|/var)?/tmp(/|['\"])''')
for c in ['"/private/tmp/x"',"'/var/tmp/y'","'/tmp/z'",'"/private/var/tmp/w"','"/var/folders/ab/T"']:
    print(('HIT ' if P.search(c) else 'miss'),c)
E
```

---

## ⑥ 待决（2 条，各带推荐）

1. **HG-SEC-255 内容确认**：yongzheng 行 8/21 双 `反间计` 与 4 处 strategy 改名是否页面本意？**推荐**：请 data owner 确认；若为误编辑，本批先修产物再重跑 `scripts/backfill-table-json.py --apply`（工具可用、幂等已验证），不要另写脚本。
2. **HG-SEC-250 测试补位 vs 计数同步**：新增用例会把 473 → 474，需同步 `AGENTS.md:6/:44` + `documents/testing.md` + `tests/test_help_contract.py` 口径三处。**推荐**：下一批与 249（`verified` 黏滞）同批做，一次改完计数；本轮不阻断。

---

## ⑦ 记账

- 本轮发现: **9 条**（5 🟡 = 249 / 250 / 252 / 253 / 254；4 🟢 = 255 / 256 / 257 / 258；251 号未分配，247 复核项沿原编号记在 ④ 表）+ 结转未闭合 2 条（247 🟢、248 🟢 以 256 复发）⇒ `findings_total 11 / open 11`；上轮 246 主项闭合、245 部分闭合。
- 阻断项 0；两笔均**可进入下一批**，无需回滚。
- **推送状态（并发更正）**：本报告与台账在落盘后被并行会话提交并推送（`f036d23` 报告 / `b6924bf` 台账，远端 `github/main` = `b6924bf`，与本地 `HEAD` 同值）。本轮「未推送、待口令」的原裁定已由该次并发落仓覆盖；本笔为记账修正（仅计数与状态句，不改判定）。
- 不属本批（按来件边界不重复记账）：`demos/chaitin`（自建页）/ `demos/the-price-you-choose`（源缺失）/ `demos/slimdown`（自建构建链）三个 skip；`AGENTS.md` 计数仍 473；`documents/data-formats.md` 未提 `legacy` 段（本轮记为 🟢 建议，随 256 同批并入）。
