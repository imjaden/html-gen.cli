# GitHub Issue 反馈通道 skill 沉淀 — 实现审计复审报告 v1.1

> 闭环: HTML-GEN-CL011 · 步骤: [5/6] 实现审计复审（re-audit）
> 日期: 2026-09-12 · 执行: Security Reviewer
> 复审对象: commit `b52afa5`（ops 事实订正 HG-SEC-155..157）对上一轮 v1.0 审计（CONDITIONAL PASS）的处置
> 设计基线: `documents/solutions/github-issue-feedback-skill-design-v1.2-20260912.md`（评审 PASS 100/A，`f3be5d9`；本轮新增 §3.4 勘误段）
> 独立复验: 全部逐项亲自跑命令 / 读文件 / 对照源码，未仅信 ops 自述

## 1. 结论

**CONDITIONAL PASS 95/100（A）** —— HG-SEC-155/156/157 在**源文件层**（SKILL.md + 3 references + 顶层 md/json/all.md）已真实修复并逐行对照源码核实成立；但发现 **1 🟡 + 2 🟢** 新项：

- **🟡 HG-SEC-158**：`prompts/kb/github-issue-feedback.html`（31 文件交付物之一）仍含**订正前的旧内容**（校验链旧序「行唯一定位→类型→非空」/「×8」/「约 8 处」/「把读者引导到表单」）。根因 = ops 在 `b52afa5` 执行「kb/*.html 时间戳 wildcard 已还原」时，把**内容修复与时间戳一并回退**——8 个既有 kb 页仅时间戳（还原正确），唯 `github-issue-feedback.html` 承载 HG-SEC-155..157 的内容修复被误还原。源已对、产物页仍错，交付物内部自相矛盾。
- 🟢 HG-SEC-159 / 160：字段计数 off-by-one + 设计基线残留漂移（详见 §4）。

回归验证：`pytest -n 0` **312 passed**（130.30s）；`--site` 31 文件（顶层 22 + kb/ 9），确定性集（22 顶层）逐字节一致，幂等零 diff。

## 2. 逐条核销 HG-SEC-155/156/157（源文件层）

| # | 上轮要求 | 实测核销 | 结果 |
|:--|:--|:--|:--|
| HG-SEC-155 🟡 | SKILL.md 校验链顺序「行定位→类型→非空」→ 重排为「非空→行唯一定位→类型」 | `SKILL.md` L45 现为「非空 → 行唯一定位 → 类型 → 入库 XSS 防护 → 幂等 → 冲突取最新」；源码 `plan_issues()` 实测顺序 = 非空(L245-248) → 行定位(L249-252) → 类型(L255-259)，**逐行吻合**；设计 §3.3 L72 同序已订正 + §3.4 L78 勘误段（根因注明）已加 | ✅ 源文件成立 |
| HG-SEC-156 🟢 | 「脚本名 ×8」→ 9 处 | `SKILL.md` L141 现为「脚本名 ×9（L11-19 示例命令行）」；`adoption-prompt` L164 现为「（9 处，L11-19）」；docstring 实测 L11-19 **9 处** `countries-issue-sync.py` 示例命令行（逐行计数） | ✅ 成立 |
| HG-SEC-157 🟢 | config.yml 模板 contact_links 与参考实现（仅 1 行）不符 | `issue-form-template.md` L3-5 现显式标注「参考实现当前仅 1 行 `blank_issues_enabled: false`；§3 contact_links 为增强可选项」；实测 `.github/ISSUE_TEMPLATE/config.yml` 确实仅 1 行 | ✅ 成立 |

> ⚠️ 上述三处修复在 `prompts/kb/github-issue-feedback.html` 中**未落地**（见 HG-SEC-158）——源文件已对，但产物 detail 页仍为旧文案。

## 3. 事实准确性独立复检（逐条对照源码）

| 声明 | 源码实测 | 结果 |
|:--|:--|:--|
| `--feedback-repo` 三级取值（CLI > env > JSON） | `html-gen.py` `feedback_repo_args()` L142-147：`getattr(args,'feedback_repo')` → env → JSON；空串禁用 | ✅ |
| `options.feedback` 五字段语义 | `layout-table.html` `buildFeedbackUrl()` L1087-1109：repo/dataset/key(默认 name)/altKey(默认空)/template(默认 data-fix.yml) | ✅ |
| 页面预填参数集 template/title/page/dataset/row/row_en | `buildFeedbackUrl()` L1101-1109：`add('template'...)`/`add('title'...)`/`add('page'...)`/`add('dataset'...)`/`add('row'...)`/`add('row_en'...)`；v1.3 起不预填 field/current | ✅ |
| 校验链 11 步顺序 + 各步失败语义 | `plan_issues()` L226-283 逐条：page→dataset→字段解析→硬保护→白名单→非空→行定位→类型→XSS→幂等→冲突；11 步失败文案与 `feedback-targets-schema.md` §2 逐字一致 | ✅ |
| CLI 十态 | SKILL.md L90-100 十行命令 + schema §4 十行表，与 argparse 十种组合一致 | ✅ |
| 退出码 0/1/2 | `die(msg, code=2)` 缺省 2；return 1（拉取失败 L495/预检脏 L537,539/重建失败 L551/提交失败 L596）；return 0（L499/L522/L530） | ✅ |
| HINT(L302)/prog(L432)/DEFAULT_CONFIG(L40) | L302 `HINT='python3 scripts/countries-issue-sync.py'`；L432 `prog='countries-issue-sync.py'`；L40 `DEFAULT_CONFIG=.../feedback-targets.yaml`；无 DEFAULT_TARGET | ✅ |
| docstring 4 类形态 + 计数 | 脚本名 ×9(L11-19) / 表单模板名(L5) / target 名(L19) / 设计文档名(L25)；SKILL.md L141-142 正确区分 docstring 4 类 vs 代码 HINT/prog | ✅ |
| 安全红线 6 条 ↔ 实现 | guarded_fields L210-215 先于 editable L242 / XSS `<`·`>` 拒绝 L262-265 / 显式 pathspec L328+332（无 `-A`）/ 写盘前预检 L534-539 / 失败不回滚 L585 / shell=False L51 | ✅ 6 条全吻合 |
| 回评/提交消息格式 | 提交 `data@{scope}: apply {#N,#M} {fields} 更新` L560；回评含短 sha + 待推送 L583/L590-594 | ✅ |
| form 模板 ↔ data-fix-countries.yml 差异 | 结构一致（markdown/page/dataset/row/row_en/dropdown field/suggested/source/note）；仅 page placeholder 与 dropdown 15 选项为案例占位（模板「改 3 处」设计） | ✅ |
| 其他计数（十态=10 / 6 红线 / 15 选项 / 84 行 / 600 行 / 155 行） | 逐项实测一致 | ✅ 除「20 项」见 HG-SEC-159 |

## 4. 新发现项

| # | 严重度 | 位置 | 描述 | 处置建议 |
|:--|:--|:--|:--|:--|
| HG-SEC-158 | 🟡 | `prompts/kb/github-issue-feedback.html` | 该 kb detail 页（交付物 31 文件之一）仍为 `b52afa5` **订正前**内容：数据流图校验链旧序「行唯一定位 → 类型 → 非空」、「脚本名 ×8」、「（约 8 处）」、「把读者引导到表单」。根因 = 「kb/*.html 时间戳 wildcard 已还原」把内容修复与时间戳一并 `git checkout` 回退；8 个既有 kb 页仅时间戳（还原正确），唯本页承载 HG-SEC-155..157 内容修复被误还原 | 重跑 `python3 html-gen.py prompt --site` 后**提交本页内容修复**（接受其时间戳/字数变化，因内容确已变更：字数 2,800→2,808） |
| HG-SEC-159 | 🟢 | `feedback-targets-schema.md` §1 L7 | 表头写「target 字段表（**20 项**）」，实际枚举行 **19**（16 具体字段 + page+dataset 组合 + repo 覆盖 + 多 target 三隐式）；设计 §3.1/§3.3「20 字段」同源 | 表头「20 项」→「19 项」，设计两处「20 字段」→「19 字段」 |
| HG-SEC-160 | 🟢 | 设计基线 §8 L191 + §3.1/§3.3 | 设计 §8「脚本名 ×8」未随 HG-SEC-156 订正（156 仅订正 skill 双文件）；§3.1 L58/§3.3 L72「安全红线 **5 条**」实为 **6 条**；§3.4 勘误段仅收 HG-SEC-155 未收其余 | §3.4 勘误段补记：§8 ×8→×9、5 红线→6、20 字段→19 |

> 非 finding 观察：HG-SEC-158 与 155/156/157 同源——源文件已修复，仅产物 kb 页未同步，属「重生成→提交」一步遗漏，非新的事实错误。

## 5. 回归证据

| 项 | 命令 | 实测 |
|:--|:--|:--|
| 全量测试 | `/opt/homebrew/Caskroom/miniconda/base/envs/py3.12/bin/python -m pytest tests/ -q -n 0` | **312 passed in 130.30s** |
| `--site` 规模 | `python3 html-gen.py prompt --site` | **31 文件**（顶层 22 + kb/ 9），统计行「9 skills (31 文件: …)」 |
| 幂等（确定性集） | `--site` 两次重生成 | 顶层 22 文件与仓库提交版**逐字节一致**（零 diff） |
| kb 时间戳 wildcard | `git status prompts/` | 9 个 kb 页仅时间戳/字数变化；8 页纯时间戳，`github-issue-feedback.html` 含内容漂移（见 HG-SEC-158） |

> 注：`python3`（3.9.6）与 homebrew 3.14 均无 pytest；权威基线 = conda py3.12 env（pytest 9.1.0），与 ops 报告一致。

## 6. 评分

| 项 | 值 |
|:--|:--|
| 基线 | 100 |
| HG-SEC-158（🟡） | -5 |
| HG-SEC-159/160（🟢） | 0（仅记录） |
| **总分** | **95 / 100（A）** |
| **结论** | **CONDITIONAL PASS**（1 🟡 待 ops 一步重生成修复，非阻塞但属交付物事实准确性） |

## 7. 处理

- ⏳ CONDITIONAL PASS → 写报告 + review-log + .review-level.yaml，**不 commit / 不 push**（待 ops 重生成 kb 页 + 订正计数后复审转 PASS）
- 修复 = ① `--site` 重生成并提交 `kb/github-issue-feedback.html` 内容修复；② 表头「20 项」→「19 项」+ 设计 §3.4 勘误段补记（🟢 随修）
- 报告: `documents/review/github-issue-feedback-skill-impl-audit-v1.1-20260912.md`
