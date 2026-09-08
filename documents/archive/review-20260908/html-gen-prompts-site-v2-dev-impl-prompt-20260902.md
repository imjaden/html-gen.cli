你以 dev role 在 html-gen.cli 项目实施 HTML-GEN-CL008（prompt 在线阅读站点 v2：C 型知识库门户 + 体系化沉淀），严格按设计文档执行。

【设计文档】
documents/solutions/html-gen-prompts-site-v2-design-v1.0-20260902.md
（当前 HEAD 以 git log 为准；评审 PASS 95/A，折叠项 HG-SEC-100..105 须随实施落实/订正入文）

【评审折叠项（须随实施落实，对应设计文档节）】
- HG-SEC-100（🟡 必改）：§7 补全两处直调 Namespace 完整字段——
  step4 cmd_doc（kb detail 8 页）：input={skill}.md、output=kb/{skill}.html、title=skill 名、
    subtitle=None、quiet=True、github_url=''、home_url=''（favicon 不传沿用默认注入）；
  step5 cmd_knowledge（门户 index）：data/groups/output/title/welcome/subtitle=None/quiet=True/
    github_url=''/home_url='https://html-gen.cli.jaden.tech/'（cmd_knowledge 的 subtitle/output
    为直接属性访问，缺 subtitle → AttributeError；缺 home_url → env 兜底，test_09 必红）；
  title/welcome 文案自定（如 title="html-gen Prompt 站点"）；
  test_09 扩展：对 kb/*.html 8 页同样断言零 github-corner、零 env 污染
- HG-SEC-101（🟢）：§6 注明 desc 为注册表元数据——layout-knowledge url 优先（layout-knowledge.html:396），
  全条目带 url → desc 不在门户 UI 渲染（供 desc-only/未来用途）
- HG-SEC-102（🟢）：§4.2 注明 _kb-data 条目 append 序 = SKILL_TO_GROUP → GUIDE_MAP → CASE_MAP
  （layout-knowledge 侧栏按数据数组内 section 首现顺序渲染，须保证组内 指令 CLI→模板语法→使用案例）
- HG-SEC-103（🟢）：§7 流程补 kb/ mkdir（cmd_doc/cmd_knowledge 均不建父目录）；kb/{skill}.html 清理
  须对 kb/ 内已知名再循环（顶层 iterdir 扫不到子目录，containment 语义同顶层）；step5 cmd_knowledge
  输出 redirect_stdout 抑制（否则 --quiet 非「仅打印路径」）；统计「28 文件」与清理集（顶层 20 + kb 8）
  解耦实现
- HG-SEC-104（🟢）：html-gen.py 内部文本 18→28 同步：HELP_PROMPT:771-772、argparse --site help:886、
  cmd_prompt_site docstring:1009、统计文案
- HG-SEC-105（🟢）：§5 注明 _kb-groups.json/_kb-data.json 因 Jekyll _ 前缀规则不会被 Pages 发布
  （预期行为，运行时数据已内联 index.html）

【需求摘要】
CL007 已上线 B 型门户（18 文件）。v2 三动机：① 门户无模板维度导航（HG-SEC-092）；② skills/ 自身文档
未同步 --site（8 篇 SKILL.md 均无 --site 字样，实证）；③ 跨项目复用（http-server.cli 同构）。
目标：/prompts/ 门户改 C 型 knowledge（5 tab = A 表格/B 文档/C 知识库/D 幻灯片/通用 CLI；纵向 =
指令 CLI/模板语法/使用案例 + cli 组 页面规范/测试规范）+ kb/{skill}.html detail 页 ×8 +
_kb-groups.json/_kb-data.json + 两级沉淀（html-gen skills 文档同步 + cli-prompts-site 通用 skill 落库 +
hs 实施 prompt 打印转交）。契约 {skill}.md/.json + all.md 逐字规则不变。

【实施范围】
1. html-gen.py cmd_prompt_site（html-gen.py:1008）扩展：
   - 注册表常量：SKILL_TO_GROUP（8 skills→group/section，§4.2）+ GUIDE_MAP（6 guides，§4.2）+
     CASE_MAP（12 cases，§4.2）+ groups 定义（5 group，§4.1）——随 --site 构建
   - 内存对象增：_kb-groups.json / _kb-data.json（{title,group,section,badge,desc,url,kind}，
     desc：skill=frontmatter description 首行 _skill_desc；guide/case=注册表一句；url 相对门户：
     kb/{skill}.html / ../demos/*.html / ../demos/chaitin/*.html）
   - 流程：内存构建(fail-fast 零写盘) → 清理 known 名（顶层 20 + kb/ 内 8，containment 保留无关文件，
     kb/ mkdir）→ 写 16 md/json + all.md + _kb json → cmd_doc 渲染 8 kb/{skill}.html（Namespace 见
     HG-SEC-100，stdout 抑制）→ cmd_knowledge 渲染 index.html（Namespace 见 HG-SEC-100，stdout 抑制，
     groups=_kb-groups.json、data=_kb-data.json）→ 统计 `[站点] {dir} 已生成: 8 skills (28 文件:
     门户 + kb×8 + md/json×16 + all.md)`
   - 计数文本 18→28 同步（HELP_PROMPT/argparse help/docstring，HG-SEC-104）
2. tests/test_prompt_site.py：
   - test_01 更新：顶层 20（index/_kb-groups/_kb-data/all.md/16）+ kb/ 8；stdout 含 28
   - test_05 重写：门户 DOM = kw-tab/kwSidebar/5 tab 标签（A 表格/B 文档/C 知识库/D 幻灯片/通用 CLI）；
     零 github-corner；home 指向站点
   - 新增 test_11_kb_data_schema / test_12_kb_detail_pages / test_13_contract_unchanged（按 §8）
   - test_06 幂等集更新为 20（17 + _kb-groups + _kb-data + index.html；kb/*.html 排除 doc meta）；
     test_09 扩展 kb 页 env pin（HG-SEC-100）
   - 其余 test_02/03/04/07/08/10 规则不变回归（契约断言保持）
3. 文档同步（§9）：skills/html-gen/SKILL.md（prompt 段补 --site + 门户 5 tab + curl 契约）、
   skills/html-gen-cli-spec/SKILL.md（子命令表补 prompt --site 行）、README.md/README.zh.md
   （在线阅读小节补门户结构 5 tab + kb/）、AGENTS.md（prompts/ 行 28 文件 + kb/ + _kb json；
   prompt 子命令段 18→28）
4. 重跑 `python3 html-gen.py prompt --site`（默认目录）→ 提交产物（28 文件 + kb/）；diff 仅预期文件
5. cli-prompts-site 通用 skill 落库（§10 大纲 7 节，devops 类）→ 打印 hs 实施 prompt 转交
   （含 URL/HTTP-SERVER-CL 编号/验收；不代改 hs）

【提交规范】
- 单 commit：`feat@html-gen: prompt --site v2 C 型门户 + kb detail (HTML-GEN-CL008)`
  （若拆分：代码/测试/文档/产物按项目惯例；禁止混入无关改动）
- 禁止：git push、git checkout -- .、手改 prompts/ 产物（产物由生成器得出）

【完成后报告（必须附证据）】
1. git log --oneline -2 实际输出
2. git status --short 实际输出（应为干净或仅预期文件）
3. `python3 html-gen.py prompt --site --dir /tmp/prompts-verify` 实际输出 + 文件清单（顶层 20 + kb/ 8）
4. 专项测试实际输出：python3 -m pytest tests/test_prompt_site.py tests/test_prompt_cmd.py -q
5. 全量测试：python3 -m pytest tests/ -q -n 4 实际输出（基线 265，预计 ~268）
6. 幂等实测：连续两次 --dir 生成 → 20 确定性文件 diff 为空；kb/*.html 排除
7. 每个新增常量/函数的 grep 证据行（SKILL_TO_GROUP / cmd_prompt_site 改造 / test_11..13）
8. cli-prompts-site skill 落库 + hs 实施 prompt 文本（转交附件）

注：/usr/bin/python3 才是带 pytest 的解释器；后台 shell 会解析到 conda python（无 pytest），
测试必须前台显式 /usr/bin/python3 -m pytest 或本机 python3 验证。
