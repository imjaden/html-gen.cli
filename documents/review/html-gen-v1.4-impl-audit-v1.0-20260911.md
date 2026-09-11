# html-gen 反馈通道 v1.4 实现审计报告 v1.0（2026-09-11）

> 闭环: HTML-GEN-CL009 · 类型: 实现审计（delta，只读）· 设计基线: `documents/solutions/countries-issue-feedback-design-v1.4-20260911.md`

## 元信息

| 项 | 值 |
|:---|:---|
| Reviewer | Security Reviewer |
| Level | L2（implementation-audit） |
| Scope | `a2880fb..HEAD`（3 笔：0bad457 feat@sync 实现+设计 / 9f1ed83 docs@html-gen 文档同步 / 537eeb4 docs@readme README 同步） |
| Verdict | 🟡 **CONDITIONAL PASS 95/100（A）** — 1 🟡 delta 引入（非阻断）+ 3 🟢 记录 + 1 🟡 pre-existing 未变 |
| Score | 95 / 100 |
| Tracking | HG-SEC-140（🟡 delta 引入）+ HG-SEC-141..143（🟢 records） |
| 是否可推 | ✅ 可推（唯一 🟡 非阻断，见 §9 修复建议） |

## 1. 结论

v1.4 增量（`--apply` 自动提交 + `--list` 引导行 + `python3` 口径）实现与设计 §2..§6 逐条命中，核心安全要求（B1 显式 pathspec、C1 写盘前预检、G1 失败不回滚、退出码语义、shell=False 全链路）均真实落位。测试 305 passed（串/并双绿，1 次并行 flaky 已隔离复跑恢复）。唯一 delta 引入的 🟡：`git_commit()` 的 `git commit` 未带 pathspec，会提交整个已暂存索引——在「并行会话已 `git add` 无关文件」的边界场景下，仍可裹走非本次改动，未完全达成设计 B1 的「本次提交只含本次处置」意图（验收标准 #1 在边界下不保证）。一行修复即可闭合，非阻断。

## 2. 逐条核对（设计 §2..§6 vs 实现）

| 设计项 | 要求 | 实现位置 | 结论 |
|:---|:---|:---|:---|
| §2.1 A1/I1 触发 | 仅 `--apply` 且非 `--no-commit`；list/dry-run/check-template 恒不提交；只 commit 不 push | main L546 `if not args.no_commit:`；L509/514 早退；无 push 调用 | ✅ |
| §2.2 B1 显式 pathspec | `paths=[data,html]`；禁 `git add -A` | `git_paths` L301-306；`git add --` L324；全脚本 grep 无 `add -A`/`add .` | 🟡 部分：`git add` 带 pathspec，但 `git commit` L327 未带（见 HG-SEC-140） |
| §2.3 C1 写盘前预检 | `git status --porcelain -- <data> <html>` 非空 → 拒绝 exit 1，在写盘前 | `git_dirty` L309-314；main L522-529（在写盘 L530 与重建 L540 之前） | ✅ |
| §2.4 D1/E1 提交消息 | `data@<scope>: apply #N <field> 更新 (HTML-GEN-CL009)`；scope=`commit.scope`→`dataset`→`data`；多 issue `#N,#M`；一条提交 | main L547-550；config `commit.scope: countries` L42-43 | ✅ |
| §2.5 G1/H1 | 无变化不空提交；失败不回滚 + exit 1 + 回评注明 | `git_commit` L317-331（`no-change`）；main L555-562、L573-580 | ✅ |
| §2.6 F1 回评 | 写盘→重建→提交→回评；带本地短 sha（待推送）；删「提交由维护者完成」 | main L540-542（提交）→ L573-579（回评）；L564-571 文案分支 | ✅ |
| §3 O1/Q1 引导行 | 每条 issue 后 `→ python3 … --issue N --dry-run`，可执行+跳过都打印，5 空格缩进 | main L504、L507（HINT L298） | ✅ |
| §3 P1 | 引导行不进 `--json` | `--json` 分支 L495-498 早退，无 hint | ✅ |
| §4 M1 口径 | docstring/提示统一 `python3 scripts/…`；`[执行]` 保留精确命令 | docstring L11-19；`[执行]` L340 用 `sys.executable`+绝对路径 | ✅ |
| §5 J1 配置 | `target.commit.scope` | feedback-targets.yaml L42-43 | ✅ |

## 3. 真实运行验证（本审计实测）

| 命令 | 结果 |
|:---|:---|
| `python3 -m pytest tests/ -q -n 0` | **305 passed**（128.51s） |
| `python3 -m pytest tests/ -q -n 4` | **305 passed**（37.32s；首轮 1 例 `test_videos::test_07_split_preview_videos` 并行 flaky，隔离复跑 1 passed，重跑全量 305 passed） |
| `python3 scripts/countries-issue-sync.py --list` | `[列表] 待处理 1 条 / 可执行 0 条 / 跳过 1 条` + `#4 [跳过] note 建议值与现值一致` + 引导行 `     → python3 scripts/countries-issue-sync.py --issue 4 --dry-run`，exit 0 |
| `python3 scripts/countries-issue-sync.py --check-template` | `[校验] …一致（15 项）`，exit 0 |
| `git status --short` | 空（工作树干净） |
| `git log -1 --stat` | HEAD 537eeb4 仅 README.md 1 文件，无测试提交残留 |

## 4. 安全面核查

- **B1 pathspec 实证**：全脚本 grep 仅 `git add --`（L324）/`git commit`（L327）/`git status --porcelain --`（L311）/`rev-parse`（L330），无 `git add -A` / `git add .`。✅
- **预检顺序**：main L522-529 预检 → L530 写盘 → L540 重建 → L544 提交。预检在写盘与重建**之前**。✅
- **shell 注入**：gh/git 调用统一走 `run()`（L50-51 `subprocess.run(..., shell=False, ...)` list-form），无字符串拼接 shell 命令。✅
- **提交裹走无关文件（HG-SEC-140）**：见 §9。🟡
- **--no-commit 跳预检**：设计约定（§2.1 提交仅在 `--apply && !--no-commit`；预检是提交前置）。test_33 明确断言「--no-commit 时不做预检」。✅ 语义等同 v1.3（不提交=直接写盘），属有意的维护者逃生口。
- **退出码语义**：预检脏/预检失败/提交失败 → exit 1（L527/529/580）；参数错误（`--field` 无 `--issue`、config 缺失）→ exit 2（L460/448）。✅

## 5. 兼容与回归

- v1.3 行为不回退：主键/匹配键硬保护（`guarded_fields` L210-215）、双形态字段解析（`resolve_field` L191-207）、`--check-template`（L365-417）、`--issue/--field/--value/--value-file` 人工裁决（L427-432、L459-468）均未改动。
- `--json` 结构不变：L495-498 仍输出 `{status, data:{actions, skipped}}`，无新增字段（test_39 断言 `sorted(keys)==['actions','skipped']`）。
- 文档一致性：AGENTS.md（v1.4 自动提交 bullet + 305 tests 计数 + python3 口径）、README.md（下拉选字段 + 提交两文件 + `--no-commit`）、features.md（295→305）、prompts/{all,html-gen.md,html-gen.json,kb/*.html}、skills/html-gen/SKILL.md 均同步 v1.4 设计引用 + python3 口径，与实现一致。✅
- 测试计数 305 与 AGENTS.md/features.md 声明的 305 一致。✅

## 6. ops 已完成验证（如实记录，可复核）

| 项 | 结果 | 复核 |
|:---|:---|:---|
| 无变化路径 `--issue 4 --apply` | 跳过、无提交、树干净、rc=0 | ✅ 本审计 `--list` 复现 issue #4 幂等跳过 |
| 提交路径 测试 issue #5 | `[提交] 6915436`，`git show --name-only` 仅 2 文件，回评含 sha，已 `git reset --hard HEAD~1` 回收 | ✅ 历史无 6915436 残留（`git log` 干净） |
| C1 真实预检 | 脏文件 + 可执行 issue → rc=1、数据未覆盖、无重建，已复原 | ✅ 代码路径 L524-529 确认 |
| issue #4 真实反馈保持 OPEN | 内容与现值一致 → 幂等跳过 | ✅ `--list` 确认 |

## 7. Findings

| # | Severity | Title | File:Line | Status |
|:--|:--|:--|:--|:--|
| HG-SEC-140 | 🟡 | `git commit` 未带 pathspec，可能裹走无关已暂存文件 | scripts/countries-issue-sync.py:327 | Open（建议修，非阻断） |
| HG-SEC-141 | 🟢 | `rev-parse --short HEAD` 未检 returncode，罕见失败时回评误写「未产生提交」 | scripts/countries-issue-sync.py:330-331 | Open（记录） |
| HG-SEC-142 | 🟢 | 多 issue 提交 body 每行重复全量 `#N,#M`（设计 §2.4 为逐条 `#N`） | scripts/countries-issue-sync.py:551-553 | Open（记录） |
| HG-SEC-143 | 🟢 | issue #4（阿尔巴尼亚 note）数据变更与 feat@sync 实现提交混包，未走独立 `data@countries: apply #N` | 0bad457 | Open（记录） |

### HG-SEC-140 详情（🟡，delta 引入）

`git_commit()` 流程：`git_dirty` → `git add -- <paths>` → `git commit -m … -m …`（**无 pathspec**）→ `rev-parse`。`git commit` 不带 pathspec 会提交**整个已暂存索引**，而非仅两目标文件。

C1 预检（`git status --porcelain -- <data> <html>`）只过滤两目标文件，**看不见**索引里其他已暂存文件。故当并行会话/其他脚本（如 `cloudwise-news-sync.py` 的 `git add -A` 被中断）已 `git add` 无关文件时，预检通过、本次 `git commit` 一并裹走。

**实证**（本审计 temp repo 复现）：
```
M  other.txt            # 并行会话已 stage 无关文件（未提交）
 M data/d.json /  M demos/x.html   # 本脚本待提交两文件
git add -- data/d.json demos/x.html && git commit -m '…'
git show --name-only HEAD → data/d.json, demos/x.html, other.txt   # other.txt 被裹走
```

这恰好是设计 §2.2 B1 引述的「并行会话 WIP（CL002 FIND-002）」场景，B1 的「本次提交只含本次处置」意图未在 commit 步闭环，验收标准 #1（`git log -1 --name-only` 仅两文件）在边界下不保证。

**修复（一行）**：提交也带 pathspec —— `git commit -m title -m body -- <data> <html>`（已实证：同场景 `git commit … -- data demos` 后 `git show` 仅两文件，`other.txt` 仍留在 index 未提交）。

## 8. Positives

- B1 显式 pathspec 落在 `git add --`（区别于既有 `cloudwise-news-sync.py` 的 `add -A`），代码注释明示 CL002 教训
- C1 预检真实拦截写盘/重建/提交（test_34 断言数据未覆盖、无 rebuild/commit/comment）
- G1 失败不回滚 + 回评「提交失败，待维护者处理」+ exit 1（test_37 断言数据已写、回评含措辞）
- F1 回评带真实本地短 sha `（待推送）`，删除 v1.3「提交由维护者完成」旧文案（test_31）
- TC-30 用**真实 git 仓库**验证 pathspec 与 no-change（非纯桩），测试质量高
- `--list` 引导行可执行/跳过均打印且不进 `--json`（test_36/38/39）

## 9. Pre-existing（非本 delta 引入，未变）

- **HG-SEC-134（🟡，仍 open）**：可写文本列（note/capital_zh/capital_en/ethnic_groups/religions）`escape=None`，layout-table raw innerHTML 渲染 → stored XSS。v1.4 未触碰渲染/转义逻辑，风险面不变；唯一增量是 `--apply` 自动提交会把 XSS 载荷一并提交进历史。仍建议 follow-up（加 `col.escape: true` 或脚本 string 字段 escapeHtml）。
- HG-SEC-135（🟢）：docstring `:5` 仍引 `data-fix.yml`（实际模板为 `data-fix-countries.yml`），`:21` 设计引用已由 v1.4 更正为 v1.4。部分闭合。
- HG-SEC-136（🟢）：AGENTS.md 摘要段仍写 `data-fix.yml` + 「预填 field/current」，v1.4 未更正摘要段。仍 open。

## 10. 处理

- 结论：🟡 CONDITIONAL PASS 95/A，唯一 🟡（HG-SEC-140）非阻断（低概率、人工触发、一行修复），报告显式声明可推。
- 提交：`audit@review: 反馈通道 v1.4 实现审计 CONDITIONAL PASS (HTML-GEN-CL009)`（显式 pathspec：报告 + review-log + .review-level.yaml）。
- 推送：`git push github main`（ff-only，不推 gitee，不 force）。
- follow-up 建议（非阻断）：HG-SEC-140 一行修复 `git commit … -- <paths>`；HG-SEC-134 加 `col.escape`。
