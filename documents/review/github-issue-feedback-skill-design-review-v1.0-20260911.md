# GitHub Issue 反馈通道 skill 沉淀设计 — review报告 v1.0

> 日期: 2026-09-11
> 文件: documents/solutions/github-issue-feedback-skill-design-v1.0-20260911.md
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 待 push commit: 无（CONDITIONAL PASS，不 commit）
> review维度: 合理性 / 严格性 / 安全性
> 闭环: HTML-GEN-CL011 [2/6] 设计评审

```
┌─ DESIGN REVIEW ────────────────────────────────────┐
│  Document: github-issue-feedback-skill-design v1.0 │
│  Version : v1.0 (2026-09-11)                        │
│  Commit  : 3f7e0ad (设计文档基线)                    │
├─────────────────────────────────────────────────────┤
│  合理性   🟢 (0 个待确认)                            │
│  严格性   🟡 (2 个遗漏: 改动面清单不完备)             │
│  安全性   🟢 (0 个未覆盖点)                          │
└─────────────────────────────────────────────────────┘
```

## 数据验证

逐锚点核对设计文档引用 file:line 与源码现状（方法：read_file / search_files / wc -l / git）。

| 验证项 | 方法 | 结果 |
|:-------|:-----|:-----|
| `cmd_prompt` L928-1030（SKILL.md + references 拼接 + --brief/--json） | read_file | ✅ 已确认 L928-1030，行为与设计描述一致 |
| `SITE_GROUPS` L1038-1044（5 tab） | read_file | ✅ 已确认 5 组 table/doc/knowledge/slide/cli |
| `SKILL_TO_GROUP` L1046-1055（8 项） | read_file | ✅ 已确认 8 项，含 pages-index(页面规范)/test-speed-optimization(测试规范) |
| `_site_kb_items` L1106-1130 | read_file | ✅ 已确认 skill/guide/case 三 kind，badge Prompt/指南/案例 |
| `cmd_prompt_site` L1133-1269 | read_file | ✅ 已确认（含 --dir 守卫、containment 清理、内存 fail-fast） |
| `n_total = len(skills)*3 + 4` L1264（动态计数） | read_file | ✅ 已确认动态计算，9 skill → 31 文件，无需改 |
| `_site_all_md` L1293-1299（all.md 头部） | read_file | ✅ 已确认 L1296「项目 8 个 skills prompt」硬编码 |
| 硬编码「28 文件」位置 | grep | ✅ 已确认 3 处用户可见 L793/L911/L1134；**另有 1 处注释 L1263（设计漏列/误分类，见 HG-SEC-146）** |
| 注释「×8 / 8 个」位置 | grep | ✅ L1138/L1207/L1234/L1296 确认；**L1134 同含 ×8（设计漏列）；L1137/L1202/L1219 含「顶层 20 / 16 md/json / kb 8」（设计漏列）** |
| `EXPECTED_SKILLS` L16-19 / `EXPECTED_TOP` L22-24 / `EXPECTED_KB` L25 | read_file | ✅ 已确认，8 skill 清单 |
| 「28 文件」断言 L109 / 「8 个 ## 段」L179 / 「8 个 kb detail」L309 | read_file | ✅ 已确认（L109 为硬断言，L179/L309 为注释） |
| **test 未列硬断言 L239/L252/L342** | read_file | ❌ **3 处硬断言设计 §4.2 遗漏，将致测试红（见 HG-SEC-145）** |
| `AGENTS.md:58`「18 文件」过期值 | read_file | ✅ 已确认现存「18 文件」，实际当前为 28（既存漂移属实，顺带修复合理） |
| `skills/html-gen/SKILL.md` L63/69/314 | read_file | ✅ L63「28 文件」/ L69「×8」确认；**L314 为变更记录历史条目（见 HG-SEC-147）** |
| `skills/html-gen-cli-spec/SKILL.md:35`「站点 (28 文件)」 | read_file | ✅ 已确认 |
| `README.zh.md:84`「站点（28 文件）」 | read_file | ✅ 已确认 |
| `features.md` 是否存在「skills/能力段」 | grep '^#' | ❌ **无此段（见 HG-SEC-148）**；L24 已有 --feedback-repo 条目，L261 CLI 计数 7 |
| `skills/` 现状 8 个 skill | ls | ✅ 已确认 8 目录；references 长度分布 36~91 行 |
| 跨项目 prompt 先例 `table-demo-prompt.md` | wc -l | ✅ 36 行（远短于拟写 ~220 行 adoption-prompt，见 HG-SEC-150） |
| 反馈四件套（页面/表单/配置/脚本） | read_file/grep | ✅ 全确认：layout-table.html L357-360 FB_CFG + L1124-1126 ✏️；html-gen.py L134-149 三级取值 + L524-525 调用 + L893 参数；data-fix-countries.yml 84 行（dropdown 15 项 + textarea + 主键/匹配键/videos 不入下拉）；feedback-targets.yaml 71 行全字段；countries-issue-sync.py 600 行 |
| CL010 入库 `<`/`>` 拒绝 | read_file | ✅ 已确认 L262-264 `if '<' in new or '>' in new: skips.append(...拒绝)` |
| C1「改 3 处」脚本 countries 硬编码位置 | grep 'countries' | ✅ 已确认仅 docstring(L5-25/93)/HINT(L302)/prog(L432) 三处；DEFAULT_CONFIG(L40) 为通用路径；**无 DEFAULT_TARGET 硬编码**。位置正确，但 docstring 含 4 种形态（见 HG-SEC-149） |

## 合理性评估

设计决策 A2-H1 逐项核对，全部自洽、有据：

| # | 项 | 评估 |
|:-:|:---|:---|
| REA-1 | A2 命名 `github-issue-feedback`（不带 html-gen- 前缀） | ✅ 与先例 pages-index / test-speed-optimization 一致，跨项目语义中性 |
| REA-2 | B1 SKILL.md + 3 references | ✅ 「可复制」是核心价值，可整体转交的接入 prompt 必要 |
| REA-3 | C1 脚本冻结仅文档化 | ✅ 改名波及 37 测试用例 + 文档，风险不对称，另立闭环合理 |
| REA-4 | D1 门户归 table 组「指令 CLI」 | ✅ 能力 table 专属（✏️ + --feedback-repo 均 table-only）；(group, section) 语义成立：group=5 tab 之一，section=组内 skill 分类；复用既有 tab 不触发门户结构变更（§1.3 非目标） |
| REA-5 | E1 references 全量进 prompt + 单篇 ≤250 行 | ✅ 与 cmd_prompt L1024-1030 拼接行为一致；行数预算可实现（详见 HG-SEC-150 可行性注记） |
| REA-6 | F1 仅项目 skills，不写 ops profile | ✅ 单一事实源，避免双份漂移 |
| REA-7 | G1 测试文档全量同步 | ✅ 意图正确；但 §4.2 清单不完备（HG-SEC-145），实现后 §5.4 不可达 |
| REA-8 | H1 独立立项 CL011 | ✅ CL010 已入审计阶段，scope 隔离合理 |

**合理性结论**：决策层零偏差，架构分解自然，目标/非目标边界清晰，与上游 CL009/CL010 现状衔接正确。🟢

## 严格性评估

| # | 项 | 评估 |
|:-:|:---|:---|
| RIG-1 | §4.2 测试同步清单完备性 | ❌ **遗漏 3 处硬断言（HG-SEC-145）** |
| RIG-2 | §4.1 代码硬编码计数清单完备性 | ❌ **5 处注释遗漏 + 1 处误分类（HG-SEC-146）** |
| RIG-3 | 验收 §5 八项可判定性 | 🟡 依赖 RIG-1/RIG-2 修复后可达；「31 文件」与门户条目判定明确 |
| RIG-4 | 单篇行数预算可执行性 | 🟢 可达（详见 HG-SEC-150） |

**严格性结论**：决策完备、验收口径清晰，但「改动面精确清单」§4 存在真实遗漏，尤其测试断言面会直接击穿 §5.4「测试全绿」验收。🟡

## 安全事项

本设计为纯文档/skill 沉淀 + 挂载注册，零功能变更，无注入/越权/敏感信息面。反馈能力的安全红线（白名单+主键双层保护 / 入库 `<`/`>` 拒绝 / 显式 pathspec / 写盘前预检 / shell=False）在 CL009/CL010 已落地并经审计，本轮仅文档化转述，不引入新攻击面。

🟢 SEC-145 — 无新增安全风险

本设计不引入执行路径变更（C1 脚本冻结、零模板/渲染/参数语义变更），skill 正文为 markdown 文档（经 `html-gen prompt` / `--site` 前端渲染时走既有 frontmatter 剥离与 textContent/HTML 转义路径），无新增注入向量。

## 评分

| 项 | 严重度 | 扣分 |
|:---|:---|:---|
| HG-SEC-145 §4.2 遗漏 3 处硬断言 | 🟡 MEDIUM | -5 |
| HG-SEC-146 §4.1 计数注释清单不完整+误分类 | 🟡 MEDIUM | -5 |
| HG-SEC-147~150（4 项） | 🟢 LOW | 0 |

得分: 90 / 100

## 结论

**CONDITIONAL PASS** — 设计决策层（A2-H1）全部成立、自洽，架构合理，安全面无新增风险。但「改动面精确清单」§4 存在两处真实遗漏（2 🟡），其中 §4.2 漏列 3 处硬测试断言将直接导致 §5.4「测试全绿」验收不可达，属阻断性 completeness gap，需 ops 修正 §4 后再进 [3/6] 实现（或复审）。

## 发现项

### 🟡 HG-SEC-145 — §4.2 测试同步清单遗漏 3 处硬断言（阻断 §5.4）

设计 §4.2 仅列「L5 docstring / L16-19 EXPECTED_SKILLS / L109 28→31 / L179 8→9 / L309 8→9」。实测 `tests/test_prompt_site.py` 另有 3 处**硬断言**未列，第 9 个 skill 加入后必红：

| 行 | 现状 | 需改 |
|:-:|:---|:---|
| L239 | `assert len(deterministic) == 20` | → `22`（EXPECTED_TOP 由 4+8×2=20 变 4+9×2=22） |
| L252 | `assert len(list((d/'kb').glob('*.html'))) == 8` | → `9` |
| L342 | `assert len(items) == 26` | → `27`（8 skill + 6 guide + 12 case = 26 → 9+6+12=27） |

设计的「28→31、8→9」措辞未覆盖「20→22 / 26→27」两个量级；§6 风险缓解仅引 L109 一处断言兜底，未覆盖上述 3 处。

**处置建议**：§4.2 显式补列 L239（20→22）、L252（8→9）、L342（26→27）三行及目标值；§6 风险缓解第一行把「L109 断言统计行」扩为「L109/L239/L252/L342 四处断言」。

### 🟡 HG-SEC-146 — §4.1 代码硬编码计数清单不完整 + 一处误分类

设计 §4.1 三行分类与实测不符：

1. **L1263 误分类**：`# 统计「28 文件」与清理集解耦...` 是「28 文件」注释，非「×8/8个」。应归入「28→31」组（第 4 处 28 文件）。
2. **L1134 遗漏 ×8**：docstring「(28 文件): ... kb/{skill}.html ×8」同时含 28 文件 **和** ×8，设计仅列于 28 文件组，遗漏 ×8→×9。
3. **漏列 3 处「顶层 20 / 16 md/json / kb 8」注释**：L1137「(顶层 20 + kb/ 8...)」、L1202「# 顶层 20 = ... + 16 md/json」、L1219「# ── 写 16 md/json ...」。skill 8→9 后这些应同步为 22 / 18 / 9，否则注释与 §4.4「顶层 22」叙事自相矛盾。

**处置建议**：§4.1 补齐：28 文件组 = L793/L911/L1134/L1263；×8/8个 组 = L1134(×8)/L1138/L1207/L1234/L1296；新增「顶层 20→22、16→18、kb/8→9」组 = L1137/L1202/L1219。

### 🟢 HG-SEC-147 — SKILL.md L314 为历史变更记录，勿改写

`skills/html-gen/SKILL.md:314` 位于「变更记录」，是 v2.5.0（2026-09-02）的历史条目「prompts/ 在线阅读站点 28 文件...」。§4.3 指示「28→31」会改写历史事实。应改为**追加**新变更记录条目（v2.7.0，CL011 skill 沉淀），L63/L69 才是当前 spec 正文（这两处 28→31 / ×8→×9 正确）。

### 🟢 HG-SEC-148 — features.md「skills/能力段」悬空引用

`features.md` 章节实测为：CLI命令 / 模板功能 / 数据格式 / 基础设施 / localStorage命名空间 / 项目统计，**无「skills」或「能力」段**。§4.3 的「加在 skills/能力段」无可落点。建议指定具体位置：在「### 主命令组」表 L24（--feedback-repo 行）附近新增一条「GitHub Issue 反馈通道 skill 沉淀（github-issue-feedback，挂载 html-gen prompt/--site）」能力行，或新建「### skills」子节。

### 🟢 HG-SEC-149 — C1「改 3 处」措辞未覆盖 docstring 全形态

实测 `countries` 硬编码确为 3 位置（docstring/HINT/prog，无 DEFAULT_TARGET），C1 定位正确。但 docstring 内「countries」有 **4 种形态**：脚本名（×8）、表单模板名 `data-fix-countries.yml`（L5）、target 名 `countries`（L19）、设计文档名 `countries-issue-feedback-design-v1.4`（L25）。§8「改 3 处（替换脚本名）」仅提脚本名，下游照做会漏改表单模板名/target 名 → `--check-template` 破。adoption-prompt（①）应逐项枚举这 4 类替换。

### 🟢 HG-SEC-150 — 全文输出量级提示（非阻断）

拟写 skill 全文约 630 行（180 + 220 + 130 + 100），约为现有最大 skill（html-gen-slide 365 行）1.7 倍；adoption-prompt ~220 行是既有先例 table-demo-prompt.md（36 行）的 6 倍。E1 ≤250/篇可达，但 `feedback-targets-schema.md`（~130 行）承载 20 字段 + 10 步校验链 + 10 态 CLI + 5 红线偏紧，建议放宽至 200+ 行（仍在 ≤250 内）。超长内容按 §3.4 红线改指路设计文档。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | §4.2 补列 L239(20→22)/L252(8→9)/L342(26→27) 三处硬断言 | 严格性 🟡 HG-SEC-145 |
| □ | §4.1 补 28 文件 L1263 + ×8 L1134 + 顶层20/16/kb8 L1137/L1202/L1219 | 严格性 🟡 HG-SEC-146 |
| □ | L314 改「追加新变更记录条目」而非改写历史 | 🟢 HG-SEC-147 |
| □ | features.md 指定 skill 沉淀条目的具体落点 | 🟢 HG-SEC-148 |
| □ | adoption-prompt 枚举 docstring 4 类 countries 替换 | 🟢 HG-SEC-149 |
| □ | schema 参考行数预算放宽至 ~200 行 | 🟢 HG-SEC-150 |
