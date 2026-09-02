# html-gen prompt --site 在线阅读站点 实现审计 — review报告 v1.0

> 日期: 2026-09-02
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 实现 commit: d4ec017（feat@html-gen: prompt --site 在线阅读站点 · HTML-GEN-CL007，kind=independent）
> commit 范围: fe2ee22..d4ec017（设计 v1.0 → 设计订正 9c0cb1a → 评审/实施 prompt cd6c724 → feat d4ec017，共 4 commits）
> 设计基线: documents/solutions/html-gen-prompts-site-design-v1.0-20260902.md（PASS 85/A，折叠项 HG-SEC-086..095 已订正入文）
> 评审报告: documents/review/html-gen-prompts-site-design-review-v1.0-20260902.md
> review维度: 设计-实现一致性 / 折叠项落实 / dev 实施决策 / 回归面 / 产物一致性 / 文档同步 / 安全 / 验收清单

## 数据验证（本审计独立复跑，非测试自证）

| # | 验证项 | 方法 | 结果 |
|:-:|:-------|:-----|:-----|
| 1 | 全量回归 | `python3 -m pytest tests/ -q -n 4`（两次独立运行） | ✅ 第二次 **263 passed**（35.76s）；第一次 4 failed 均在 test_videos.py，单线程重跑 8 passed、并行重跑即恢复 → 判定为 Selenium 并行负载瞬时 flake，非 CL007 回归（CL007 未触碰 videos/table 渲染路径；详见"回归面"注记） |
| 2 | 专项三件套 | test_prompt_site + test_prompt_cmd + test_corner_privacy | ✅ **19 passed**（8+5+6，0.73s） |
| 3 | 产物一致性（核心） | tmp `--dir` 重新生成 vs 提交的 prompts/ 逐字节比较 | ✅ 18 文件集合精确一致；**17 确定性文件 byte-identical**（all.md + 8 md + 8 json）；index.html 除去「创建/编辑」meta 时间戳行（grep -v 后 diff 为空），与 HG-SEC-086 预期完全吻合 |
| 4 | 幂等 | 上表 #3 隐含（提交产物 == 当前生成器输出） | ✅ 17 文件确定性 + index 结构稳定 |
| 5 | HELP_PROMPT --site | grep html-gen.py:771-772 | ✅ `html-gen prompt --site` / `--site --dir` 两行已入 HELP_PROMPT（HG-SEC-094 落实） |
| 6 | README 双份 | git show d4ec017 -- README.md README.zh.md | ✅ 中英各 +29/+28 行：4 条 URL/curl 示例 + 生成命令 + frontmatter 剥离差异说明（§6.5 要求） + 勿手改/互斥说明 |
| 7 | AGENTS.md 同步 | git show d4ec017 -- AGENTS.md（0 行）+ grep --site/prompts/ | ⚠️ **零同步**（两处被「受保护文件」审批拦截）：prompt 子命令段无 --site；目录结构无 prompts/ 行；测试计数 247 亦已 stale（现 263）→ 判定非阻断遗留，见 HG-SEC-099 |
| 8 | 凭据扫描 | prompts/ 18 文件 + html-gen.py 新增段（api_key/secret/token/password/私钥/AWS/sk- 模式） | ✅ 零命中；产物内容源仅 skills/ 受控文件 |
| 9 | 互斥出口 | test_07 + 手工读 cmd_prompt:906-912 | ✅ 5 组合（skill/brief/json 各形态）exit 1 + stderr「互斥」 |
| 10 | 提交面 | git show d4ec017 --stat | ✅ 22 文件：html-gen.py + 2 README + tests/test_prompt_site.py + prompts/ 18 产物；无夹带 |

## 维度评估

### 1. 设计-实现一致性（§5 CLI / §6 内容 / §7 测试计划逐项）

| 设计 § | 规格 | 实现 | 判定 |
|:-------|:-----|:-----|:----:|
| §5 | `prompt --site [--dir]`，默认仓库根/prompts/ | cmd_prompt_site:1022-1023（default_out = `Path(__file__).parent/'prompts'`） | ✅ |
| §5 | 互斥 skill/--brief/--json → stderr+exit1 | cmd_prompt:906-912（顶部 site 分支先校验） | ✅ |
| §5 | 生成流程 1 收集 skills（sorted，复用遍历） | cmd_prompt_site:1029-1034（与 cmd_prompt:922-926 同构） | ✅ |
| §5 | 流程 2 内存全量构建 fail-fast、零写盘 | 1040-1063：全部 read_text 入 try，OSError → stderr+exit1；写盘在 1075+（其后） | ✅ |
| §5 | 流程 3 清理仅已知产物名 containment | 1065-1073：`known` = index.html + all.md + 8×{skill}.md/.json，仅 `is_file() and name in known` 删除 | ✅（HG-SEC-088） |
| §5 | 流程 5 cmd_doc Namespace：input/output/title/home_url/github_url="" /quiet=True | 1085-1095：github_url=''（HG-SEC-090）、home_url=站点根、favicon 不传（env 兜底 → 默认注入）、redirect_stdout 抑制内部输出 | ✅ |
| §5 | 流程 6 统计行 `[站点] … 已生成: N skills (18 文件)`；--quiet 仅目录 | 1097-1100 | ✅ |
| §6.1 | {skill}.md = strip_frontmatter(SKILL.md) + references（`\n\n---\n\n## {stem}\n` + 原文），原文直读不剥离 | 1044-1054 + test_02 全 8 skill 逐字断言 | ✅ |
| §6.2 | json 信封 status/error/data{name,content,references}；content=去 fm 正文；references 键=stems | 1055-1059 + test_03 | ✅ |
| §6.3 | all.md 唯一顶层 h1（fence-aware）+ 8 段标题 + desc 引用 + 正文删 h1 + references 拼接 | _site_all_md:1124-1130 + _site_skill_section:1112-1121 + _fence_top_h1_indices:283-304 + test_04（fence-aware 计数==1） | ✅（refs h1 剥离为 dev 扩展，见 HG-SEC-096） |
| §6.4 | index.html = cmd_doc 渲染（B 型 doc，零新模板） | 1085-1095 + test_05（doc-body/doc-sidebar/标题/无 github-corner/home-link 指向站点） | ✅ |
| §6.5 | 双形态差异文档化（CLI 含 fm vs 站点剥离） | README 双份注明 + {skill}.md 与 CLI 直出仅差 frontmatter | ✅ |
| §7 | test_01..test_08 八用例 | tests/test_prompt_site.py 8 方法全实现，隔离 `--dir /tmp` + test_08 断言仓库 prompts/ 不变 | ✅ |
| §9 | README/HELP_PROMPT（AGENTS.md 被拦截） | 见数据验证 #5/#6/#7 | ⚠️ 仅 AGENTS.md 遗留 |

### 2. 折叠项落实（HG-SEC-086..095）

| ID | 折叠要求 | 落实证据 | 判定 |
|:---|:---------|:---------|:----:|
| HG-SEC-086 | 幂等断言限定 17 文件，index 改结构断言 | test_06:211-221：deterministic 列表 = all.md+8md+8json 字节 diff；index 仅结构断言 | ✅ closed |
| HG-SEC-087 | h1 删除/计数 fence-aware（复用 md_to_html 围栏语义） | `_fence_top_h1_indices`（html-gen.py:283-304，与 md_to_html:138-160 同解析语义）+ 测试侧 `fence_top_h1_count` 镜像实现 + test_04 计数==1 | ✅ closed |
| HG-SEC-088 | 清空目录 → 只删已知产物名 containment | 1065-1073 + test_06 预置 keep-me.txt/notes.md/sub/ → 全保留且内容不变 | ✅ closed |
| HG-SEC-090 | cmd_doc github_url='' 显式（防 env 覆盖） | SimpleNamespace github_url=''（1091）；test_05 元素级断言零 github-corner | ✅ closed（缺 env-set 回归测试，见 HG-SEC-097） |
| HG-SEC-091 | test_02 补 html-gen-slide 2 refs 显式断言 | test_02:116-119：selenium-h3-toggle-testing / slide-mode-null-guards + 内容标记 | ✅ closed |
| HG-SEC-094 | HELP_PROMPT 补 --site | html-gen.py:771-772 | ✅ closed |
| HG-SEC-089 | references 4→3 笔误 | 设计 §3 已订正；实现 glob 3 文件（slide×2+table×1）；test REFS_BY_SKILL 注释引用 HG-SEC-089 | ✅ closed |
| HG-SEC-092 | all.md TOC 扁平记录不修 | 设计 §6.3 已记录；实现保持 `## {skill.name}` | ✅ closed |
| HG-SEC-093 | §6.2 限定"结构同构" | 设计已订正；json content 与 CLI 直出差异（去 fm）由 §6.5/README 注明 | ✅ closed |
| HG-SEC-095 | YAML 多行 description 截断记录 | `_skill_desc` 首行语义（268-277）+ 设计 §6.3 记录 | ✅ closed |

10/10 折叠项全部落实，无「折入即忘」。

### 3. 两个 dev 实施决策评估

**a) all.md 内 references 段剥离 reference 自身首个顶层 h1（单篇 {skill}.md 保留原样）— 合理，不破坏 §6.1**

- §6.1 的「原文直读/拼接与 CLI 全文一致」契约作用于 **{skill}.md**：实现保留 ref 原 `# 标题`（1047-1054），test_02 逐字断言通过，契约成立。
- all.md 属 §6.3 阅读页形态：正文 h1 已被段标题 `## {skill.name}` 替代剥离（§6.3 明文），references 若保留自身 `# ` 会在合集页产生额外顶层 h1，直接违反 §6.3 规则 1「唯一顶层 h1」及 test_04 fence-aware 计数==1——3 个 references 均以 `# ` 开头（设计评审数据验证 #5 实证）。dev 扩展剥离 refs 首 h1 是满足 §6.3 规则的唯一自洽路径。
- 被剥离内容仅为冗余标题行（段标题 `## {stem}` 已承载），正文其余逐字保留；ref 完整原文仍经 {skill}.md 与 .json data.references 字节可达。
- 结论：**不破坏 §6.1 语义**（{skill}.md 逐字契约无损），all.md 处理与 skill 正文同规则、结构一致。唯一缺憾是设计 §6.3「references 拼接同 6.1」字面未注明此剥离 → 🟢 HG-SEC-096（回写一句即可）。

**b) corner_args 从 `or 链` 改为「None→env 兜底；显式 ''→禁用」— 对既有命令零回归**

- 调用点全量核查：corner_args 仅 4 处消费（cmd_doc:381 / cmd_slide:451 / cmd_table:506 / cmd_knowledge:556）+ 本批新增 cmd_prompt_site 直传 Namespace（1085）。demo --rebuild 的 SimpleNamespace（1211-1215）`github_url=None` → 新语义与旧 `or 链` 完全一致（None→env），无变化。
- 语义差异仅出现在「调用方显式传空串 + env 已设」：旧行为 env 胜出（corner 出现，'' 无法禁用 env）；新行为 '' 禁用。不存在依赖「显式 '' 反而读 env」的合理调用方；新语义与 favicon（HG-SEC-073，`favicon_args` is-not-None 判定）及 README「显式空串禁用」惯例对齐，属缺陷修正而非行为破坏。
- env 兜底路径（未传参场景）在 doc/slide/table/knowledge/demo 逐点不变；test_corner_privacy 6 例（默认无/显式注入/env 兜底/CLI>env/doc 支持）全部通过。
- 结论：**零回归**（本审计复跑 6/6 过 + 全量 263 过）。两点改进空间见 🟢 HG-SEC-097（env-set 场景缺回归测试 pin 此语义；--github-url/--home-url argparse help 未注「显式空串禁用」，favicon help 有）。

### 4. 回归面充分性

- test_prompt_cmd 5 例原样通过（skill 全行为零回归：list/full/brief/不存在/json 信封），confirm 设计 §5「无参/带参/--brief/--json 完全不变」。
- test_corner_privacy 6 例通过，pin 住 corner/home 隐私默认 + env 兜底 + CLI 优先。
- 全量 263 = 基线 255 + 8（test_prompt_site），ops 与复核一致。
- 充分性缺口：HG-SEC-090 的「github_url='' 防 env 覆盖」目前只被 test_05（未设 env 场景）间接覆盖——若 corner_args 回归 `or 链`，test_05 不红（无 env 时新旧行为相同）。建议补一条 env-set 用例 pin（见 HG-SEC-097）。test_prompt_site 本身 8/8 无缺失、无自证循环（断言独立读文件/读产物，非回显生成器 stdout）。
- 环境注记（非 finding）：全量并行首跑出现 test_videos 4 failed（test_06/07/08），单线程 8 passed、并行复跑 263 passed——Selenium 并行负载瞬时 flake，与 CL007 无涉（videos 渲染路径零改动；首跑与本批并行测试残留浏览器进程争抢资源相关）。建议项目侧留意 test_videos 在 -n 4 下的稳定性，但不在本审计计分范围。

### 5. 产物一致性（prompts/ 提交 vs 生成器当前输出）

独立复跑（数据验证 #3）：提交的 18 文件与 `prompt --site --dir <tmp>` 当前输出 **17 文件逐字节一致**；index.html 仅 meta「创建/编辑」分钟粒度时间戳行不同（HG-SEC-086 已知且预期）→ 提交产物未漂移、无手工编辑痕迹，生成器确定性达标。

### 6. 文档同步

- README.md/README.zh.md：✅ 双份同步且含 §6.5 要求的 frontmatter 差异说明 + 4 条 URL/curl + 勿手改 + 互斥。
- HELP_PROMPT：✅（argparse --help 自动 + HELP 文本手工双覆盖）。
- AGENTS.md：❌ 两处被「受保护文件」审批拦截（① prompt 子命令段 --site 行；② 目录结构 prompts/ 行；另测试计数 247→263 stale 可顺带）。判定：**非阻断遗留待用户**（运行/测试/产物均不依赖 AGENTS.md 同步；仅 agent 文档准确性问题）→ 🟢 HG-SEC-099。建议用户批准后由 dev 补一行级 commit。

### 7. 安全

- 内容源受控：prompts/ 全部产物由 skills/*/SKILL.md + references/*.md 派生，无外部输入进入 HTML/SQL/命令上下文；`{skill}` 名来自仓库子目录名（glob/sorted），无路径穿越面。
- 渲染安全：all.md → cmd_doc → md_to_html，既有转义管线（_md_escape 先行、无 raw-HTML 透传、图片不解析），SKILL.md 内嵌 `github-corner` 等 HTML 片段以 `&lt;` 转义呈现（test_05 元素级断言佐证）。
- 写盘安全：清理仅删 18 个已知产物名（is_file 判定，目录/子目录不动），`--dir` 任意路径 containment 生效（HG-SEC-088 实证）；内存构建失败零写盘。
- 凭据：全产物 + 新增代码零命中；无新依赖、无 CDN、无外呼。
- 边界余量：--dir 空串解析为 `.`（cwd）且仓库根含同名 index.html（落地页）在 known 集内 → 见 🟢 HG-SEC-098 防御建议；被删除 skill 的旧产物不在 known 集 → 残留语义与设计文本漂移 → 见 🟢 HG-SEC-096。

### 8. 验收清单 §8 逐项可执行性

| # | 条目 | 状态 |
|:-:|:-----|:----:|
| 1 | --dir 临时目录 18 文件齐全 | ✅ 本审计复跑 18 文件精确 |
| 2 | 8 skill .md 正文 == strip(SKILL.md) | ✅ test_02 + 独立逐字节比对 |
| 3 | 8 json 信封键/content/refs | ✅ test_03 + 独立比对 |
| 4 | all.md 结构断言 | ✅ test_04 |
| 5 | index.html 静态断言 | ✅ test_05 |
| 6 | 幂等 17 文件 + 无关文件保留 | ✅ test_06 + 独立比对 |
| 7 | 互斥 exit 1 | ✅ test_07 + 手工读码 |
| 8 | 仓库内真实生成 → 仅 prompts/ 新增 → commit | ✅ feat d4ec017 即此步产物 |
| 9 | push 后 curl 实测（/prompts/、all.md、{skill}.md/.json） | ⏳ **待 push**（AGENTS.md 仅 commit 不 push 约定；push 后需按设计 §10 实测 .md/.json MIME 并记录） |
| 10 | 全量 pytest -n 4 | ✅ 263 passed（复跑） |

## 安全事项

- 无 🔴/🟡 级安全项；prompts/ 生成链路内容源受控、渲染走既有转义、清理 containment 实证、零凭据/零新依赖。
- 🟢 HG-SEC-098 — --dir 边界防御（见 Findings）。

## Findings（本审计新增，HG-SEC-096..099，均 🟢 记录非阻断）

| # | 严重度 | 问题 | 建议 |
|:-:|:------:|:-----|:-----|
| HG-SEC-096 | 🟢 | all.md 内 references 首 h1 剥离（dev 决策 3a）合理且必要，但设计 §6.3「references 拼接同 6.1」字面未注明；另 §5 步 3「skill 被删除后其旧产物名不在已知集 → 由本清理移除」与 §10「生成前清空目录 → 旧产物不残留」文字与实现不符——known 集由**当前** skills 计算，被删/改名 skill 的旧产物不在集内 → 实际残留（当前 8 skills 固定 + prompts/ git 跟踪 + 手动生成，无现实风险，仅文本漂移） | 回写设计 §6.3 一句「all.md 内 references 首个顶层 h1 一并剥离（段标题已承载）」，§5/§10 改为「仅清理当前产物名；被删 skill 旧产物需手动移除或由清理扩展历史名集」；不改代码亦可接受 |
| HG-SEC-097 | 🟢 | corner_args「显式 ''→禁用 env」新语义（决策 3b，零回归）缺回归测试 pin：test_05 未设 HTML_GEN_GITHUB_URL env，若 corner_args 回退 `or 链`，env 覆盖隐私意图的缺陷不会红；另 --github-url/--home-url 的 argparse help 未注「显式空串禁用」（--favicon help 已注），语义变更后文档不一致 | test_corner_privacy 或 test_prompt_site 补一例：设 HTML_GEN_GITHUB_URL + `prompt --site` → 断言 index.html 无 github-corner；help 文案顺手补「显式空串禁用; env: HTML_GEN_GITHUB_URL」 |
| HG-SEC-098 | 🟢 | `--dir ''` 空串 → `Path('')` = `.`（cwd），且仓库根 index.html（落地页）在 known 清理集内 → 在仓库根误跑空串 --dir 会覆盖/删除落地页（git 可恢复，但破坏性意外） | cmd_prompt_site 入口加防御：`args.dir` 为空串或解析后 == 仓库根/`Path.cwd()` 时 stderr 拒绝 exit 1（一行级） |
| HG-SEC-099 | 🟢 | AGENTS.md 两处同步被「受保护文件」审批拦截（prompt 段 --site 行、目录结构 prompts/ 行；测试计数 247 stale）→ agent 文档与实现漂移，非阻断 | 用户批准后补 docs 行级 commit（dev profile 或 review 均可）；内容已在上文维度 6 指明 |

## 评分

| 扣分项 | 严重度 | 分值 |
|:-------|:------:|:----:|
| HG-SEC-096..099（4 项，记录/建议，无阻断） | 🟢×4 | 0（记录） |
| 设计折叠项 HG-SEC-086..095 | ✅ closed 本次实现 | 0 |

得分: 100 - 0 = **100 / 100 → A**

## 结论

**PASS（100/A，通过）** — 实现与设计 §5/§6/§7 逐项一致，10 项设计折叠（HG-SEC-086..095）全部落实并有源码行号 + 测试 + 独立复跑证据；两个 dev 实施决策（all.md refs h1 剥离 / corner_args 空串语义）经评估均合理、零回归；产物 17 文件与提交逐字节一致（index meta 除外，HG-SEC-086 已知预期）；全量 263 passed（复跑确认，首跑 videos 瞬时 flake 与环境相关非本批回归）。无 🔴/🟡。4 项 🟢 记录（设计文本回写、env-set 回归测试、--dir 边界防御、AGENTS.md 同步遗留）均非阻断，择机处理即可。验收清单 1-8/10 已闭环；#9 curl 实测待 push 后按设计 §10 补录。

## 遗留清单（待用户/后续）

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | AGENTS.md 两处同步（prompt 段 --site + 目录结构 prompts/ + 测试计数）— 需用户批准受保护文件后补 commit | 文档 🟢 HG-SEC-099 |
| □ | push 后 curl 实测 /prompts/、all.md、{skill}.md/.json（含 .json MIME 记录） | 验收 #9 |
| □ | （可选）HG-SEC-097 env-set 回归测试 + help 文案对齐 | 测试 🟢 |
| □ | （可选）HG-SEC-098 --dir 空串/仓库根防御 | 防御 🟢 |
| □ | （可选）HG-SEC-096 设计 §5/§6.3/§10 文本回写 | 文档 🟢 |
