# GitHub Issue 反馈通道 skill 沉淀设计 — review 复审报告 v1.2（re-review2）

> 日期: 2026-09-12
> 文件: documents/solutions/github-issue-feedback-skill-design-v1.2-20260912.md（commit c76542a）
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> review 维度: 合理性 / 严格性 / 安全性
> 闭环: HTML-GEN-CL011 [2/6] 设计评审第二轮复审
> 上一轮: v1.1 报告（CONDITIONAL PASS 95/A，HG-SEC-151..153 + 附注）

```
┌─ DESIGN REVIEW (re-review2) ─────────────────────┐
│  Document: github-issue-feedback-skill-design    │
│  Version : v1.2 (2026-09-12, commit c76542a)     │
│  Baseline: v1.1 (b2bf584) → v1.0 (3f7e0ad)       │
├──────────────────────────────────────────────────┤
│  合理性   🟢 (决策层 A2-H1 未变且自洽)            │
│  严格性   🟢 (151..153 全闭环; 1 🟢 新记录)       │
│  安全性   🟢 (0 新增风险)                         │
└──────────────────────────────────────────────────┘
```

## 一、逐条核销 HG-SEC-151..153 + 附注 + 自查补漏（实测核对，非文字接受）

方法：read_file / search_files / rg 全仓，逐行比对 v1.2 §4 引用的 file:line 与源码/测试/文档现状。

| Finding | v1.2 处置主张 | 实测核对 | 结论 |
|:---|:---|:---|:---|
| HG-SEC-151 (🟡) | §4.3 新增「README 双源」组（6 行：README.md 英文 + README.zh.md × L84/L95/L96） | `README.md` L84 `Generate the prompts/ site (28 files)` / L95 `Per-skill doc detail page (×8)` / L96 `All 8 skills in one fetch`；`README.zh.md` L84 `生成 prompts/ 站点（28 文件）` / L95 `每 skill doc detail 页（×8）` / L96 `8 skills 全量`——两文件 6 行均实测存在，§4.3 L125/L126 目标值 31 / ×9 / 9 skills 正确 | ✅ 真实成立 |
| HG-SEC-152 (🟢) | 折入 §4.3（非冻结），handbook 15 行清单；依据先例 CL009 `1b1ac53` 同 commit 更新 handbook | handbook（`documents/html-gen-cli-handbook-v1.0-20260908.md`）L43/L64/L77/L95/L96/L101/L107/L108/L109/L169/L204/L227/L262/L266/L273 共 15 行均实测存在且行号精确；先例 `git show 1b1ac53` 证实该 commit 确为 CL009 `feat@table` 且改动该 handbook（2 行） | ✅ 真实成立 |
| HG-SEC-153 (🟢) | §4.3 frontmatter 附注 `2.4.0 → 2.7.0`（落后变更记录 v2.6.0 两版） | `skills/html-gen/SKILL.md` L4 `version: 2.4.0`，变更记录最新 L313 `v2.6.0`——落后 2 版（2.4.0→2.5.0→2.6.0）属实，目标 2.7.0 正确 | ✅ 真实成立 |
| 附注 (🟢) | §4.2 B 组「注释与消息串」6 行 | `tests/test_prompt_site.py` L5 docstring / L21 / L104 / L235-236 / L179 / L309 / L370 均实测存在；L370 `'8 skill 条目不齐'` 为断言消息串，L179/L309 实为注释（B 组标题「注释与消息串」已涵盖，分类无实质影响） | ✅ 真实成立 |
| 自查补漏 | `skills/html-gen/SKILL.md:70`（×16→×18）+ `pages-content-handbook:32`（268→311） | SKILL.md L70 `prompts/{skill}.md / .json ×16`；`documents/pages-content-handbook-v1.0-20260908.md` L32 `现仓 268 collected`——均实测存在 | ✅ 真实成立 |

**核销结论**：HG-SEC-151/152/153 + 附注 + 自查补漏 五项全部真实成立，非文字接受。v1.2 §0 变更摘要表与 §4.2/§4.3 实际修订内容一致。

## 二、独立复跑「穷举」扫描

不因「已按 findings 修正」而放过，独立 rg 全仓（排除 `.git/ cache/ demos/ data/ prompts/ documents/review/ documents/archive/`），模式扩为 `28 文件|28 files|×8|×16|×18|×9|8 skills|9 skills|8 篇|9 篇|26 条|27 条|顶层 20|顶层 22|16 md/json|18 md/json|kb/ 8|kb/ 9|268|311|18 文件|31 文件|31 files|288`。

### 覆盖判定（§4.1 / §4.2 / §4.3 逐条比对）

- **§4.1 代码**：L793/L911/L1134/L1263（28 文件组）、L1134(×8)/L1138/L1207/L1234/L1296（×8 组）、L1137/L1202/L1219（顶层 20·16·kb8 组）、L1046-1055 `SKILL_TO_GROUP` 8 项、L1264/L1268-1269（动态无需改）——全仓 grep 与 read_file 逐字一致，无遗漏。
- **§4.2 测试**：test_prompt_site.py 4 处硬断言（L109/L239/L252/L342）+ 派生断言（EXPECTED_TOP/EXPECTED_KB）+ B 组 7 处注释/消息串；test_prompt_cmd.py L21-24 抽样断言——全部在列。
- **§4.3 文档**：AGENTS.md L58 + 目录结构段 / features.md L24 / skills 2 篇 / README 双源 6 行 / 两 handbook 16 行——全部在列。

### 🟢 HG-SEC-154 — AGENTS.md L326「288 tests」现行状态计数漂移未同步（新发现，穷举遗漏）

独立扫描发现一处 §4.3 未覆盖的现行状态计数：

| 位置 | 现状 | 实际 | 归属 |
|:---|:---|:---|:---|
| `AGENTS.md:326` | `├── tests/  # Selenium + 回归测试 (288 tests)` | 实测 311（`pytest --collect-only` = 311 collected） | 现行状态断言（目录结构段） |

设计 §4.3 已对 AGENTS.md 动手两处（L58「18 文件→31」+ L327 附近 skills 清单），并已决定同步测试计数（§4.3 L128 handbook L64「268→311」、L141 pages-content「268→311」），但 AGENTS.md 目录结构段的「288 tests」（同为测试计数，只是既存漂移值不同：handbook 记 268、AGENTS.md 记 288）未列入。按 §0 自定规则「现行状态断言（如 pytest 268）→ 纳入本轮同步」，属「全仓 grep 穷举」主张的一处遗漏（设计 grep 模式含「268」但无「288」，故 handbook 被捕获而 AGENTS.md 漏网）。

**判定**：🟢 LOW（既存漂移、dev-facing 非对外契约、非阻塞、非本轮 delta 引入）。处置建议：§4.3 增一行「`AGENTS.md` L326 `288 tests` → `311`」，随 [3/6] 一并同步，避免 AGENTS.md 出现 L299「311」与 L326「288」自相矛盾。

### 范围外观察（不计入 finding，供 ops 知悉）

- `AGENTS.md:299`「311 tests（31 文件；…）」中「31 文件」为测试文件数，实测 `tests/test_*.py` 30 个（off-by-one，既存误差，非 CL011 引入）；且与设计 §4.3 目标「31 文件」（prompts/ 产物数）同字不同义，实现时勿混淆两处「31 文件」口径。

## 三、范围判定规则核验（§0 新增）

§0 三类判定自洽，实际应用无误：

| 类别 | 判定 | 应用点 | 核验 |
|:---|:---|:---|:---|
| 现行状态断言 | 纳入同步 | §4 全部计数文案 | ✅ 一致 |
| 历史归属行 | 不改写，如需体现新闭环则追加 | handbook L61/L62（CL007/CL008 演进行）、L90（`### 5.1 v1 契约（CL007，18 文件）`）、SKILL.md 变更记录 v2.5.0（L314） | ✅ 一致（§4.3 L140/L122 均「不改写/追加」） |
| 归档快照 | 不触碰 | documents/review/*、documents/archive/*、cache/ | ✅ 一致（穷举扫描已排除） |

🟢 观察（不阻断）：§5.2 标题（L101 `### 5.2 v2 门户（CL008，28 文件）`）被 §4.3 L131 处理为「改计数保留归属（现 31 文件）」，而 §5.1（L90）被处理为「不改写」。两者均带闭环归属（CL008/CL007），§0 的「历史归属行」示例清单仅列 §5.1，未说明 §5.2 为何按「现行状态」改计数。隐式判据是「v1 = 历史契约快照 vs v2 = 现行门户」，本轮 §4.3 L131 已给逐行指令（实施无歧义），建议后续在 §0 补一句该判据以免再起歧义。

## 四、决策层回归

§2 决策表 A2/B1/C1/D1/E1/F1/G1/H1 与 v1.0/v1.1 逐项一致，未变且自洽：D1↔§4.1 `SKILL_TO_GROUP` +1 项 `('table','指令 CLI')`、E1↔§3.1 合计 ~700 行每篇 ≤250、G1↔§4 精确清单、H1↔独立 CL011。v1.2 仅动 §0（范围规则）、§4.2（B 组）、§4.3（README 双源 + handbook + frontmatter + 自查补漏），未触碰决策层。

## 五、安全事项

与 v1.0/v1.1 一致：纯文档/skill 沉淀 + 挂载注册，零功能变更（C1 脚本冻结、零模板/渲染/参数语义变更），无新增注入/越权/敏感信息面。反馈能力安全红线（白名单+主键双层保护 / 入库 `<`/`>` 拒绝 / 显式 pathspec / 写盘前预检 / shell=False）已在 CL009/CL010 落地，本轮仅文档化转述。

🟢 无新增安全风险。

## 六、评分

| 项 | 严重度 | 扣分 |
|:---|:---|:---|
| HG-SEC-151..153 + 附注 + 自查补漏（五项核销） | — | 0（已正确修正） |
| HG-SEC-154 AGENTS.md L326「288 tests」漂移遗漏 | 🟢 LOW | 0 |

得分: **100 / 100（A）**

## 七、结论

**PASS** — 上一轮 HG-SEC-151（🟡）及 HG-SEC-152/153（🟢）+ 附注 + 自查补漏 五项全部真实核销（逐行实测核对成立），「改动面精确清单」§4 完备性已达可实施口径；决策层 A2-H1 未变且自洽；安全面无新增风险。独立复跑穷举仅发现 1 处 🟢 既存漂移遗漏（HG-SEC-154：AGENTS.md L326「288 tests」→ 实测 311，dev-facing 非阻断），随 [3/6] 一并折入即可，不阻塞开工。

## 八、发现项汇总

| # | 严重度 | 摘要 |
|:--|:--|:--|
| HG-SEC-151..153 + 附注 + 自查补漏 | ✅ 已核销 | v1.2 五项修正真实成立 |
| HG-SEC-154 | 🟢 record | AGENTS.md L326「288 tests」现行状态计数漂移未同步（实测 311），§4.3 穷举遗漏；建议随 [3/6] 折入「288→311」一行 |

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:---|
| — | （无阻塞项；HG-SEC-154 为 🟢 随实施折入，非本轮阻塞） | — |
