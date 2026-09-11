# HTML-GEN-CL009 v1.3 实现审计报告

- **审计类型**: implementation-audit（实现审计，只读）
- **项目**: html-gen.cli（A 型表格 GitHub Issue 反馈通道）
- **设计基线**: `documents/solutions/countries-issue-feedback-design-v1.3-20260911.md`
- **改动范围**: `7821427..e0e4d78`（4 笔）
  - `7750b86` docs@design 设计 v1.3
  - `79ad685` feat@table 字段下拉 + 主键硬保护 + 模板一致性校验
  - `15685c8` data@countries issue #2 处置（阿尔及利亚 note 概况补充）
  - `e0e4d78` docs@html-gen 文档同步
- **日期**: 2026-09-11
- **Reviewer**: Security Reviewer
- **Level**: L2

## 结论

🟢 **PASS 100/100（A）** — delta 零 🔴 / 零 🟡 引入，1 🟡 pre-existing（非本 delta 引入）+ 5 🟢 记录。

v1.3 设计（B1/A1/D1/N1/L1/O1/I1 + C1/E1/F2/G1/H1/K1/M1）逐条核对命中，实现与设计基线吻合。295 tests 串/并双绿，`--check-template` exit 0，issue #2/#3 均 CLOSED，工作树干净。安全面主键/匹配键双层硬保护 + 字段解析歧义面 + OSError 处理 + gh shell=False 全部落实。

## 一、逐条核对：设计 §3/§4/§6/§7/§8 vs 实现

| # | 检查项 | 设计 § | 实现落点 | 状态 |
|:-:|:--|:--|:--|:-:|
| 1 | 表单 8 字段（删 current，field 改 dropdown） | §3.1/§6 | `.github/ISSUE_TEMPLATE/data-fix-countries.yml`（page/dataset/row/row_en/field/suggested/source/note） | ✅ |
| 2 | dropdown 15 选项 `标签｜key`，不含 PK/匹配键/videos | §3.2 | 模板 options 15 项；`country_zh`/`country_en`/`videos` 均不在选项 | ✅ |
| 3 | editable 15 项（去两键列）+ key_guard | §8 | `feedback-targets.yaml` editable 15 + `key_guard: [country_zh, country_en]` | ✅ |
| 4 | template 名 + parse_fields 含 current shim | §8/M1 | `template: data-fix-countries.yml` + `current: 当前值 # 兼容 shim` 注释 | ✅ |
| 5 | buildFeedbackUrl 去 field/current、带 template | §4/D1 | `layout-table.html` `buildFeedbackUrl`（L1096-1110） | ✅ |
| 6 | FB_CFG 引用 template | §4/M1 | `FB_CFG.template \|\| 'data-fix.yml'` 回退；数据 JSON `options.feedback.template` | ✅ |
| 7 | resolve_field（K1/O1/N1） | §7.2 | `resolve_field()` L187-203 | ✅ |
| 8 | guarded_fields（A1） | §7.2 | `guarded_fields()` L206-211（key_field/alt_key/key_guard/protected） | ✅ |
| 9 | plan_issues 硬保护 | §7.2 step 4 | L234-237「受保护列」拒绝（config 误列也拦） | ✅ |
| 10 | check_template（L1） | §6/§7.1 | `check_template()` L325-377 | ✅ |
| 11 | argparse --field/--value/--value-file/--check-template | §7.1 | L388-392 + 联用校验 L417-418 | ✅ |
| 12 | override_value 写入 | §7.1/N1 | L419-426 读取 + L241 override + L480 写回 | ✅ |
| 13 | 数据 JSON options.feedback.template | §3.3 | `data/_countries-data.json` `"template": "data-fix-countries.yml"` | ✅ |
| 14 | data-fix.yml 删除、config.yml 保留 | §6 | 重命名为 data-fix-countries.yml；config.yml `blank_issues_enabled: false` 保留 | ✅ |
| 15 | 测试 TC-02′/05′/23~29 | §9 | `tests/test_issue_feedback.py` 9 用例全覆盖 | ✅ |

## 二、真实运行验证（本审计亲跑）

| 命令 | 结果 |
|:--|:--|
| `/usr/bin/python3 -m pytest tests/ -q -n 0` | **295 passed**（125.94s，串行权威） |
| `/usr/bin/python3 -m pytest tests/ -q -n 4` | **295 passed**（38.99s，无 flaky） |
| `scripts/countries-issue-sync.py --check-template` | exit 0（「模板 … 与 config.editable / 数据列标签 一致（15 项）」） |
| `scripts/countries-issue-sync.py --list` | exit 0（「无待处理 issue（repo=imjaden/html-gen.cli, label=data-fix）」） |
| `gh issue view 2/3` | #2 CLOSED（05:13:10Z）、#3 CLOSED（05:12:28Z） |
| `git status --short` | 空（工作树干净） |
| `--value-file /nonexistent` | `[错误] 读取 --value-file 失败: [Errno 2]…` exit 2（OSError 已处理，无 traceback） |

## 三、安全面核对

- **主键/匹配键硬保护（A1）**：`guarded_fields()` 并集 `key_field`/`alt_key`/`key_guard`/`protected`，plan_issues 在 editable 校验前拦截；`test_24` 模拟 config 误列 `country_zh` 进 editable 仍被「受保护列」拒绝。双层（配置 + 代码）成立。
- **resolve_field 解析歧义面（K1/O1）**：`标签｜key` 取末段 `｜` 之后；无 `｜` 时整串按 key 精确匹配（旧 issue 兼容）；两者皆不匹配 → `字段值无法识别` 跳过。`--field` override 优先。
- **--value-file 读文件**：`except OSError` 干净退出（exit 2，无 traceback）；路径来自 operator CLI 参数（人工裁决入口），非 gh issue body，无任意路径读面。
- **check_template 读 .github/**：读取 trusted 仓库内路径 `PROJECT_ROOT/.github/ISSUE_TEMPLATE/<template>`，非外部输入。
- **gh 调用**：`run()` 统一 `subprocess.run(cmd, shell=False, capture_output=True, text=True)`，list/comment/close 全 list-form（HG-SEC-110 已闭环）。

## 四、兼容性

- **v1.2 旧 issue（#2 body 含 `### 当前值`）**：`parse_fields` 保留 `current: 当前值` shim，`parse_issue_body` 仍能定位该段不污染其它字段；#2 已按 I1 处置（`--issue 2 --field note --value-file`）并 CLOSED。
- **新旧 body 双形态字段映射**：`备注｜note` → `note`（末段规则）；裸 `note` → `note`（回退）；`test_23` 覆盖 `大洲｜unknown｜region_tags` → `region_tags`（末段取末 `｜`）。

## 五、回归与越界

- 295 tests 串/并双绿，无 flaky（test_index_landing 未复现）。
- 文档同步面（设计 §10）：AGENTS.md（v1.3 bullet + template/check-template/--issue 参数）、features.md（288→295）、skills/html-gen/SKILL.md（v1.3 段落 + 设计 v1.3 路径）、prompts/*（`--site` 重生成，与 SKILL.md 一致）。
- 未触碰无关文件：diff 仅 23 文件，均为反馈通道 + 文档同步面；无 data 越界（仅阿尔及利亚 note 一字段变更）。

## 六、Findings

| # | 严重度 | 标题 | 位置 | 状态 |
|:-:|:-:|:--|:--|:-:|
| HG-SEC-134 | 🟡 | 反馈值写入后无 HTML 转义 → 潜在 stored XSS（pre-existing，非本 delta 引入） | `layout-table.html:586-589` + 可写文本列 escape=None | open（follow-up 建议） |
| HG-SEC-135 | 🟢 | countries-issue-sync.py docstring 陈旧（data-fix.yml + 设计 v1.0 路径） | `scripts/countries-issue-sync.py:5,:21` | open |
| HG-SEC-136 | 🟢 | AGENTS.md 反馈通道摘要段陈旧（data-fix.yml + 预填 field/current） | `AGENTS.md:100` | open |
| HG-SEC-137 | 🟢 | resolve_field「兜底：整串即 key」死代码分支 + 注释误导 | `scripts/countries-issue-sync.py:201` | open |
| HG-SEC-138 | 🟢 | --value-file OSError exit 2（审计期望 1）+ --value/--value-file 未互斥 | `scripts/countries-issue-sync.py:419-426` | open |
| HG-SEC-139 | 🟢 | 设计 §3.1 id 列「value」笔误（应「suggested」，与 §8/实现一致） | 设计 v1.3 §3.1 | open |

### HG-SEC-134（🟡 pre-existing，非阻断）

可写文本列（`note`/`capital_zh`/`capital_en`/`ethnic_groups`/`religions`）`escape=None`，在 `layout-table.html` L586-589 走 raw `innerHTML` 渲染（仅 `col.escape` 或 `pills` 类型会 `escapeHtml`）。攻击者可通过公开 data-fix issue 提交 `<img onerror>` / `<script>` 值，维护者 `--apply` 后写入 `demos/countries-table.html`，访客浏览器执行 → stored XSS。

- **定性**：本 delta（v1.3）**未引入**此面 —— v1.0~v1.2 已存在同款 write→raw-render 路径；v1.3 通过「textarea 多行长文本 + issue #2 note 大段正文处置」**放大暴露面**（note 成为首要文本注入目标）。
- **缓解**：需维护者 review 后 `--apply`（`--list`/`--dry-run` 预览 `old → new` 有人工闸门）；当前数据 0 处 `<`/`>`（线上安全）。
- **修法（follow-up）**：sync 脚本对 string 字段写回前 `escapeHtml`，或为可写文本列加 `col.escape: true`（模板已支持，非新机制）。

其余 5 项 🟢 均为文档漂移/死代码/参数语义/设计笔误，不阻断、不扣分。

## 七、评分

- Delta 基准 100；HG-SEC-135..139（🟢）扣 0；HG-SEC-134（🟡 pre-existing）不计入本 delta 评分。
- **Score: 100 / 100（A）→ PASS**

## 八、处理

- PASS → 审计三件套（报告 + review-log.md + .review-level.yaml）+ commit `audit@review: 反馈通道 v1.3 实现审计 PASS (HTML-GEN-CL009)`。
- 随后 `git push github main`（ff-only，不推 gitee，不 force）。
- HG-SEC-134（🟡 pre-existing）建议 follow-up 修复（加 col.escape / 脚本转义），非阻断。
