你以 review role 对 HTML-GEN-CL008（prompt --site v2：C 型知识库门户 + kb detail + 体系化沉淀）
做实现审计，按治理规范给出审计结论。

【审计对象】
项目：/Users/jadenli/CodeSpace/html-gen.cli
实现 commit：479f053（feat@html-gen: prompt --site v2 C 型门户 + kb detail (HTML-GEN-CL008)）
设计基线：documents/solutions/html-gen-prompts-site-v2-design-v1.0-20260902.md
设计评审：PASS 95/A（commit 2f748fe，折叠项 HG-SEC-100..105）
commit 范围：456a12c..479f053（设计 v1.0 → 评审 → feat）
参考：documents/review/html-gen-prompts-site-v2-design-review-v1.0-20260902.md
（评审报告 + v2-dev-impl-prompt-20260902.md 同目录）

【实现范围（feat 479f053）】
- html-gen.py：cmd_prompt_site 扩展（注册表 SKILL_TO_GROUP/GUIDE_MAP/CASE_MAP + groups 5 定义 →
  _kb-groups.json/_kb-data.json；kb/{skill}.html detail ×8；index.html C 型门户 cmd_knowledge 渲染；
  计数文本 18→28 同步 HELP/help/docstring）
- tests/test_prompt_site.py（test_01 28 文件 / test_05 门户 kw-tab / test_11 schema / test_12 kb /
  test_13 契约不变 / 幂等 20 / 互斥守卫 env 回归）
- prompts/ 产物 28 文件重生成 + skills/html-gen/SKILL.md + html-gen-cli-spec/SKILL.md 补 --site
- README.md/README.zh.md 门户说明
- AGENTS.md 两处同步被「受保护文件」审批拦截（dev 与 ops 均超时 deny）→ 遗留待用户

【ops 独立核查结果（已复跑，供复核）】
1. 全量 pytest -n 4 = 268 passed（265→268，+3）；专项 test_prompt_site+prompt_cmd = 18 passed
2. 独立断言：顶层 20 + kb/ 8 精确集合；_kb-groups 5 tab（A表格/B文档/C知识库/D幻灯片/通用CLI）；
   _kb-data kinds = skill 8 + guide 6 + case 12；字段 {title,group,section,badge,desc,url,kind} 齐；
   skill 条目 url=kb/{name}.html；group 均合法；guide/case URL 文件存在性全过（无缺失）
3. 门户 DOM：kw-tab/kwSidebar/5 tab 标签文案；零 github-corner 锚点；kb/html-gen.html 含 doc-body
4. 契约回归：8 个 {skill}.md == strip(SKILL.md)+refs 逐字
5. 幂等：确定性集 19（all.md+_kb×2+16 md/json）byte-identical；kb/ 保留；regen exit 0
6. git：feat 单 commit 22 文件无夹带；树干净（AGENTS.md 未改）

【审计维度】
1. 设计-实现一致性：§4 注册表/§5 产物 28/§6 内容/§7 CLI 规格/§8 测试 逐项
2. 折叠项落实：HG-SEC-100（直调 Namespace 全字段：cmd_doc subtitle=None/github_url=''/home_url 等 +
   cmd_knowledge subtitle/welcome + test_09 扩展 kb 页 env pin）/ 101（desc 元数据注明）/
   102（append 序 SKILL→GUIDE→CASE）/ 103（kb mkdir + kb 内 known 清理 + step5 stdout 抑制）/
   104（HELP_PROMPT/argparse help/docstring 18→28）/ 105（_kb Jekyll _ 前缀不发布注明）
3. 门户实际渲染正确性：建议浏览器/静态抽检——_kb-data 条目在 index.html 内联后 5 tab 结构完整、
   iframe URL（kb/、../demos/）在产物中成对出现（抽查 2-3 个 url 字符串）；若可跑 Selenium 则
   验证 kw-tab 点击后 iframe 加载 kb/html-gen.html 无 JS 错误（drama 既有用例可参照；非强制）
4. 契约与兼容：{skill}.md/.json/all.md 规则逐字保留（test_13/既有 test_02/03/04 全过佐证）；
   旧 18 文件 URL 无破坏（.md/.json/all.md 仍原位）；known 清理 28 containment
5. 回归面：全量 268 + 既有非 prompt_site 测试零回归
6. 安全：注册表 URL 相对路径无外链注入；github_url='' 防 env；_kb json 不发布（HG-SEC-105）
7. 文档：skills 双篇同步（--site 出现）、README 双份；AGENTS.md 两处遗留判定非阻断
8. 验收清单 §11：1-9 逐项（#9 cli-prompts-site 落库 + hs 转交为收尾步，ops 执行，审计确认前置条件已备）

【期望输出】
- 结论：通过（≥85/A）/ 有条件通过（80-84/B）/ 驳回（<80），附分数
- findings 按严重度编号（HG-SEC-NNN 续号或自编号），每条「问题+建议」
- 审计报告落 documents/review/html-gen-prompts-site-v2-impl-audit-v1.0-20260902.md
- 更新 review-log.md / .review-level.yaml（仅 commit 不 push）
- 若发现需修复项：给 ops 独立 fix@ 清单（不回 dev）
