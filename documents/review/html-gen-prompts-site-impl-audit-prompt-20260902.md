你以 review role 对 HTML-GEN-CL007（html-gen prompt --site 在线阅读站点）做实现审计，
按治理规范给出审计结论。

【审计对象】
项目：/Users/jadenli/CodeSpace/html-gen.cli
实现 commit：d4ec017（feat@html-gen: prompt --site 在线阅读站点 (HTML-GEN-CL007)）
设计基线：documents/solutions/html-gen-prompts-site-design-v1.0-20260902.md
（评审 PASS 85/A，折叠项 HG-SEC-086..095 已订正入文，commit fe2ee22/9c0cb1a）
评审报告：documents/review/html-gen-prompts-site-design-review-v1.0-20260902.md
commit 范围：fe2ee22..d4ec017（设计 v1.0 → 设计订正 → 评审/实施 prompt → feat）

【实现范围（feat d4ec017）】
- html-gen.py：prompt parser 加 --site/--dir；cmd_prompt 顶部互斥校验（--site 与
  skill/--brief/--json → stderr+exit1）；cmd_prompt_site（1008-1100）；_site_skill_section /
  _site_all_md / _strip_leading_h1 / _fence_top_h1_indices（283-304/1103-1130）；
  corner_args 语义变更（None→env 兜底 / 显式''→禁用，与 favicon_args 对齐）
- tests/test_prompt_site.py（8 用例）+ 全量 263 passed（基线 255+8，ops 已独立复跑）
- README.md/README.zh.md「在线阅读 & curl 获取」小节 + HELP_PROMPT 补 --site
- prompts/ 18 产物文件（index.html + all.md + 8 md + 8 json）

【ops 独立核查结果（已复跑，供复核）】
1. 全量 pytest -n 4 = 263 passed（35.96s）；专项 test_prompt_site+test_prompt_cmd = 13 passed
2. 独立断言（非测试自证）：18 文件集合精确；8 skill 的 .md 正文 == strip_frontmatter(SKILL.md)
   + references 拼接逐字；json 信封键齐 content==正文 references 键==stems；all.md 顶层 h1 计数
   ==1（fence-aware）、8 段标题、8/8 desc 引用行；index 含 doc-body/doc-sidebar/标题、零 github
   外链（github_url='' 生效）、home 指向站点；17 确定性文件幂等 + 无关文件保留；互斥组合 exit 1
3. 默认目录重生成：仅 index.html meta 时间戳行差异（HG-SEC-086 已知），已还原保持 feat commit 纯净

【审计维度】
1. 设计-实现一致性：§5 CLI 规格 / §6 内容规格 / §7 测试计划逐项比对
2. 折叠项落实：HG-SEC-086（幂等 17 文件）/ 087（fence-aware h1）/ 088（清理仅已知产物名
   containment）/ 090（cmd_doc github_url='' 显式）/ 091（slide 2 refs 断言）/ 094（HELP_PROMPT）
3. 两个 dev 实施决策合理性：
   a) all.md 内 references 段剥离 reference 自身首个顶层 h1（保证唯一顶层 h1），单篇
      {skill}.md 保留 ref 原 h1（与 CLI 全文一致）——评估是否破坏设计 §6.1「原文直读」语义
   b) corner_args 语义从 `or 链` 改为「None→env 兜底；显式''→禁用」——评估对既有
      table/doc/knowledge/demo 的 env 兜底行为是否零回归（test_corner_privacy 6 过）
4. 回归面：既有 test_prompt_cmd 5 例 + corner_privacy + 全量 263 的充分性
5. 产物一致性：prompts/ 提交内容与生成器当前输出 17 确定性文件逐字一致（index meta 除外）
6. 文档同步：README 双份 / HELP_PROMPT；AGENTS.md 两处同步被「受保护文件」审批拦截
   （① prompt 子命令段 --site 行；② 目录结构 prompts/ 行）→ 判定是否非阻断遗留待用户
7. 安全：prompts/ 产物内容源受控（skills/）；无凭据；json/md 无路径穿越；--dir 清理 containment
8. 验收清单 §8：1-10 项逐项可执行性

【期望输出】
- 结论：通过（≥85/A）/ 有条件通过（80-84/B）/ 驳回（<80），附分数
- findings 按严重度编号（沿用 HG-SEC-NNN 或审计自编号），每条「问题+建议」
- 审计报告落 documents/review/html-gen-prompts-site-impl-audit-v1.0-20260902.md
- 更新 review-log.md / .review-level.yaml（仅 commit 不 push，AGENTS.md 约定）
