# html-gen prompt 在线阅读站点 v2 实现审计 — review报告 v1.0

> 日期: 2026-09-02
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 实现 commit: 479f053（feat@html-gen: prompt --site v2 C 型门户 + kb detail · HTML-GEN-CL008，kind=independent）
> commit 范围: 456a12c..479f053（设计 v1.0 → 设计评审 2f748fe → feat 479f053，共 3 commits）
> 设计基线: documents/solutions/html-gen-prompts-site-v2-design-v1.0-20260902.md（PASS 95/A，折叠项 HG-SEC-100..105）
> 评审报告: documents/review/html-gen-prompts-site-v2-design-review-v1.0-20260902.md
> review维度: 设计-实现一致性 / 折叠项落实 / 门户渲染正确性 / 契约与兼容 / 回归面 / 安全 / 文档同步 / 验收清单 §11

## 数据验证（本审计独立复跑，非测试自证）

| # | 验证项 | 方法 | 结果 |
|:-:|:-------|:-----|:-----|
| 1 | 全量回归 | `/usr/bin/python3 -m pytest tests/ -q -n 4` | ✅ **268 passed**（35.53s）；基线 265 → +3（test_11/12/13），与设计 §8 预期精确一致 |
| 2 | 专项 | test_prompt_site + test_prompt_cmd | ✅ **18 passed**（13+5，0.62s） |
| 3 | 产物集合（核心） | 独立 `--dir /tmp/prompts-audit-v2` 生成 | ✅ 顶层 20（index/_kb-groups/_kb-data/all.md/16 md|json）+ kb/ 8 = **28 文件精确**；stdout 统计行「8 skills (28 文件: 门户 + kb×8 + md/json×16 + all.md)」 |
| 4 | _kb-groups | 解析 5 group | ✅ key=table/doc/knowledge/slide/cli，label=A 表格/B 文档/C 知识库/D 幻灯片/通用 CLI，与 §4.1 逐字一致 |
| 5 | _kb-data schema（核心） | 解析 26 items | ✅ kinds = skill 8 + guide 6 + case 12；字段集恰为 {title,group,section,badge,desc,url,kind}；8 skill url=kb/{name}.html 全对；group 全在 groups keys；guide/case 18 url 相对 ../demos/ 指向仓库 demos/ 文件**全部存在**（零注册表漂移）；badge Prompt 8/指南 6/案例 12 |
| 6 | section 首现序（HG-SEC-102） | 遍历 _kb-data | ✅ table/doc/knowledge/slide = 指令 CLI→模板语法→使用案例；cli = 指令 CLI→页面规范→测试规范（与 layout-knowledge Object.keys 首现序语义吻合） |
| 7 | desc 取值 | 与 skills/*/SKILL.md frontmatter description 首行比对 | ✅ 8/8 逐字一致（HG-SEC-095 首行语义沿用） |
| 8 | 产物一致性 | 提交 prompts/ vs 独立生成 28 文件逐字节 | ✅ **20 确定性文件 byte-identical**（含 index.html——knowledge 无 doc meta，幂等集 20 成立）；kb/ 8 页差异仅「创建/编辑」meta 分钟粒度时间戳行（非-meta diff = 0/页，HG-SEC-086 同类预期） |
| 9 | 幂等 + containment | 同目录二次/三次生成 | ✅ 确定性 20 文件 byte-identical；顶层无关文件 + kb/ 内无关文件（user-notes.md/orphan.txt）均保留且内容不变 |
| 10 | 契约回归（核心） | strip(SKILL.md)+refs 拼接 vs 提交 {skill}.md | ✅ 8/8 逐字一致（镜像 html-gen.py strip_frontmatter 正则）；json 信封 status/error/data{name,content,references} 8/8；content==strip(SKILL.md)；all.md 唯一顶层 h1 `# html-gen Prompt 合集` 不变 |
| 11 | 门户 DOM（静态） | grep 独立生成 index.html | ✅ kwTabBar/kwSidebar/kwSectionsContainer；5 tab 标签文本全中；title「html-gen Prompt 站点」+ welcome「从上方类目选择…」；零 github-corner 锚点；home-link 指向 https://html-gen.cli.jaden.tech/；无未替换占位符；doc-body 不存在（C 型，非 B 型） |
| 12 | iframe URL 成对 | 统计 index.html 内 url | ✅ kb/ 8 url 各 1 现 + ../demos/ 18 url（guide 6 + case 12）全现，抽查 countries-table/drama-knowledge/slide-demo/chaitin-company-profile 均命中 |
| 13 | kb detail 页 | 读 3 页抽样 + 全 8 页测试 | ✅ doc-body + `<title>{skill 名}</title>`；内容含 .md 正文关键标记（html-gen/html-gen-table）；零 corner、零 home-link（test_09 env pin 扩展全过） |
| 14 | Selenium 门户交互（可选增强） | headless Chrome 加载独立生成 index.html | ✅ 5 tab 渲染（📊A表格/📄B文档/📚C知识库/🎞️D幻灯片/🛠️通用CLI）；点 A 表格 → html-gen-table 条目 → iframe src=`kb/html-gen-table.html?sidebar=0&toolbar=0&t=…`（自动裸模式追加，双 chrome 化解实证）；iframe 内 doc-body 加载；门户页与内嵌页 **零 JS 错误** |
| 15 | 计数文本 18→28 | grep html-gen.py README×2 skills×2 | ✅ HELP_PROMPT:771 / argparse --site help:888 / cmd_prompt_site docstring:1111 全 28；代码/文档零残留「18 文件」 |
| 16 | 凭据/注入扫描 | _kb-data 全字段 + index.html ITEMS 段 | ✅ 无 `</script` 突破串；inject() 对 _SCRIPT_KEYS（groups/items）`</`→`<\/` 转义（html-gen.py:45-47）→ script 上下文注入面关闭 |
| 17 | 提交面 | git show 479f053 --stat + git status | ✅ 单 feat commit 22 文件无夹带（html-gen.py/tests/2 README/2 skills/prompts 28 产物含新增）；树干净；AGENTS.md 零改动（受保护文件拦截，见 HG-SEC-106） |

## 维度评估

### 1. 设计-实现一致性（§4 注册表 / §5 产物 28 / §6 内容 / §7 CLI / §8 测试 逐项）

| 设计 § | 规格 | 实现 | 判定 |
|:-------|:-----|:-----|:----:|
| §4.1 | groups 5 定义 | SITE_GROUPS html-gen.py:1015-1021 逐字一致 | ✅ |
| §4.2 | SKILL_TO_GROUP 8 skills | :1023-1032 逐字一致（含 cli 组 页面规范/测试规范） | ✅ |
| §4.2 | GUIDE_MAP 6 guides | :1035-1048 逐字一致 | ✅ |
| §4.2 | CASE_MAP 12 cases | :1051-1080 逐字一致（table 4/doc 3/knowledge 4/slide 1） | ✅ |
| §5 | 产物 28 = 顶层 20 + kb/ 8 | top_known 4+16 / kb_known 8（:1180-1185）；test_01 精确集合 | ✅ |
| §5 | 旧 16 md/json + all.md URL 原位保留 | 文件仍写 out_dir 根；逐字契约不变（数据验证 #10） | ✅ |
| §5 | known 清理 28 containment | 顶层 + kb/ 内已知名再循环（:1187-1194，HG-SEC-103）；无关文件保留（数据验证 #9） | ✅ |
| §6 | _kb-data 条目 7 字段 + kind | _site_kb_items :1083-1107；字段集与 kind 语义全对（数据验证 #5） | ✅ |
| §6 | desc：skill=frontmatter 首行；guide/case=注册表一句 | :1097 / :1100-1106 注册表内联；数据验证 #7 8/8 | ✅ |
| §6 | kb/{skill}.html = cmd_doc 渲染 .md（strip+refs 同源） | :1211-1223（输入即 :1197 写的 {skill}.md） | ✅ |
| §6 | index.html = cmd_knowledge 渲染（直调 Namespace） | :1225-1238 | ✅ |
| §7 | 流程 1 收集+内存构建 fail-fast 零写盘 | :1152-1176（try 全读，OSError→exit1；写盘在清理后） | ✅ |
| §7 | 流程 3/4/5 清理→写→detail→门户 | :1178-1238 顺序与设计 step2-5 一致 | ✅ |
| §7 | 统计 28 与清理集解耦 + --quiet 仅路径 | n_total=len(skills)*3+4（:1240-1246）；--quiet 独立实测只打印目录 | ✅ |
| §8 | test_01 28 / test_05 门户 DOM / test_11 schema / test_12 kb / test_13 契约 / 幂等 20 / 互斥守卫 env 回归 | 13 方法全实现（见 折叠项 与 数据验证） | ✅ |

### 2. 折叠项落实（HG-SEC-100..105）

| ID | 折叠要求 | 落实证据 | 判定 |
|:---|:---------|:---------|:----:|
| HG-SEC-100 | step4 cmd_doc Namespace 全字段：input/output/title/subtitle=None/quiet=True/github_url=''/home_url='' | :1213-1221（favicon 不传沿用默认注入，符合修复建议原文）；step5 cmd_knowledge：data/groups/output/title='html-gen Prompt 站点'/welcome='从上方类目选择…'/subtitle=None/quiet=True/github_url=''/home_url='https://html-gen.cli.jaden.tech/'（:1226-1236）；test_09 扩展 kb 8 页零 corner/零 env 污染/无 home-link 断言（test_prompt_site.py:309-317） | ✅ closed |
| HG-SEC-101 | desc 注明注册表元数据（url 优先不渲染） | _site_kb_items docstring :1084-1089 明示 + 代码注释「全条目带 url → desc 不参与门户 UI 渲染」；与 layout-knowledge:396 url 优先实证一致 | ✅ closed |
| HG-SEC-102 | _kb-data append 序 SKILL_TO_GROUP→GUIDE_MAP→CASE_MAP | :1092-1106 严格按序 append；注册表头注释 :1011-1013 写明；test_11 section 首现序断言（test_prompt_site.py:371-383） | ✅ closed |
| HG-SEC-103 | kb/ mkdir + kb 内 known 清理 + step5 stdout 抑制 + 统计解耦 | kb_dir.mkdir :1190-1191；kb_known 循环 :1192-1194；cmd_doc/cmd_knowledge 均包 redirect_stdout :1222/1237；n_total 公式 :1240 | ✅ closed |
| HG-SEC-104 | 代码内 18→28（HELP_PROMPT/argparse/docstring） | :771 / :888 / :1111（数据验证 #15） | ✅ closed |
| HG-SEC-105 | _kb json Jekyll _ 前缀不发布注明 | skills/html-gen/SKILL.md 产物说明行「Jekyll `_` 前缀不发布，已内联 index.html」+ 设计 §5 既有「（下划线前缀，非 curl 契约）」 | ✅ closed（实现侧注记；设计 doc §5 未追加明示句，见 🟢 HG-SEC-107） |

6/6 折叠项全部落实，均有源码行号 + 测试 + 独立复跑证据，无「折入即忘」。

### 3. 门户实际渲染正确性

- 静态：kw-tab 三标记、5 tab 标签文案、title/welcome、home-link、零 corner、零占位符（数据验证 #11）；iframe url（kb/ 8 + ../demos/ 18）成对出现在产物（#12）。
- 动态（Selenium，本审计实跑）：5 tab 渲染 → 点 A 表格 → html-gen-table 条目 → iframe 自动带 `?sidebar=0&toolbar=0&t=`（layout-knowledge 裸模式降级机制实证）→ 内嵌 doc-body 正常加载，门户页 + 内嵌页零 JS 错误（#14）。设计 §6/§12 的「iframe 双 chrome」风险被模板层自动裸模式机制完全化解，视觉抽查达标。

### 4. 契约与兼容

- {skill}.md/.json/all.md 生成规则与 CL007 逐字一致：test_13（抽样全等 + json 信封 + fence-aware h1）+ 既有 test_02/03/04 全过 + 本审计镜像 strip 逻辑独立比对 8/8（数据验证 #10）。
- 旧 18 文件 URL 无破坏：16 md/json + all.md 仍位于 prompts/ 根，URL 原位；index.html 由 B 型合集页变 C 型门户属设计 §5 明确行为变更（外部 /prompts/ URL 本身不变）。
- known 清理 containment：新增 kb/ 子目录仅删 8 个已知 detail 名，顶层仅删 20 已知名；无关文件保留实测（#9）。

### 5. 回归面

- 全量 268 passed（基线 265 → +3，设计 §8 预测精确）；专项 18 passed。
- 既有非 prompt_site 测试零回归（knowledge/drama/doc/table 等全部绿）；corner_privacy 6 例过（github_url='' 隐私语义未回归）。
- 幂等/互斥/守卫/env-set（test_06/07/08/09/10）全部保持，env-set 扩展后仍绿。

### 6. 安全

- 内容源受控：注册表（SITE_GROUPS/SKILL_TO_GROUP/GUIDE_MAP/CASE_MAP）为生成器内置常量 + skills/*/SKILL.md 项目受控文本；guide/case url 全部为相对路径（kb/、../demos/），**零外链注入**（数据验证 #5/#12）。
- script 上下文注入关闭：ITEMS/GROUPS 走 inject() `_SCRIPT_KEYS` `</`→`<\/` 转义（html-gen.py:45-47），_kb-data 内容无 `</script` 突破串（#16）；desc 因全条目带 url 永不进入 innerHTML（layout-knowledge:396 url 优先）。
- github_url='' 显式禁用 > env 兜底（HG-SEC-090 语义沿用）：index + kb 8 页均零 corner（test_09 + Selenium 实证）；home_url 门户指向站点、detail 无 home 入口——操作机设 env 不污染产物（#13/#14）。
- _kb json 因 Jekyll `_` 前缀不发布（HG-SEC-105，预期）；运行时数据已内联 index.html。
- 凭据扫描零命中；零新依赖、无 CDN、无外呼；清理 containment 不扩大误删面（--dir 守卫 test_10 回归过）。

### 7. 文档同步

- skills/html-gen/SKILL.md：prompt 段补 `--site`（28 文件 + 5 tab + kb detail + curl 契约 + _kb Jekyll 注记 + 变更记录 v2.5.0）✅
- skills/html-gen-cli-spec/SKILL.md：子命令表 prompt 行补 `--site`/`--dir`/28 文件 ✅
- README.md/README.zh.md：在线阅读小节 18→28 + C 型门户 5 tab + kb/ URL 表 + curl 示例 ✅（双份同步）
- AGENTS.md：两处同步（prompt 段 18→28 / 目录结构 prompts/ 行）被「受保护文件」审批拦截（dev 与 ops 均超时 deny）→ **遗留待用户**，非阻断（见 🟢 HG-SEC-106）。
- html-gen.py 内部计数文本 18→28 全同步（HG-SEC-104，数据验证 #15）。

### 8. 验收清单 §11 逐项

| # | 条目 | 状态 |
|:-:|:-----|:----:|
| 1 | --dir 临时目录 → 28 文件（顶层 20 + kb/ 8） | ✅ 独立复跑精确（#3） |
| 2 | _kb-data schema + 8 skill url=kb/ + guide/case url 存在性 | ✅ test_11 + 独立断言（#5） |
| 3 | 8 kb detail doc 渲染 + 门户 kw-tab/5 tab | ✅ test_12/test_05 + 静态（#11/#13） |
| 4 | 契约回归（16 md/json + all.md 逐字） | ✅ test_13 + 独立镜像比对（#10） |
| 5 | 幂等 20 确定性文件 byte-identical；kb/*.html 排除 | ✅ 独立二次生成（#9） |
| 6 | 互斥/守卫/env-set 回归 + 全量 pytest ~268 | ✅ 268 passed（#1/#2） |
| 7 | skills 文档同步 + 重跑产物 diff 仅预期 | ✅ skills×2 + README×2 同步；提交产物 == 生成器当前输出 20 文件一致（#8） |
| 8 | 默认目录真实生成 → commit → push 后 curl + iframe 视觉抽查 | ⏳ commit 已完成（feat 479f053）；push + curl 实测待用户推送后执行（仅 commit 不 push 约定）；iframe 视觉抽查以本审计 Selenium 实跑替代完成 |
| 9 | cli-prompts-site 落库 + hs 转交 | ✅ 前置已备：~/.hermes/profiles/dev/skills/devops/cli-prompts-site v1.0.0（7 节大纲完整，含 hs 移植清单 §6 + CNAME/CL 编号/验收）；hs 实施 prompt 转交为 ops 收尾步，不在 feat 提交面 |

## 安全事项

- 无 🔴/🟡 级安全项：注册表零外链、script 上下文注入关闭、github_url='' 防 env、_kb json 不发布、清理 containment 不扩大、零凭据零新依赖。
- 门户渲染经 Selenium 实跑零 JS 错误；iframe 双 chrome 由模板自动裸模式参数化解。

## Findings（本审计新增，HG-SEC-106..108，均 🟢 记录非阻断）

| # | 严重度 | 问题 | 建议 |
|:-:|:------:|:-----|:-----|
| HG-SEC-106 | 🟢 | AGENTS.md 两处同步未落地（prompt 子命令段 18→28 文件说明 + 目录结构 prompts/ 行 28 文件/kb/ 子目录/_kb json）——「受保护文件」审批 dev 与 ops 均超时 deny → 遗留待用户（与 CL007 HG-SEC-099 同型，b6734c6 系 CL007 获批后补 commit 的先例） | 用户批准后补 docs 行级 commit；内容见维度 7 |
| HG-SEC-107 | 🟢 | 设计 v1.0 文档未随折叠项订正入文：HG-SEC-100 修复建议原文为「§7 显式给出两处 Namespace 字段清单」、105 为「§5 加一句明示」——实现侧已全量承载（代码注释 + test_09 扩展 + SKILL.md 注记），但 design doc §5/§6/§7 文本未追加（对照 CL007 有 9c0cb1a 设计订正 commit） | （可选）补 docs@html-gen 设计订正 commit 回写 §5/§6/§7 折叠文本；不改亦可接受——代码/测试/产物文档已构成完整痕迹 |
| HG-SEC-108 | 🟢 | CL008 设计评审 commit 2f748fe 未同步 append review-log.md / .review-level.yaml（CL007 adccea9/a3eed86 惯例为三件套同 commit）→ 设计评审 PASS 95/A 的 trail 记录缺失 | 本次实现审计 commit 一并回填设计评审条目（PASS 95/A, HG-SEC-100..105）至 review-log.md + .review-level.yaml；后续评审须三件套同 commit |

## 评分

| 扣分项 | 严重度 | 分值 |
|:-------|:------:|:----:|
| HG-SEC-106..108（3 项，记录/建议，无阻断） | 🟢×3 | 0（记录） |
| 设计折叠项 HG-SEC-100..105 | ✅ closed 本次实现 | 0 |

得分: 100 - 0 = **100 / 100 → A**

## 结论

**PASS（100/A，通过）** — 实现与设计 §4 注册表（8 skills + 6 guides + 12 cases + 5 groups 逐字一致）/ §5 产物 28（顶层 20 + kb/ 8 精确集合）/ §6 内容（7 字段 + kind + desc 取值 + url 相对路径）/ §7 CLI 流程（fail-fast → containment 清理 → kb detail → C 型门户 → 统计解耦）/ §8 测试 逐项一致；6 项设计折叠（HG-SEC-100..105）全部落实并有源码行号 + 测试 + 独立复跑证据；产物一致性最强证据：提交 prompts/ 与生成器当前输出 **20 确定性文件 byte-identical**（kb/ 8 仅 meta 时间戳差，幂等集 20 成立且实测二次生成零 diff）；契约 {skill}.md/.json/all.md 逐字无漂移；门户 C 型渲染经静态 + Selenium 双重验证（5 tab + iframe 自动裸模式加载 + 零 JS 错误）；全量 268 passed（265→+3 精确）；安全面干净（零外链注入、script 上下文转义、github_url='' 防 env、_kb json 不发布、containment 不扩大）。无 🔴/🟡。3 项 🟢 记录（AGENTS.md 同步遗留待用户 / 设计 doc 折叠文本可选回写 / 设计评审 trail 回填）均非阻断。验收清单 1-7、9 前置条件已闭环；#8 的 push + curl 实测待用户推送后执行。

## 遗留清单（待用户/后续）

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | AGENTS.md 两处同步（prompt 段 18→28 + 目录结构 prompts/ 行）— 需用户批准受保护文件后补 commit | 文档 🟢 HG-SEC-106 |
| □ | push 后 curl 实测 /prompts/ 门户 200（kw-tab）+ /prompts/kb/html-gen.html 200 + {skill}.md/.json/all.md 200 契约回归 + iframe 视觉抽查 | 验收 #8 |
| □ | cli-prompts-site 收尾：hs 实施 prompt 打印转交（ops 执行，含 URL/HTTP-SERVER-CL 编号/验收） | 验收 #9 |
| □ | （可选）设计 v1.0 §5/§6/§7 折叠文本订正入文 | 文档 🟢 HG-SEC-107 |
