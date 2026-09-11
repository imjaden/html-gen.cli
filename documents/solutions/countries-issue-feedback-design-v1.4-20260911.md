# A 型表格 GitHub Issue 反馈通道设计 v1.4 (2026-09-11)

> 闭环: HTML-GEN-CL009（修订并入 v1.4 delta）· 模式: 独立
> v1.4 增量: **`--apply` 自动提交（本地 commit）** + **`--list` 逐条引导行** + **`python3` 书写口径**
> 决策（全量）: A1 B1 C1 D1 E1 F1 G1 H1 I1 J1 K1 L1 M1 N1 O1 P1 Q1
> 基线: v1.3（字段下拉 + 主键双层保护）已上线并 push

## 1. v1.3 → v1.4 变更摘要

| 项 | v1.3 | v1.4 |
|:---|:---|:---|
| `--apply` 提交 | 不提交（回评写「提交由维护者完成」） | 写盘 + 重建后**自动 commit**（本地，不 push） |
| 提交范围 | — | 显式 pathspec：仅 `target.data` + `target.html`（B1） |
| 提交预检 | — | 写盘前检查两文件无未提交改动，否则拒绝（C1） |
| 开关 | — | 默认提交；`--no-commit` 关闭（A1） |
| 回评 | 无 sha | 带**真实本地短 sha**（F1） |
| `--list` | 仅汇总 + 条目 | 每条下追加引导行 `--issue N --dry-run`（O1/Q1） |
| 命令书写 | 混用 | 面向人的示例/引导统一 `python3 scripts/…`（M1） |
| 配置 | — | `target.commit.scope`（J1） |

## 2. 提交步骤规格

### 2.1 触发
- 仅在 `--apply` 且**非** `--no-commit` 时执行（A1/I1）
- `--list` / `--dry-run` / `--check-template` 恒不提交
- 只 `git commit`，**不 push**（I1；推送走 review 通道）

### 2.2 范围（B1，安全关键）
```python
paths = [target['data'], target['html']]     # data/_countries-data.json, demos/countries-table.html
```
- 一律使用**显式 pathspec**，禁止 `git add -A`
- 理由：本仓历史上存在并行会话 WIP（CL002 FIND-002 / code-inventory 并发提交），`add -A` 会裹走非本次改动
- 这是对既有先例 `scripts/cloudwise-news-sync.py`（`git add -A`）的**有意偏离**，需在代码注释中说明

### 2.3 写盘前预检（C1）
- `git status --porcelain -- <data> <html>`；非空 → 拒绝执行（exit 1），提示先提交或回滚
- 目的：确保本次提交的 diff 只含本次处置

### 2.4 提交消息（D1/E1）
- 标题：`data@<scope>: apply #N <field> 更新 (HTML-GEN-CL009)`；多 issue → `#N,#M`；多字段 → 逗号连接去重
- `<scope>` 取 `target.commit.scope`，回退 `target.dataset`，再回退 `data`
- body：逐条列 `- #N <行标签>.<字段>: 旧 → 新`，附产物路径
- 一次 `--apply` 批量 → **一条提交**（E1）

### 2.5 提交失败与无变化（G1/H1）
- 无变化（pathspec diff 为空）→ 不产生空提交，打印 `[提交] 无变化，跳过`
- 提交失败 → **不自动回滚**（数据已写、产物已重建）；打印 `[错误]`，回评注明「提交失败，待维护者处理」，exit 1
- rebuild 失败 → 保持 v1.3 语义（立即返回，不进入提交）

### 2.6 回评联动（F1）
- 顺序：写盘 → 重建 → **提交** → 回评 → （可选）关闭
- 文案：`- 产物已重建：<html>；本地提交 \`<short_sha>\`（待推送）`
- 提交失败/无变化时的措辞：`提交失败，待维护者处理` / `本次无文件变化，未产生提交`
- 明确写「本地提交（待推送）」，避免读者误以为已在远端

## 3. `--list` 输出规格（O1/Q1）

```
[列表] 待处理 2 条 / 可执行 1 条 / 跳过 1 条
  #3 不丹 · note: 旧 → 新
     → python3 scripts/countries-issue-sync.py --issue 3 --dry-run
  #2 [跳过] 字段值无法识别（'country_zh' 不在可写列中）
     → python3 scripts/countries-issue-sync.py --issue 2 --dry-run
```
- 汇总行与条目行**格式不变**（降低既有断言冲击）
- 引导行：5 空格缩进 + `→ `，可整行复制
- 可执行与跳过项**都打印**（O1）
- 引导行**不进 `--json`**（P1）

## 4. `python3` 书写口径（M1）

| 位置 | 处理 |
|:---|:---|
| docstring 用法块 | 统一 `python3 scripts/countries-issue-sync.py …` |
| argparse help 中的示例 | 同上 |
| `--list` 引导行 | `python3 scripts/countries-issue-sync.py --issue N --dry-run` |
| dry-run/apply 提示行 | 同上（如 `--apply`、`--no-commit` 提示） |
| `[执行]` 重建行 | **保留** `sys.executable` + 绝对路径（N1：实际执行命令的审计/复现契约） |

## 5. 配置增量（J1）

```yaml
targets:
  countries:
    ...
    commit:
      scope: countries      # 提交消息 data@<scope>: …
      # enabled: true       # 可选；缺省 true（等价于默认提交，--no-commit 可临时关闭）
```

## 6. 测试计划（`tests/test_issue_feedback.py`）

| 用例 | 断言 |
|:---|:---|
| TC-30 提交生效且仅两文件 | 临时仓库/桩：`git_paths()` == [data, html]；commit 调用只带这两个 pathspec |
| TC-31 `--no-commit` | 不调用 git commit；回评无 sha 措辞（或标注未提交） |
| TC-32 预检拒绝 | `git_check_clean` 对脏文件返回错误；main 在写盘前 exit 1 |
| TC-33 dry-run/list 不提交 | 不调用 git commit |
| TC-34 无变化跳过 | `git_status_paths()` 为空 → `('no-change')` |
| TC-35 回评含 sha | body 含 `本地提交` + sha 片段 |
| TC-36 `--list` 引导行 | 输出含 `→ python3 scripts/countries-issue-sync.py --issue <N> --dry-run`（可执行 + 跳过各一） |
| TC-37 `--json` 无引导行 | JSON 结构不变、无 hint 字段 |
| TC-38 消息构造 | 标题 `data@countries: apply #N <field> 更新 (HTML-GEN-CL009)`；多 issue 用 `#N,#M` |

实现方式：对 git 调用做 subprocess 桩（`mod.run` monkeypatch），避免测试真的提交仓库。

## 7. 验收标准

1. `--apply` 后：`git log -1 --name-only` 仅含 `data/_countries-data.json` + `demos/countries-table.html`
2. 回评正文含真实本地短 sha，且措辞为「待推送」
3. `--no-commit` 时无提交、工作区保留改动
4. 目标文件脏时 `--apply` 在写盘前拒绝（exit 1）
5. `--list` 每条 issue 后跟 `python3 … --issue N --dry-run` 引导行
6. 全量测试通过（基线 295 + 新增）

## 8. 风险与边界

- 引导行假定在项目根执行（相对路径）；异地执行需自行补路径
- 回评中的 sha 为本地提交号；推送由 review 完成，推送后该 sha 不变（ff-only）
- 自动提交不放宽「人工触发」：不做定时自动 apply
- 多案例复用：新 target 未配 `commit.scope` 时回退 `dataset`
- 若并行会话恰好改同一两文件 → C1 预检拦截，要求人工裁决

## 9. 版本演进

| 版本 | 日期 | 要点 |
|:---|:---|:---|
| v1.0 | 2026-09-10 | 页面 ✏️ 按钮 + Issue Form + 同步脚本（六项校验） |
| v1.1 | 2026-09-10 | 折入设计评审 HG-SEC-110..118 |
| v1.2 | 2026-09-10 | 文案改「数据反馈」+ `--issue` 直查 |
| v1.3 | 2026-09-11 | 字段下拉 + 主键双层保护 + `--check-template` + 人工裁决入口（issue #2 驱动） |
| **v1.4** | 2026-09-11 | **`--apply` 自动提交（显式 pathspec）+ `--list` 引导行 + `python3` 口径** |
