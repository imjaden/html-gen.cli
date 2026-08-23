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
| HG-SEC-005 | 🟡 | daming-strategy-table.html 列宽与 data JSON 不同步（bddfc4f 压缩生成物未回填 JSON） | demos/drama/daming-strategy-table.html ↔ data/_drama-table-daming-strategy.json | ✅ Resolved |
| HG-SEC-006 | 🟢 | review-log.md 历史 13 次 review 未追加条目（审计追踪缺口，本次已补） | review-log.md | ✅ Resolved |

### Positives

- 生成物/数据双向一致验证充分（COLUMNS/DATA 逐字段对比，含列序与宽度）
- 用户手工补数据已回填 JSON 且零丢失，diff 核验过
- 全角括号 tab label 在 URL group 参数中自动 encodeURIComponent，实测往返恢复正常
- 36计策框架→17 行数据无死链，12 个 iframe refs 全存在

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-005 | daming 列宽不同步 | 🟡 | P2 | ✅ Closed (aeadf85) |
| HG-SEC-006 | review-log 历史缺口 | 🟢 | P2 | ✅ Closed (923a47e) |

---

## 2026-08-22 — 尾项复核：HG-SEC-005/006 关闭

- **Reviewer**: Security Reviewer
- **Level**: L2 (Implementation Audit 尾项复核)
- **Scope**: 未 push 2 commits（aeadf85 fix@html-gen / 923a47e docs@html-gen），ops 修复复核
- **Verdict**: PASS
- **Score**: 100 / 100 (Rating: A)

### Summary

2026-08-22 朱元璋实现审计遗留的 2 个非阻断 findings 已全部关闭：HG-SEC-005（🟡 daming-strategy 列宽不同步）由 aeadf85 回填 JSON 6 列宽至生成物压缩值并重新生成 html，JSON 与 COLUMNS 逐字段 MATCH（strategy 60 / category 60 / idiom 90 / event 160 / figures 90 / origin 160 / origin_figures 140）；HG-SEC-006（🟢 review-log 历史缺口）由 923a47e 从 .review-level.yaml review_history 补录 14 条（2026-07-12 ~ 2026-08-21），现共 16 条与 review_history 对齐。两 commit 改动范围干净（aeadf85 仅 data JSON + daming html；923a47e 仅 review-log.md）。全量 146 tests 复跑通过（24.97s）。

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-005 | 🟡 | daming-strategy 列宽不同步 | data/_drama-table-daming-strategy.json ↔ demos/drama/daming-strategy-table.html | ✅ Resolved |
| HG-SEC-006 | 🟢 | review-log 历史缺口 | review-log.md | ✅ Resolved |

### Positives

- 修复范围精确：aeadf85 仅动 data JSON 6 列宽 + 重新生成对应 html，无夹杂其他改动
- 923a47e 补录条目按日期排序、跳过已有 2 条（2026-07-17 Pilot / 2026-08-22 本次审计），无重复
- 全量回归 146 passed 无回归

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-005 | daming 列宽不同步 | 🟡 | P2 | ✅ Closed (aeadf85) |
| HG-SEC-006 | review-log 历史缺口 | 🟢 | P2 | ✅ Closed (923a47e) |

---

## 2026-08-23 — index-landing-design v1.0（GitHub Pages 落地页）

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: documents/index-landing-design-v1.0-20260822.md — 根 index.html 落地页（hero 100vh + 模板网格）+ README 精简 + commit 87834ef
- **Verdict**: PASS
- **Score**: 95 / 100 (Rating: A)

### Summary

GitHub Pages 站点首页落地页设计评审通过。根 index.html 新建（首屏 100vh hero：价值定位+安装+4 条快速开始命令；第二屏 4 模板网格复用 demos/index.html 内容）、README 精简为仓库说明，与用户确认清单 1C/2A+B+C/3A/4B/5A/6A 全部一致。数据验证核实：根目录确实无 index.html、style-guide.css 6361 字节（复用不复制）、install.sh 支持 install 子命令、CNAME=html-gen.lab.jaden.tech、README 现状 85 行/3338 字节。唯一 🟡 SEC-007：路径迁移清单通配符 `template-*-guide-*` 漏掉 grid 内实际引用的 2 个非 guide 模板文件（template-B-markdown-spec、template-D-slide-demo，L124/L194 演示链接），清单"8 处引用点"数字与实测 12 目标文件+CSS 不符；§4 验证步骤的 404 检查可兜底，非阻塞。4 个 🟢 记录（CSS query 参数、hero 命令文本来源、README 章节去留、AGENTS.md 漂移备注）。

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-007 | 🟡 | 路径迁移清单不完整：通配符漏 template-B-markdown-spec + template-D-slide-demo（grid 内 B/D 卡演示链接），"8 处"数字不准确 | documents/index-landing-design-v1.0-20260822.md §2 | ✅ Closed (543c9bf v1.1) |

### Positives

- 待确认清单 6 项全部定稿且与本次 prompt 一致，需求追溯清晰（REA-5 1:1 对应）
- 漂移风险（1C）在设计 §风险显式接受并给出治理建议，符合用户"两份独立维护"决策
- 现状评估准确：demos/index.html 被 README/usage-guide/hermes-profile-skills-list 多处引用，设计明确不移动不删除
- 验证步骤覆盖关键坑（相对路径无 404 + 无 JS 错误 + 100vh 检查），能兜底清单遗漏
- 复用而非重建：CSS 复用根 style-guide.css（6361 字节确认）、github-corner 复制自 demos

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-007 | 路径迁移清单不完整 | 🟡 | P2 | ✅ Closed (543c9bf v1.1 + 实现审计验证 17/17) |

---

## 2026-08-23 — index-landing 实现审计（GitHub Pages 落地页）

- **Reviewer**: Security Reviewer
- **Level**: L2 (Implementation Audit)
- **Scope**: 未 push 6 commits（87834ef/c4340b7/543c9bf/47a3a84/2472152/87d678f），根 index.html 落地页（hero 100vh + 4 模板网格）+ README 精简 + hero 100vh 修复（87d678f）
- **Verdict**: PASS
- **Score**: 100 / 100 (Rating: A)

### Summary

实现与已评审设计 v1.1 高度一致：17 处路径迁移逐条匹配（grep 17 唯一本地引用，无 `../` 残留，CSS 根级），HG-SEC-007 经 543c9bf v1.1 补全清单后关闭；Hero 满足确认清单 2A+B+C（价值定位/安装/4 命令 doc-table-knowledge-slide，无导航锚点）与 3A（100vh）；87d678f 修复经独立 headless Chrome 复测正确（style 块 3 开 3 闭注释无 stray `*/`，.hero 在 cssRules，heroHeight=viewport=614px ratio 1.0）；README 保留定位/目录/站点链接/本地开发 4 项，85→27 行（-68%）；commit 6/6 type@scope 且 feat/docs/fix/review 职责分离；demos/ 零误改；18 URL 全 200；全量 pytest 146 passed (25.47s) 无回归。2 个 🟢 记录（HG-SEC-012 README 快速开始保留与设计 §3 偏差；HG-SEC-013 内链 target=_blank 缺 rel="noopener"，外链已带），均不阻断。

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-007 | 🟡 | 路径迁移清单不完整（设计 v1.0，前置评审遗留） | documents/index-landing-design-v1.0-20260822.md §2 | ✅ Closed (543c9bf v1.1 + 实现验证 17/17) |
| HG-SEC-012 | 🟢 | README 保留「快速开始」与设计 §3 移除清单不一致（案例演示/测试/零依赖 3 节亦被移除，前置 SEC-010 建议保留） | README.md ↔ 设计文档 §3 | ⏳ Open（待确认） |
| HG-SEC-013 | 🟢 | 根 index.html 内链 target=_blank 缺 rel="noopener"（tpl-guide ×4 / demo-item ×9 等，均 demos/ 同源；外链 github-corner 已带） | index.html | ⏳ Open（待确认） |

### Positives

- 17 处路径迁移与 v1.1 清单逐条一致，v1.0 通配符遗漏的 4 个非 templates 文件（countries/knowledge-demo/table-actions-demo/usage-guide）全部覆盖，验证兜底到位
- 修复链完整闭环：ops 发现（HG-SEC-008 渲染 386px vs 757px）→ 根因定位（注释 `*/` 提前闭合）→ fix 独立提交（87d678f 仅 1 行）→ 复测 ratio 1.0
- 独立复跑证据链齐：18 URL 全 200、headless Chrome hero 100vh、146 tests 无回归，与 ops 核查记录一致
- commit 粒度规范：design/review/feat/docs/fix 六 commit 职责单一，消息均符合 type@scope
- 外链安全处理正确：github-corner 均带 rel="noopener" + target=_blank

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-007 | 路径迁移清单不完整 | 🟡 | P2 | ✅ Closed (543c9bf v1.1 + 实现验证 17/17) |
| HG-SEC-012 | README 快速开始与设计 §3 偏差 | 🟢 | P3 | ⏳ Open（待确认：接受现状或按设计移除） |
| HG-SEC-013 | 内链缺 rel="noopener" | 🟢 | P3 | ⏳ Open（待确认：建议批量补） |


