# html-gen prompt 在线阅读站点 v2 设计 — review报告 v1.0

> 日期: 2026-09-02
> 文件: documents/solutions/html-gen-prompts-site-v2-design-v1.0-20260902.md
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 待 push commit: 456a12c（docs@html-gen: prompt 在线阅读站点 v2 设计 (C型门户+体系化沉淀) · HTML-GEN-CL008，kind=independent）
> review维度: 合理性 / 严格性 / 安全性
> 前置: CL007 设计评审 PASS 85/A（documents/review/html-gen-prompts-site-design-review-v1.0-20260902.md）

## 数据验证

| # | 验证项 | 方法 | 结果 |
|:-:|:-------|:-----|:-----|
| 1 | 8 skills 与 SKILL_TO_GROUP 一致 | `ls skills/` | ✅ 8/8：html-gen / html-gen-cli-spec / html-gen-doc / html-gen-knowledge / html-gen-slide / html-gen-table / pages-index / test-speed-optimization |
| 2 | 动机②「skills 无 --site 文档」缺口真实 | `rg "prompt --site\|--site\|在线阅读站点" skills/` | ✅ 0 命中——8 篇 SKILL.md 均未提 --site（html-gen / cli-spec 确为 CL004 时代文本），§9 同步必要性成立 |
| 3 | GUIDE_MAP 6 guides 文件存在 | `ls demos/*.html` | ✅ usage/table/doc/knowledge/slide-guide + markdown-spec 6/6 |
| 4 | CASE_MAP 12 案例文件存在 | `ls demos demos/chaitin demos/cloudwise` | ✅ 根级 9 + chaitin/company-profile.html + chaitin/business-model.html + cloudwise/company-profile.html 12/12 |
| 5 | knowledge 渲染是否注入时间戳 | read html-gen.py:529-580 (cmd_knowledge) | ✅ 无——inject 仅 title/subtitle/welcome/groups/items/corner/home/favicon 固定字段；layout-knowledge 模板静态 → index.html 字节确定，幂等集 20 成立（17+2 _kb+index） |
| 6 | doc meta 分钟粒度注入 | read html-gen.py:364-369 (cmd_doc) | ✅ `创建/编辑 {st_ctime/st_mtime} %Y-%m-%d %H:%M` → kb/*.html 排除幂等集正确（HG-SEC-086 同类） |
| 7 | C 型 url vs desc 实际优先级 | read layout-knowledge.html:396-398 | ✅ **url 优先**（if item.url → iframe；else if item.desc → 内联）；§6 全条目带 url → desc 实际不渲染（见 🟢 HG-SEC-101） |
| 8 | iframe 双 chrome 模板机制 | read layout-knowledge.html:396 | ✅ C 型选择条目时自动追加 `?sidebar=0&toolbar=0&t=`（doc 裸模式）——§6/§12 的预演风险已被模板层机制大幅化解，仅剩视觉抽查 |
| 9 | cmd_knowledge 直调字段契约 | read cmd_knowledge:532-568 + parser:869-881 | ⚠️ 直调必需 `data/groups/output/title/subtitle/welcome`（subtitle/output 为**直接属性访问**非 getattr）+ corner/favicon getattr 兜底（见 🟡 HG-SEC-100） |
| 10 | 全量测试当前数 | `python3 -m pytest tests/ --collect-only -q` | ✅ **265 tests**（0.12s collect），§8「265 → +3 ~ 268」精确 |
| 11 | 现有 test 编号与 §8 回归引用 | read tests/test_prompt_site.py | ✅ test_01..10 齐；test_07/09/10 语义 = 互斥/env-set/--dir 守卫，引用正确 |
| 12 | hs 移植清单锚点 | 实测 http-server.cli | ✅ `src/http_server_cli/cli.py:686 def _cmd_prompt(manager, args)` **存在且同名**（§10 item6 参考点精确）；skills/ 6/6 含 SKILL.md；CNAME=`http-server.cli.jaden.tech` ✅；HTTP-SERVER-CLNNN 编号体系在 cache/review-prep 实证 |
| 13 | 12 决策完整性 | 读 §2 决策表 | ✅ A1 B1+B3 C1 D1 E1+E2 F1 G1 G1a-1 G1b-1 H1 I1 J1 K-1 L-1 全部在表，与探讨记录一致 |
| 14 | 文件命名 / commit 格式 | 目检 + git log | ✅ `html-gen-prompts-site-v2-design-v1.0-20260902.md` kebab-case v1.0；`docs@html-gen: ... (HTML-GEN-CL008)` 符合项目惯例 |

## 合理性评估

| # | 项 | 评级 | 说明 |
|:-:|:---|:----:|:-----|
| 1 | 三动机覆盖 | ✅ | 动机①（门户 IA）→ §4/§5/§6/§7 F1 G1 H1 I1；动机②（沉淀缺口）→ §9 skills 同步，缺口实证（数据验证 #2）；动机③（跨项目）→ §10 cli-prompts-site + C1 转交。全覆盖无遗漏 |
| 2 | 12 决策跨节一致 | ✅ | §2 → §4（F1/G1/G1a/G1b/注册表）、§5（E1+E2/K-1/D1）、§6（H1 内容规格）、§7（I1 流程）、§9（A1 内部层）、§10（B1+B3/L-1）、§11（C1 转交）映射无矛盾 |
| 3 | C 型 IA 能力内 | ✅ | 横向 5 group（renderTabs 实测支持多 tab）/ 纵向 section（renderSidebar 按 section 分组）/ badge（含未知 badge 灰底 fallback）/ url iframe 均在 layout-knowledge 现成能力内；无模板改动约束满足 |
| 4 | 5 tab 与产品体系对齐 | ✅ | A/B/C/D 四模板 + 通用 CLI（base html-gen 归 CLI 指令维）划分语义自洽；cli 组 section 集（指令 CLI/页面规范/测试规范）与素材一致 |
| 5 | 条目混合设计 | ✅ | skill（badge Prompt，detail 页 iframe）+ guide（指南）+ case（案例）三源混合符合 G1「skill detail+guide+案例」目标；知识库无 desc-only 条目 → 全部走 iframe，规避 desc 内联样式差 |
| 6 | section 排序机制 | 🟢 HG-SEC-102 | layout-knowledge 侧栏**按数据数组内 section 首现顺序**渲染（Object.keys(sections) 保留首现序）；§4.2 只给目标序未给实现约束——生成器须按 SKILL_TO_GROUP → GUIDE_MAP → CASE_MAP 类别序 append（组间交错不影响组内序，因按 group 过滤后保序），否则 cli 组「指令 CLI→页面规范→测试规范」会被打乱 |
| 7 | desc 字段语义 | 🟢 HG-SEC-101 | §6 定义全条目 desc，但 url 优先（数据验证 #7）→ desc 在门户 UI 永不展示；§6 未说明 desc 定位，易误读为「门户显示摘要」 |

## 严格性评估

| # | 项 | 评级 | 说明 |
|:-:|:---|:----:|:-----|
| 1 | 幂等集 20 | ✅ | 数据验证 #5/#6：knowledge 路径零时间戳 → index 确定性成立，17+2+1=20 byte-identical 断言可执行；kb/*.html 排除理由充分（doc meta 分钟粒度，HG-SEC-086 先例） |
| 2 | 契约逐字保留 | ✅ | E1+E2：{skill}.md/.json 生成规则不变（strip+refs / 信封），all.md 规则不变；test_13 显式标注「契约不变」回归；test_01/05 断言变更已文档化（§8 + §12） |
| 3 | known 清理集 containment | ✅ | 28 = 原 18 + _kb-groups.json + _kb-data.json + kb/{skill}.html×8，语义 HG-SEC-088/096 延续；被删/改名 skill 旧产物残留策略沿用（git 跟踪 + 人工），§12 已记录 |
| 4 | §7 直调 Namespace 契约 | 🟡 HG-SEC-100 | cmd_knowledge 的 `subtitle`/`output` 为直接属性访问：§7 step5 字面清单（data/groups/output/title/欢迎语/quiet/github_url）**缺 subtitle → AttributeError**；缺 home_url → corner_args env 兜底 → **test_09（env-set 不变回归）必红**（evil HOME_URL 注入 index）；§7 step4 的 kb 8 页 cmd_doc 未 pin github/home → 操作机设 env 时 8 个 commit 页被注入角落/首页（HG-SEC-090/097 同风险类，新 8 页未覆盖）；title/welcome 具体文案未定（w-title 欢迎面板显示 📚+title，缺省会落「知识库」通用文案） |
| 5 | kb/ 目录与清理细节 | 🟢 HG-SEC-103 | cmd_doc 写 `out_dir/kb/*.html` 前需 `kb/` mkdir（cmd_doc 自身不建父目录，write_text 直接失败）；现有清理循环 `out_dir.iterdir()` 只扫顶层，kb/{skill}.html 需对 kb/ 内**已知名**再循环（containment 同语义）；step5 cmd_knowledge quiet 分支会打印「✅ 已生成」一行 → 需 redirect_stdout（同 step4），否则 `--quiet 仅打印路径` 语义破坏；统计文案 28 与清理集（顶层 20）需解耦实现 |
| 6 | 代码内计数同步 | 🟢 HG-SEC-104 | §9 文档同步漏 html-gen.py 内部文本：HELP_PROMPT:771-772「(18 文件)」、argparse `--site` help:886「(18 文件)」、cmd_prompt_site docstring:1009「(18 文件)」、统计旧文案——均须 18→28（HG-SEC-094 先例同型） |
| 7 | 测试充分性 | ✅ | test_11 schema/url 存在性防注册表漂移、test_12 kb detail、test_13 契约、幂等 20、互斥/守卫/env-set 回归、计数 265→268——覆盖充分；**无 Selenium iframe 用例可接受**：C 型 iframe 加载路径已被既有 knowledge/drama Selenium 覆盖（drama-knowledge 等），test_11 Path 断言兜住 url 漂移，验收 #8 含 iframe 视觉抽查 |
| 8 | _kb json 发布推论 | 🟢 HG-SEC-105 | _ 前缀文件被 Jekyll 忽略 → Pages 上 /prompts/_kb-*.json 将 404（与「非 curl 契约」一致；运行时数据已内联 index.html）；建议 §5 加一句明示，防未来误作外部数据源 |

## 安全事项

- **无注入路径**：新增数据全部来自生成器内置注册表常量 + 项目受控 skills/*/SKILL.md；GROUPS/ITEMS 经 `json.dumps` 注入 `<script>`，title/badge/section 均为受控值且 title 走 textContent 渲染；desc 因全条目带 url 永不进入 innerHTML（即使含 `<` 也不构成渲染面）。✅
- **无凭据/无第三方依赖**：零新依赖、无 API key、无 CDN 变更。✅
- **清理 containment**：known-name 语义延续（HG-SEC-088/096），--dir 空串/仓库根守卫已存在（test_10 回归）；误删面未扩大（kb/ 内亦只删已知名）。✅

🟡 HG-SEC-100 — §7 直调 Namespace 契约不完整 + kb detail env pin 缺失（严格性/安全性）

`cmd_knowledge` 对 `subtitle`/`output` 是直接属性访问（html-gen.py:558/564，非 getattr），`corner_args`/`favicon_args` 对缺失属性走 env 兜底。设计 §7 step5 字面字段清单缺 `subtitle`/`home_url`：按字面实施 → step5 AttributeError；即便补 subtitle，缺 home_url 时 §8「test_09 env-set 不变回归」必失败（测试设 `HTML_GEN_HOME_URL=evil`，Namespace 无 home_url → env 注入 index）。同理 step4 的 8 个 kb detail 页未声明 github/home pin——操作机若设 `HTML_GEN_GITHUB_URL`/`HTML_GEN_HOME_URL`/`HTML_GEN_FAVICON`（本工具自身文档化特性），8 个 commit 入库页被环境注入角落/入口/favicon，与「隐私默认不带」意图相悖，且跨环境产物不确定。

修复建议：§7 显式给出两处完整 Namespace 字段清单：
- step4 cmd_doc：`input={skill}.md、output=kb/{skill}.html、title=skill 名、subtitle=None、quiet=True、github_url=''、home_url=''`（favicon 不传沿用默认注入，与 CL007 index 行为一致）；
- step5 cmd_knowledge：`data/groups/output/title/welcome/subtitle=None/quiet=True/github_url=''/home_url='https://html-gen.cli.jaden.tech/'`；
- 补 title/welcome 具体文案（如 title="html-gen Prompt 站点"，welcome 门户引导语）；test_09 扩展：对 8 个 kb detail 页同样断言零 github-corner、零 env 污染。

## 评分

| 扣分项 | 严重度 | 分值 |
|:-------|:------:|:----:|
| HG-SEC-100 §7 Namespace 契约不完整 + kb env pin 缺失 | 🟡 | -5 |
| HG-SEC-101..105（5 项） | 🟢 | 0（记录） |

得分: 100 - 5 = **95 / 100 → A**

## 结论

**PASS（95/A，通过）** — 架构正确：三动机完整落地、C 型 IA 全部在 layout-knowledge 现成能力内（url 优先/自动裸模式 iframe 已核实）、注册表与素材零漂移（12/12 案例、6/6 指南、8/8 skills 实证存在）、幂等集 20 成立（knowledge 无 meta 注入实证）、hs 移植锚点全部实测命中（cli.py:686 _cmd_prompt / 6 skills / CNAME / CL 编号体系）。无 🔴 阻断项。唯一 🟡（HG-SEC-100）为直调 Namespace 契约完整性 + kb detail env pin，属实现前规格订正，折叠进 dev 实施即可，不阻塞开工。评审通过后由 dev role 按设计文档实施，折叠项以 D-item 编号折入对应实现步。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | HG-SEC-100 §7 补两处完整 Namespace（subtitle/home_url/github_url 显式 + title/welcome 文案）；test_09 扩展 kb 页 env pin 断言 | 严格性 🟡 |
| □ | HG-SEC-101 §6 写明 desc 为注册表元数据（url 条目下门户 UI 不渲染，供 desc-only/未来用途） | 文档 🟢 |
| □ | HG-SEC-102 §4.2 补生成器 append 序约束（SKILL_TO_GROUP → GUIDE_MAP → CASE_MAP；模板按 section 首现序渲染） | 文档 🟢 |
| □ | HG-SEC-103 §7 流程补 kb/ mkdir、kb 内 known 名清理、step5 stdout 抑制、统计 28 与清理集解耦 | 实现 🟢 |
| □ | HG-SEC-104 补 html-gen.py 内部文本 18→28 同步（HELP_PROMPT/argparse help/cmd_prompt_site docstring） | 文档 🟢 |
| □ | HG-SEC-105 §5 注明 _kb json 因 Jekyll _ 前缀规则不发布（预期，数据已内联）；Selenium iframe 交互为可选增强非必需 | 文档 🟢 |
