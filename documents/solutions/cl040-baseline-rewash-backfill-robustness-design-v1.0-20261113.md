# baseline 二次洗白收口 + 回填工具健壮性 + 门禁文档校准（方案 v1.0 · 待实施）

- 日期：2026-11-13 · 编号：`HTML-GEN-CL040` · 分类：治理 · 优先级：P1
- 需求条目：`cache/draft/TODO-20261109.md:31`
- 来源：`cache/logs/review-cl038-039.log:124-136`（HG-SEC-249/250/252/253/254/256/257/258）
- 状态：**方案定稿，源码/测试/数据零改动**（本文档是本批唯一产物）
- 约束：不 push；不勾选 draft 条目；不动他线 WIP（slimdown 页 89fe30f 之后的未审提交不在本批范围）

---

## 0. 结论摘要

| 条目 | 现状（本次实测） | 方案落点 | 需审批 |
|:--|:--|:--|:--|
| ① HG-SEC-249 二次洗白 | **已复现**：`--force` 后一次普通 `--update` 把 `verified` 翻回 `true`，`--check` 50/50 全绿 | D1：`verified` 语义改为「verify 绿 ∧ 无参数回归」+ 旧基线 `verified=false` 时普通 `--update` 拒绝 + `--check` ⚠️ | 否 |
| ② HG-SEC-250 新门零覆盖 | `grep param_regression\|param-lost tests/` 仍为空 | D2：`test_baseline_gate.test_10` 一例（473→474）；推荐同批加 `tests/test_backfill_tool.py` 4 例（→478） | **是**（AGENTS.md 计数） |
| ③ HG-SEC-252 legacy 悬挂 | 5 处 → **现 2 处**（a3af4b6 已重键 yongzheng 3 处）：daming:21 `走为上计`、zhuyuanzhang:16 `走为上计` | D3：数据 re-key 2 处（字节中性）+ 工具加 dangling 报告 | 否 |
| ③ HG-SEC-253 孤儿三静默面 | **三面全部复现**（见 §1.3） | D4：`--apply` 前置校验（行数相等 + 行键唯一）+ `--drop-orphans` 清既有 `legacy` | 否 |
| ③ HG-SEC-254 标签反转 | **已复现**：新增字段印成 `→'<dropped>'`，被摘字段印成 `'<none>'→None` 且丢值 | D5：正名 + 带真值 + 删 `SKIP_KEYS` 死代码 | 否 |
| ④ HG-SEC-256 文档算术 | `testing.md:57` 写 39（实测 42）；`:71` 写 47/47（实测 50/50） | D6：42 / 50/50 / 47 文件 / 10 例 + 数字守卫并入 `test_08` | 否 |
| ④ HG-SEC-257 判据漏形态 | 正则漏 `/private/var/tmp`、`/var/folders` | D7：并集正则（11 形态探针实测，仓内零漂移） | 否 |
| ④ HG-SEC-258 文案/权限/索引 | `--help` 未提参数回归；`backfill-table-json.py` 644；不在 `cli-reference` 索引 | D8：文案 + `chmod 755` + 索引 2 行 + 补 `--dry-run` 实装（新条 **259**） | 否 |

**合计**：脚本 3 文件 + 测试 2 文件 + 数据 2 文件 + 文档 4 文件；计数 473 → **478**（一次审批）。

---

## 1. 现状与实测证据（全部可复跑）

复跑环境：`/Users/jadenli/CodeSpace/html-gen.cli`，py3.12，`baseline.py --check` 当前 **50/50**。
探针目录用 scratch（`/Users/jadenli/.hermes/profiles/dev/cache/scratch/cl040-*`），真仓零写入。

### 1.1 HG-SEC-249 二次洗白：完整复现

临时根只放 1 个可 verify 产物（`demos/countries-table.html`），四步走：

```bash
T=$(mktemp -d "$TMPDIR/cl040-XXXX")
cp html-gen.py style-guide.css layout-*.html "$T"/ ; mkdir -p "$T"/data "$T"/demos
cp data/_countries-data.json "$T"/data/
python3 html-gen.py table -d data/_countries-data.json --title=国家 \
    --github-url=https://github.com/x/y -o "$T"/demos/countries-table.html
python3 scripts/baseline.py --update --root "$T"                    # ① corner=True verified=True
python3 html-gen.py table -d data/_countries-data.json --title=国家 -o "$T"/demos/countries-table.html   # ② 漏 --github-url
```

实测输出（本次逐字）：

```
--- 2) 漏参后 --update 应拒 ---
❌ demos/countries-table.html: 基线有 corner、新快照没有（重建时丢了对应 CLI 参数？）
   拒绝重建基线：先按产物原参数（--github-url/--home-url）重刷；确属产品决策要摘掉角标，加 --force。
rc=1
--- 3) --update --force ---
✅ 已重建基线: …/data/_render-baseline.json（50 个文件，verified=False）   corner= False verified= False
--- 4) 普通 --update（二次洗白） ---
✅ 已重建基线: …/data/_render-baseline.json（50 个文件，verified=True）    corner= False verified= True
--- 5) --check ---
基线一致: 50/50
```

⇒ 参数存在性钉子被**永久**抹平：此后 ``--check`` 的 `param-lost:corner` 分支（`scripts/baseline.py:399-402`）永远不会再触发。

### 1.2 HG-SEC-252 legacy 行名现状：5 → 2

`a3af4b6`（`fix@data: dedupe yongzheng strategy row 21, align legacy keys (HG-SEC-255)`）已对 yongzheng 重键并新增 `renames` 说明，剩余 2 处按名 join 为 0：

```bash
python3 -c "
import json
for f in ['data/_drama-table-daming-strategy.json','data/_drama-table-zhuyuanzhang-strategy.json']:
    d=json.load(open(f)); n=[r['strategy'] for r in d['data']]
    print(f, len(n), 'dangling:', [k for k in d['legacy']['idiom'] if k not in n])"
```

实测：

```
data/_drama-table-daming-strategy.json 22 dangling: ['走为上计']       # 对应行 21「走为上」，legacy 值「三十六计走为上」
data/_drama-table-zhuyuanzhang-strategy.json 17 dangling: ['走为上计'] # 对应行 16「走为上」，值「走为上计」
yongzheng: legacy = {idiom: 3 条（已重键）, renames: 3 条}  → dangling 0
```

值未丢、配对无错配（值出自同一条旧行），只是「按行名恢复」对这两条不成立。

### 1.3 HG-SEC-253 孤儿提取三静默面：全部复现

夹具（`f253a` 行键重复 / `f253b2` 旧源 5 行 vs 产物 2 行 / `f253c` 已有 `legacy` + `--drop-orphans`），实测：

```
# (a) 行键重复 ⇒ 静默覆盖
$ python3 scripts/backfill-table-json.py --pair f253a.html=f253a.json --apply
   data 行 2 → 2；字段差异 2 行；保留未渲染字段 {'idiom': 2}       ← 报 2 条
   ✅ 已回填                                                     rc=0
写盘后：legacy = {'idiom': {'离间计': '值2'}}                      ← 只剩 1 条，值1 静默丢失

# (b) zip 按索引截断 ⇒ 尾部旧行整行消失
$ python3 scripts/backfill-table-json.py --pair f253b2.html=f253b2.json --apply
   data 行 5 → 2；字段差异 3 行；保留未渲染字段 {'idiom': 2}       ← 只说 2 条，C/D/E 三行全丢
   ✅ 已回填                                                     rc=0
写盘后：rows= 2 legacy= {'idiom': {'A': 'iA', 'B': 'iB'}}

# (c) --drop-orphans 不清既有 legacy
$ python3 scripts/backfill-table-json.py --pair f253c.html=f253c.json --drop-orphans
   （无任何提示）                                                 rc=0
磁盘 legacy 仍在：{'idiom': {'A': '旧值', 'Z': '僵尸'}}
```

三面共同特征：**rc=0 + 只报「保留」不报「丢弃」**，与文档口径「`--drop-orphans` 才丢」相反。

### 1.4 HG-SEC-254 字段级差异标签反转

```
$ python3 scripts/backfill-table-json.py --pair f254.html=f254.json     # 新增 note，摘掉 idiom
   columns 2 → 2；新增 ['note']；移除 ['idiom']；宽度变更 []
   data 行 1 → 1；字段差异 1 行；保留未渲染字段 {'idiom': 1}（不丢数据，--drop-orphans 才丢）
     行 0: note: None→'<dropped>', idiom: '<none>'→None
```

真值：`note` 是**新增**（应显示 `None→'n1'`），`idiom` 是**摘除**（应显示 `'走为上'→None`）。
现输出把两者语义互换 + 丢值：`note` 的新值 `n1` 没印出，`idiom` 的旧值 `走为上` 没印出。
`SKIP_KEYS`（`:24`）全仓唯一引用即定义处 —— 死代码（`grep -rn SKIP_KEYS` 仅命中 `:24`）。

### 1.5 HG-SEC-256/257/258 实测

```bash
python3 -c "import importlib.util,pathlib;spec=importlib.util.spec_from_file_location('b','scripts/baseline.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);print(len(m.SUBSET), len(m.build_jobs(pathlib.Path('.').resolve())), len(m._BASE_SUBSET), len(m._CASE_DOC))"
# → 50 42 23 19        ⇒ 「39 个可 verify 产物 = 50 项」应为 42；50 = 5 模板/样式 + 2 手写 + demos-index + 42
python3 scripts/baseline.py --check 2>&1 | tail -1     # → 基线一致: 50/50（非 47/47）
ls -l scripts/backfill-table-json.py                   # → -rw-r--r--（baseline.py 为 -rwxr-xr-x）
grep -n "baseline" documents/cli-reference.md          # → 无命中：两个门禁/回填脚本都没进脚本索引
python3 scripts/baseline.py --help | sed -n '/--update/p;/--force/p'
# → --update 重建基线（默认先 verify）   /   --force --update 跳过 verify（越权）   ← 均未提参数回归拦截
```

`testing.md:43` 的「46 文件」也与实测 47 不符（`ls tests/test_*.py | wc -l` = 47）—— 同批顺带修正。

**新发现（本批登记，编号 HG-SEC-259 · NIT）**：`--dry-run` **只在文档里存在**，脚本没有该参数。
`scripts/backfill-table-json.py:9` 与 `documents/testing.md:91` 都写 `--dry-run`，但实测 `--dry-run` 报
`error: unrecognized arguments: --dry-run`（rc=2），缺省行为才是 dry-run（`:98-99`）。别人按文档先
`--dry-run` 会当场撞 rc=2 —— 与 AGENTS「同步脚本先 --dry-run 再 --apply」的仓内惯例直接冲突。

---

## 2. 根因链（path:line）

### ① HG-SEC-249：`verified` 既不是判据也不黏滞

```
cmd_update(root, force)                                     scripts/baseline.py:337-364
 ├─ fresh = snapshot(root)                                  :338   corner/home 从产物正则回收（:193-194）
 ├─ if not force:                                           :339   ── 门只在「非 force」分支
 │   ├─ cmd_verify(...) != 0 → 拒                            :340-343
 │   └─ _param_regressions(root, fresh)                      :344
 │        └─ 只遍历 base['files']，判据 exp[flag] and act[flag] is False   :329-333
 │             ▲ 洗白后 base 里 corner 已是 False  ⇒ 谓词恒假 ⇒ 返回 []（永远放行）
 ├─ data = {..., 'verified': not force, 'files': fresh}      :352-358   ← 只看本次调用，不看旧基线
 └─ 写盘覆盖旧文件                                            :359-361
```

三重失效叠加：

1. **verify 抓不到漏参**：`build_jobs` 的参数全靠 `_recovered_common`（`:219-227`）从产物回收，
   产物已无 `github-corner` ⇒ 回收集也无 `--github-url` ⇒ 重渲与产物逐字节相同 ⇒ verify 绿（`:290-299`）。
   这是已知设计缺口（`:189-191` 注释自陈），存在性钉子原本是补它的唯一手段。
2. **`_param_regressions` 的参照系被自证污染**：它以「旧基线」为参照（`:325-334`），
   而 `--force` 那次已把 `corner:false` 写进旧基线 ⇒ 参照系归零 ⇒ 二次调用恒放行。
3. **`verified` 是孤儿字段**：全仓 `grep -rn verified scripts/ tests/` 只有 `:356` 写入、`:363` 打印、
   `tests/test_baseline_gate.py:149` 一处断言；**没有任何门禁/输出读它** ⇒ 即便翻回 true 也不报警、
   不留痕，`--check`（`:367-423`）看到的只是「基线有 corner:false、产物也 corner:false」的一致性假象。

⇒ 结论：修复必须同时补「参照系粘滞」（旧基线 `verified=false` 时普通 `--update` 拒）与
「`verified` 语义可判定」（= verify 绿 ∧ 无参数回归），并让它进 `--check` 的输出面。

### ② HG-SEC-250：新门无自动化覆盖

`tests/test_baseline_gate.py` 9 例（`:56-182`）里最接近的是 `test_07`（`:131-149`），它只覆盖
「产物**落后** ⇒ `--update` 拒 / `--force` 标 `verified=false`」—— 走的是 `:340` 的 verify 分支。
`_param_regressions`（`:318-334`）与 `--check` 的 `param-lost` 分支（`:399-402`）**零断言**：
删掉 `:344` 那一行、或删掉整个 `_param_regressions`，全量仍 473 passed。

判别性前提必须写死在用例里：**重渲后 `--verify` 必须 rc=0**（否则测的是 verify 分支，不是钉子分支）。

### ③ HG-SEC-252/253/254：回填脚本

`scripts/backfill-table-json.py`
- 行标识：`:79` `rid = str(old.get('strategy') or f'row{idx}')` —— 只取旧行名，改名即断链（252）；
  且不查唯一性 ⇒ 同名行覆盖（253a）。
- 孤儿提取：`:78` `zip(raw['data'], data)` 按索引截断 ⇒ 任一方向的长度差都让尾部旧行整行消失（253b）；
  `:76` 的 `if not a.drop_orphans` 只拦「本次提取」，不碰已存在的 `raw['legacy']` ⇒ `--drop-orphans`
  对已回填文件无效（253c）。
- 差异报告：`:39-43` `extra`（旧有新增无 = 被摘除）标 `('<none>', None)`、`gone`（新增有旧无 = 新增）
  标 `(None, '<dropped>')` —— 名字与值双向错位，且两侧都丢真值（254）；`:24` `SKIP_KEYS` 死代码。

### ④ HG-SEC-256/257/258

- `documents/testing.md:57`（39 应为 42）、`:71`（47/47 应为 50/50）、`:43`（46 文件应为 47）、
  `:98`（9 例 → 10 例）、`:100`（覆盖描述需补参数回归例）。数字无守卫 ⇒ 同款复发（前身 HG-SEC-248）。
- `tests/test_selenium_infra.py:93` 判据 `['"](?:/private|/var)?/tmp(/|['"])` 是枚举，
  `/private/var/tmp`（`/var/tmp` 的 realpath）与真实 `TMPDIR` 形态 `/var/folders/…` 不命中（257）。
- `scripts/baseline.py:431-436` 三处 help 文案停留 v1.1；`scripts/backfill-table-json.py` 权限 644；
  `documents/cli-reference.md:118-131` 核心文件表无这两个脚本（258）。

---

## 3. 文件级改动清单

| # | 文件 | 改动 | 条目 |
|:--|:--|:--|:--|
| 1 | `scripts/baseline.py` | `cmd_update`：新增旧基线 `verified is False` ⇒ 普通 `--update` 拒绝；`verified` 改判为 `verify_ok and not drops`（force 也跑 verify，但 force 只解除拒绝、不写 true）；`--check` 末尾 `verified is False` 打 ⚠️（rc 不变）；`:431-436` help 文案；`:363` 计数文案改「n 项钉子 / m 项实存」 | 249 / 258 / 259 顺带 |
| 2 | `tests/test_baseline_gate.py` | 新增 `test_10_param_regression_blocks_update_and_sticks`（覆盖 249+250）；`test_08` 内补 2 条文档数字守卫 assert（不新增用例） | 250 / 256 |
| 3 | `tests/test_backfill_tool.py`（新） | 4 例：行数不等拒写 / 行键重复拒写 / `field_diff` 方向与取值 / `legacy` dangling 报告 | 252 / 253 / 254 |
| 4 | `scripts/backfill-table-json.py` | 前置校验（`--apply` 前行数相等 + 行键唯一，失败 rc=2 且不写盘；`--drop-orphans` 放行）；`--drop-orphans` 时 `raw.pop('legacy', None)`；`field_diff` 正名 + 带真值；删 `SKIP_KEYS`；新增 dangling legacy 键报告；补 `--dry-run` 实装（no-op，与缺省同义）；权限 644→755 | 252 / 253 / 254 / 258 / 259 |
| 5 | `data/_drama-table-daming-strategy.json`<br>`data/_drama-table-zhuyuanzhang-strategy.json` | `legacy.idiom` 的 `走为上计` 重键为 `走为上`（值不变）；各补一条 `renames` 说明（仿 yongzheng） | 252 |
| 6 | `tests/test_selenium_infra.py` | `:93` 判据换并集正则（含 `/private/var/tmp`、`/var/folders/`） | 257 |
| 7 | `documents/testing.md` | `:43` 46→47 文件 + `test_baseline_gate 9`→`10`；`:57` 39→42；`:71` 47/47→50/50；`:91` `--dry-run` 口径随实装校正；`:98` 9 例→10 例；`:100` 补参数回归 + 二次洗白拒写；新增 `test_backfill_tool.py` 覆盖描述 | 256 / 258 / 259 |
| 8 | `documents/cli-reference.md` | 核心文件表（`:122-130`）新增 `scripts/baseline.py`、`scripts/backfill-table-json.py` 两行；新增小节「渲染基线门禁」4 条命令 | 258 |
| 9 | `AGENTS.md` | `:6` 期望 473→478；`:44` 473 tests（47 文件，含 102 subtests）→ 478 tests（48 文件，含 102 subtests） | **审批**（见 §8） |
| 10 | `README.md:137` / `README.zh.md:135` | 473→478（两处均注明权威在 AGENTS.md） | 250 连带 |

不改：`html-gen.py`、`layout-*.html`、`style-guide.css`、产物 HTML、`data/_render-baseline.json`
（本批不动产物字节 ⇒ 门禁 50/50 应保持全绿，这也是验收判据之一）。

---

## 4. 决策项与推荐

### D1（HG-SEC-249）`verified` 粘滞 + 拒绝策略

- **A（推荐）**：`verified` 语义 = 「本次基线在 verify 绿、且无参数回归的前提下建立」：
  ```python
  verify_ok = (cmd_verify(root, quiet=True) == 0)          # force 也跑（force 只解除拒绝）
  drops = _param_regressions(root, fresh)
  old, _ = load_baseline(root)
  if not force:
      if not verify_ok: 拒
      if drops: 拒
      if old and old.get('verified') is False: 拒          # ← 新增：二次洗白抬成两次显式 --force
  data['verified'] = bool(verify_ok and not drops)
  ```
  `--check` 在 `base['verified'] is False` 时末行打 `⚠️ 基线为越权建立（verified=false）：角标/首页钉子可能已失效`，**rc 不变**（不破坏 `test_01/test_03` 的 rc=0 断言）。
  终止性：第一次 `--force`（真摘角标）⇒ `drops` 非空 ⇒ 写 false；第二次 `--force` ⇒ 基线已无该钉子 ⇒ `drops` 空且 verify 绿 ⇒ 写 true。**两次显式 force 才洗白，且中间态留痕**。
- **B**：只加拒绝（`old.verified is False` ⇒ 拒），`verified` 仍写 `not force`。**不推荐**：`--force` 永远写 false ⇒ 一旦越过一次就永久 false、每次普通 `--update` 都被拒（死锁），只能靠删基线文件解。
- **C**：只让 `--check` 打 ⚠️，不拦。**不推荐**：`--update` 仍能一次洗白，只是多一行提示。
- 代价：`--force` 从「跳过 verify」变「跳过拒绝」，耗时与普通 `--update` 同（真仓约 1 次全量重渲，实测 42 件判定）。风险等级低（force 的写盘语义不变）。

### D2（HG-SEC-250）测试补位与计数审批

- **A**：仅 `test_baseline_gate.test_10`（473→**474**）。
- **B（推荐）**：A + 新 `tests/test_backfill_tool.py` 4 例（473→**478**）。理由：253 是**静默丢数据**级，
  修完无测试等于把「下一轮重构删掉校验」的复发面留着，与 250 同病；且计数只需一次审批。
- **C**：B + 为 `--check` ⚠️ 再加 1 例（→479）。**不推荐**：`test_10` 已断言 warning 文案，重复。
- 附带（不计数）：`test_08` 内补 2 行 assert，把 `testing.md` 的「42 件判定 / 50 项」与 `len(build_jobs)` / `len(SUBSET)` 绑死（256 的复发守卫，不新增用例 ⇒ 不动计数）。

### D3（HG-SEC-252）legacy 行标识

- **A**：数据侧 re-key 2 处 **+** 工具侧键格式改 `f'{rid}#{idx}'`，并保留旧键兼容读。
- **B（推荐）**：数据侧 re-key 2 处（`走为上计` → `走为上`，值不动）+ 各补 `renames` 说明；工具侧只新增 **dangling 报告**（`legacy` 里按名 join 不到的键逐条列出，非破坏、不改格式）。
  理由：`legacy` 无任何读者（本批已 grep 确认），改格式需迁移 42 条既有键且无守卫；而 dangling 报告能在下次改名时当场暴露，成本近零。
- **C**：`legacy` 值改结构化 `{rid: {idx, value}}`。**不推荐**：收益是「按行名恢复」更稳，但需一次性迁移 + 无消费者验证，超出 P1 口径。
- 字节中性已确认：`legacy` 是 JSON 顶层额外键，模板只序列化 `columns/data`（`:73-74` 注释），
  ⇒ re-key 后 `baseline.py --check` 必须仍 50/50（验收项）。

### D4（HG-SEC-253）回填工具前置校验

- **A（推荐）**：`--apply` 前校验 ① `len(raw['data']) == len(data)` ② 行标识唯一；任一失败 ⇒ 打具体差异、**rc=2、不写盘**，提示 `--drop-orphans` 表示「已知旧行会被丢弃」。`--drop-orphans` 时 `raw.pop('legacy', None)`。
- **B**：只告警不拒（保留 rc=0）。**不推荐**：静默丢数据正是本条要收口的东西。
- rc 约定：0 正常（含 dry-run）/ 2 输入被拒（与 argparse 的 2 同族但文案可区分）/ 1 保留给未来的渲染/IO 失败。

### D5（HG-SEC-254）差异报告正名

- **A（推荐）**：`field_diff` 返回 `{'added': {k: n[k]}, 'dropped': {k: o[k]}, 'changed': {k: (o[k], n[k])}}`；
  打印形如 `行 0: +note='n1'  -idiom='走为上'`（`+` 新增带新值 / `-` 摘除带旧值 / `~` 变更带双值）；
  删除 `SKIP_KEYS`（行级字段集合来自行本身，顶层键天然不进 diff）。
- **B**：只对调两个标签、不补值。**不推荐**：复核者仍看不到「被摘掉的是什么值」。

### D6（HG-SEC-256）文档数字

- **A（推荐）**：`39`→`42`、`47/47`→`50/50`、`46 文件`→`47 文件`、`9 例`→`10 例`；守卫并入 `test_08`（见 D2 附带）。
- **B**：只改数字、不加守卫。**不推荐**：这是 HG-SEC-248→256 的第二次复发。

### D7（HG-SEC-257）tmp 判据

- **A（推荐）**：并集正则（已实测 11 形态 + 仓内零漂移）：
  ```python
  pat = re.compile(r'''['"](?:/(?:private/)?(?:var/)?tmp)(?:/|['"])|['"]/var/folders/''')   # noqa: tmp-path-guard
  ```
  覆盖 `/tmp/`、`/private/tmp/`、`/var/tmp/`、`/private/var/tmp/`、`/var/folders/`；`noqa: tmp-path-guard` 逃生口保留。
- **B**：改成 `Path(tempfile.gettempdir())` 前缀匹配。**不推荐**：判据要看「写字面量」，不是「看本机 TMPDIR 值」。

### D8（HG-SEC-258 + 259）文案/权限/索引/`--dry-run`

- **A（推荐）**：`--update` help 补「先 verify + 参数回归拦截（旧基线 verified=false 时拒）」；
  `--force` help 补「跳过拒绝，不写 verified=true」；`chmod 755 scripts/backfill-table-json.py`；
  `cli-reference.md` 核心文件表补两行（baseline + backfill）+ 新增「渲染基线门禁」小节；
  `backfill --dry-run` 实装为显式 flag（与缺省同义，防文档/实现继续背离）。
- **B**：改文档去掉 `--dry-run`（两处）。**不推荐**：与 AGENTS「同步脚本先 --dry-run」惯例相悖，且用户已按文档用过。

### D9（新 · ⚪ 非阻塞）`--update` 计数文案

临时根只有 1 个真实文件时仍打印「（50 个文件，verified=True）」（快照含 50 项，其中 49 项 `sha256=None`）。
**推荐**：改「（钉子 50 项 · 实存 1 项，verified=…）」。不影响判据，可随 D1 顺带。

---

## 5. 验收判据（命令 + 预期输出，可复跑）

> 全部在 `/Users/jadenli/CodeSpace/html-gen.cli` 下执行；V1 的 `$T` 见 §1.1 的建根步骤。

**V1 · HG-SEC-249 二次洗白已封（D1）**

```bash
python3 scripts/baseline.py --update --root "$T"; echo rc=$?          # 洗白第 4 步：普通 --update
```
预期：
```
❌ 上一份基线是越权建立的（verified=false）—— 先确认产物已按原参数重刷；确属产品决策再 --force。
rc=1
```
```bash
python3 -c "import json;d=json.load(open('$T/data/_render-baseline.json'));print(d['files']['demos/countries-table.html'].get('corner'), d['verified'])"
# 预期: False False        ← 未被翻回 true
python3 scripts/baseline.py --update --force --root "$T"; echo rc=$?  # 第二次显式 force 才允许
# 预期 rc=0，且 verified=True（verify 绿、无 drops）
python3 scripts/baseline.py --check --root "$T" | tail -1              # 预期: 基线一致: 50/50
```

**V2 · HG-SEC-250/252/253/254 测试（D2/D3/D4/D5）**

```bash
python3 -m pytest tests/test_baseline_gate.py -q -n 0        # 预期: 10 passed
python3 -m pytest tests/test_backfill_tool.py -q -n 0        # 预期: 4 passed
python3 -m pytest tests/ -q -n 4                             # 预期: 478 passed
```
判别性（变异，手工跑一次即回滚）：
```bash
# M1 删 baseline.py:344 的 _param_regressions 调用 ⇒ test_10 红
# M2 删 D1 的 old.verified is False 拒绝分支 ⇒ test_10 第三段红
# M3 把 verified 改回 not force ⇒ test_10 第三段红
# M4 去掉 --apply 前行数校验 ⇒ test_backfill_tool 行数用例红
# M5 field_diff 标签换回旧写法 ⇒ 方向用例红
```

**V3 · 回填工具三静默面（D4，§1.3 夹具复跑）**

```bash
python3 scripts/backfill-table-json.py --pair "$S/f253a.html=$S/f253a.json" --apply; echo rc=$?
# 预期: ❌ 行标识重复「离间计」出现 2 次（行 0/1）—— 加 --drop-orphans 表示接受丢旧行；rc=2，文件未改
python3 scripts/backfill-table-json.py --pair "$S/f253b2.html=$S/f253b2.json"; echo rc=$?
# 预期: ❌ 行数不等 5 → 2（尾部 3 行旧数据将丢失）；rc=2
python3 scripts/backfill-table-json.py --pair "$S/f253c.html=$S/f253c.json" --drop-orphans --apply
python3 -c "import json;print(json.load(open('$S/f253c.json')).get('legacy'))"      # 预期: None（已清）
```

**V4 · 差异报告方向（D5）**

```bash
python3 scripts/backfill-table-json.py --pair "$S/f254.html=$S/f254.json"
# 预期末段: 行 0: +note='n1'  -idiom='走为上'
```

**V5 · legacy 悬挂清零（D3）**

```bash
python3 -c "
import json
for f in ['data/_drama-table-daming-strategy.json','data/_drama-table-zhuyuanzhang-strategy.json']:
    d=json.load(open(f)); n=[r['strategy'] for r in d['data']]
    print(f, 'dangling:', [k for k in d['legacy']['idiom'] if k not in n])"
# 预期: 两行均 dangling: []
python3 scripts/baseline.py --check | tail -1        # 预期: 基线一致: 50/50（legacy 不进产物，字节中性）
```

**V6 · tmp 判据（D7）**

```bash
python3 -m pytest tests/test_selenium_infra.py -q -n 0          # 预期: 4 passed
# 探针：把 '"/private/var/tmp/probe"' 与 '"/var/folders/xy/T/f"' 写进任一 tests 文件 ⇒ test_05 红；
#       旧正则对这两形态 0 命中，新正则 2 命中（§1.5 已实测）
```

**V7 · 文案/权限/索引（D8/259）**

```bash
python3 scripts/baseline.py --help | sed -n '/--update/p;/--force/p'
# 预期: --update 重建基线（先 verify；参数回归或旧基线 verified=false 时拒绝；--force 越权）
#       --force  跳过上述拒绝（不把 verified 置 true）
ls -l scripts/backfill-table-json.py | cut -c1-10               # 预期: -rwxr-xr-x
grep -c "scripts/baseline.py\|scripts/backfill-table-json.py" documents/cli-reference.md   # 预期: ≥2
python3 scripts/backfill-table-json.py --pair "$S/f254.html=$S/f254.json" --dry-run; echo rc=$?
# 预期: 正常输出 + rc=0（不再是 unrecognized arguments）
```

**V8 · 文档数字（D6）**

```bash
grep -n "42 个可 verify\|50/50\|47 文件\|10 例" documents/testing.md | head
grep -rn "473 tests\|期望 473" AGENTS.md README.md README.zh.md    # 预期: 无命中（已改 478）
```

**V9 · 全量回归 + 门禁（每批必跑）**

```bash
python3 -m pytest tests/ -q -n 4        # 预期 478 passed（约 55s）
python3 scripts/baseline.py --check     # 预期 基线一致: 50/50（rc=0）
python3 scripts/baseline.py --verify    # 预期 rc=0（42 判定全 current）
```

---

## 6. 测试计划

### 6.1 新增 `test_baseline_gate.test_10_param_regression_blocks_update_and_sticks`

夹具沿用 `test_07`（`:131-149`）的最小根，但**产物必须真实渲染**（这是判别性关键）：

```
tmp = mkdtemp; cp html-gen.py, style-guide.css, layout-table.html, data/_countries-data.json
1) render table + --github-url → --update            → rc0；corner=True、verified=True
2) 同源不加 --github-url 再渲一次（产物字节变、但仍是当前模板产物）
3) --verify                                          → 断言 rc==0   ★「verify 绿」前提
4) --update                                          → 断言 rc==1、stderr 含「基线有 corner」、
                                                       基线文件 sha256 与步骤 1 完全相同（拒写）
5) --update --force                                  → rc0；corner=False、verified=False
6) --update（普通）                                   → 断言 rc==1、stderr 含「越权建立」、
                                                       verified 仍 False、corner 仍 False   ★249 回归
7) --check                                           → rc0 且 stdout 含 ⚠️ 与「verified=false」
```

- 步骤 3 是 250 的判别断言：删掉 `_param_regressions` 调用（M1）步骤 4 会变 rc=0；
  把 `verified` 写回 `not force`（M3）或删 D1 新分支（M2）步骤 6 会变 rc=0。
- 全部走 `--root` 临时副本，真仓零写入（沿用 `run()` 助手 `:39-43`）。

### 6.2 新增 `tests/test_backfill_tool.py`（4 例）

| 用例 | 输入 | 断言 |
|:--|:--|:--|
| `test_01_row_count_mismatch_refuses_apply` | 旧源 5 行 / 产物 2 行 | rc=2、JSON 文件 mtime+内容未变；加 `--drop-orphans` → rc=0 且 `data` 2 行 |
| `test_02_duplicate_row_key_refuses_apply` | 两行同 `strategy` | rc=2、stderr 点名重复键；`--drop-orphans` 放行 |
| `test_03_field_diff_direction_and_values` | 新增 `note` / 摘除 `idiom` | `+note='n1'`、`-idiom='走为上'`，且不再出现 `'<dropped>'` 字面 |
| `test_04_legacy_dangling_reported` | `legacy.idiom={'旧名':'v'}` + 行名已改 | dry-run 输出含 dangling 列表；真数据三表 dangling 为 0（读 `data/_drama-table-*strategy.json`，只读） |

夹具全在 `tempfile.mkdtemp()`（守 `test_selenium_infra.test_05` 的 tmp 判据），脚本以
`run_gen` 同款 subprocess 调 `scripts/backfill-table-json.py`，不 import（脚本是 CLI 工具）。

### 6.3 既有用例影响面

- `test_01/03/04/06` 读真仓 `--check`：真仓基线 `verified=true` ⇒ D1 的 ⚠️ 不出现、rc 不变 ⇒ 不受影响。
- `test_07` 断言 `--force` 后 `verified=false`：D1 下该根产物是假 HTML、verify 红 ⇒ `verified = verify_ok and not drops` = False ⇒ **仍绿**。
- `test_02/05` 不涉 `verified`。
- `test_08` 追加 2 条 assert（文档数字），当前真仓数字修正后应绿。
- `test_selenium_infra.test_05` 判据收紧后，仓内 `tests/**/*.py` 逐行比对**零命中差异**（§1.5 已实测）。

### 6.4 计数与文档同步面（一次改全）

`AGENTS.md:6`、`AGENTS.md:44`、`README.md:137`、`README.zh.md:135`、`documents/testing.md:43`（文件数 47 / `test_baseline_gate 10` + 新增 `test_backfill_tool 4`）、`:98`（10 例）。
`features.md` 只指向 AGENTS（`:203`），无需数字改动 —— 若采纳 D2-B，可在其脚本清单补一行 `backfill-table-json.py`（可选）。

---

## 7. 风险与回滚

| # | 风险 | 影响 | 缓解 |
|:--|:--|:--|:--|
| R1 | D1 让 `--force` 也跑 verify ⇒ 真仓约 1 次全量重渲（42 件），`--force` 变慢 | 中（仅运维体验） | 提示语给出耗时预期；确需极速可后续加 `--no-verify`（本批不做，避免开关膨胀） |
| R2 | D1 拒绝路径让「合法摘角标」需要两次 `--force` | 低 | 错误文案直接给两条命令（先按原参数重刷 / 确认后 `--force`） |
| R3 | 旧基线若已是 `verified=false`（历史遗留），首次普通 `--update` 会拒 | 中 | `--check` ⚠️ 会提前暴露；`--force` 一次即恢复常态（verify 绿 + drops 空） |
| R4 | D4 引入 rc=2 可能与调用方（cron/手工脚本）对不上 | 低 | 本仓无该脚本的自动化调用方（`grep -rn backfill` 仅文档）；文案明确「rc=2=输入被拒」 |
| R5 | D3 re-key 动数据文件 | 低 | `legacy` 不进产物 ⇒ 字节中性；验收 V5 用 `--check` 50/50 兜底；改动前 `git diff` 仅 2 处键名 |
| R6 | 计数 478 若漏改任一文档面 ⇒ 下一轮评审再记一条 | 中 | §6.4 五面清单 + V8 的 `grep -rn "473"` 必须零命中 |
| R7 | 本批跨 4 类改动，单笔提交难评审 | 中 | 按 §9 四批落地，每批一次 `--check` + 全量回归 |

**回滚**：每批独立 commit（`type@scope: subject`，path-scoped `--only`）；数据/脚本类回滚用
`git checkout <sha>^ -- <path>`；`data/_render-baseline.json` 不在本批改动范围，无需回滚。

---

## 8. 审批登记（AGENTS.md 计数 473 → 478）

- **触发**：D2-B 新增 5 例（`test_baseline_gate` +1、`tests/test_backfill_tool.py` +4）。
- **需改文本（精确，两行）**：
  - `AGENTS.md:6` ``（期望 473 passed）`` → ``（期望 478 passed）``
  - `AGENTS.md:44` ``- 473 tests（47 文件，含 102 subtests）`` → ``- 478 tests（48 文件，含 102 subtests）``
- **审批路径（按仓内先例 CL028「审批窗口放行后两处均落」）**：
  1. 首选：本会话内用户放行后直接写 `AGENTS.md`（两处 + 不改 4,000B 上限，改完 `wc -c AGENTS.md` 复核）。
  2. 若本会话 `AGENTS.md` 写入被 managed 拦截（dev CLI 会话历史现象）：代码/测试/文档先落并 push 前置完成，
     `AGENTS.md` 两行以「待批文本」形式写进交付回执，由用户在放行窗口或 default 会话落地；
     **未落地前不得 `step-done` 报「计数已同步」**，回执须写明「计数待批」。
- **同步面**（与 AGENTS 同批）：`README.md:137`、`README.zh.md:135`、`documents/testing.md:43`、`:98`。
- **若采纳 D2-A（仅 474）**：上述文本把 478→474、48 文件→47 文件；其余步骤不变。

---

## 9. 落地顺序（实施批，供下一步派发）

1. **批1 安全门**：`scripts/baseline.py`（D1 + D8 文案 + D9）→ `tests/test_baseline_gate.py`（test_10 + test_08 守卫）→ V1/V2/V9。
2. **批2 回填工具**：`scripts/backfill-table-json.py`（D4/D5/D3 报告/259/chmod）→ `tests/test_backfill_tool.py` → V3/V4/V7。
3. **批3 数据**：两表 `legacy.idiom` re-key + `renames` → V5（`--check` 必须 50/50）。
4. **批4 文档 + 审批**：`tests/test_selenium_infra.py`（D7）→ `documents/testing.md` / `cli-reference.md` → 计数四面 → V6/V8/V9。

每批提交后跑 `python3 scripts/baseline.py --check`（预期 50/50）与全量 `pytest -q -n 4`；
`baseline.py --update` **本批不需要**（无产物/模板字节变化，若跑出 verified 变化即说明有意外写入，须回查）。
