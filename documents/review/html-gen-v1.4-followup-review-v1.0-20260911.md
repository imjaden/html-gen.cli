# html-gen 反馈通道 v1.4 follow-up 修复复核报告 v1.0（2026-09-11）

> 闭环: HTML-GEN-CL009 · 类型: 实现审计尾项复核（delta，只读）· 前置: `documents/review/html-gen-v1.4-impl-audit-v1.0-20260911.md`（CONDITIONAL PASS 95/A）

## 元信息

| 项 | 值 |
|:---|:---|
| Reviewer | Security Reviewer |
| Level | L2（implementation-audit-recheck） |
| Scope | `6a5b56d..HEAD`（1 笔：`ee85686 fix@sync: HG-SEC-140/141/142/135/136 跟进修复`） |
| Verdict | 🟢 **PASS 100/100（A）** — 5 项 targeted findings 全闭合，delta 零 🔴/🟡 引入，1 🟢 记录（HG-SEC-144 pre-existing） |
| Score | 100 / 100 |
| Tracking | HG-SEC-140/141/142/135/136（✅ closed ee85686）+ HG-SEC-144（🟢 record） |
| 是否可推 | ✅ 可推（无阻断；ff-only，不 force，不推 gitee） |

## 1. 结论

`ee85686` 对上一轮 CONDITIONAL PASS 遗留的 5 项 finding 全部真实修复，逐条实证闭合。核心安全项 HG-SEC-140（🟡）经代码层 + 独立 temp-repo 实证双重确认：`git_commit()` 的 commit 命令现已带 `-- <paths>`，已暂存的无关文件不再被裹走。回归 305 passed 串/并双绿（本轮并行 0 flaky），targeted test_issue_feedback 37 passed（TC-30 已含「已暂存无关文件不得被裹走」回归）。delta 未引入任何新 🔴/🟡；唯一新记 🟢 HG-SEC-144（`data-fix.yml` 回退默认值仍残留于代码 2 处，v1.3 rename 遗留、pre-existing、零当前影响）。HG-SEC-134（🟡 pre-existing stored XSS）本轮未修，如实保留为 open（用户决策项）。

## 2. 逐条闭合核对

| # | 严重度 | 期望修复 | 复核点 | 结论 |
|:--|:--|:--|:--|:--|
| HG-SEC-140 | 🟡 | `git commit` 带 `-- <paths>` | `git_commit()` L328-329 commit 命令含 `--` + 两 pathspec；**实证**：temp repo 先 `git add staged.txt` 再调 `git_commit` → `git show --name-only` 仅 `data/d.json`+`demos/x.html`，`git status` 仍 `A  staged.txt` | ✅ Closed |
| HG-SEC-141 | 🟢 | rev-parse 失败不再误报「未产生提交」 | L332-337 检 `returncode != 0 or not short` → 返回 `sha-unknown`；main L565-568/L576-577 文案「本地提交已产生（sha 读取失败，待维护者确认）」且 exit 0 | ✅ Closed |
| HG-SEC-142 | 🟢 | body 逐条使用 `#N` | L557-559 cbody 每行 `- #{a['issue']} …`，不再重复全量 `#N,#M` | ✅ Closed |
| HG-SEC-135 | 🟢 | docstring 模板名 | docstring L5 引 `data-fix-countries.yml`（原 `data-fix.yml`）；L25 设计引用已 v1.4 | ✅ Closed |
| HG-SEC-136 | 🟢 | AGENTS.md 摘要段 | 摘要段为 `data-fix-countries.yml` + 「字段由下拉选择，不含主键/匹配键/视频列」+ 「自动提交两文件（本地，`--no-commit` 关闭）」；`grep data-fix.yml` 命中 0 处 AGENTS.md（无裸残留） | ✅ Closed |

## 3. 真实运行验证（本复核实测）

| 命令 | 结果 |
|:---|:---|
| `python3 -m pytest tests/test_issue_feedback.py -q -n 0` | **37 passed**（3.07s；TC-30 含「已暂存无关文件不得被裹走」回归） |
| `python3 -m pytest tests/ -q -n 0` | **305 passed**（127.64s） |
| `python3 -m pytest tests/ -q -n 4` | **305 passed**（40.68s；本轮 0 flaky） |
| `python3 scripts/countries-issue-sync.py --check-template` | `[校验] 模板 data-fix-countries.yml … 一致（15 项）`，exit 0 |
| `python3 scripts/countries-issue-sync.py --list` | `待处理 1 条 / 可执行 0 条 / 跳过 1 条` + `#4 [跳过] note 建议值与现值一致` + 引导行 `→ python3 scripts/countries-issue-sync.py --issue 4 --dry-run`，exit 0 |
| `git status --short` | 空（工作树干净） |

## 4. HG-SEC-140 独立实证（temp repo，非测试桩）

```
git init tmp; git add staged.txt          # 模拟并行会话已暂存无关文件
mod.PROJECT_ROOT = tmp
git_commit(target, 't', 'b', ['data/d.json','demos/x.html'])
  → sha='276bc57' err=None
git show --name-only HEAD → ['data/d.json', 'demos/x.html']   # 仅两目标文件
git status --porcelain    → 'A  staged.txt'                    # 无关文件仍留 index
```

与 TC-30 扩展回归断言一致，双源互证：`git commit … -- <paths>` 在「并行会话已 `git add` 无关文件」边界下确实只提交本次处置两文件。

## 5. Findings

| # | Severity | Title | File:Line | Status |
|:--|:--|:--|:--|:--|
| HG-SEC-140 | 🟡 | `git commit` 未带 pathspec，可能裹走无关已暂存文件 | scripts/countries-issue-sync.py:327 | ✅ Closed (ee85686) |
| HG-SEC-141 | 🟢 | `rev-parse` 未检 returncode，罕见失败误报「未产生提交」 | scripts/countries-issue-sync.py:330-331 | ✅ Closed (ee85686) |
| HG-SEC-142 | 🟢 | 多 issue 提交 body 每行重复全量 `#N,#M` | scripts/countries-issue-sync.py:551-553 | ✅ Closed (ee85686) |
| HG-SEC-135 | 🟢 | docstring 模板名陈旧 | scripts/countries-issue-sync.py:5 | ✅ Closed (ee85686) |
| HG-SEC-136 | 🟢 | AGENTS.md 摘要段陈旧 | AGENTS.md:100 | ✅ Closed (ee85686) |
| HG-SEC-144 | 🟢 | `data-fix.yml` 回退默认值仍残留于代码 2 处（v1.3 rename 遗留） | scripts/countries-issue-sync.py:373 / layout-table.html:1100 | Open（🟢 record，pre-existing） |

### HG-SEC-144 详情（🟢，pre-existing，非本 delta 引入）

v1.3 将模板 `data-fix.yml` 重命名为 `data-fix-countries.yml`，但两处**回退默认值**未同步更新：

- `scripts/countries-issue-sync.py:373`：`tmpl_rel = target.get('template') or 'data-fix.yml'`（`check_template` 默认路径）
- `layout-table.html:1100`（及 demos/countries-table.html:1340、demos/demos-index.html:1333 生成物）：`add('template', (FB_CFG && FB_CFG.template) || 'data-fix.yml')`

当前唯一案例 countries 两处均显式指定 `data-fix-countries.yml`（feedback-targets.yaml:18 `template:` / data/_countries-data.json `options.feedback.template`），故回退分支从未命中，**零当前影响**。未来新增 target 若漏配 `template`：浏览器侧会拼出指向不存在模板的 `?template=data-fix.yml`（死链），脚本侧 `check_template` 会以「模板不存在」exit 1（安全失败）。建议 follow-up：回退默认改 `data-fix-countries.yml`（或删除回退、强制显式声明）。非阻断。

## 6. Pre-existing（非本 delta 引入，如实保留）

- **HG-SEC-134（🟡，仍 open，用户决策项）**：可写文本列（note/capital_zh/capital_en/ethnic_groups/religions）`escape=None`，layout-table raw innerHTML 渲染 → stored XSS。本轮未修，风险面不变（唯一增量 `--apply` 自动提交会把 XSS 载荷一并提交进历史）。建议 follow-up：加 `col.escape: true` 或脚本 string 字段 escapeHtml。
- **HG-SEC-143（🟢，仍 open，历史记录）**：issue #4（阿尔巴尼亚 note）数据变更与 feat@sync 提交混包。属历史提交卫生问题，不改写历史无法修复（同 HG-SEC-130 作者占位性质）。

## 7. Positives

- 修复链完整：HG-SEC-140 一行修复同时补了 TC-30 扩展回归（真实 git 仓库验证，非纯桩），fix 与 test 同 commit 闭环
- HG-SEC-141 引入 `sha-unknown` 语义分支，区别于 `no-change`/失败，回评文案精确区分三态
- 本轮并行全量 305 passed 零 flaky（上轮 1 例 test_videos 并行 flaky 未复现）
- commit 职责单一：ee85686 仅动 AGENTS.md + 脚本 + test（3 文件），无夹杂

## 8. 处理

- 结论：🟢 PASS 100/A，无阻断，可推。
- 提交：`audit@review: v1.4 跟进修复复核 PASS (HTML-GEN-CL009)`（显式 pathspec：报告 + review-log + .review-level.yaml）。
- 推送：`git push github main`（ff-only，不 force，不推 gitee）。
- follow-up（非阻断）：HG-SEC-144 回退默认改 `data-fix-countries.yml`；HG-SEC-134 加 `col.escape`。
