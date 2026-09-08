# html-gen prompt 在线阅读站点 v2 设计（C 型知识库门户 + 体系化沉淀）v1.0 (2026-09-02)

> 闭环: HTML-GEN-CL008 · kind=independent（独立闭环，不经 1acl-orchestrator）
> 探讨确认（2026-09-02）: A1 B1+B3 C1 D1 E1+E2 F1 G1 G1a-1 G1b-1 H1 I1 J1 K-1 L-1
> 前置: HTML-GEN-CL004（prompt CLI 子命令）/ CL007（--site v1：B 型合集门户 18 文件已上线 push）
> 影响: html-gen.py（--site 扩展）+ prompts/ 产物（18 → 28 文件）+ skills/ 文档 ×2 + README ×2 + AGENTS.md + Hermes devops skill（cli-prompts-site 新增）

## 1. 背景与需求

CL007 上线后三个动机驱动 v2：

1. **门户信息架构不足**：B 型 doc 合集单页 TOC h2/h3 扁平（HG-SEC-092 已记录），无「模板 × 内容维度」
   导航；平台用户找「A 表格模板怎么用 + 案例」需长页滚动；与 html-gen 产品体系（4 模板）不对齐。
2. **沉淀缺口**：CL007 文档同步漏了 skills/ 自身——skills/html-gen/SKILL.md 与
   html-gen-cli-spec/SKILL.md 仍是 CL004 时代文本，平台读 /prompts/html-gen.md 学不到 `--site`；
   「按规范生成」的规范文本本身未含本功能。
3. **跨项目复用诉求**：http-server.cli（hs）与 html-gen 同构（hs prompt 参考 html-gen prompt；
   skills/ 6 篇；独立 Pages 域 http-server.cli.jaden.tech），CL007 的 prompts 站点方案可迁移，
   需沉淀为通用 skill 并转交 hs 项目实施。

v2 目标：/prompts/ 门户改 C 型 knowledge（横向 5 tab = A 表格/B 文档/C 知识库/D 幻灯片/通用 CLI，
纵向 = 指令 CLI/模板语法/使用案例），并完成两级沉淀（html-gen 内部 skills 同步 + 跨项目通用 skill）。

## 2. 决策记录（探讨锁定 2026-09-02）

| 项 | 决策 | 说明 |
|:---|:---|:---|
| A1 | 两级沉淀 | html-gen skills 文档补 --site；另建跨项目通用 skill |
| B1+B3 | 通用 skill 内容 | 通用生成骨架 + html-gen 参考实现 + hs 移植清单 + 测试/验收要点 |
| C1 | hs 落地通道 | 本次只沉淀 + 打印 hs 实施 prompt 转交（hs 项目自闭环，ops 不代改 hs 源码） |
| D1 | 门户形态 | /prompts/ 改 C 型 knowledge（layout-knowledge） |
| E1+E2 | 契约/URL | {skill}.md/.json + all.md 逐字保留；门户仍 /prompts/（index.html 换 knowledge 产物） |
| F1 | 横向 tab | 5 group：A 表格/B 文档/C 知识库/D 幻灯片/通用 CLI |
| G1 | 纵向 section | 指令 CLI / 模板语法 / 使用案例（条目混合 skill detail + guide + 案例页） |
| G1a-1 | 案例数量 | 每模板选代表性 2-4 个（按可用素材；注册表可后续扩） |
| G1b-1 | 通用 tab section | 指令 CLI（html-gen、html-gen-cli-spec）/ 页面规范（pages-index）/ 测试规范（test-speed-optimization）；不设语法/案例维 |
| H1 | skill 详情载体 | 每 skill 生成 doc detail 页（推翻 B 型前提下的旧 H1「不做 per-skill html」） |
| I1 | 生成机制 | 生成器内置映射表（skill→group/section + guide/demo 注册表），随 --site 生成 knowledge data |
| J1 | 范围 | 沉淀与改造合一 CL（HTML-GEN-CL008） |
| K-1 | 产物布局 | prompts/kb/{skill}.html ×8 + prompts/_kb-groups.json + _kb-data.json |
| L-1 | 通用 skill 命名 | cli-prompts-site（Hermes devops 类） |

## 3. 现状与约束（实测 2026-09-02）

- prompts/ 现状：B 型 doc 合集 index.html（8 skill 全文约 5 千词）+ 16 md/json + all.md，
  URL 契约已上线（curl 全绿，见 CL007 复盘）。
- C 型素材齐备：demos/ 18 html 含 guides（usage/table/doc/knowledge/slide-guide +
  markdown-spec）+ 案例（countries/provinces/table-features/hermes-profile-skills-list/
  drama-knowledge/chaitin/cloudwise-business-analysis/knowledge-demo/slide-demo）；
  chaitin/cloudwise 内容子页（doc 渲染，如 company-profile.html）可作 B 文档案例。
- C 型能力现成：layout-knowledge（横向 group 标签栏 + 纵向 section/badge + iframe/desc +
  搜索 + 选择恢复）；company-report.py 已演示 knowledge 站点生成管线。
- knowledge data 形态实证（data/_drama-kb-data.json）：items {title, group, section, url,
  section_icon?}；groups 独立 json（{key,label,icon} 结构见 AGENTS.md）。
- 约束：零依赖/零新模板；产物无 frontmatter（Jekyll 实证，CL007 §3 沿用）；iframe 相对 URL
  （门户在 /prompts/，guide/demo 在 /demos/ → ../demos/xxx.html）。

## 4. 门户信息架构与注册表

### 4.1 groups（横向 tab，5 个）

```json
[
  {"key": "table",     "label": "A 表格",   "icon": "📊"},
  {"key": "doc",       "label": "B 文档",   "icon": "📄"},
  {"key": "knowledge", "label": "C 知识库", "icon": "📚"},
  {"key": "slide",     "label": "D 幻灯片", "icon": "🎞️"},
  {"key": "cli",       "label": "通用 CLI", "icon": "🛠️"}
]
```

### 4.2 注册表（生成器内置 dict，html-gen.py 常量）

SKILL_TO_GROUP（8 skills；skill 条目 = detail 页 kb/{skill}.html，badge「Prompt」）：

| skill | group | section |
|:---|:---|:---|
| html-gen-table | table | 指令 CLI |
| html-gen-doc | doc | 指令 CLI |
| html-gen-knowledge | knowledge | 指令 CLI |
| html-gen-slide | slide | 指令 CLI |
| html-gen | cli | 指令 CLI |
| html-gen-cli-spec | cli | 指令 CLI |
| pages-index | cli | 页面规范 |
| test-speed-optimization | cli | 测试规范 |

GUIDE_MAP（demos guides；badge「指南」，desc 一句）：
table-guide.html→(table,模板语法) · doc-guide.html→(doc,模板语法) ·
knowledge-guide.html→(knowledge,模板语法) · slide-guide.html→(slide,模板语法) ·
usage-guide.html→(cli,指令 CLI) · markdown-spec.html→(doc,模板语法)（md 输入语法，随 doc 组）

CASE_MAP（使用案例；badge「案例」，desc 一句）：
table: countries-table.html（全球 195 国速查表）· provinces-table.html（中国 34 省速查表）·
table-features-demo.html（表格功能全演示）· hermes-profile-skills-list.html（Hermes Skills 列表）
doc: chaitin/company-profile.html（长亭公司档案）· cloudwise/company-profile.html（云智慧公司档案）·
chaitin/business-model.html（长亭商业模式）
knowledge: drama-knowledge.html（以剧读史）· chaitin-business-analysis.html（长亭商业分析）·
cloudwise-business-analysis.html（云智慧商业分析）· knowledge-demo.html（知识库功能演示）
slide: slide-demo.html（幻灯片演示）
（cli 组无案例维，见 G1b-1）

条目排序：同 section 内按注册表顺序；section 顺序：指令 CLI → 模板语法 → 使用案例（模板组）/
指令 CLI → 页面规范 → 测试规范（cli 组）。

## 5. 产物与 URL 规格（28 文件）

| 文件 | URL | 说明 |
|:---|:---|:---|
| prompts/index.html | /prompts/ | C 型 knowledge 门户（改；URL 不变） |
| prompts/_kb-groups.json | — | 5 group 定义（下划线前缀，非 curl 契约；commit 入库） |
| prompts/_kb-data.json | — | 门户条目 {title,group,section,badge,desc,url,kind} |
| prompts/kb/{skill}.html ×8 | /prompts/kb/{skill}.html | skill detail 页（doc 渲染 {skill}.md） |
| prompts/{skill}.md/.json ×16 | /prompts/{skill}.md|.json | 保留，逐字不变（契约回归断言） |
| prompts/all.md | /prompts/all.md | 保留，逐字不变 |

URL 相对路径（门户 iframe）：kb/{skill}.html（同目录）；../demos/*.html、../demos/chaitin/*.html。
known 清理集更新 = 原 18 + _kb-groups.json + _kb-data.json + kb/{skill}.html ×8（28 个已知名，
containment 语义不变，HG-SEC-088/096 沿用）。

## 6. 内容规格

- _kb-data.json 条目：{title, group, section, badge, desc, url, kind}；kind ∈ skill/guide/case；
  desc：skill = frontmatter description 首行（HG-SEC-095 限制沿用）；guide/case = 注册表内一句；
  title：skill = 目录名；guide/case = 注册表语义名。
- kb/{skill}.html：cmd_doc 渲染 prompts/{skill}.md（strip 后正文 + refs，与 curl .md 同源），
  title = skill 目录名，quiet；产物含 doc meta（分钟粒度，幂等断言排除）。
- index.html：cmd_knowledge 直调渲染（Namespace：data=_kb-data.json、groups=_kb-groups.json、
  output=index.html、title/欢迎语、quiet；github_url 显式空串防 env，CL007 HG-SEC-090 沿用）。
- iframe 形态风险：detail 页为 doc 模板（自带侧栏/工具栏），嵌 C 型门户 iframe 可能双导航。
  以既有 C 型案例（drama 子页/knowledge-demo）同构为准；若双 chrome 明显，detail 生成采用
  门户内嵌参数（如 ?sidebar=0/裸模式）降级——实现阶段预演确认，验收含 iframe 视觉抽查。

## 7. CLI 规格（--site 扩展）

```
html-gen prompt --site [--dir <path>]
```

流程扩展（cmd_prompt_site 内，互斥/--dir 守卫不变）：
1. 收集 skills + 内存构建 8 md + 8 json + all.md（不变，fail-fast 零写盘）
2. 构建门户产物内存对象：按 §4 注册表生成 _kb-groups/_kb-data 文本；
   detail 输入即步骤 1 的 {skill}.md（写盘后经 cmd_doc 渲染 kb/{skill}.html）
3. 清理 known 28 名 → 写 16 md/json + all.md + _kb-groups.json + _kb-data.json
4. cmd_doc 渲染 8 个 kb/{skill}.html（title=skill 名，quiet，stdout 抑制）
5. cmd_knowledge 渲染 index.html（门户）
6. 统计 `[站点] {dir} 已生成: 8 skills (28 文件: 门户 + kb×8 + md/json×16 + all.md)`

## 8. 测试计划（tests/test_prompt_site.py 更新）

- test_01 更新：文件断言 = 顶层 20（index/_kb-groups/_kb-data/all.md/16）+ kb/ 子目录 8；
  stdout 统计含 28。
- test_05 重写：index.html 门户 DOM = layout-knowledge 标记（kw-tab/kwSidebar/5 tab 标签
  A 表格/B 文档/C 知识库/D 幻灯片/通用 CLI）；无 github-corner 锚点；home 指向站点（沿用）。
- 新增 test_11_kb_data_schema：_kb-data.json 可解析；条目 kind/section/badge/url 齐；
  skill 8 条 kind=skill 且 url=kb/{name}.html；guide/case url 指向 demos 实际存在文件
  （Path 存在性断言，防注册表漂移）；group 全在 _kb-groups keys。
- 新增 test_12_kb_detail_pages：8 个 kb/{skill}.html 存在且含 doc-body/标题=skill 名；
  内容含 {skill}.md 正文关键标记（抽样 html-gen/html-gen-table）。
- 新增 test_13_contract_unchanged：{skill}.md == strip(SKILL.md)+refs（既有断言保持，
  显式标注契约不变）；json 信封不变；all.md 唯一顶层 h1（fence-aware）不变。
- 幂等：确定性集 = 17 + _kb-groups.json + _kb-data.json + index.html（knowledge 无 doc meta）
  = 20 文件 byte-identical；kb/*.html 排除（doc meta 分钟粒度，HG-SEC-086 同类）。
- 互斥/守卫/env-set（test_07/09/10）不变回归。
- 全量预期 265 → +3 ~ 268。

## 9. skills 文档同步（A1 内部层）

- skills/html-gen/SKILL.md：prompt 子命令段补 `--site`（生成 prompts/ 在线阅读站点 28 文件 +
  门户 5 tab 说明 + curl 契约 URL）。
- skills/html-gen-cli-spec/SKILL.md：CLI 子命令表补 prompt --site 行。
- 同步后重跑 `--site` 使 detail/门户/md 产物反映（产物由生成器产出，勿手改）。
- README.md/README.zh.md：「在线阅读 & curl 获取」小节补门户结构说明（5 tab + kb/ 路径）。
- AGENTS.md：prompts/ 行更新（28 文件 + kb/ 子目录 + _kb json）。

## 10. cli-prompts-site 通用 skill 大纲（A1 跨项目层 / B1+B3 / L-1）

名称：cli-prompts-site（Hermes devops 类，本闭环收尾时落库）
内容：
1. 适用判定：CLI 项目 + skills/ 目录（SKILL.md）+ 已有 prompt 子命令（或待建）+ GitHub Pages 域
2. 通用骨架：prompt --site 等价物设计（互斥/守卫/known-name 清理/fail-fast）
3. 产物契约：{skill}.md/.json + all.md + 门户（B 或 C 型可选）+ kb detail（C 型）
4. 关键坑：frontmatter 剥离（Jekyll 实证 SKILL.md 404/SKILL.html 200、README.md 200）、
   doc meta 分钟粒度幂等排除、knowledge iframe 相对 URL、_kb json 下划线前缀
5. html-gen 参考实现（html-gen.py cmd_prompt_site + 注册表 + test_prompt_site.py 要点）
6. hs 移植清单（http-server.cli）：实现 hs prompt --site（参考 _cmd_prompt:686）、skills 6 篇
   映射、CNAME http-server.cli.jaden.tech、URL 契约、测试、CL 编号 HTTP-SERVER-CLNNN
7. 验收/测试要点（文件集/契约/门户 DOM/幂等/互斥）

## 11. 验收清单（ops 核查 / 审计复用）

1. `python3 html-gen.py prompt --site --dir /tmp/...` → 28 文件（顶层 20 + kb/ 8）
2. _kb-data.json schema + 8 skill 条目 url=kb/{name}.html + guide/case url 文件存在性断言
3. 8 kb/{skill}.html doc 渲染（doc-body/标题）；门户 index kw-tab + 5 tab 标签
4. 契约回归：16 md/json + all.md 与 CL007 规格逐字一致（strip 规则断言通过）
5. 幂等：20 确定性文件 byte-identical；kb/*.html 排除
6. 互斥/守卫/env-set 回归；全量 pytest 265 → ~268 passed
7. skills/ 文档同步（html-gen + cli-spec 补 --site）；重跑产物 diff 仅预期文件
8. 默认目录真实生成 → commit；push 后 curl：/prompts/ 门户 200（kw-tab）、
   /prompts/kb/html-gen.html 200、{skill}.md/.json/all.md 200 契约回归、iframe 视觉抽查（双 chrome）
9. cli-prompts-site skill 落库；hs 实施 prompt 打印转交（含 URL/编号/验收）

## 12. 风险与边界

- iframe 双 chrome（detail 侧栏）→ 预演确认，必要时裸模式参数（§6）
- kb detail doc meta 分钟粒度 → 幂等排除（§8）
- 注册表漂移（guide/demo 文件被删/改名）→ test_11 文件存在性断言兜底
- 旧 test_01/05 断言变更属预期行为变更（文档化）；外部 curl 契约零破坏
- 案例数量受素材限制（slide 仅 1 案例）→ G1a 语义「2-4 或按可用素材」
