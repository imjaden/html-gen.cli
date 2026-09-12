# GitHub Issue 反馈通道 skill 沉淀设计 — review 复审报告 v1.1

> 日期: 2026-09-12
> 文件: documents/solutions/github-issue-feedback-skill-design-v1.1-20260912.md（commit b2bf584）
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 待 push commit: 无（CONDITIONAL PASS，不 commit）
> review 维度: 合理性 / 严格性 / 安全性
> 闭环: HTML-GEN-CL011 [2/6] 设计评审复审
> 上一轮: v1.0 报告（CONDITIONAL PASS 90/A，HG-SEC-145..150）

```
┌─ DESIGN REVIEW (re-review) ───────────────────────┐
│  Document: github-issue-feedback-skill-design     │
│  Version : v1.1 (2026-09-12, commit b2bf584)      │
│  Baseline: v1.0 (2026-09-11, commit 3f7e0ad)      │
├───────────────────────────────────────────────────┤
│  合理性   🟢 (0 待确认，决策层 A2-H1 未变)          │
│  严格性   🟡 (1 新遗漏: §4.3 文档面清单仍不完备)    │
│  安全性   🟢 (0 新增风险)                           │
└───────────────────────────────────────────────────┘
```

## 一、逐条核销 HG-SEC-145..150（实测核对，非文字接受）

方法：read_file / search_files / grep 全仓，逐行比对 v1.1 设计引用的 file:line 与源码/测试现状。

| Finding | v1.1 修正主张 | 实测核销 | 结论 |
|:---|:---|:---|:---|
| HG-SEC-145 | §4.2 补列 L239(20→22) / L252(8→9) / L342(26→27)；§6 缓解扩为四处断言 | `tests/test_prompt_site.py` 实测 L239 `assert len(deterministic)==20`、L252 `assert len(...glob('*.html'))==8`、L342 `assert len(items)==26`；v1.1 §4.2 三行及目标值 22/9/27 全部在列；§6（L175）已写「测试兜底四处断言 L109/L239/L252/L342（v1.1 扩）」。L342 的 27 = 9 skill + 6 guide + 12 case 与 GUIDE_MAP(6)/CASE_MAP(12) 实测一致 | ✅ 真实成立 |
| HG-SEC-146 | §4.1 重排三组：28 文件组 4 处 / ×8 组 5 处 / 顶层 20·16·kb8 组 3 处 | `html-gen.py` 实测：A 组 L793(HELP_PROMPT)/L911(argparse)/L1134(docstring)/L1263(注释) 均为「28 文件」；B 组 L1134(×8)/L1138(8 个)/L1207(8 个)/L1234(×8)/L1296(8 个 skills)；C 组 L1137(顶层20+kb/8)/L1202(顶层20+16)/L1219(写16) 均属实。三组归类与行号逐字一致 | ✅ 真实成立 |
| HG-SEC-147 | §4.3 改为「追加 v2.7.0 + 不改写 v2.5.0 历史行」 | `skills/html-gen/SKILL.md` 实测 L314 = 「- v2.5.0 (2026-09-02): …28 文件…」（历史变更记录行）；L63「28 文件」/L69「×8」为当前 spec 正文。v1.1 §4.3 明确「追加新条目、不得改写 v2.5.0、L63/L69 才做 28→31/×8→×9」 | ✅ 真实成立 |
| HG-SEC-148 | §4.3 指定落点：「### 主命令组 (html-gen CLI)」L24 `--feedback-repo` 行之后新增；不新造段 | `features.md` 实测 L24 = `html-gen table --feedback-repo — …` 行；全文章节为 CLI命令/模板功能/数据格式/基础设施/localStorage/项目统计，确无「skills/能力」段。落点具体、不新造段成立 | ✅ 真实成立 |
| HG-SEC-149 | §8 枚举 docstring 4 类 countries + HINT + prog + DEFAULT_CONFIG 无需改 | `scripts/countries-issue-sync.py` 实测：docstring L5 表单模板名 `data-fix-countries.yml`、L19 target 名 `countries`、L25 设计文档名 `countries-issue-feedback-design-v1.4`、L11-18 脚本名 ×8；HINT L302、prog L432、DEFAULT_CONFIG L40（通用路径，无 countries、无 DEFAULT_TARGET） | ✅ 真实成立 |
| HG-SEC-150 | schema 预算放宽 ~130→~200 行（仍 ≤250） | v1.1 §3.1/§3.3 已写 `feedback-targets-schema.md # ~200 行`，合计 ~700 行，每篇 ≤250（E1） | ✅ 真实成立 |

**核销结论**：HG-SEC-145..150 六项修正全部真实成立，非文字接受。v1.1 §0 变更摘要表与 §4/§6/§8 实际修订内容一致。

## 二、独立复检 §4 完备性（新发现）

不因「已按 findings 修正」而放过，独立 grep 全仓「28 文件 / 18 文件 / ×8 / 8 个 skill / 26 条 / 8 篇 / 311」等计数文案与断言，重点复核 README*.md、documents/ 手册、tests/test_prompt_site.py 全文。

### 硬断言面（test_prompt_site.py）— 全覆盖 ✅

§4.2 已列 8 处（L5/L16-19/L109/L179/L239/L252/L309/L342），其中 4 处硬断言 L109/L239/L252/L342 及 L111/L115（EXPECTED_TOP/EXPECTED_KB 由列表派生，自动跟随）全部在列，无遗漏硬断言。第 9 skill 加入后不再有测试红风险。

### 🟡 HG-SEC-151 — §4.3 漏 README「×8 / 8 skills」文案（对外契约，同类于 HG-SEC-146）

§4.3 仅列 `README.zh.md L84「28 文件」→ 31`，但：

1. **README.zh.md 同文件 L95/L96 漏列**：L95 `每 skill doc detail 页（×8）`、L96 `8 skills 全量` 在 skill 8→9 后均须 → ×9 / 9 skills。§4.3 列了该文件的 L84 却漏同表 L95/L96，属「列了文件但枚举不完整」。
2. **README.md（英文）整体漏列**：英文 README 是并行维护的对外文档，L95 `Per-skill doc detail page (×8)`、L96 `All 8 skills in one fetch` 同样需 → ×9 / 9 skills。§4.3 完全未提 README.md。

按 G1 决策「硬编码文案/门户产物构成**对外契约**，不同步即站点缺项或文档失真」，README ×8/8 skills 属公开契约文案。遗漏后实现者照 §4.3 实施会留下公开 README 事实性错误（页面已 9 个 skill，README 仍写 ×8）。§5#6「文档面 7 处同步（§4.3 全表）」主张因此不成立。

**处置建议**：§4.3 增补两处 —— (a) `README.zh.md L95/L96` ×8→×9 / 8 skills→9 skills；(b) 新增 `README.md`（英文）L95/L96 同一替换。同步 §5#6 的「7 处」计数上修。

### 🟢 HG-SEC-152 — handbook 计数文案未覆盖 + 无冻结声明（待确认 scope）

`documents/html-gen-cli-handbook-v1.0-20260908.md`（documents/ 根，非 archive/）含多处 current-state 计数文案，skill 8→9 后漂移：

| 行 | 现状 | 漂移后 |
|:--|:--|:--|
| L43 | 文本/JSON/站点 **28 文件** | 31 |
| L77 | skills/ 现挂载 **8 篇** + references **3 个** | 9 篇 + references 6 个（新 skill 自带 3 references） |
| L95/L96 | `{skill}.md/.json` **×8** | ×9 |
| L107 | `_kb-data.json` **26 条条目（skill×8+guide×6+case×12）** | 27（9+6+12） |
| L108 | `kb/{skill}.html` **×8** | ×9 |
| L169 | 生成 prompts/（**28 文件**） | 31 |
| L227 | 产物布局 `…kb/{skill}.html` **×8** | ×9 |

注：L62（CL008「28 文件」）、L90/101（§5.1/5.2 版本历史标题）为**历史事实**，不应改。

设计 §4.3 未列该 handbook，亦未像 F1（「不写 ops profile」）那样显式声明「handbook 为 2026-09-08 v1.0 快照、本轮冻结不追改」。二者只能取一：补进 §4.3 或显式声明冻结。现为悬空 scope，属「模糊点待确认」。

**处置建议**：ops 二选一并落笔 —— (a) §4.3 增补 handbook 上述 8 处（历史行 L62/L90/101 除外）；或 (b) §1.3 非目标 / §4.3 显式声明「handbook v1.0 为快照，本轮不追改」。

### 🟢 HG-SEC-153 — frontmatter version 既存漂移未注明（非本 delta 引入）

`skills/html-gen/SKILL.md` 实测 frontmatter `version: 2.4.0`（L4），而「## 变更记录」最新为 v2.6.0（L313）—— frontmatter 落后 2 个版本（handbook L269 已记为「frontmatter 2.4.0 vs 变更记录 v2.5.0 版本口径待核」的既存遗留）。设计 §4.3「同步 frontmatter version: 2.7.0」目标值正确，但隐含「当前为 2.6.0」，未注明实际为 2.4.0。属既存漂移（非本轮引入），目标值 2.7.0 不受影响。

**处置建议**：§4.3 附注「frontmatter 现为 2.4.0（既存落后 2 版），直接置 2.7.0」即可，避免实现者困惑。

### 🟢 附注 — test_prompt_site.py 注释/消息串计数文案未逐项枚举（非阻断）

§4.2 已覆盖全部**硬断言**，但测试文件内仍存 4 处**注释/断言消息串**计数文案未逐项列出：L21（`顶层 20 = … + 16 md/json`）、L104（`28 文件 (顶层 20 + kb/ 8)`）、L235-236（`确定性集 20 = 16 md/json…`）、L370（`'8 skill 条目不齐'` 断言消息）。这些不红测试（非断言比较值），但同属 HG-SEC-146 类「计数文案」，实施时会漂移为陈旧注释。建议 §4.2 附注「注释文案同步（L21/L104/L235-236/L370）」或声明「仅正文/断言为契约，注释文案不追改」。

## 三、决策层回归

§2 决策表 A2/B1/C1/D1/E1/F1/G1/H1 与 v1.0 逐项一致，论证未改；v1.1 仅改动 §0（变更摘要）、§3.1/§3.3（行数预算）、§4（改动面清单）、§6（风险缓解）、§8（复用指引），均属「改动面完备性」修正，未触碰决策层。D1（门户归 table 组）与 §4.1 `SKILL_TO_GROUP` +1 项 `'github-issue-feedback': ('table', '指令 CLI')` 自洽；E1 ≤250 行/篇与 §3.1 总预算 ~700 行自洽；G1 与 §4 精确清单意图一致（但见 HG-SEC-151 文档面仍漏）。

## 四、安全事项

与 v1.0 一致：纯文档/skill 沉淀 + 挂载注册，零功能变更（C1 脚本冻结、零模板/渲染/参数语义变更）。无新增注入/越权/敏感信息面。反馈能力安全红线（白名单+主键双层保护 / 入库 `<`/`>` 拒绝 / 显式 pathspec / 写盘前预检 / shell=False）已在 CL009/CL010 落地，本轮仅文档化转述。

🟢 无新增安全风险。

## 五、评分

| 项 | 严重度 | 扣分 |
|:---|:---|:---|
| HG-SEC-145..150（六项核销） | — | 0（已正确修正） |
| HG-SEC-151 §4.3 漏 README ×8/8 skills | 🟡 MEDIUM | -5 |
| HG-SEC-152 handbook scope 待确认 | 🟢 LOW | 0 |
| HG-SEC-153 frontmatter 既存漂移 | 🟢 LOW | 0 |
| test_prompt_site 注释文案未枚举 | 🟢 LOW | 0 |

得分: **95 / 100**

## 六、结论

**CONDITIONAL PASS** — 上一轮 HG-SEC-145..150 六项已全部真实修正（逐行实测核对成立），决策层 A2-H1 未变且自洽，安全面无新增风险。但独立复检在 README*.md 发现 1 处同类 🟡 遗漏（HG-SEC-151：README.zh.md L95/L96 + 英文 README.md 的「×8/8 skills」对外契约文案），「改动面精确清单」§4.3 仍不完备，§5#6「文档面 7 处」主张不成立。需 ops 折入 HG-SEC-151（+ 建议一并处置 HG-SEC-152/153 的待确认项）后复审，或按 🟡 单项补丁后 PASS。

## 七、发现项汇总

| # | 严重度 | 摘要 |
|:--|:--|:--|
| HG-SEC-145..150 | ✅ 已核销 | v1.1 六项修正真实成立 |
| HG-SEC-151 | 🟡 open | §4.3 漏 README.zh.md L95/L96 + 英文 README.md 的 ×8/8 skills 文案 |
| HG-SEC-152 | 🟢 待确认 | handbook current-state 计数文案（28 文件/×8/26 条目/8 篇）未覆盖 + 无冻结声明 |
| HG-SEC-153 | 🟢 record | frontmatter 2.4.0 vs 变更记录 v2.6.0 既存漂移（目标 2.7.0 不受影响） |

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:---|
| □ | §4.3 补 README.zh.md L95/L96 + README.md（英文）L95/L96 ×8→×9 / 8→9 | 严格性 🟡 HG-SEC-151 |
| □ | §5#6「7 处」计数随 HG-SEC-151 上修 | 严格性 🟡 HG-SEC-151 |
| □ | handbook（html-gen-cli-handbook）补进 §4.3 或显式声明冻结 | 🟢 HG-SEC-152 |
| □ | §4.3 附注 frontmatter 现为 2.4.0（置 2.7.0） | 🟢 HG-SEC-153 |
| □ | §4.2 附注 test 文件注释文案同步（L21/L104/L235-236/L370）或声明不追改 | 🟢 附注 |
