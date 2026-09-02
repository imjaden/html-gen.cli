# html-gen prompt 在线阅读站点设计 v1.0 (2026-09-02)

> 闭环: HTML-GEN-CL007 · kind=independent（独立闭环，不经 1acl-orchestrator；调度器当前 paused 佐证无并发）
> 探讨确认: A1 B3 C1 D1 E1 F1（2026-09-02）· G1 H1 I1（2026-09-02）
> 前置: HTML-GEN-CL004（prompt CLI 子命令）/ CL006（独立模式闭环实录）
> 影响: html-gen.py（prompt 子命令扩展）+ 新增 prompts/ 目录 + README.md/README.zh.md + AGENTS.md
> 评审: PASS 85/A（2026-09-02, documents/review/html-gen-prompts-site-design-review-v1.0-20260902.md）;
>       折叠项 HG-SEC-086..095 已订正入文（版本保持 v1.0，非阻断）
> 实现审计: PASS 100/A（2026-09-02, documents/review/html-gen-prompts-site-impl-audit-v1.0-20260902.md）;
>       记录项 HG-SEC-096..099（096 措辞 / 097 env 回归 / 098 --dir 守卫已落实; 099 AGENTS.md 待用户）

## 1. 背景与需求

在线功能平台期望按 html-gen 的 prompt 规范（skills/*/SKILL.md）生成 markdown 或渲染
HTML。平台需要两种获取方式：

1. **在线阅读**：单一稳定 URL 的渲染页面（深色、TOC 导航），覆盖全部 skills 全文
   （含 references）；
2. **curl 获取**：每 skill 一个稳定 URL 返回纯 markdown；一个 URL 返回 JSON 信封；
   可一次拉取全量合集。

约束：复用现有 GitHub Pages 站点（https://html-gen.cli.jaden.tech，
github imjaden/html-gen.cli main 分支），零新模板、零外部依赖。

## 2. 决策记录（探讨锁定，2026-09-02）

| 项 | 决策 | 说明 |
|:---|:---|:---|
| A 落地形态 | A1：生成 prompts/ 静态目录并 commit | Pages 原样服务；不新增 .nojekyll（避免全站构建行为变更） |
| B curl 格式 | B3：每 skill .md + .json | md=纯 markdown；json=CLI 信封同构 |
| C 在线阅读 | C1：B 型 doc 模板渲染合集页 | html-gen doc 生成，零新模板 |
| D 生成机制 | D1：html-gen prompt 子命令扩展 --site | 惯例对齐 demo --rebuild |
| E 覆盖范围 | E1：全部 8 个 skills + references | html-gen / html-gen-cli-spec / html-gen-doc / html-gen-knowledge / html-gen-slide / html-gen-table / pages-index / test-speed-optimization |
| F 文档 | F1：README 加「在线阅读 & curl 获取」小节 | 中英双份 |
| G 合集形态 | G1：全量合集单页 | index.html 为合集页；顺带发布 all.md 供一次 curl 全量 |
| H 独立渲染 | H1：不做每 skill .html | 浏览器阅读走合集页，机器走 .md/.json |
| I 触发时机 | I1：仅手动生成 commit | 无 cron/CI |

派生实现约束（本版新定，理由见 §3 实测）：站点产物一律剥离 YAML frontmatter。

## 3. 现状与约束（实测 2026-09-02）

- Pages 站点在线：https://html-gen.cli.jaden.tech/ → 200；demos/*.html 等静态文件正常。
- skills/ 已 git 跟踪：8 个 SKILL.md（1185 行）+ 3 个 references/*.md（177 行：
  html-gen-slide×2 + html-gen-table×1）。【HG-SEC-089 订正：原文 4 个为笔误】
- **Jekyll 实证**：/skills/html-gen/SKILL.md → 404（带 frontmatter 文件被 Jekyll 转换）；
  /skills/html-gen/SKILL.html → 200 text/html —— 原始 markdown 在 Pages 域不可达。
- **无 frontmatter 实证**：/README.md → 200 text/markdown —— 无 frontmatter 的 .md
  被 Pages 原样服务（curl 可得原始字节）。这是本方案可行性的核心依据。
- 仓库根无 .nojekyll；决策 A1 不引入。
- raw.githubusercontent.com 可达（200 text/plain）但本网络超时不稳定、非自定义域名，
  不作对外依赖 URL。
- 结论：**产物一律无 frontmatter + 置于 prompts/ 目录并 commit** → Pages 原样服务。

## 4. 产物与 URL 规格

目录 `prompts/`（仓库根，与 demos/ 同级；生成物 commit 入库，勿手改）。

共 18 文件：

| 文件 | URL | 内容 |
|:---|:---|:---|
| prompts/index.html | https://html-gen.cli.jaden.tech/prompts/ | B 型 doc 渲染的合集阅读页 |
| prompts/all.md | https://html-gen.cli.jaden.tech/prompts/all.md | 8 skills 全文合集（curl 一次全量） |
| prompts/{skill}.md ×8 | https://html-gen.cli.jaden.tech/prompts/{skill}.md | 单 skill 纯 markdown（正文 + references） |
| prompts/{skill}.json ×8 | https://html-gen.cli.jaden.tech/prompts/{skill}.json | 单 skill JSON 信封 |

{skill} = skills/ 子目录名（html-gen、html-gen-cli-spec、html-gen-doc、
html-gen-knowledge、html-gen-slide、html-gen-table、pages-index、test-speed-optimization）。

## 5. CLI 规格

```
html-gen prompt --site [--dir <path>]
```

- `--site`：生成 prompts/ 站点。默认输出目录 = html-gen.py 仓库根 / prompts/
  （与 demos/ 同级，Path(__file__).resolve().parent / 'prompts'）。
- `--dir <path>`：输出目录覆盖（供测试/临时预览使用，不改仓库）。
- 互斥：`--site` 与 skill 位置参数 / `--brief` / `--json` 同时传入 → 错误提示到
  stderr + exit 1（提示与 demo --rebuild 等参数语义不冲突）。
- 现有无参 / 带参 / --brief / --json 行为**完全不变**（零回归，test_prompt_cmd 不动）。

生成流程（cmd_prompt 顶部 `if args.site:` 分支 → cmd_prompt_site(args)）：

1. 收集 skills：复用现有遍历逻辑（SKILLS_DIR/skills/*/SKILL.md，sorted）。
2. **内存构建全部产物内容**（8 md + 8 json + all.md 文本）。任一文件读失败 →
   fail-fast stderr + exit 1；此时零写盘（避免半成品目录）。
3. **清理已知产物名**：仅删除 index.html / all.md / 8×{skill}.md / 8×{skill}.json
   （共 18 个已知产物名，以**当前遍历到的 skills** 为准），目录内其他文件一律保留——含
   `--dir` 自由路径时的 containment（误传 ~/ 等不误删无关文件）【HG-SEC-088】；
   注意：若某 skill 被删除，其旧 {skill}.md/.json 不在 known 清理集 → 会残留，
   由 git rm / 人工处理（containment 优先于自动清除）【HG-SEC-096 订正：原文字
   「旧产物由本清理移除」与实现不符】。
4. 写 8 个 {skill}.md、8 个 {skill}.json、all.md。
5. 调 cmd_doc 渲染 index.html：构造 Namespace 显式传 input=all.md 路径、
   output=index 路径、title="html-gen Prompt 合集"、
   home_url="https://html-gen.cli.jaden.tech/"、
   github_url=""（空串显式禁用，防 HTML_GEN_GITHUB_URL env 覆盖隐私意图）、
   quiet=True（favicon 不传沿用默认注入；CLI 参数优先于 env）【HG-SEC-090】。
6. 打印统计 `[站点] prompts/ 已生成: 8 skills (18 文件)`；--quiet 仅打印目录路径。

## 6. 内容规格

### 6.1 {skill}.md（curl 纯 markdown）

= SKILL.md 剥离 frontmatter 后的正文 + references 拼接。拼接规则与 CLI `html-gen
prompt <skill>` 全文一致：每 reference 前 `\n\n---\n\n## {stem}\n` + reference 原文。
references 文件按文件名 sorted glob（references/*.md），原文直读不剥离（无 frontmatter 约定）。

### 6.2 {skill}.json（curl JSON）

信封与 CLI `html-gen prompt <skill> --json` **结构同构**（status/data/error 键名
与嵌套一致；content 值为剥离 frontmatter 的正文，与 CLI 直出含 frontmatter 不同——
差异说明见 §6.5）【HG-SEC-093】：

```json
{"status": "ok", "error": "", "data": {
  "name": "{skill}",
  "content": "{去 frontmatter 后的 SKILL.md 正文，与同 skill 的 .md 正文段逐字一致}",
  "references": {"{stem}": "{reference 原文}", ...}
}}
```

### 6.3 all.md（合集，index.html 的渲染输入）

组装规则：

1. 首行 `# html-gen Prompt 合集`（唯一顶层 h1；B 型 doc 标题由此/--title 决定）。
2. 说明引用块（用途、生成命令、URL 提示）。
3. 每 skill 一段，顺序同遍历（sorted）：
   - 段标题 `## {skill.name}`（与正文 h2 同级 → TOC 扁平，skill 边界靠阅读顺序区分；
     已评估为可接受结构，记录不修）【HG-SEC-092】；
   - 下一行 `> {frontmatter description}`（description 缺失则省略；提取沿用 `_skill_desc`
     语义即 `description:` 行首行——html-gen-slide 的 description 为多行 YAML，仅取首行，
     继承既有 cmd_prompt 限制，记录不修）【HG-SEC-095】；
   - 正文 = 该 skill 剥离 frontmatter 后的内容，**删除正文首个顶层 `# ` 标题行**（若有，
     段标题已承载，避免重复 h1/h2）；「删除 / h1 计数」必须 **fence-aware**：3 个 skill
     正文的代码围栏内含 `# ` 注释行（html-gen 7 / html-gen-table 3 / test-speed-optimization 2），
     不得计入；实现复用 md_to_html 的围栏解析语义【HG-SEC-087】；
   - 正文余下原样（h2/h3 进入 doc TOC）；
   - references 拼接同 6.1（置于该 skill 段末尾）；all.md 内 ref 段复用正文规则：
     `## {stem}` 段标题已承载 → 剥离 reference 自身首个顶层 `# ` 标题（fence-aware），
     保唯一顶层 h1；单篇 {skill}.md 保留 ref 原样（与 CLI 全文一致）【HG-SEC-096 记录】。

### 6.4 index.html

html-gen doc 渲染 all.md（B 型文档模板：侧边栏 TOC + 深色主题 + 搜索等既有能力），
不引入新模板。目录请求 https://html-gen.cli.jaden.tech/prompts/ 由 Pages 返回 index.html。

### 6.5 一致性契约

- prompts/{skill}.md 正文段 == strip_frontmatter(SKILL.md) **逐字一致**；
- prompts/{skill}.json 的 data.content 与同 skill .md 正文段一致；
- 现有 CLI 输出（本地交互形态）不变：`html-gen prompt <skill>` 仍含 frontmatter 原文。
  差异仅 frontmatter 一段，理由 = Jekyll 原样服务要求 + 干净内容；README 注明。

## 7. 测试计划（tests/test_prompt_site.py，新增）

统一用 `--dir /tmp/...` 临时目录，**绝不触碰仓库 prompts/**（若存在断言其不变）：

1. test_01_site_generates_18_files：8 md + 8 json + all.md + index.html。
2. test_02_skill_md_equals_stripped_skill：全部 8 skill，md 正文段 == strip_frontmatter(SKILL.md)；
   html-gen-table 含 references 拼接段（## table-demo-prompt）；html-gen-slide 的 2 个
   references（selenium-h3-toggle-testing / slide-mode-null-guards）显式断言
   【HG-SEC-091】；html-gen 无 references 不含 `## ` ref 段。
3. test_03_skill_json_envelope：json.loads 通过；status/error/data 键齐；data.name 正确；
   data.content == 同 skill .md 正文段；data.references 键 == 实际 references stems。
4. test_04_all_md_structure：不以 `---` 开头；含 8 个 `## {skill.name}` 段标题；
   含 `# html-gen Prompt 合集` 唯一顶层 h1（计数 == 1，**fence-aware**：围栏内 `# ` 行不计）
   【HG-SEC-087】；references 原文出现在对应段。
5. test_05_index_html_dom：index.html 含 doc-body / 侧边栏容器 / 标题文本；零 JS 错误可
   用现有 doc 模板测试的 Selenium 模式（可选，若静态断言充分可不启浏览器）。
6. test_06_idempotent：连续生成两次 → **17 个确定性文件**（8 md + 8 json + all.md）
   diff 为空；index.html 改结构/标题断言（cmd_doc meta 含分钟粒度时间戳，字节 diff 会
   跨分钟 flaky）【HG-SEC-086】；兼 containment：目录预置无关文件 → 断言保留
   【HG-SEC-088】。
7. test_07_site_exclusive：--site 与 skill / --brief / --json 组合 → exit 1 + stderr 提示。
8. test_08_default_dir_untouched：默认路径生成逻辑不因测试而写仓库（集成用例显式断言）。

回归：test_prompt_cmd.py 既有 5 例不变；全量 `python3 -m pytest tests/ -q -n 4` 通过
（基线 255，预计 +8 → 263）。

## 8. 验收清单（dev 实施后 ops 核查）

1. `python3 html-gen.py prompt --site --dir /tmp/prompts-verify` → 18 文件齐全。
2. python 断言全部 8 skill：.md 正文段 == strip_frontmatter(SKILL.md)。
3. 8 个 .json json.loads + 信封键 + content 一致。
4. all.md 结构断言（唯一顶层 h1、8 段标题、references 出现）。
5. index.html 静态断言（doc 模板关键元素 + 标题）。
6. 幂等：**17 个确定性文件**（8 md + 8 json + all.md）两次生成 diff 为空；
   index.html 结构断言；目录预置无关文件 → 保留【HG-SEC-086/088】。
7. 互斥组合 exit 1。
8. 仓库内真实 `html-gen prompt --site` 生成 → git status 仅 prompts/ 新增 → commit。
9. push 后 curl 实测：/prompts/ 200 html；/prompts/all.md 200（text/markdown）；
   /prompts/html-gen.md 200 且内容 == strip(SKILL.md)；/prompts/html-gen.json 200 且
   json.loads 通过。（.md 的 MIME 以 README.md=text/markdown 为实证；.json MIME 待 push
   后实测记录，内容不受影响。）
10. 全量 pytest -n 4 通过。

## 9. 文档同步

- README.md / README.zh.md：prompt 命令示例后新增「在线阅读 & curl 获取」小节：
  prompts/ 说明 + 4 条 URL/curl 示例（/prompts/、all.md、{skill}.md、{skill}.json）
  + 生成命令 `html-gen prompt --site` + 「生成物勿手改，由 --site 重新生成」。
- AGENTS.md：目录结构补 prompts/ 行；prompt 子命令段补 `--site`。
- html-gen.py HELP_PROMPT（prompt 帮助文本段，html-gen.py:713 起）：补 `--site`
  （argparse --help 自动覆盖；HELP 文本同步）【HG-SEC-094】。

## 10. 边界与风险

- .json MIME：Pages 对无 frontmatter .json 的服务方式待 push 后 curl 实测记录
  （即便 content-type 为 application/octet-stream 之类，内容不变，平台侧可接受）。
- 目录请求 /prompts/（带尾斜杠）返回 index.html 为 Pages 标准行为；README 统一用带斜杠 URL。
- all.md/index 体积：skills 合计约 1362 行 md，doc 渲染无性能问题（perf_warning 仅 slide
  模式触发，doc 不受影响）。
- prompts/ 全部重生成语义：生成前清空目录 → 若某 skill 被删除，旧产物不残留（目录专用，
  README 注明勿手改，同 demos 治理）。
- 触发时机手动（I1）：skills 内容变更后需人工重跑 `html-gen prompt --site` 并 commit
  （复盘遗留项可提示用户）。
