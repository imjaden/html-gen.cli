# html-gen — review-log

> 作用: review运行日志; 由 ops profile 在 review 后 append，review profile 验证后更新状态。
>
> 触发机制: ops profile 完成校准/审计后写入条目（状态=⏳ AWAITING REVIEW）；
>         review profile 验证通过后将状态更新为 ✅ PASS。
>
> 文件命名: 固定为 `review-log.md`，小写，无版本号。

## 2026-07-12 — FAIL (HG-SEC-001..HG-SEC-004)

- **Reviewer**: Security Reviewer
- **Level**: L2 (implementation-audit)
- **Scope**: 
- **Verdict**: FAIL
- **Score**: 60 / 100
- **Tracking**: HG-SEC-001..HG-SEC-004

## 2026-07-12 — PASS (HG-SEC-001..HG-SEC-004 (re-review))

- **Reviewer**: Security Reviewer
- **Level**: L2 (implementation-audit)
- **Scope**: 
- **Verdict**: PASS
- **Score**: 95 / 100
- **Tracking**: HG-SEC-001..HG-SEC-004 (re-review)

## 2026-07-14 — PASS (N/A (全量复查: 15 commits, 0 new findings))

- **Reviewer**: Security Reviewer
- **Level**: L2 (implementation-audit)
- **Scope**: 
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (全量复查: 15 commits, 0 new findings)

## 2026-07-17 — Pilot: features.md + review-log.md 创建

- **review 者**: ops/hermes-skills (hermes-1.2.0)
- **范围**: 创建 html-gen 项目 features.md 和 review-log.md，验证 skill-templates 模板通用性
- **状态**: ✅ PASS
- **报告**: 模板验证通过，html-gen 项目已接入治理体系

## 2026-07-23 — 46 unpushed commits, 4 design documents, 72 project files

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: 46 unpushed commits, 4 design documents, 72 project files
- **Verdict**: PASS
- **Tracking**: HG-DESIGN-CONV-001 (commit convention)

## 2026-08-06 — drama-kb-table-design-v1.0

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: drama-kb-table-design-v1.0 — 以剧读史知识库表格化改造
- **Verdict**: CONDITIONAL_PASS
- **Score**: 90 / 100
- **Tracking**: D2-1 (剧中设定标注), D2-2 (JSON列定义), D4-1 (测试补充)
- **报告**: documents/review/drama-kb-table-review-v1.0-20260806.md

## 2026-08-06 — drama-kb-table

- **Reviewer**: Security Reviewer
- **Level**: L2 (implementation-audit)
- **Scope**: drama-kb-table — dev 实施 (5595f42) + ops 修复 (cc6dbee)
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (3 review findings closed, ops 2 fixes verified)
- **报告**: documents/review/drama-kb-table-implementation-review-v1.0-20260806.md

## 2026-08-08 — table-quickfilter-default

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: table-quickfilter-default — 筛选默认行为调整 (保守默认 + 显式声明)
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (7 requirements covered, 0 blocking)
- **报告**: documents/review/table-quickfilter-default-review-v1.0-20260808.md

## 2026-08-08 — table-quickfilter-default

- **Reviewer**: Security Reviewer
- **Level**: L2 (implementation-audit)
- **Scope**: table-quickfilter-default — dev 实施 (65c32c1) + ops 核查 (e0ca95e)
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (D1-D7 fully implemented, 84 tests, firstKeyCol dynamic)
- **报告**: documents/review/table-quickfilter-default-implementation-review-v1.0-20260808.md

## 2026-08-12 — heading-levels-fix

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: heading-levels-fix — h4-h6 标题渲染支持
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (CONDITIONAL PASS → 复检 D-新增 anchor-loop split closed)
- **报告**: documents/review/heading-levels-fix-review-v1.0-20260812.md

## 2026-08-13 — 12 unpushed commits

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: 12 unpushed commits — prompt CLI + h4-h6 + table pills/split
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (12/12 commit convention, 18 files naming, 100 tests)
- **报告**: documents/review/batch-12commits-review-v1.0-20260813.md

## 2026-08-19 — doc-body-width-levels

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: doc-body-width-levels — 三级宽度 URL 入参
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (narrow/medium/wide, body class, 无持久化)
- **报告**: documents/review/doc-body-width-levels-review-v1.0-20260819.md

## 2026-08-19 — test-speed-optimization

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: test-speed-optimization — 测试执行效率优化 (xdist + sleep 调低 + WebDriverWait)
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (3 非阻塞建议: 依赖固化/并行复核/事实源单一)
- **报告**: documents/review/test-speed-optimization-review-v1.0-20260819.md

## 2026-08-19 — doc-meta-path-showmd

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: doc-meta-path-showmd — meta 显示 md 路径 (show-md 入参 + 脱敏)
- **Verdict**: REJECT
- **Score**: 85 / 100
- **Tracking**: M4-1 (L311 闸门不匹配脱敏文件名, 标题复制静默失效)
- **报告**: documents/review/doc-meta-path-showmd-review-v1.0-20260819.md

## 2026-08-21 — test-speed-optimization

- **Reviewer**: Security Reviewer
- **Level**: L2 (implementation-audit)
- **Scope**: test-speed-optimization — 实施链 (xdist + sleep + WebDriverWait + flaky fix)
- **Verdict**: PASS
- **Score**: 100 / 100
- **Tracking**: N/A (T1-T7 全落地, 并行 25.17s, 146 tests 无回归)
- **报告**: documents/review/test-speed-optimization-implementation-review-v1.0-20260821.md

## 2026-08-22 — 朱元璋（2006）知识库实现审计

- **Reviewer**: Security Reviewer
- **Level**: L2 (Implementation Audit)
- **Scope**: 未 push 9 commits（05feb12/1fd5e8d/a2cec02/bddfc4f/36d3975/77ea871/07d622c/bdfd497/e17c465），朱元璋知识库 + handoff 文档
- **Verdict**: PASS
- **Score**: 95 / 100 (Rating: A)

### Summary

朱元璋（2006）知识库功能完整落地：菜单标签统一带年份（1B）、概述+时间轴+36计策框架（2A，用户手工补 17 条已回填 JSON）、时间轴范围含剧前史/剧后余波（3A）、豆瓣链接覆盖三剧（4B），全部符合探讨确认清单。定向 16 tests + 全量 146 tests 通过；浏览器实测 4 tabs 顺序、timeline 默认筛选洪武 3 行/清筛选 7 行、strategy 17 行、URL 全角括号参数编码往返恢复、零 JS 错误。生成物与 data JSON 逐字段一致；顺带修复的 yongzheng/history 列序同步已验证。授权 push 9 commits 至 github/main。

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-005 | 🟡 | daming-strategy-table.html 列宽与 data JSON 不同步（bddfc4f 压缩生成物未回填 JSON） | demos/drama/daming-strategy-table.html ↔ data/_drama-table-daming-strategy.json | Open |
| HG-SEC-006 | 🟢 | review-log.md 历史 13 次 review 未追加条目（审计追踪缺口，本次已补） | review-log.md | Open |

### Positives

- 生成物/数据双向一致验证充分（COLUMNS/DATA 逐字段对比，含列序与宽度）
- 用户手工补数据已回填 JSON 且零丢失，diff 核验过
- 全角括号 tab label 在 URL group 参数中自动 encodeURIComponent，实测往返恢复正常
- 36计策框架→17 行数据无死链，12 个 iframe refs 全存在

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-005 | daming 列宽不同步 | 🟡 | P2 | Open |
| HG-SEC-006 | review-log 历史缺口 | 🟢 | P2 | Open |

