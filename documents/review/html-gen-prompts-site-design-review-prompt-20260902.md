你以 review role 审计以下设计方案，按治理规范给出评审结论。

【审计对象】
项目：/Users/jadenli/CodeSpace/html-gen.cli
方案文档：documents/solutions/html-gen-prompts-site-design-v1.0-20260902.md
（当前 HEAD: fe2ee22，方案已 commit，HTML-GEN-CL007 独立闭环 kind=independent）

【背景】
在线功能平台期望按 html-gen 的 prompt 规范（skills/*/SKILL.md）生成 markdown 或渲染 HTML，需要两种获取方式：浏览器在线阅读（单一稳定 URL 渲染页）+ curl 稳定拉取（每 skill 纯 markdown / JSON 信封）。约束：复用现有 GitHub Pages 站点（https://html-gen.cli.jaden.tech，github imjaden/html-gen.cli main 分支），零新模板、零外部依赖。

探讨决策已全部闭合（2026-09-02，A1 B3 C1 D1 E1 F1 + G1 H1 I1）：生成 prompts/ 静态目录并 commit（不引入 .nojekyll）；每 skill .md + .json（CLI 信封同构）；index.html = B 型 doc 模板渲染全量合集页（html-gen doc 生成）；扩展 html-gen prompt 子命令 --site（惯例对齐 demo --rebuild）；覆盖全部 8 skills + references；README 中英双份加「在线阅读 & curl 获取」小节；顺带发布 all.md 供一次 curl 全量；不做每 skill 独立 .html；仅手动生成 commit，无 cron/CI。

关键实测依据（2026-09-02，已实证）：Pages 站点在线；带 frontmatter 的 skills/*/SKILL.md 被 Jekyll 转换（/skills/html-gen/SKILL.md → 404，SKILL.html → 200），原始 md 不可达；无 frontmatter 的 /README.md → 200 text/markdown 原样服务。→ 设计定论：站点产物一律剥离 frontmatter（派生实现约束，设计 §2/§6.5）。

【审计维度】
1. 需求覆盖：在线阅读 + curl md + curl json + 一次全量 all.md + README 小节是否全部落实；与 9 项决策一致性
2. 架构与风格一致性：零依赖约束；argparse 互斥/exit/stderr 风格是否与现有命令一致；复用 strip_frontmatter()/cmd_doc() 的调用方式是否稳妥（cmd_doc 直调需构造 args Namespace，注意其 sys.exit 路径与 meta 计算副作用）
3. 产物规格正确性：18 文件清单；frontmatter 剥离理由是否成立；{skill}.md 的 references 拼接规则与 CLI 全文输出规则一致性；{skill}.json 信封（data.content == .md 正文段）；all.md 汇编规则（唯一顶层 h1、段标题、删正文首 h1、references 段归属）是否会产生文档结构歧义；「CLI 现有输出不变（含 frontmatter）vs 站点产物剥离 frontmatter」双形态差异是否可接受且被文档化
4. 生成流程风险：清空输出目录的幂等语义（误删风险与目录专用治理）；内存构建 fail-fast 先于写盘的顺序是否合理；--dir 测试隔离是否充分（绝不触碰仓库 prompts/）；index.html 经 cmd_doc 渲染时 title/home_url/quiet 传参是否完整
5. Pages/URL 边界：/prompts/ 目录请求返回 index.html 是否为 Pages 标准行为；.json/.md MIME 的不确定性是否被风险化；prompts/ 产物 commit 入库与 demos/ 治理一致性
6. 测试规划：test_prompt_site 8 用例是否覆盖生成完整性/内容逐字一致/json 信封/all.md 结构/幂等/互斥/默认目录隔离；既有 test_prompt_cmd 是否零回归；Selenium 需求是否过度（index 为既有 doc 渲染管线产物）
7. 文档同步完整性：README.md/README.zh.md 小节位置与示例；AGENTS.md 目录结构 + prompt 子命令段；是否遗漏 skills/ 或 help 文本同步（评估是否必要）
8. 验收清单可执行性：dev 验收/ops 核查/curl 实测条目是否命令级可跑、断言是否无歧义

【期望输出】
- 结论：通过（≥85/A）/ 有条件通过（80-84/B）/ 驳回（<80），附分数
- 修改意见按文档小节/SC 编号定位，每条给「问题 + 建议改法」
- 指出遗漏的风险点（如有）
- 若为有条件通过/驳回：明确需修订的文档位置（v1.1 bump 规则：git mv + frontmatter version 同步）

评审通过后由 dev role 按设计文档实施。
