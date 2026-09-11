# html-gen 推送前复核（round-3）— review 报告 v1.0

- **日期**: 2026-09-11（round-3，两轮历史清理后）
- **Reviewer**: Security Reviewer
- **Level**: L2（push-review / commit-range-audit）
- **范围**: `github/main..HEAD` 共 12 笔（`f2de562..1b060b9`）
- **结论**: 🟢 **PASS 100 / 100（A）** — 无 🔴 / 🟡，1 🟢 记录（作者占位，非阻断）

---

## 0. 结论

**PASS**。两轮历史清理（清理 1 历史重写移除 code-inventory；清理 2 删除 MyVideos 文档）均已完成且无残留，CL009 链 9 笔 SHA 未变，回归 288 passed（串行/并行双绿），CL009 交付面抽查全中，12 笔 commit 类型扫描全规范。唯一遗留为 🟢 记录 HG-SEC-130（10 笔 commit 作者占位 `t <t@t.com>`，因「不改写历史」约束无法修复，非阻断）。可执行 ff-only push。

---

## 1. 核验证据表（必做 6 项）

| # | 核验项 | 命令 | 期望 | 实测 | 判定 |
|:--:|:---|:---|:---|:---|:--:|
| 1 | 无 MyVideos 残留 | `grep -rn "MyVideos" --include=* .`（排除 .git/ cache/） | 0 行 | **0 行** | ✅ |
| 2a | 无 code-inventory 提交 | `git log --all --oneline -- data/_code-inventory-data.json demos/code-inventory` | 空 | **0 行** | ✅ |
| 2b | 无 code-inventory 对象 | `git rev-list --all --objects \| grep -c code-inventory` | 0 | **0** | ✅ |
| 2c | HEAD 树无 code-inventory | `git ls-tree -r HEAD --name-only \| grep -c code-inventory` | 0 | **0** | ✅ |
| 3 | 无悬挂引用 | `grep -rn "html-gen-fix-design-v1.0-20260806\|heading-levels-fix-design-v1.0-20260812\|handoff-html-gen-dev" --include=*.md .`（排除 .git/ cache/） | 0 行 | **0 行** | ✅ |
| 4 | 回归串行 | `python3 -m pytest tests/ -q -n 0` | 288 passed | **288 passed**（128.48s） | ✅ |
| 4 | 回归并行 | `python3 -m pytest tests/ -q -n 4` | 288 passed | **288 passed**（37.96s，见 §4 flaky 说明） | ✅ |
| 5a | CL009 交付 | `grep -c spFeedbackBtn demos/countries-table.html` | 1 | **1** | ✅ |
| 5b | CL009 交付 | `grep -c 'class="github-corner"' demos/countries-table.html` | 1 | **1** | ✅ |
| 5c | CL009 交付 | `scripts/countries-issue-sync.py --list` | 正常退出 | **「无待处理 issue」exit 0** | ✅ |
| 6 | commit 类型扫描 | 12 笔 `type@scope` | 无 add@/fixed@/remove@ | **全规范**（见 §5） | ✅ |

> 说明：命令实际以 `/usr/bin/python3`（3.9.6，pytest 8.4.2 / xdist 3.8.0 / selenium 4.36.0）执行；`python3` 裸名在后台 shell 会被 conda 初始化 + 别名钩子劫持到 Homebrew python@3.14（无 pytest），故全程显式用绝对路径。

---

## 2. 两轮清理确认

### 清理 1（历史重写，用户决策 B）

- 原历史含 5 笔 code-inventory 提交（来源 MyVideos 项目 documents 番号主表），其中 `data/_code-inventory-data.json`（334 KB，832 番号 + 649 magnet + 成人片商名）构成公开仓库合规风险（上轮判 🔴 HG-SEC-125）。
- 已整体从历史移除 + `reflog expire --expire=now --all` + `git gc --prune=now` 物理清除本地对象。
- `git rev-list --all --objects` 中 code-inventory 计数 = **0**（§1 核验 2b），确认对象库已无该内容。
- `demos/countries-table.md` 来源行改「公开数据集（World Bank + UN M49 + zh_names 手工校核表）」（`510c5b4`）。

### 清理 2（`1b060b9`，用户指令「删除提及 MyVideos 的文档」）

- 删除 3 文件：`documents/archive/root-20260908/html-gen-fix-design-v1.0-20260806.md`、`…/heading-levels-fix-design-v1.0-20260812.md`、`documents/handoff/handoff-html-gen-dev.md`。
- 清理 6 处悬挂引用（verify-prompt-d1d6 / handoff-html-gen-review / verify-prompt-heading-levels / heading-levels-fix-review-v1.0 / heading-levels-fix-review-prompt / doc-slide-template-handbook §6.4 + 归档表行）。
- §1 核验 3 确认三文件路径名 grep 零残留。
- **注**：这 3 个文件存在于已发布历史（`6631eed` 及更早），本次仅使其从 HEAD 起不存在；从已发布历史抹除需 force-push，未执行（符合「不 force」约束）。

---

## 3. Findings 处置表（HG-SEC-125..133，续接 CL009 实现审计的 124 之后）

round-2 推送复核曾编号 HG-SEC-125..133，其审计轨迹（报告 + review-log + .review-level.yaml 条目）因引用了被清理的 code-inventory 提交而在清理 1 中被一并移除。本轮在「唯一结论源」中重建该轨迹，使编号与存活的 commit 消息（`9974fe8` 引用 HG-SEC-128/132）一致。

| ID | 严重度 | 描述 | 处置 | 证据 |
|:--:|:--:|:---|:---|:---|
| HG-SEC-125 | 🔴 | code-inventory 公开 832 JAV 番号 + 649 magnet + 成人片商名 | ✅ 已处置 | 清理 1 历史重写 + gc；§1 核验 2a/2b/2c = 0 |
| HG-SEC-126 | 🔴 | title 漂移破坏 `demo --rebuild` 幂等 | ✅ 已处置 | 相关提交随历史重写移除；回归 test_08/test_09 通过 |
| HG-SEC-127 | 🟡 | 三处非 rebuild 一致漂移 | ✅ 已处置 | 同上（registry 口径随历史移除） |
| HG-SEC-128 | 🟡 | 设计 v1.2 §4.1/§6.1/§6.3/§13 五处「数据纠错」残留 | ✅ 已处置 | `9974fe8`；现存 4 处「纠错」均为修订记录/决策表 B1/通用词，非实现措辞 |
| HG-SEC-129 | 🟢 | commit 类型非规范 add@/fixed@/remove@ | ✅ 已处置 | 清理 1 移除相关提交；12 笔扫描全规范（§5） |
| HG-SEC-130 | 🟢 | 10 笔 commit 作者占位 `t <t@t.com>` | ⚠️ **open（非阻断）** | 「不改写历史」约束下无法修复；git 身份已配置 `Jaden.Li <jaden.li@jaden.tech>`，后续 commit 正常 |
| HG-SEC-131 | — | （round-2 未分配） | 缺口 | 保持空缺，不复用 |
| HG-SEC-132 | 🟢 | test parse 函数 staticmethod 包装前提存疑 | ✅ 已处置 | `9974fe8` 改 patch 时捕获 + finally 恢复；test L318/L346 已落地 |
| HG-SEC-133 | 🟢 | features.md「数据文件 8」未随 code-inventory 递减为 7 | ✅ 已处置 | `features.md:257` 现为「数据文件 \| 7」 |

**汇总**: 🔴 0 / 🟡 0 / 🟢 1（HG-SEC-130，open 非阻断）。8 findings，7 已处置，1 open（🟢 记录）。

---

## 4. 回归测试说明（1 次 flaky，非回归）

- 串行 `-n 0`：**288 passed**（128.48s），零失败。
- 并行 `-n 4` 首跑：**287 passed + 1 error**（`tests/test_templates.py::TestDocShowMd::test_doc_show_md_param`）。
  - 隔离单跑该用例 `-n 0`：**1 passed**（0.52s）——flaky，非代码回归。
  - 复跑全量 `-n 4`：**288 passed**（37.96s）——恢复全绿。
  - 判定：并行 xdist 下 Selenium 偶发超时（本机 10:21 时段有另一项目 review 的并发负载 + conda 初始化钩子干扰后台 shell），与任务提示第 4 点的既有实证一致。
- 跑完后 `git status --short` 为空，工作树干净。

---

## 5. commit 类型扫描（12 笔）

| SHA | type@scope | 判定 |
|:---|:---|:--:|
| f2de562 | data@countries | ✅ |
| 4e14795 | docs@design | ✅ |
| 46ea35d | audit@review | ✅ |
| c918522 | docs@design | ✅ |
| 1e8b24d | feat@table | ✅ |
| 8022fba | docs@verify | ✅ |
| bcc02b9 | audit@review | ✅ |
| be9f8ff | docs@design | ✅ |
| 49bf912 | fix@table | ✅ |
| 510c5b4 | docs@html-gen | ✅ |
| 9974fe8 | fix@html-gen | ✅ |
| 1b060b9 | chore@html-gen | ✅ |

类型集合 {data, docs, audit, feat, fix, chore}，全部符合 `type@scope: subject` 规范；**无 add@/fixed@/remove@ 类非规范项**。

---

## 6. 安全面复核（增量）

- 12 笔 diff 全量扫描（`git diff github/main..HEAD -- '*.py'`）：`shell=True` 命中 **0**，唯一 `subprocess.run` 为 `scripts/countries-issue-sync.py` 的 `run()`（`shell=False` + list-form，HG-SEC-110 既定要求）。
- `scripts/countries-issue-sync.py` 的 HG-SEC-119 修复已落地：`gh_issue_by_number()` 改用 `gh issue view --json` 直查，`in:number` 仅存于注释（L50 说明文字），命令路径 0 处。
- 无凭据/token/密码/magnet/成人片商名残留（§1 核验 1/2 + f2de562 数据 diff 敏感词扫描 = 0）。
- 被删文档（清理 2）仅历史归档 + handoff，删除后 6 处悬挂引用归零。

---

## 7. 评分

```
Base: 100
🔴 HIGH   × 0 → -0
🟡 MEDIUM × 0 → -0
🟢 LOW    × 1 → -0（记录，不计分）
──────────────
Score: 100 / 100 → Rating A → PASS
```

---

## 8. 推送记录

- **推送方式**: `git push github main`（ff-only，不 force，不推 gitee `origin`）
- **推送前**: `git rev-parse --short HEAD` = `1b060b9`；`git rev-parse --short github/main` = `6631eed`；`github/main..HEAD` = 12 笔
- **推送提交数**: 13 笔（12 笔复核对象 + 1 笔审计 commit）
- **推送后**: 以 `git ls-remote github main` 为权威（见最终回复；ff 推送后 `github/main` 应等于审计 commit SHA）

---

## 9. 处理

- ✅ PASS → 审计三件套（本报告 + review-log.md + .review-level.yaml）+ commit（`audit@review: html-gen 推送前复核 round-3 PASS (HG-SEC-125..133)`）
- 推送 `git push github main`（ff-only）；不推 gitee；不 force
- 遗留 HG-SEC-130（作者占位）🟢 非阻断，记录不改写历史
