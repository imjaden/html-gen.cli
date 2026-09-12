# GitHub Issue 反馈通道 skill 沉淀 — 实现审计第三轮复审报告 v1.2

> 闭环: HTML-GEN-CL011 · 步骤: [5/6] 实现审计第三轮复审（re-audit-2）
> 日期: 2026-09-12 · 执行: Security Reviewer
> 复审对象: commit `ba6d702`（kb 内容页补正 + 计数字段订正 HG-SEC-158..160）对上一轮 v1.1 审计（CONDITIONAL PASS）的处置
> 设计基线: `documents/solutions/github-issue-feedback-skill-design-v1.2-20260912.md`（评审 PASS 100/A，`f3be5d9`；§3.4 含勘误 + 勘误补记）
> 独立复验: 全部逐项亲自跑命令 / 读文件 / 逐字节比对，未仅信 ops 自述

## 1. 结论

**PASS 100/100（A）** —— HG-SEC-158/159/160 三处全部真实修复并逐字节核销；产物一致性全量复检（31 文件）**零内容漂移**；回归 `pytest -n 0` **312 passed** + `--site` 31 文件幂等。本轮**无新发现项**。

## 2. 逐条核销 HG-SEC-158/159/160

| # | 上轮要求 | 实测核销（独立打开文件/产物） | 结果 |
|:--|:--|:--|:--|
| HG-SEC-158 🟡 | `prompts/kb/github-issue-feedback.html` 承担旧内容（155..157 修复被 `git checkout` 与时间戳一并回退） | 该页 L531 现为「→ 非空 → 行唯一定位 → 类型 → 入库 XSS 防护 → 幂等 → 冲突取最新」（正确新序）；L666「脚本名 ×9（L11-19 示例命令行）」；L697「1. target 字段表（19 项：16 具体字段 + 3 隐式机制）」；旧串「行唯一定位 → 类型 → 非空」「×8」「约 8 处」「把读者引导到表单」「20 项」grep **全部 0 命中** | ✅ |
| HG-SEC-159 🟢 | schema §1「20 项」实为 19 枚举行 | `feedback-targets-schema.md` L7 表头「19 项：16 具体字段 + 3 隐式机制」；逐行计数 = 16 具体字段（repo/label/dataset/template/page/data/html/key_field/alt_key/editable/protected/key_guard/commit.scope/types/parse_fields/rebuild.args）+ 3 隐式（page+dataset 组合 / repo 覆盖 / 多 target）= **19 行** | ✅ |
| HG-SEC-160 🟢 | 设计基线残留：§8「×8」、§3.1/§3.3「20 字段」「5 红线」 | §8 L193「脚本名 ×9（示例命令行 L11-19）」；§3.1 L58「19 项字段 + 校验链 + 十态 CLI + 6 红线」；§3.3 L72「target 19 项字段表 + … + 安全红线 6 条」；§3.4 L80 已追加「勘误补记（HG-SEC-159/160）」 | ✅ |

> 佐证：kb 页 doc meta 字数 2,800（v1.0）→ 2,808（v1.1）→ **2,812**（v1.2），内容确随 155..157 与 159 两次订正真实变更，非仅时间戳刷新。

## 3. 产物一致性全量复检（本轮重点，源于 158 的同型风险）

方法：`html-gen prompt --site --dir <临时目录>` 生成基准 → 与仓库 `prompts/` 逐文件逐字节比对；另用源文件（SKILL.md + references）**独立重建**产物验证拼接公式，不依赖生成器执行结果。

### 3.1 全量 31 文件比对结果

| 类别 | 文件数 | 明细 |
|:--|:--:|:--|
| 逐字节一致 | **22** | 顶层 index.html / all.md / _kb-groups.json / _kb-data.json / 18 个 `{skill}.md`·`{skill}.json` |
| 仅时间戳差异 | **9** | `kb/*.html` ×9（doc meta「创建/编辑」行，HG-SEC-086 既有 wildcard） |
| **内容差异** | **0** | 无 |

### 3.2 源文件独立重建（逐字验证）

| 产物 | 重建公式 | 实测 |
|:--|:--|:--|
| `prompts/github-issue-feedback.md` | `strip_frontmatter(SKILL.md)` + 3 篇 references 按 stem 排序拼接（`\n\n---\n\n## {stem}\n{raw}`） | 逐字一致 ✅ |
| `prompts/github-issue-feedback.json` | `{status:ok, error:'', data:{name, content=stripped, references={stem: raw}}}` | 逐字一致 ✅ |
| `prompts/all.md` 该 skill 段 | `## {name}` + `> description` + 正文（删 h1）+ 各 reference（删自身首 h1） | 逐字一致 ✅（全 9 skill 段全量重建 == 仓库） |
| `_kb-data.json` 该条目 | title/group/desc/url/kind | `{title: github-issue-feedback, group: table, section: 指令 CLI, badge: Prompt, url: kb/github-issue-feedback.html, kind: skill}` 字段正确 ✅ |
| `kb/github-issue-feedback.html` | 内容与 `.md` 一致（除 doc meta 时间戳行） | 比对归入「仅时间戳差异」✅ |

### 3.3 其余 30 文件一致性（尤其本轮改过的源）

- `prompts/html-gen*.{md,json}`（`skills/html-gen/SKILL.md` 本轮曾改）：与源**逐字节一致**（在 22 一致集内），无 stale。
- 既有 8 个 kb 页仅时间戳差异，属 HG-SEC-086 wildcard，符合预期。

## 4. 回归证据

| 项 | 命令 / 方法 | 实测 |
|:--|:--|:--|
| 全量测试 | `conda py3.12 -m pytest tests/ -q -n 0` | **312 passed in 130.60s** |
| `--site` 规模 | `python3 html-gen.py prompt --site --dir <tmp>` | **31 文件**（`9 skills (31 文件: 门户 + kb×9 + md/json×18 + all.md)`） |
| 幂等（同秒） | 两次独立生成两临时目录逐字节比对 | **31/31 逐字节一致**（含 kb，同秒时间戳相同） |
| 幂等（跨时间） | 新生成 vs 仓库（10:38 提交版） | 22 一致 + 9 仅时间戳，0 内容差异 |

> 环境：`python3`（`/usr/bin/python3` 3.9.6）与 conda py3.12（pytest 9.1.0）均可用；权威回归基线 = conda py3.12（与 ops 报告一致）。

## 5. 评分

| 项 | 值 |
|:--|:--|
| 基线 | 100 |
| HG-SEC-158/159/160（已核销） | 0 |
| 新发现 | 0 |
| **总分** | **100 / 100（A）** |
| **结论** | **PASS**（无 open finding，无残留漂移） |

## 6. 处理

- ✅ PASS → 写报告 + review-log + .review-level.yaml，**commit 全部审计记录 + push `github` main（ff-only，不推 gitee、不 force）**
- 同步：v1.0/v1.1 两条 CONDITIONAL_PASS 的 `findings_open` 归零（findings 已由 v1.1/v1.2 逐条核销关闭）+ 追加本条 PASS 记录
- 报告: `documents/review/github-issue-feedback-skill-impl-audit-v1.2-20260912.md`
