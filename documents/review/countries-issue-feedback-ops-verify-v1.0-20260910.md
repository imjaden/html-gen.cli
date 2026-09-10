# GitHub Issue 反馈通道 — ops 独立核查记录 v1.0（HTML-GEN-CL009）

> 日期: 2026-09-10 · 角色: ops（独立模式，不信任 dev 自报）
> 范围: commit `c918522`（设计 v1.1）+ `1e8b24d`（实现）
> 设计基线: documents/solutions/countries-issue-feedback-design-v1.1-20260910.md
> 设计评审: PASS 85/A（documents/review/countries-issue-feedback-design-review-v1.0-20260910.md）

## 1. 复核项与证据

| # | 项 | 命令 / 方法 | 结果 |
|:-:|:---|:---|:---|
| 1 | 全量回归 | `/usr/bin/python3 -m pytest tests/ -q -n 4` | ✅ **285 passed**（268 → +17，含新增 test_issue_feedback） |
| 2 | 单文件确定性 | `pytest tests/test_issue_feedback.py -q -n 0` | ✅ 17 passed |
| 3 | 产物重建 | `html-gen.py table -d data/_countries-data.json -o demos/countries-table.html --github-url … --home-url … --feedback-repo …` | ✅ 109 列/195 行；corner/home/favicon 各 1；`options.feedback` 内联 |
| 4 | 内联一致性 | 逐字符串比对 DATA/COLUMNS/TABS/OPTIONS ↔ JSON | ✅ 四项逐字一致 |
| 5 | 页面渲染（真实浏览器） | 打开 `demos/countries-table.html?split=0` → 读 `#spFeedbackBtn` / `window.buildFeedbackUrl(window.splitRow)` | ✅ 按钮「✏️」在位；URL 含 `template=data-fix.yml&title=…&page=…&dataset=countries&row=不丹&row_en=Bhutan` |
| 6 | 真实 issue 端到端 | `gh issue create --label data-fix`（#1）→ `--list` → `--dry-run` → `--apply --close` | ✅ 预览零写盘（`git status` 0 行）；apply 后 JSON 仅 1 字段变化（不丹 pop_wan 79→80）、产物同步重建、`[执行]` 打印四参数、issue 回评 + CLOSED |
| 7 | 写回格式 | `git diff --numstat` | ✅ 1 增 1 删（无格式抖动、无尾换行新增） |
| 8 | 测试数据回滚 | `git checkout -- data/_countries-data.json demos/countries-table.html` | ✅ 工作树回到 `1e8b24d` 干净态 |
| 9 | label 就位 | `gh label list --search data-fix` | ✅ `data-fix` #FBCA04「案例数据纠错（页面 ✏️ 按钮提交）」 |

## 2. 独立发现（写入复盘）

- **gh 搜索索引延迟**：刚 `gh issue create` 后立即 `gh issue list --label data-fix` 返回空，
  ~2 秒后可查到。脚本行为正确（空列表 → 「无待处理 issue」退出 0），但**自动化/人工首次查询
  可能扑空**。对策（本次已用的模式）：创建后稍候再查，或后续接入 watchdog 时按 `--issue <n>` 直查。
- **`file://` 下 page 参数为完整文件路径**：本地预览时 `location.pathname` 含
  `/Users/.../demos/countries-table.html`。脚本的页面匹配含 basename 退化，实测可正确路由；
  线上（`https://html-gen.cli.jaden.tech/demos/countries-table.html`）则为规范相对路径。
- **HG-SEC-118 未实测**：URL `?title=` 是否覆盖 Issue Form 的固定 `title`，需 GitHub 登录态
  渲染新 issue 页；本机浏览器无 GitHub 会话，**未能实测**。影响面：若不可覆盖，title 恒为
  `[数据纠错] `，功能与解析不受影响（正文段落才是数据来源）。此为**遗留待验证**项。
- 设计评审 🟡 HG-SEC-110..113 全部落定：gh 调用 list-form + `shell=False`（`run()` 统一封装）；
  repo 落 `options.feedback`（videos syncer 重建不再丢按钮）；body 解析「空行 + `### `」切段 +
  未知段并入上一字段；`rebuild.args` 含 `--favicon`；文档同步面（AGENTS/features/README×2/
  skills/handbook×2/prompts）齐备。

## 3. 结论

**核查 PASS** — 设计 → 实现 → 真实数据落点全程可复现；测试数据已回滚；无阻塞项。
遗留：HG-SEC-118（title 覆盖，需登录态实测）、gh 搜索索引延迟（记录，不阻断）。
