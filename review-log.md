# html-gen — review-log

> 作用: review运行日志; 由 ops profile 在 review 后 append，review profile 验证后更新状态。
>
> 触发机制: ops profile 完成校准/审计后写入条目（状态=⏳ AWAITING REVIEW）；
>         review profile 验证通过后将状态更新为 ✅ PASS。
>
> 文件命名: 固定为 `review-log.md`，小写，无版本号。

## 2026-07-17 — Pilot: features.md + review-log.md 创建

- **review 者**: ops/hermes-skills (hermes-1.2.0)
- **范围**: 创建 html-gen 项目 features.md 和 review-log.md，验证 skill-templates 模板通用性
- **状态**: ✅ PASS
- **报告**: 模板验证通过，html-gen 项目已接入治理体系

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

