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



---

## 2026-08-23 — index-landing 实现审计尾项处置（HG-SEC-012/013）

- **处置方**: ops（实现审计 PASS 100/A 后尾项）
- **Scope**: HG-SEC-012（README 快速开始与设计 §3 偏差）、HG-SEC-013（内链缺 rel="noopener"）

### 处置决定

| # | Severity | 决定 | 依据 |
|:--:|:---:|:---|:---|
| HG-SEC-012 | 🟢 | 接受现状（README 保留简短快速开始） | README 是 GitHub 仓库主页，保留 4 条可执行命令对访客直接可用；27 行已满足"精简为仓库说明"（4B）；设计 §3 移除清单为草稿口径，实现保留更符合用户意图 |
| HG-SEC-013 | 🟢 | 已补（ops 批量修复） | index.html 14 个内链 target="_blank" 补 rel="noopener"，headless Chrome 复测无 JS 错误、hero 100vh、4 卡正常 |

### 复核

- HG-SEC-013 修复 commit 后全量 pytest 146 passed 无回归（前一轮已验，本轮仅属性级修改）
- review-log 两 🟢 关闭，无新增 findings

---

## 2026-08-23 — index-landing UI polish 实现审计（github-corner/scroll-hint/guide 案例章节）

- **Reviewer**: Security Reviewer
- **Level**: L2 (Implementation Audit)
- **Scope**: 未 push 3 commits（78e6c0c/c59d657/1221110），根 index.html 落地页 UI 增量（github-corner 可点+hover、scroll-hint 滑屏、移除底部案例清单、四卡标题统一）+ 4 guide「模板案例」章节 + 版本 v2.3/v1.2 + 重新生成 html
- **Verdict**: PASS
- **Score**: 100 / 100 (Rating: A)

### Summary

实现与用户确认清单 4 项逐条一致：① github-corner 去 pointer-events:none、删 .github-corner-hit 隐藏区（落地页 0 残留），hover octocat-wave 动画保留且实际可触发；② scroll-hint 纯 CSS 平滑滑屏（html scroll-behavior smooth + a href="#templates" + section id），ops Selenium 点击后 top=0px；③ 底部「案例演示清单」37 行区块移除，4 guide md 补「模板案例」章节（A 5/B 7/C 4/D 1，顺序与用户口径一致：A 按 demos-index→hermes-skills→countries→phase2→table-actions，C 按 drama→chaitin→cloudwise→knowledge-demo），A/B/C→v2.3、D→v1.2 日期 2026-08-23，html-gen doc 重新生成 diff 干净（仅 meta 时间 + 字数 + 案例章节 + 迭代行）；④ 四卡标题全「案例演示」（4/4），demo-item icon+name+desc+arrow 结构齐全，案例内容不变（A 3/B 3/C 3/D 1）。demos/index.html（featured 数据源）零误改；16 个案例链接目标全部实测存在；新增 target=_blank 全带 rel="noopener"（17 个 0 缺失）；commit 3/3 type@scope 且 feat/docs/chore 源与产物分离；无凭证/无新增外部资源。ops 核查记录（Selenium 8093 / curl 200 / pytest 146 passed）复核无遗漏。1 个 🟢 记录（HG-SEC-014 layout 模板层 github-corner-hit 残留，范围外），不阻断。前置 HG-SEC-012/013 尾项已关闭，同步 YAML findings_open 2→0。

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-014 | 🟢 | layout 模板层（layout-doc/table/knowledge.html）仍保留 .github-corner-hit 隐藏区模式，据此生成的 demo（chaitin/cloudwise 等）仍含该元素；本次范围仅为根落地页 | layout-doc.html:201,229 / layout-table.html:233,247 / layout-knowledge.html:167,189 | ⏳ Open（待确认：接受或后续模板统一时迁移） |

### Positives

- 确认清单 4 项全部精确落地，无遗漏无过度（案例内容保持不变的约束被严格遵守）
- guide 案例章节与用户指定口径/顺序逐行一致（A/C 型顺序、B 型 7 项、D 型手工 1 项均精确匹配）
- 源 md 与生成 html 分 commit（docs/chore），再生成 diff 干净无漂移，便于事后审查
- 链接安全一致：新增 target=_blank 全部带 rel="noopener"；16 案例链接目标全存在，无死链
- ops 证据链完整且与独立复核一致（grep 残留 0、链接目标 ls 全 OK、secret scan 干净）

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-012 | README 快速开始与设计 §3 偏差 | 🟢 | P3 | ✅ Closed（2026-08-23 尾项处置：接受现状） |
| HG-SEC-013 | 内链缺 rel="noopener" | 🟢 | P3 | ✅ Closed（2026-08-23 尾项处置：ops 已补） |
| HG-SEC-014 | layout 模板层 github-corner-hit 残留 | 🟢 | P3 | ⏳ Open（待确认：接受或模板统一时迁移） |

---

## 2026-08-23 — index-landing UI polish 审计尾项处置（HG-SEC-014）

- **处置方**: ops（实现审计 PASS 100/A 后尾项）
- **Scope**: HG-SEC-014（layout 模板层 github-corner-hit 残留）

### 处置决定

| # | Severity | 决定 | 依据 |
|:--:|:---:|:---|:---|
| HG-SEC-014 | 🟢 | 接受现状，不迁移 | layout 模板层（layout-doc/table/knowledge）生成的 demo 页右上角有工具栏按钮，`.github-corner-hit` 双层可点区（外层 pointer-events:none 穿透 + hit 36px）是 2026-08 有意设计（commit 204f9e1 "github-corner 双层可点区(外层穿透+hit 36px) 防遮挡工具栏按钮"），与根落地页（无工具栏）场景不同；如模板统一时移除需回归验证工具栏可点性，本次范围仅根落地页，不动模板层 |

### 复核

- review-log 三 🟢 全部关闭（HG-SEC-012/013/014），无新增 findings
- 待推 4 commits 由 review 授权（实现审计 PASS 100/A）

---

## 2026-08-23 — html-gen → html-gen.cli 改名实现审计（github/pages links 批量更新 + 上箭头返回首页 + 手工微调）

- **Reviewer**: Security Reviewer
- **Level**: L2 (Implementation Audit)
- **Scope**: 未 push commits（github/main..HEAD 1 个：020ac34；982a818 CNAME 已含于 github/main，gitee 尚缺 2 个），改名 R1-R5（46 html github 链接替换 + README/CNAME 域名 + A/B 上箭头 + 手工微调 4 项 + gitee remote 配置）
- **Verdict**: PASS
- **Score**: 100 / 100 (Rating: A)

### Summary

实现与用户确认清单 R1-R5 逐条一致：① github 链接 46 文件批量替换完整（`git grep html-gen.cli` = 46；旧链接排除历史文档 0 残留；双后缀 html-gen.cli.cli 0；knowledge-demo 单链接无 hit 层正确）；② README 站点链接 + CNAME 双更新为 html-gen.cli.jaden.tech，产品名 D1A 严格保持（README h1/index title/hero 均为 "html-gen" 未误改）；③ 上箭头 A 形式（h2 标题行可见文本链接 + 全局 smooth）与 B 形式（固定按钮初始 opacity/visibility 隐藏、scrollY > innerHeight 显示、回顶隐藏、aria-label）双实现符合 D5C；④ 手工微调 4 项全部纳入（hero-blocks 1024px / demo-name display:block / '↓ 模板说明' / 四卡「模板」措辞 8 处）；⑤ R5 gitee origin remote set-url 正确（origin→gitee html-gen.cli.git、github→github html-gen.cli.git，无 commit）。历史文档边界清晰：documents/ review-log .review-level.yaml cache/ diff 0 文件，旧链接仅保留于设计评审报告（预期）；demos/index.html featured 清单零误改。全量 pytest 独立复核 146 passed（25.28s，无 flaky 复现）。无凭证、无 XSS、无新增外部资源。1 个 🟢 记录（HG-SEC-015 href="#" 空锚点实现细节，不阻断）。

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-015 | 🟢 | A/B 上箭头均用 `href="#"` 空锚点（会替换 URL hash、依赖全局 smooth），建议改 `href="#top"` + 显式 scrollTo；行为已验证正确，无安全影响 | index.html:216,360 | ⏳ Open（待确认：接受或后续优化） |

### Positives

- 链接替换干净彻底：46/46 覆盖、0 残留、0 双后缀，sed 边界控制（历史文档/cache 保留旧链接）严格
- D1A 产品名约束被严格遵守：仅链接与域名变更，README h1 / index title / hero 产品名零误改
- commit 单一性符合 D6B：R1-R4 合成 1 个 commit，R5 为 git 配置无 commit；CNAME 用户提交独立清晰
- A/B 上箭头可访问性达标：A 可见文本、B aria-label，均非纯图标裸链接
- ops 证据链完整且与独立复核一致（grep 残留 0、Selenium 8094 四断言、pytest 146 passed 复核无 flaky）

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-015 | A/B 上箭头 href="#" 空锚点细节 | 🟢 | P3 | ⏳ Open（待确认：接受或后续优化） |

---

---

## 2026-08-23 — html-gen.cli 改名审计尾项处置（HG-SEC-015）

- **处置方**: ops（实现审计 PASS 100/A 后尾项）
- **Scope**: HG-SEC-015（A/B 上箭头 href="#" 空锚点）

### 处置决定

| # | Severity | 决定 | 依据 |
|:--:|:---:|:---|:---|
| HG-SEC-015 | 🟢 | 已优化（ops 直改） | index.html `<html>` 加 id="top"，A/B 上箭头 href 改 `#top`（不再污染 URL hash，依赖全局 smooth scroll 行为不变）；Selenium 复测 A/B 回顶 scrollY=0 通过 |

### 复核

- 改动仅 index.html 2 行 + html 标签；Selenium 8094 复测四断言通过；pytest 全量 146 passed（上一轮已验，本轮属性级）
- review-log 四 🟢 全部关闭（HG-SEC-012/013/014/015）

---

## 2026-08-23 — P4 落地页清单项：HG-SEC-014 文档化关闭

- **处置方**: ops（P4 模板层 github-corner-hit 差异统一）
- **Scope**: HG-SEC-014（layout 模板层 .github-corner-hit 残留）

### 处置决定

| # | Severity | 决定 | 依据 |
|:--:|:---:|:---|:---|
| HG-SEC-014 | 🟢 | 文档化关闭（不改模板代码） | layout 模板层（doc/table/knowledge/slide）生成的 demo 页右上角有工具栏按钮，「pointer-events:none 穿透 + hit 36px」是防遮挡的有意设计（commit 204f9e1）；根落地页无工具栏故全图标可点。两模式差异已写入 AGENTS.md「双源漂移」备注（commit 402fe29）。模板层若改为全图标可点需回归工具栏可点性，留待模板统一重构 |

### 复核

- AGENTS.md 已记录两模式差异；review-log 四 🟢 全部关闭（HG-SEC-012/013/014/015，计数修正 2026-08-23 HG-SEC-016）

---

## 2026-08-23 — 落地页回归测试 + 文档同步实现审计（P1-P4）

- **Reviewer**: Security Reviewer
- **Level**: L2 (Implementation Audit)
- **Scope**: 未 push 3 commits（221be4a test@ / 402fe29 docs@ / 68d2734 docs@），P1-P4：test_index_landing 落地页回归测试 8 用例 + AGENTS/features 同步（双源漂移备注 + 测试数 154 + github-corner 差异文档化）+ review-log HG-SEC-014 文档化关闭
- **Verdict**: PASS
- **Score**: 100 / 100 (Rating: A)

### Summary

3 commits 与 P1-P6 逐条一致。P1 回归测试 8 用例断言真实行为（hero 100vh 比例 >0.95、github-corner pointer-events auto + hover octocat-wave + 链接 html-gen.cli + 无 hit 区、scroll-hint 滑屏到位 <60px、back-top A/B href=#top 回顶 scrollY==0 与显隐、四卡标题「案例演示」+ demo-item 结构、无 JS 错误、无旧链接旧域名），独立复跑 8 passed in 6.83s；pytest --collect-only 154 与 AGENTS.md 18 文件逐文件计数完全一致。P2 双源漂移备注（根 index.html 与 demos/index.html 独立副本 + featured 数据源 + github-corner 两模式）准确；P3 AGENTS/features 同步仅覆盖需求 4 主题（测试数/目录/备注/GitHub Corner 行），无额外漂移；P4 模板层「穿透+hit 36px」vs 根落地页「全可点+hover」差异文档化，HG-SEC-014 关闭记录合规。P5 线上 7 URL 全 200、drama 页 github-corner 指向 html-gen.cli、demos/ 旧链接 0 残留。P6 ops profile html-gen-workflow skill 已含 test_index_landing 信息（跨 profile 只读核查）。commit 分组 test@/docs@ 职责分离。HG-SEC-015 关闭属实（b940b3b 已在 github/main：index.html html id=top + href=#top），本次同步 .review-level.yaml 前置条目 findings_open 1→0。2 个 🟢 记录（HG-SEC-016 review-log「五 🟢」计数与 4 个 ID 不符 + 与前置尾项处置条目重复；HG-SEC-017 _errors() 覆盖 1/8），均不阻断，由 ops 尾项处置。

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-016 | 🟢 | review-log 68d2734「五 🟢 全部关闭」与所列 4 个 ID（012/013/014/015）不符，应为「四」；且与前置「HG-SEC-014 尾项处置」条目（L350）重复关闭同一 finding | review-log.md:435 | ⏳ Open（待确认：修正计数或合并条目） |
| HG-SEC-017 | 🟢 | test_index_landing 仅 test_01 调用 _errors()（1/8 覆盖），后续测试方法若触发 console 错误将漏检；项目约定「每个测试方法独立加载页面，_errors() 检查 JS 错误」 | tests/test_index_landing.py | ⏳ Open（待确认：补断言或文档化豁免） |

### Positives

- 断言全部指向真实行为（几何/计算样式/动画/滚动位置），无脆弱属性快照；hero 用比例而非硬编码像素
- 等待机制稳健：主元素 WebDriverWait + 交互固定 sleep（1.2s 有 skill 文档依据，smooth scroll 完成），file:// 下 hash 规范化坑（split('#')[-1]）已处理
- 测试数 154 逐文件核对一致（collect-only 18 文件求和），AGENTS/features 同步零漂移
- HG-SEC-015 修复链完整（review 记录 → b940b3b 修复 → 本次验证 #top 在线上文件 + YAML findings_open 同步）
- commit 分组干净：test@（测试文件）/ docs@（文档）/ docs@（review-log）三 commit 单一职责

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-016 | review-log「五 🟢」计数不符 + 重复关闭条目 | 🟢 | P3 | ⏳ Open |
| HG-SEC-017 | test_index_landing _errors() 覆盖不足 | 🟢 | P3 | ⏳ Open |

---

## 2026-08-23 — P1-P6 审计尾项处置（HG-SEC-016/017）

- **处置方**: ops（P1-P6 实现审计 PASS 100/A 后尾项）
- **Scope**: HG-SEC-016（review-log 计数）、HG-SEC-017（_errors 覆盖）

### 处置决定

| # | Severity | 决定 | 依据 |
|:--:|:---:|:---|:---|
| HG-SEC-016 | 🟢 | 已修正 | review-log 68d2734「五 🟢」→「四 🟢」（HG-SEC-012/013/014/015 恰 4 项），修正处标注 HG-SEC-016 处置痕迹 |
| HG-SEC-017 | 🟢 | 已补强 | tests/test_index_landing.py setUp 加载后统一 _errors() 断言（覆盖全部 8 用例，不再仅 test_01）；8 passed + 全量 154 passed 复跑确认（首轮 2 errors 为并行瞬态，单跑 test_table_features 11 passed、重跑全量通过） |

### 复核

- review-log 七 🟢 全部关闭（HG-SEC-012/013/014/015/016/017）；无新增 findings

---

## 2026-08-24 — 省份表 + 国家双向关联设计评审（provinces-table-design v1.0）

- **review 者**: Security Reviewer（L2）
- **Scope**: commit `51bf5b5`（docs@html-gen: provinces table + countries cross-link design v1.0，未 push）；设计文档 `documents/solutions/provinces-table-design-v1.0-20260824.md`；探讨确认清单 1A-6A 全选
- **Verdict**: ⏳ CONDITIONAL PASS 70/B（🔴 1 / 🟡 3 / 🟢 6）— 非 PASS，不生成 dev 实施 prompt

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-018 | 🔴 | RIG-1 单位换算缺失：国家表 gdp_yi 为亿美元、area_km2 为 km²，与省份亿元/万km² 直接比较 → 实测 0 命中（归一化后 10/15 命中）；§三"GDP 统一亿元"与国家表实际单位自相矛盾 | provinces-table-design-v1.0 §三/§四 | ⏳ Open |
| HG-SEC-019 | 🟡 | RIG-2 列宽未指定：影院模型 11+3 列默认 120px，备注/3 标签 pills 列截断 | §二 A/B | ⏳ Open |
| HG-SEC-020 | 🟡 | RIG-3 测试基线过时：§七/TC-09"146"应为 154；T 清单 10 条 vs "~13 tests"表述不一 | §七/§九 | ⏳ Open |
| HG-SEC-021 | 🟡 | RIG-4 双向一致性示例错误：荷兰 vs 广东面积 Δ76.9%（阈值 30%），示例与规则矛盾 | §四 4 | ⏳ Open |
| HG-SEC-022 | 🟢 | OBS-1 匹配脚本未命名 + `_provinces-source.json` 不入 git 但无 .gitignore 防护 | §五 | ⏳ Open（随 v1.1 处理） |
| HG-SEC-023 | 🟢 | OBS-2 台湾归华南 vs 主流华东惯例（决策已确认）；港澳人口非七普口径；README 需补数据源行 | §三 | ⏳ Open（随 v1.1 处理） |
| HG-SEC-024 | 🟢 | OBS-3 国家表新列编号 12/13/14 为省份表延续，实际插入 15/16/17，建议标注"追加列" | §二 B | ⏳ Open（随 v1.1 处理） |
| HG-SEC-025 | 🟢 | OBS-4 双向匹配阈值方向不对称（相对省份 vs 相对国家），建议单方向匹配 + 反向回填 | §四 | ⏳ Open（随 v1.1 处理） |

### Positives

- 六要素闭环（字段表/口径/关联规则/数据源策略/测试/生成命令），§八 扩展 11 项不入表显式声明"非缺口"
- 模板能力全部实测可用：searchFields / format thousands / freeze / 序号列 / tabs contains / demo --rebuild 自动扫描
- 广东 135673 亿 / 12601 万 / 17.97 万km² 数据事实与官方口径一致
- commit `docs@html-gen:` + 文件名 Style A 均符合项目规范

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-018 | 单位换算缺失（面积/GDP 双维度 0 命中） | 🔴 | P0 | ⏳ Open |
| HG-SEC-019 | 列宽未指定 | 🟡 | P1 | ⏳ Open |
| HG-SEC-020 | 测试基线 146→154 | 🟡 | P2 | ⏳ Open |
| HG-SEC-021 | 荷兰示例与规则矛盾 | 🟡 | P2 | ⏳ Open |
| HG-SEC-022~025 | OBS-1~4（随 v1.1 处理） | 🟢 | P3 | ⏳ Open |

- 报告: `documents/review/provinces-table-design-review-v1.0-20260824.md`
- 待处理: ops 修 v1.1 后复审；未 push（CONDITIONAL 不 push）

---

## 2026-08-24 — 省份表 + 国家双向关联设计复审（provinces-table-design v1.1）

- **review 者**: Security Reviewer（L2）
- **Scope**: commit `93009fd`（docs@html-gen: provinces design v1.1 — fix review RIG-1~4 + OBS-1~4，rename v1.0→v1.1 + .gitignore）；设计文档 `documents/solutions/provinces-table-design-v1.1-20260824.md`
- **Verdict**: ✅ PASS 100/A（🔴 0 / 🟡 0 / 🟢 1）— v1.0 扣分项全部修复，生成 dev 实施 prompt

### Fix Verification

| # | v1.0 问题 | v1.1 修复 | 验证 |
|:--:|:---|:---|:---:|
| HG-SEC-018 | 🔴 RIG-1 单位换算缺失（0 命中） | §三 归一化（面积 ÷10000、GDP ×7.08 2023 年均国家统计局口径）+ None 防护（6 国缺 GDP/梵蒂冈全缺）+ TC-06 换算断言 | ✅ 实测命中对成立，归一化后 15/8/10 命中 |
| HG-SEC-019 | 🟡 RIG-2 列宽未指定 | §二 A 11 列 + §二 B 3 列全部显式 width（pills 170px、note 200px） | ✅ |
| HG-SEC-020 | 🟡 RIG-3 基线 146 过时 | §七/§九 基线 154 → 预计 +11~12，10 条 + 1-2 条表述统一 | ✅ 实测 154 |
| HG-SEC-021 | 🟡 RIG-4 荷兰示例矛盾 | §四 6 替换真实命中对（广东↔柬埔寨/乌拉圭/叙利亚/墨西哥/日本/韩国/西班牙） | ✅ 实测 Δ≤10% |
| HG-SEC-022~025 | 🟢 OBS-1~4 | 脚本命名+gitignore / 港澳台归因+README 来源行 / 追加列 15/16/17 标注 / 单方向匹配+反向回填 | ✅ 全部落位 |

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-026 | 🟢 | OBS：§四 6 人口示例数字（墨西哥 12846/日本 12452）与表内实际值（13086/12398）口径年份偏差——命中对仍成立（Δ≤4%），实施时以匹配脚本计算为准 | ⏳ 记录（不阻断） |

### Positives

- 换算闭环三层一致：口径（§三）→ 规则（§四:1 归一化先行）→ 测试（TC-06），杜绝 naive 0-命中错误模式
- None 防护语义精确（"该维度不参与匹配"而非"该国全部跳过"），与 TC-04 衔接无歧义
- v1.0 8 项发现全部实质修复（非声明式修复），正文与修订记录一致

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-018~021 | RIG-1~4 | 🔴/🟡 | P0-P2 | ✅ Closed（v1.1） |
| HG-SEC-022~025 | OBS-1~4 | 🟢 | P3 | ✅ Closed（v1.1） |
| HG-SEC-026 | 人口示例数字口径偏差 | 🟢 | P3 | ⏳ 记录 |

- 报告: `documents/review/provinces-table-design-review-v1.1-20260824.md`
- 实现 prompt: ✅ 已生成（cache/review-prep/prompt-provinces-dev-20260824.md，转 dev）
- 处理: PASS → 审计交付物 commit + push（连同设计文档 51bf5b5 + 93009fd 共 3 commits）

---

## 2026-08-24 — 省份表 + 国家双向关联实现审计（provinces-table implementation）

- **review 者**: Security Reviewer（L2）
- **Scope**: 未 push 5 commits（`73bc988` chore@ provinces-match 脚本 / `f6a3e7c` feat@ 省份表 data+demos / `323771a` feat@ 国家表回填 3 列 / `7dd1c18` test@ 省份表测试 / `31c8c60` fix@ backfill 同对规则）；设计 `documents/solutions/provinces-table-design-v1.1-20260824.md`（复审 PASS 100/A）
- **Verdict**: ✅ PASS 100/A（🔴 0 / 🟡 0 / 🟢 1）

### Summary

5 commits 与设计 v1.1 逐项一致，TC-01~10 全部成立：省份表 34 行 11 列（width 110/60/100/90/110/110/110/170/170/170/200 与 §二 A 一致）+ tabs 全部/7 区域 + options pageSize30/exportCSV/searchFields；港澳台 region_tags=华南 + note 口径说明；国家表 195 行 17 列（新 3 列 15/16/17 pills 170px），中国行 3 列留空（设计允许）。单位归一化独立复算：304 个省份侧 pills 阈值违规 0，广东 GDP↔韩国/西班牙/墨西哥、面积↔柬埔寨/乌拉圭/叙利亚在表内，杜绝 0-命中；`31c8c60` 修复后国家表 backfill 与脚本重跑输出 0 差异（同对回填规则成立）；None 防护恰 6 国缺 gdp_yi + 梵蒂冈全缺不参与匹配。双向互证 271/304=89.1%（与 ops 报告一致，TC-05 抽查 12 对 10 命中）。生成物 provinces-table.html COLUMNS/DATA/TABS/OPTIONS 与 JSON 零差异；registry count 59→60 可见（featured=false 符合设计）。测试 26 passed（13+13，含韩国 gdp_province 含广东、柬埔寨 area_province 含广东断言）；全量 166 passed + 1 环境性失败（test_history_tables::test_01 系其他会话重生成 demos/drama/history-strategy-table.html 9 列 schema 导致，与本次零交集，不代修不扣分）。commit 5/5 type@scope 小写英文 subject、无 WIP 混入；命名 provinces-*/countries-* 一致；凭证扫描 0 命中。1 个 🟢 记录（HG-SEC-027 人工复核 3 处省份侧单元格在 backfill 生成后修改 → 4 个不对称格：德国/西班牙回填空 + 土库曼斯坦/澳大利亚保留过期项，互证率 89.1% 而非 100%，建议后续复核后以最终省份表为事实源重跑回填）。授权 push 5 commits 至 github/main。

### Findings

| # | Severity | Title | File | Status |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-027 | 🟢 | 人工复核 3 处省份侧单元格（黑龙江 area 土库曼斯坦→德国 / 上海 pop 布基纳法索→斯里兰卡 / 广东 gdp 澳大利亚→西班牙）在 backfill 生成后修改，导致 4 格不对称（德国/西班牙 area/gdp_province 空，土库曼斯坦/澳大利亚保留过期省份）；互证率 89.1%；脚本以硬编码 PROVINCES 为事实源不读最终省份表 | data/_countries-data.json ↔ data/_provinces-data.json + scripts/provinces-match.py | ✅ Closed（a331ac1，2026-08-24 尾项复核） |

### Positives

- 数据质量高：304 个省份侧关联 pills 全部落在阈值内（0 违规），"归一化先行"设计修复闭环在实现层得到验证
- 双向机制修复链完整：ops 发现 323771a 独立重算偏差 → 31c8c60 改同对回填 → 复验脚本输出与 JSON 0 差异，互证率 88.5%→89.1%
- 测试超出设计要求：T1-T10 全落地 + 国家表 3 条反向回填断言（设计仅要求 1-2 条），并含"杜绝 0-命中"的归一化对照断言
- 生成物一致性验证充分：HTML 注入 const 与 JSON 逐字段比对零差异（含 width）
- None 防护语义精确（6 国仅 GDP 维度跳过，面积/人口维度仍参与），与设计 TC-04 一致
- commit 粒度与命名规范：chore/feat/test/fix 职责分离，provinces-* 与 countries-* 模式一致

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-027 | 复核后未重跑 backfill（4 格不对称） | 🟢 | P3 | ✅ Closed（a331ac1 fix backfill 事实源，2026-08-24 尾项复核） |

- 报告: `documents/review/provinces-table-implementation-review-v1.0-20260824.md`
- 处理: PASS → 授权 push 5 commits（73bc988/f6a3e7c/323771a/7dd1c18/31c8c60）至 github/main

---

## 2026-08-24 — 省份 backfill 尾项复核（HG-SEC-027 关闭）

- **review 者**: Security Reviewer（L2）
- **Scope**: 未 push 1 commit（`a331ac1` fix@html-gen: backfill countries provinces columns from final provinces data）；用户决策 1B 修复
- **Verdict**: ✅ PASS 100/A（🔴 0 / 🟡 0 / 🟢 0，HG-SEC-027 关闭）

### Summary

a331ac1 将反向回填事实源从脚本内硬编码 PROVINCES 常量改为读取最终 `data/_provinces-data.json`（含人工复核编辑），关联列按「、」split；独立重跑 backfill vs 提交态 195 国 × 3 列 585 格 **0 差异**。5 字段变化全部符合预期：3 处补全（德国 area_province=黑龙江 / 西班牙 gdp_province=广东 / 斯里兰卡 pop_province=北京、上海）+ 2 处过期残留清除（土库曼斯坦 area_province=四川 / 澳大利亚 gdp_province=江苏）。双向互证率 271/304=89.1% → **274/304=90.1%**，30 个剩余 miss 全部为双侧 top-3 截断（rank 4-8），**0 个非截断/不对称格**，原 4 格不对称全部修复。省份表 `_provinces-data.json` 零改动；生成物 countries-table.html 195 行与 JSON 逐字段 0 差异。专项 26 passed（test_provinces_table 13 + test_countries_table 13）；全量 164 passed + 3 环境性 WIP 失败（daming/yongzheng/history strategy-table 系并发会话重生成 9 列 schema，与本次零交集，不代修不扣分）。commit 仅 3 文件（脚本 +11/-3 / 国家表 JSON / 生成物 1 行），无 WIP 混入。授权 push 1 commit 至 github/main。

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-027 | 复核后未重跑 backfill（4 格不对称） | 🟢 | P3 | ✅ Closed（a331ac1，2026-08-24 尾项复核） |

- 报告: `documents/review/provinces-table-implementation-review-v1.0-20260824.md`（追加「尾项复核 — HG-SEC-027 关闭」章节）
- 处理: PASS → 授权 push 1 commit（a331ac1）至 github/main

---

## 2026-08-24 — provinces 匹配规则 v1.2 变更复核（用户决策 1A/2A/3A/4B）

- **review 者**: Security Reviewer（L2）
- **Scope**: 未 push 2 commits（`a148b8d` docs rename provinces-table-design v1.1→v1.2 / `db4d818` fix@html-gen: countries provinces columns as country-basis independent match + overflow notes）；ops 直改 + review 尾项复核（不走设计评审）
- **Verdict**: ✅ PASS 100/A（🔴 0 / 🟡 0 / 🟢 1 record：HG-SEC-028）

### Summary

v1.2 匹配规则变更复核通过：**范围** a148b8d 纯文档 rename（R078 仅 1 文件），db4d818 恰 3 文件（provinces-match.py / _countries-data.json / countries-table.html），无 WIP 混入。**匹配语义**（决策 1A/3A）国家侧由"同对回填"改为"国家为基准独立 pick_hits"（Δ 以国家值为基准，阈值 30/20/30%），独立复算 JSON 856 组合对 / 386 维度对 **0 阈值违规**（用户"506 对"为口径差异，0 违规一致）；独立 top-3 与 JSON 无损镜像（0 遗漏/0 多余）。抽查全对：亚美尼亚 面积=海南/台湾（Δ19.2% 不再被省份侧 top-3 挤掉，v1.1 缺陷修复）、加拿大 人口=福建/辽宁/陕西（陕西 Δ4.2%）、俄罗斯 人口=广东 + GDP=广东/江苏、韩国 GDP=广东/江苏、柬埔寨 面积=广东/贵州/湖北。**超限 note**（决策 2A）与设计 §四 6 逐字一致（动态极值新疆/澳门/广东/西藏，`; ` 连接，既有前缀保留如"无世界银行数据"/"实际行政科托努; GDP: 无相近..."），超限但 note 缺失 0、陈旧 note 0；范围内无命中仅留空符合设计语义。**空国家** 3 列全空 28 国全部可解释（中国/印度/美国大国超限 note 完整、梵蒂冈数据缺口、其余微国家）。**测试** 专项 26 passed；全量 164 passed + 3 环境性 WIP 失败（daming/yongzheng/history strategy 表被另一会话 13:15-13:35 重生成，工作区表头 ≠ HEAD，与 db4d818 零交集，不代修不扣分）。**生成物** countries-table.html 195 行与 JSON 逐字段 0 差异；`_provinces-data.json` 零改动。唯一 🟢 HG-SEC-028 为脚本 pick_hits 命名/docstring 仍为省份侧语义（国家侧复用），纯注释陈旧不影响产物。授权 push 2 commits 至 github/main。

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-028 | pick_hits 命名/docstring 仍为省份侧语义（v1.2 国家侧复用），注释陈旧 | 🟢 | P3 | 📌 Record（下轮整理脚本时泛化命名） |

- 报告: `documents/review/provinces-table-design-v1.2-change-review-20260824.md`
- 处理: PASS → 授权 push 2 commits（a148b8d / db4d818）至 github/main


## 2026-08-24 — index 落地页同步 6-commit 审计（CONDITIONAL PASS）

- **review 者**: Security Reviewer（L2）
- **Scope**: 未 push 6 commits（e1add13/0b015a4/25f299a/5e9508a/775d27f/28000b2）— index 主题切换+复制按钮+footer+动态两屏+github-corner light、demos 双源同步、drama 测试同步 11 列
- **Verdict**: ⚠️ CONDITIONAL PASS 75/100（B）（🔴 1 / 🟡 2 / 🟢 5）

### Summary

6-commit 变更集审查：落地页主题切换（:root.light + `html-gen:index_theme`，try/catch + 白名单）、5 处复制按钮（clipboard+execCommand fallback）、footer、1500px 2 列断点、动态两屏 hero（innerHeight−110 + resize 重算）、github-corner light 深三角+白猫均实现正确；demos/index.html 双源同步到位。**数据验证**：专项 21 passed（10.32s）、全量 180 collect 与 AGENTS.md 逐文件计数一致、drama 23 passed；AGENTS.md 双源漂移段与实现一致。**主要问题**：① HG-SEC-029（🔴 提交完整性）——28000b2 测试断言 11 列结构，但 4 个 drama strategy-table 的 11 列数据文件（+1719 行）仍在工作区未提交，单独 checkout 本 6-commit 单元全量会失败 3+ 用例；② HG-SEC-030（🟡 可访问性）——demos 页浅色模式"案例演示清单"/Layer 卡硬编码深色色值，h2 #e0e0e0 on #f5f5f5 ≈1.25:1 近乎不可见；③ HG-SEC-031（🟡 CSS 特异性）——root 页深色模式 `.github-corner` (0,1,0) 被全局 `a:hover` (0,1,1) 击败，实测 hover 时 octocat 变 indigo（浅色模式有保护、深色缺失）。无安全漏洞（无注入面/无凭证/无外部脚本），🔴 属非安全类提交完整性问题故按 B 条件通过。

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-029 | 28000b2 测试断言依赖未提交 11 列数据（提交单元不自洽） | 🔴 | P1 | Open |
| HG-SEC-030 | demos 页浅色模式案例清单/Layer 卡对比度不达标（h2 ≈1.25:1） | 🟡 | P1 | Open |
| HG-SEC-031 | root github-corner 深色 hover octocat 变 indigo（a:hover 特异性压制） | 🟡 | P2 | Open |
| HG-SEC-032 | demos 页内部 target=_blank 缺 rel="noopener"（与根页不一致） | 🟢 | P2 | Open |
| HG-SEC-033 | hero 复制按钮"📋 复制"点击后重置为"📋"（标签丢失） | 🟢 | P3 | Open |
| HG-SEC-034 | execCommand fallback 假成功反馈（抛异常/返回 false 仍 ✅） | 🟢 | P3 | Open |
| HG-SEC-035 | 主题按钮无 aria-pressed/状态语义 | 🟢 | P3 | Open |
| HG-SEC-036 | html-gen.py 行数漂移：AGENTS.md 569 / demos 546 / 实际 958 | 🟢 | P3 | Open |

- 报告: `documents/review/index-landing-sync-review-v1.0-20260824.md`
- 处理: CONDITIONAL PASS → 不 push；修完 P1（HG-SEC-029/030）后通知复查

---

## 2026-08-24 — index 落地页同步 6-commit 审计复查（HG-SEC-029..036 修复验证）

- **review 者**: Security Reviewer（L2）
- **Scope**: 未 push 修复 commits（`30add19` data@drama 11 列 strategy-table ×4 + `c7a5bf0` fix@index HG-SEC-030..036）；上轮 CONDITIONAL PASS 75/B 的 8 项 findings 逐一验证
- **Verdict**: ✅ **PASS 100/100（A）**（7 项完整修复 + 1 项主体修复降 🟢）

### Fix Verification

| # | 原严重度 | 修复 commit | 验证 | 结论 |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-029 | 🔴 P1 | 30add19 | 4 个 strategy-table 随测试断言一并提交（+1668 行），11 列结构（derivative/homology/synonym/antonym）确认；提交单元自洽 | ✅ 已修复 |
| HG-SEC-030 | 🟡 P1 | c7a5bf0 | 浅色对比度实测：h2 #1f2328 = **14.49:1**、p #57606a = **5.86:1**、Layer 卡 p ≈**6.35:1** 全部达标；code #6366f1 = **3.43:1** ⚠️ 残余（0.7rem 小字仍略低 AA 4.5:1） | ⚠️ 主体修复 → 🟢 residual |
| HG-SEC-031 | 🟡 P2 | c7a5bf0 | 双页 `.github-corner:hover { color: var(--gh-octocat); }` 补齐，深色 hover 不再变 indigo（特异性 0,1,1 vs 0,1,0 已保护） | ✅ 已修复 |
| HG-SEC-032 | 🟢 P2 | c7a5bf0 | demos 18/18、根页 17/17 target=_blank 全带 rel="noopener"（0 缺失）；test_05 features 增断言 | ✅ 已修复 |
| HG-SEC-033 | 🟢 P3 | c7a5bf0 | copyText orig 保存原标签，恢复不丢「📋 复制」文案 | ✅ 已修复 |
| HG-SEC-034 | 🟢 P3 | c7a5bf0 | fallback 检查 execCommand 返回值，false/异常不标记 ✅ | ✅ 已修复 |
| HG-SEC-035 | 🟢 P3 | c7a5bf0 | themeBtn 初始 + updateThemeBtn 均同步 aria-pressed（false/true） | ✅ 已修复 |
| HG-SEC-036 | 🟢 P3 | c7a5bf0 | wc -l html-gen.py = 958，AGENTS.md + demos 页同步 958 | ✅ 已修复 |

### Summary

8 项 findings 全部处置完毕：HG-SEC-029 提交完整性由 30add19 关闭（4 个 11 列 strategy-table 数据文件随测试断言一并入仓，单独 checkout 单元全量不再失败）；HG-SEC-030 主体达标（案例清单 h2/p + Layer1/3 卡 p 改语义变量后 5.86:1~14.49:1，远超原 1.25:1~2.3:1），仅 code 元素 3.43:1 残余降 🟢；HG-SEC-031/032/033/034/035/036 逐一核实代码级修复真实落位（非仅 commit 消息）。**数据验证**：全量 pytest `-n 4`（py3.12 env）**180 passed in 34.08s**（20 文件，无回归）；rel="noopener" 双页 0 缺失；html-gen.py 958 行三处一致。无安全漏洞（无注入面/无凭证/无外部脚本），8 项无 🔴/🟡 剩余，评分 75 → 100。

### Residual

- **HG-SEC-030-residual** 🟢：`html-gen demo list` code（0.7rem）对比度 3.43:1 仍略低于 AA 4.5:1，可改 var(--cobalt-700) 或加粗进一步达标（不阻断）

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-029 | 28000b2 测试断言依赖未提交 11 列数据（提交单元不自洽） | 🔴 | P1 | ✅ Closed (30add19) |
| HG-SEC-030 | demos 页浅色模式案例清单/Layer 卡对比度不达标 | 🟡 | P1 | ⚠️ Closed (c7a5bf0, code residual → 🟢) |
| HG-SEC-031 | root github-corner 深色 hover octocat 变 indigo | 🟡 | P2 | ✅ Closed (c7a5bf0) |
| HG-SEC-032 | demos 页内部 target=_blank 缺 rel="noopener" | 🟢 | P2 | ✅ Closed (c7a5bf0) |
| HG-SEC-033 | hero 复制按钮点击后标签丢失 | 🟢 | P3 | ✅ Closed (c7a5bf0) |
| HG-SEC-034 | execCommand fallback 假成功反馈 | 🟢 | P3 | ✅ Closed (c7a5bf0) |
| HG-SEC-035 | 主题按钮无 aria-pressed 状态语义 | 🟢 | P3 | ✅ Closed (c7a5bf0) |
| HG-SEC-036 | html-gen.py 行数文档漂移 | 🟢 | P3 | ✅ Closed (c7a5bf0) |

- 报告: `documents/review/index-landing-sync-review-v1.0-20260824.md`（§八 复查章节）
- 处理: PASS → 授权 push（13 commits 本地 + 本轮审计交付物）至 github/main

---
## 2026-08-24 — pages-index skill + demos-index sync 3-commit 审计（PASS）

- **Reviewer**: Security Reviewer
- **Level**: L2 (commit-range-audit)
- **Scope**: 7a0f591 docs@skills pages-index SKILL.md（117 行新文档 + AGENTS.md 树同步）/ a75733f chore@project handoff updated_at 2026-08-22→2026-08-24 / 4b06b8d sync@demos-index demos/demos-index.html 重建（内联 style-guide.css --text-*/--gh-* + :root.light 浅色组，+50/-3）
- **Verdict**: ✅ **PASS 100/100（A）**
- **Score**: 100 / 100
- **Tracking**: HG-SEC-037（🟢 记录性）
- **Findings**: 0 🔴 / 0 🟡 / 1 🟢

### 验证明细

| 项 | 结果 |
|:---|:---|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → **180 passed in 33.12s**（基线一致，无回归） |
| prompt 输出 | `python3 html-gen.py prompt pages-index --brief` → exit 0，description + 9 章节正常 |
| skill 注册 | prompt --json 含 pages-index |
| SKILL.md vs index.html 一致性 | 6/6 落位: themeBtn right:88px (index.html:196)、html-gen:index_theme (447,452)、innerHeight-110 (430)、copyText orig 恢复 + execCommand 返回值检查 (458-468)、--gh-corner-fill/--gh-octocat 深浅两组 (187-190,237)、:root.light 组 (style-guide.css 9 处) |
| 模板页 theme key 声称 | doc_theme (layout-doc.html:300) / kw_theme (layout-knowledge.html:258) / layoutslide_theme (slide-demo.html:1003) 三处全实 |
| 双源防漂移测试 | test_demos_index.py:83-104 features 与 SKILL.md 声称一致 |
| demos-index 无 JS 错误 | selenium 直接加载 → JS errors NONE、18 行表格渲染、排序点击 OK、themeBtn=0、light 未激活 |
| 生成器回归 | 重新生成 diff 已提交产物 → 仅 title 参数差异（预期），0 实质差异 |
| 提交格式 | 3/3 `type@scope: subject`（docs@skills / chore@project / sync@demos-index） |
| git 状态 | clean（无未跟踪文件）；main 领先 github/main 恰好 3 = 评审范围 |

### Findings

- 🟢 SEC-037 — demos/demos-index.html 页面本身无直接 Selenium 测试覆盖（test_demos_index.py 加载的是 demos/index.html 模板展示首页）。本次手动验证通过，建议后续将 demos-index 页面纳入测试 URL 列表兜底重建回归。记录性，不阻断。

- 报告: `documents/review/pages-index-skill-demos-index-sync-review-v1.0-20260824.md`
- 处理: PASS → 授权 push 至 github/main

---

## 2026-08-25 — index 落地页优化 3-commit 审计（PASS）

- **Reviewer**: Security Reviewer
- **Level**: L2 (commit-range-audit)
- **Scope**: 2c299ce feat@index（hero badges + 安装&快速开始合并行内复制 + 竞品对比卡 + hero-logo + footer favicon + hero 减留白 −55px）/ 8260291 test@index（+3 用例: badges/对比卡/logo, 计数 5→11, hero min-height 语义化）/ aa5bf38 docs@skills（SKILL.md 骨架 + AGENTS.md 双源段 −55）
- **Verdict**: ✅ **PASS 95/100（A）**
- **Score**: 95 / 100
- **Tracking**: HG-SEC-038（🟡 → closed 93993cb）/ HG-SEC-039..040（🟢 → closed 93993cb）
- **Findings**: 0 🔴 / 1 🟡 / 2 🟢

### 验证明细

| 项 | 结果 |
|:---|:---|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → **183 passed in 35.85s**（基线 180 + test_16/17/18，无回归） |
| prompt 输出 | `prompt pages-index --brief` → exit 0，10 章节含新增「Footer favicon 图标化」 |
| favicon 外链 | jaden.tech / github / gitee 三 URL 全 **200** |
| 对比卡溢出 | 5 视口实测 scrollWidth==clientWidth，340px 级卡内无溢出/截断（460px 表于 500px 卡 / 404px 于 444px 卡） |
| hero 动态两屏 | 1400×900 hero 764 ≥ vh−55 ✓；390 宽内容撑高 1140，min-height 语义正确 |
| hero-logo | 实载 naturalWidth 344，无 JS 错误（全视口 0 SEVERE/ERROR） |
| 双源同步 | demos footer favicon 已同步，test_05 12 特征双源一致 |
| 提交格式 | 3/3 `type@scope: subject` |
| git 状态 | clean |

### Findings

| # | Severity | Title | File:Line | Status |
|:---|:---:|:---|:---|:---:|
| HG-SEC-038 | 🟡 | PATH 行内复制 `data-copy` 内引号未转义，live DOM 截断为 `export PATH=`（复制得无效命令） | index.html:289 | ✅ RESOLVED（93993cb `&quot;` 转义 + test_10 精确值断言） |
| HG-SEC-039 | 🟢 | test_10 仅断言 data-copy 非空，未覆盖值完整性（截断缺陷未被测试暴露） | tests/test_index_landing.py | ✅ 已同步（test_10 精确值断言） |
| HG-SEC-040 | 🟢 | SKILL.md badge 示例 3 项 vs 实现 4 项（「3-4」范围可涵盖，非漂移） | skills/pages-index/SKILL.md | ✅ 已同步（badge 4 项一致） |

### Positives

- 「复制全部」data-copy 用 `&#10;`/`&quot;` 正确转义，live DOM 实测 6 行命令完整（含换行与引号）
- 对比卡转置方案（6 维度 × 4 工具）340px 级卡内实测无溢出，http-server 实证成功回哺
- hero-logo/favicon 外链 3/3 验证 200；img 非可执行资源，无 SRI 需求
- 新增测试覆盖 badges/对比卡/logo/favicon 四特性，183 全绿

- 报告: `documents/review/html-gen-index-optimize-review-v1.0-20260825.md`
- 处理: PASS → 授权 push 至 github/main（3 commits + 本轮审计交付物）

---

## 2026-08-25 — HG-SEC-038 修复复查（PASS 100/A）

- **Reviewer**: Security Reviewer
- **Level**: L2 (commit-range-audit recheck)
- **Scope**: 93993cb fix@index（HG-SEC-038 PATH data-copy `&quot;` 转义 + test_10 精确值断言 + SKILL.md badge 4 项同步）
- **Verdict**: ✅ **PASS 100/100（A）**
- **Score**: 100 / 100
- **Tracking**: HG-SEC-038..040（closed 93993cb）
- **Findings**: 0 🔴 / 0 🟡 / 0 🟢

### 验证明细

| 项 | 结果 |
|:---|:---|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → **183 passed in 35.44s**（基线 183，无回归） |
| PATH data-copy | index.html:289 `data-copy="export PATH=&quot;$HOME/.local/bin:$PATH&quot;"` 转义完整；live DOM `getAttribute('data-copy')` == `export PATH="$HOME/.local/bin:$PATH"`（test_10 精确值断言，截断不再发生） |
| 类级扫描 | 全页 11 处 data-copy 正则扫描 0 未转义内引号（修复类级，非单点） |
| 复制全部 | data-copy 6 行含安装 + slide 命令，test_10 断言 `bash install.sh install` 与 `html-gen slide` 均含 |
| SKILL.md | badge 示例 ⚡ 零依赖 · 🌙 深色主题 · 🇨🇳 中文优先 · 📦 单文件 = 实现 4 项一致 |
| 提交格式 | `fix@index: subject` ✓ |
| git 状态 | clean；main 领先 github/main 1（93993cb）+ 本轮审计交付物 |

### Findings

无剩余问题。HG-SEC-038（🟡）/ HG-SEC-039..040（🟢）全部关闭，评分 95 → 100。

- 报告: `documents/review/html-gen-index-optimize-review-v1.0-20260825.md`（§五 复查记录）
- 处理: PASS → 授权 push（93993cb + 审计交付物）至 github/main

---

## 2026-08-27 — 四模板字体倒挂修复 3-commit 审计（CONDITIONAL PASS 80/B）

- **Reviewer**: Security Reviewer
- **Level**: L2 (commit-range-audit)
- **Scope**: 8079a28 feat@templates（doc/slide 容器 font-size 0.88rem + blockquote 紧凑）/ 107affc sync@demos（25 doc 产物重生成 + slide-demo 样式同步）/ 151a929 test@templates（TestDocTypography 2 用例 + AGENTS 185）— 决策 1A/2A/3A/4A/5A
- **Verdict**: ⚠️ **CONDITIONAL PASS 80/100（B）** — 不 push
- **Score**: 80 / 100
- **Tracking**: HG-SEC-041（🔴 未修）/ HG-SEC-042（🟡 未修）
- **Findings**: 1 🔴 / 1 🟡 / 0 🟢

### 验证明细

| 项 | 结果 |
|:---|:---|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → **185 passed in 32.66s**（基线 183 + 2 新用例） |
| 模板 | layout-doc/slide 均含 font-size 0.88rem + blockquote 紧凑；callout 特异性覆盖保持 ✓ |
| doc 产物抽查 | core-products.html 含 0.88rem + 紧凑 blockquote + callout 保留，变量基座完整 ✓ |
| slide-demo.html | ❌ 变量基座丢失（SEC-041）+ 重复 style 块（SEC-042）— headless Chrome 实测 body bg 透明/text 黑 |

### Findings

| # | Severity | Title | File:Line | Status |
|:---|:---:|:---|:---|:---:|
| HG-SEC-041 | 🔴 | slide-demo.html 丢失 `:root { --cobalt-* }` 变量基座，深色主题失效 | demos/slide-demo.html:8-216 | ⏳ OPEN |
| HG-SEC-042 | 🟡 | 重复 `<style>` 块，旧副本 blockquote 0.75rem/8px 覆盖新紧凑值 | demos/slide-demo.html:330 vs 122 | ⏳ OPEN |

### Positives

- 1A 容器基座方案合理，li 继承统一；h/table/code 显式 rem 不受影响
- 3A callout 保持正确（高特异性选择器覆盖）
- 25 doc 产物重生成正确，变量基座完整，无正文意外变化
- 新测试精确断言 14.08px + blockquote 紧凑

### 根因

107affc 对 slide-demo.html 的「从 layout-slide 提取替换」错误替换了第一个 `<style>` 块的 `:root` 变量基座（应更新第二个 slide 样式块），导致变量丢失 + 重复样式块。

- 报告: `documents/review/html-gen-typography-review-v1.0-20260827.md`
- 处理: CONDITIONAL PASS → 不 push，修完后通知复查

---

## 2026-08-27 — 四模板字体倒挂修复复查（HG-SEC-041/042 关闭，PASS 100/A）

- **Reviewer**: Security Reviewer
- **Level**: L2 (commit-range-audit recheck)
- **Scope**: 8347dd8 fix@demos（slide-demo 单 style 块 + style-guide 变量基座恢复）；上轮 CONDITIONAL PASS 80/B 的 2 项 findings 逐一验证
- **Verdict**: ✅ **PASS 100/100（A）**（2 项完整修复）
- **Score**: 100 / 100
- **Tracking**: HG-SEC-041..042（closed 8347dd8）
- **Findings**: 0 🔴 / 0 🟡 / 0 🟢

### Fix Verification

| # | 原严重度 | 修复 | 验证 | 结论 |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-041 | 🔴 | 8347dd8 恢复 `:root { --cobalt-* }` 变量基座（style-guide.css 全文 + :root.light + layout-slide 样式合并为单 `<style>` 块） | headless Chrome 实测 --cobalt-500=#6366f1 / --cobalt-400=#818cf8 / --surface-900=#11111b / --font-mono='JetBrains Mono' / body bg=rgb(10,10,20) 深色 / text=rgb(224,224,224) 浅色 | ✅ 已修复 |
| HG-SEC-042 | 🟡 | 8347dd8 删除重复 `<style>` 块（2→1），blockquote 紧凑值 0.1rem/2px 16px 生效 | `<style>`=1 / `</style>`=1；`.slide-page blockquote { margin: 0.1rem 0; padding: 2px 16px }`（无旧 0.75rem/8px 副本） | ✅ 已修复 |

### 验证明细

| 项 | 结果 |
|:---|:---|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → **185 passed in 33.03s**（无回归） |
| style 块 | slide-demo.html 恰 1 个 `<style>`（grep 计数 1 开 1 闭） |
| 变量基座 | --cobalt-50..950 / surface / text / border / code / hero / gh / font / radius 全套 37 定义恢复；:root.light 浅色组完整 |
| --cobalt-500 | getComputedStyle 计算值 #6366f1 生效 |
| body | background rgb(10,10,20) 深色（原透明）、color rgb(224,224,224) 浅色（原黑） |
| slide-page 排版 | font-size 0.88rem + blockquote 紧凑 0.1rem/2px 16px + callout 特异性覆盖保留 |
| JS 错误 | window.__testErrors = []（加载 + refresh 两轮） |
| git status | 仅 2 个非范围文件（countries-table.html / history-strategy-table.html，其他 session） |

### Summary

8347dd8 将 slide-demo.html 重建为单 `<style>` 块（style-guide.css 变量基座全文 + :root.light 浅色组 + layout-slide 样式），HG-SEC-041（变量基座丢失）与 HG-SEC-042（重复块覆盖）两项完整修复。headless Chrome 实测变量基座全套生效（--cobalt-500=#6366f1 等），深色主题恢复（body 深底浅字），无 JS 错误；185 tests 全绿无回归。评分 80 → 100。

### Tracking

| Issue | Title | Severity | Priority | Status |
|:---|:---|:---:|:---:|:---:|
| HG-SEC-041 | slide-demo.html 丢失 :root 变量基座 | 🔴 | P0 | ✅ Closed (8347dd8) |
| HG-SEC-042 | 重复 style 块覆盖 blockquote 紧凑值 | 🟡 | P2 | ✅ Closed (8347dd8) |

- 报告: `documents/review/html-gen-typography-review-v1.0-20260827.md`（§六 复查记录）
- 处理: PASS → 授权 push（8347dd8 + 审计交付物）至 github/main

---

## 2026-08-28 — table videos 字段设计 v1.0 审计（CONDITIONAL PASS 85/B）

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: b0896c1 docs@table: videos field design v1.0 (HTML-GEN-CL001) — table 模板新 col.type="videos"（数组多视频 url/title/duration/platform + maxShow 折叠默认3 + 平台图标映射 + countries 巴西行 2 条 douyin 联动）；决策 A1 B1 C1 D1 E3 F1 G
- **Verdict**: ⚠️ **CONDITIONAL PASS 85/100（B）** — 不 push
- **Score**: 85 / 100
- **Tracking**: HG-SEC-043（🟡 split 预览 [object Object]）/ HG-SEC-044（🟡 platform 归一化未指定）/ HG-SEC-045（🟡 长标题截断与 nowrap CSS 冲突）open；🟢 HG-SEC-046..052（OBS，随 v1.1）
- **Findings**: 0 🔴 / 3 🟡 / 7 🟢

### 验证明细

| 项 | 结果 |
|:---|:---|
| commit 范围 | `git show b0896c1 --stat` → 仅 1 文件（设计文档 +110），无代码/数据混入 ✓ |
| 数据文件 | _countries-data.json 17 列/195 行；顶层 title == demo `<title>` == 「全球国家速查表（195 国）」；0 行含 videos ✓ |
| 列尾追加安全 | test_countries_table.py 13 用例无列数/表头硬断言，tds[] 索引断言仅 0-6，videos 追加 index 17 不破坏 ✓ |
| 模板现状 | layout-table.html grep videos = 0（新分支）；escapeHtml(:367)/window.open noopener,noreferrer(:591)/pills(:529-544) 先例可复用 ✓ |
| split 预览风险 | renderSplitPreview(:986-991) 对数组 `String(v)` → `[object Object]`；countries 分栏可达（country_zh onCellClick:'split' + videos preview:true）✗ |
| 测试基线 | 188 defs / 20 文件（与 AGENTS.md 一致）；实跑 **185 passed / 3 failed** — 均为 134e3c6 数据漂移未同步测试（塞尔维亚 region_tags 3 值 / history-strategy 重构 / table-features subtitle），与本次评审无关 |

### Findings

| # | Severity | Title | Status |
|:---|:---:|:---|:---:|
| HG-SEC-043 | 🟡 | split 预览 videos 渲染 [object Object]；设计 §5「默认 kv-list」承诺与现模板不符 | ⏳ OPEN |
| HG-SEC-044 | 🟡 | platform 归一化（trim/lowercase/别名表）未指定 | ⏳ OPEN |
| HG-SEC-045 | 🟡 | 长标题截断（word-break）与 .cell-pill nowrap CSS 冲突 | ⏳ OPEN |
| HG-SEC-046..052 | 🟢 | OBS：+N 状态机 / onclick 转义 / col.videos 键名 / split 测试缺失 / 分三组非必要 / 空壳 pill / 搜索噪音 | 随 v1.1 |

### Positives

- A-G 决策闭环，六要素齐全，dev 可直接实施；复用 pills 视觉 + hrefKey 新标签页 + escapeHtml + searchFields 白名单
- F 独立新类型正确（pills 语义是字符串分隔筛选，videos 是对象数组链接组）
- countries 联动可验收：列尾追加不破坏 13 用例，巴西行数据完整，生成命令 title 一致
- 向后兼容：videos 空/缺省 → 空单元格；CLI 零改动（数据驱动注入）

### RIG 清单（ops 修 v1.1，全部 Bucket A）

| # | 项 | 修复 |
|:-:|:---|:---|
| RIG-001 | §5 分栏预览段重写 | Array.isArray 特判：split 预览与 expand detail 逐条渲染 [icon] title (duration)+url；§7 补 test_07 |
| RIG-002 | §5 平台映射补归一化一行 | trim + lowercase + 别名表 {抖音→douyin, b站→bilibili, youtube→youtube}；未命中 → 📹 |
| RIG-003 | §5/§9 截断边界明确 | `.video-pill`：max-width 180px + white-space:normal + word-break:break-all（或 nowrap+ellipsis 二选一） |

- 报告: `documents/review/table-videos-design-review-v1.0-20260828.md`
- 处理: CONDITIONAL PASS → 不 push；ops 修 v1.1 后复审

---

## 2026-08-28 — table videos 字段设计 v1.1 复审（PASS 95/A）

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: 99cede3 docs@table: videos design v1.1 (HTML-GEN-CL001) — RIG-001..003 fix (HG-SEC-043..045) + 🟢 OBS 规格落地 (046..052) + 数据漂移断言同步；git mv v1.0→v1.1 保留历史（b0896c1 + 99cede3）
- **Verdict**: ✅ **PASS 95/100（A）** — 闭环，转 dev 实施
- **Score**: 95 / 100
- **Tracking**: HG-SEC-043..045（🟡×3，closed v1.1）/ HG-SEC-046..052（🟢 OBS，closed v1.1）/ N1（🟡 §8.7 用例数 6→8 陈旧，closed v1.1 dev prompt 内嵌）
- **Findings**: 0 🔴 / 0 🟡 (初审) / 1 🟡 (新增 N1) / 0 🟢

### 复审核对摘要

| 初审项 | 状态 | 证据 |
|:---|:---:|:---|
| RIG-001 (HG-SEC-043) | ✅ | §5 L73-76 Array.isArray 特判（split+expand 逐条渲染）；§7 test_07 |
| RIG-002 (HG-SEC-044) | ✅ | §5 L64-68 trim().toLowerCase() 归一化 + 别名映射（抖音→🎵 / b站→📺） |
| RIG-003 (HG-SEC-045) | ✅ | §5 L69-71 .video-pill 独立类 max-width:180px + white-space:normal + word-break:break-all；§9 L123 同步 |
| 🟢 046..052 | ✅ | +N 状态机 / onclick 转义 / 键名说明 / split 测试 / -n 4 兜底 / title 必填 / 搜索排除 逐项落地 |
| 漂移断言 ×3 | ✅ | 实跑复现 3 failed：塞尔维亚 pills 3 值 / 实际表头 7 列 / history-strategy subtitle 非空；方案与现状精确一致 |

### 新增发现

- N1 🟡：§8.7「test_videos.py 6 用例」未随 §7 同步（现 8 用例）—— 纯文档文本陈旧，dev prompt 核心变更 #8 内嵌修复，不阻断闭环

### 验证明细

| 项 | 结果 |
|:---|:---|
| commit 范围 | `git show 99cede3 --stat` → 1 文件 rename +35/-14 ✓ |
| git mv 历史 | `git log --follow` → b0896c1 + 99cede3 ✓ |
| 漂移断言实跑 | python3.12 -m pytest 3 项定向 → 3 failed，diff 与设计期望精确一致 ✓ |
| 数据源 | _countries-data.json subtitle=None/title 有；_drama-table-history-strategy.json subtitle=《孙子兵法》描述 ✓ |
| 治理文件 | .review-level.yaml yaml.safe_load ✓（34 条历史，末条 open=3 → 本条 open=0）|

- 报告: `documents/review/table-videos-design-rereview-v1.1-20260828.md`
- 处理: PASS → 生成 dev 实施 prompt（`cache/review-prep/prompt-table-videos-dev-20260828.md`）转 dev；实施完成后 ops 核查 → review 实施审计 → push

---

## 2026-08-28 — table videos 字段实现审计（PASS 100/A）

- **Reviewer**: Security Reviewer
- **Level**: L2 (implementation-audit)
- **Scope**: HTML-GEN-CL001 实施链 7 commits（45bf232 feat@table videos column type / a42331e sync@demos countries videos + 巴西 douyin / a9e30fa test@table 8 selenium cases / 18199be fix@tests 漂移断言同步 / 2b3c997 docs@table features+AGENTS / a3f783e docs@table §8.7 N1 fix / 6b8a4c1 fix@data 巴西长标题 + 重生成）— 设计 v1.1（99cede3）+ 评审 PASS 95/A（2a49d6e）
- **Verdict**: ✅ **PASS 100/100（A）** — 闭环，转 push
- **Score**: 100 / 100
- **Tracking**: HG-SEC-053（🟢 record；countries 巴西行 videos 无提交级回归断言，建议后续补 test_15）
- **Findings**: 0 🔴 / 0 🟡 / 1 🟢

### 验收清单 §8 核对（7/7）

| # | 验收项 | 证据 | 结果 |
|:-:|:---|:---|:---:|
| 1 | pill 渲染（图标+标题+时长） | test_01 `🎵 巴西建国史 (8:37)`；countries 实载 `🎵 每天了解一个国家，巴西 (3:22)` | ✅ |
| 2 | maxShow 折叠 +N 展开（不折叠回/re-render 重置/stopPropagation） | test_02：+1 点击 → 3 pill 全显、+N 消失；搜索重渲染回折叠态；expandVideos onclick 带 stopPropagation | ✅ |
| 3 | 点击新标签页 noopener,noreferrer + onclick 转义 | test_03 拦截 window.open 断言 (url,_blank,noopener,noreferrer)；JSON.stringify+&quot; 转义两处沿用 | ✅ |
| 4 | 平台图标映射 + 归一化 trim().toLowerCase() | test_04 douyin→🎵/其他→📹/抖音→🎵/YouTube→▶️/bilibili→📺 | ✅ |
| 5 | 空/缺失 videos → 空单元格 | test_05 无字段 + [] 均空 | ✅ |
| 6 | countries 巴西行 2 douyin 可见（长标题完整） | Selenium 实载：2 pill `🎵 巴西建国史——巴西如何从创业成功走向贫穷漩涡 (8:37)` 可见；grep 生成 HTML 双 title/双 url 命中 | ✅ |
| 7 | test_videos 8 用例 + 回归全绿 | 定向 21 passed（8+13）；全量 **196 passed in 35.33s** | ✅ |

### 设计合规（v1.1 规格 4/4）

- searchKeys 排除 videos（无 searchFields 表）✅ layout-table.html:432-433 + test_08
- split/expand Array.isArray 特判（勿 [object Object]）✅ :1071-1075/:600-606 + test_07
- .video-pill 独立类 max-width:180px + white-space:normal + word-break:break-all ✅ :42-44
- CLI 零改动 ✅ 7 commits 无一触碰 html-gen.py

### 安全与治理

- 安全 ✅ noopener,noreferrer + escapeHtml + onclick 转义（:591 先例）；无新执行面
- 治理 ✅ 7/7 commit 规范 type@scope；features.md L120/156 注册；AGENTS.md 196 tests（21 文件实测一致）；漂移 3 断言 18199be 实修（另含 provinces backfill 列索引 −2/−4）；git clean

### 发现项

- HG-SEC-053 🟢：test_countries_table.py 无巴西行 videos 断言 —— countries 页面巴西行 videos 渲染无提交级回归护栏（本次审计运行时抽查验证通过，建议后续补 test_15）

### 验证明细

| 项 | 结果 |
|:---|:---|
| commit 链 | `git log --oneline -8` → 6b8a4c1 HEAD，7 实施 commits 齐全 ✓ |
| 定向测试 | `python3 -m pytest tests/test_videos.py tests/test_countries_table.py -q -n 0` → 21 passed ✓ |
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → 196 passed in 35.33s ✓ |
| 运行时抽查 | hermes-verify-countries-brazil.py → 8/8 PASS（巴西行 2 pill/长标题/🎵/noopener/无 JS 错误）✓ |
| 数据 | _countries-data.json 18 列/195 行；巴西 2 视频四项完整；第 2 条为 ops 修正长标题 ✓ |
| 生成 HTML | 双 title/双 url/maxShow/type=videos 均命中；title 与 JSON 一致 ✓ |
| 治理文件 | .review-level.yaml yaml.safe_load ✓（35 条历史，末条 open=0 → 本条 open=0）|

- 报告: `documents/review/table-videos-impl-audit-v1.1-20260828.md`
- 处理: PASS → 完成闭环信号，复盘 md 由 ops 生成；push 授权由 review profile 执行（github/main）

---

## 2026-08-29 — table videos syncer 设计 v1.0 审计（CONDITIONAL PASS 85/B）

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: `24b9cbc` docs@table: videos syncer script design v1.0 (HTML-GEN-CL002) — yaml 增量→按 country_zh 外键匹配 json 行→url 去重补充 videos→全局镜像回写 yaml→重建 demos；决策 A/B/C/D/E/F/G/W；test_sync_videos.py 10 用例；前置 HTML-GEN-CL001（videos 字段已闭环）
- **Verdict**: ⚠️ **CONDITIONAL PASS 85/100（B）** — 不 push
- **Score**: 85 / 100
- **Tracking**: HG-SEC-054（🟡 yaml.safe_load 未指定）/ HG-SEC-055（🟡 subprocess list-form 未指定）/ HG-SEC-056（🟡 target 路径解析基准未定义）open；🟢 HG-SEC-057..060（随 v1.1）
- **Findings**: 0 🔴 / 3 🟡 / 4 🟢

### 验证明细

| 项 | 结果 |
|:---|:---|
| commit 范围 | `git show 24b9cbc --stat` → 仅 1 文件（设计文档 +137），无代码/数据混入 ✓ |
| E 命令复现 | `python3 html-gen.py table -d data/_countries-data.json -o /tmp/cl002-repro.html` → 195 行 × 18 列 · 6 标签页；产物 `<title>` == JSON 顶层 title「全球国家速查表（195 国）」== cmd_table L424 无 --title 取 json_title ✓ |
| duration 60 进制坑 | `yaml.safe_load('6:55')` → 415 / `('11:38')` → 698，设计 §3 断言精确 ✓ |
| 缅甸/伊朗基线 | data/_countries-data.json：缅甸 L3170 无 videos（0 条）、伊朗 L470 1 条「中东为何永不团结」；grep `"videos"` 恰 10 数据行（§1「已有 10 行」成立）✓ |
| yaml 草稿 | cache/data/_countries-data.videos.yaml 与设计 §3 示例逐字一致（缅甸 1 + 伊朗 1，伊朗 url 与 json 既有不同 → 1→2 成立）✓ |
| videos 列渲染 | layout-table.html L636-685 col.type="videos" + VIDEO_PLATFORM_ICONS + maxShow + noopener,noreferrer；同步器输出 douyin/bilibili/youtube 均为模板可识别 ✓ |
| 回归面 | test_countries_table.py 14 用例 / test_videos.py 8 用例无列数/videos 硬断言；videos 增不减不改 195 行计数/tab 计数/region pills ✓ |
| 前置衔接 | CL001 设计 v1.1 §3/§5：yaml 字段（country_zh/title/url/duration/platform）与 videos 对象字段一致 ✓ |

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-054 | 🟡 | §4.2 step1「解析 yaml（PyYAML）」未 pin safe_load（yaml.load 任意代码执行面） | ⏳ OPEN |
| HG-SEC-055 | 🟡 | §4.2 step8 subprocess 未 pin list-form（target 路径来自 yaml，shell=True 有注入面） | ⏳ OPEN |
| HG-SEC-056 | 🟡 | target.data/html 相对路径解析基准未定义（CWD 契约缺失，E 命令依赖 CWD=项目根） | ⏳ OPEN |
| HG-SEC-057 | 🟢 | duration int 归一化仅覆盖 M:SS，H:MM:SS（如 1:02:03→3723）未指定 | 随 v1.1 |
| HG-SEC-058 | 🟢 | 脚本名 `vides` 拼写（新建文件零迁移成本，建议直接 videos） | 待确认 |
| HG-SEC-059 | 🟢 | url 尾部空白 strip 无显式用例（§7 已列风险，§5 未断言） | 随 v1.1 |
| HG-SEC-060 | 🟢 | §1 背景「134KB」已漂移为 131.7KB（工作树未提交 restructure，非 spec 载荷） | 随 v1.1 |

### Positives

- 四段式数据流清晰（yaml 增量 → json 事实源 → yaml 镜像 → 重建 demos），additive-only + F 校验先行 + G 幂等三层写盘安全，无回滚逻辑
- 8 决策闭环、10 用例覆盖 7 决策（B/D 为环境/依赖面合理豁免）、8 验收项与测试 1:1 无悬空
- duration 60 进制坑、url strip 去重、dry-run 默认态等边界在 §7 显式列出，规格严谨
- 复用 html-gen.py table 命令 + CL001 videos 渲染（noopener,noreferrer + escapeHtml 已审计），无重复造轮子
- B 决策正确隔离手写草稿（cache/ gitignored）与入库产物

### RIG 清单（ops 修 v1.1，全部 Bucket A 一句话补齐）

| # | 项 | 修复 |
|:-:|:---|:---|
| RIG-001 | §4.2 step1 | `解析 yaml（PyYAML，safe_load）` |
| RIG-002 | §4.2 step8 | `subprocess.run([...], shell=False)` 列表参数（python3 / html-gen.py / table / -d / -o），无 shell |
| RIG-003 | §4.2 step2 | 补「相对路径以项目根为基准解析（脚本须在项目根运行或推导项目根）」 |

- 报告: `documents/review/table-videos-syncer-design-review-v1.0-20260829.md`
- 处理: CONDITIONAL PASS → 不 push；ops 修 v1.1 后复审（PASS 后生成 dev 实施 prompt 转 dev）

---

## 2026-08-29 — table videos syncer 设计 v1.1 修正（RIG-001/002/003 + 🟢 落地，⏳ 待复审）

- **闭环**: HTML-GEN-CL002 ｜ **Step**: 设计（CONDITIONAL 修正路径 §5.1，git mv v1.0→v1.1 保留历史）
- **修正提交**: `431c1df` docs@design: CL002 design v1.1 — review fixes RIG-001/002/003 (HTML-GEN-CL002)（仅设计文档 1 文件，+18/-14）
- **RIG 落点**:
  - RIG-001 (HG-SEC-054) ✅ §4.2 step1：显式 `yaml.safe_load`（禁 yaml.load / FullLoader，防 `!!python/object` 任意代码执行）
  - RIG-002 (HG-SEC-055) ✅ §4.2 step8：`subprocess.run([sys.executable 或 python3, 'html-gen.py', 'table', '-d', target.data, '-o', target.html], shell=False)` 列表参数，禁 shell=True / 字符串拼接
  - RIG-003 (HG-SEC-056) ✅ §4.2 step2：补「相对路径以项目根为基准解析（脚本须在项目根运行或以脚本位置推导项目根），勿相对 cache/data/」一行，并注明覆盖 step8 重建路径
- **🟢 落地**: HG-SEC-057（duration int 容错仅 M:SS + H:MM:SS 必须引号，§2/§5 test_02/§7 同步）/ HG-SEC-058（脚本名 vides → tool-table-videos-syncer.py，§2/§4.1/§7 + draft 同步）/ HG-SEC-059（§5 test_05 增 url 尾部空格 strip 后去重/回写断言）/ HG-SEC-060（§1 134KB → 131.7KB 实测值）
- **状态**: ✅ RE-REVIEWED 2026-08-29: PASS 95/A（RIG-001/002/003 + 🟢 057..060 closed；HG-SEC-061 阈值 fold dev prompt；见下节）

---

## 2026-08-29 — table videos syncer 设计 v1.1 复审（PASS 95/A）

- **Reviewer**: Security Reviewer
- **Level**: L2 (design-document-review)
- **Scope**: `431c1df` docs@design: CL002 design v1.1 — review fixes RIG-001/002/003 (HTML-GEN-CL002)（git mv v1.0→v1.1 保留历史，仅 1 文件 +18/-14）
- **Verdict**: ✅ **PASS 95/100（A）** — 闭环，生成 dev 实施 prompt
- **Score**: 95 / 100
- **Tracking**: HG-SEC-054..056（🟡×3，closed v1.1）+ HG-SEC-057..060（🟢，closed v1.1）+ HG-SEC-061（🟡 新发现 duration 阈值 `<6000`→`<3600`，fold dev prompt）
- **Findings**: 0 🔴 / 1 🟡（新）/ 0 🟢（残留）｜ 实现 prompt: ✅ 已生成

### RIG 核验（复审核对项 1-3）

| RIG | HG-SEC | v1.1 落点 | 结果 |
|:---|:---|:---|:---:|
| RIG-001 | 054 | §4.2 step1 显式 `yaml.safe_load`，禁 yaml.load/FullLoader | ✅ |
| RIG-002 | 055 | §4.2 step8 `subprocess.run([...], shell=False)` 列表参数，禁 shell=True/字符串拼接 | ✅ |
| RIG-003 | 056 | §4.2 step2 相对路径以项目根为基准（勿相对 cache/data/）+ step8 引用覆盖重建路径 | ✅ |

### 🟢 落地核验（复审核对项 4）

| HG-SEC | 结果 |
|:---|:---:|
| 057 | ✅ §2/§5 test_02/§7 三处同步「仅 M:SS；H:MM:SS 必须引号」（⚠️ 阈值矛盾 → HG-SEC-061） |
| 058 | ✅ 全文 vides→videos（§2/§4.1/§7 + TODO draft），无残留脚本名 |
| 059 | ✅ test_05 增 url 尾部空格 strip 断言，保持 10 用例 |
| 060 | ✅ §1 134KB→131.7KB，无残留 |

### 新发现 HG-SEC-061（🟡）

§2 补充规格「int < 6000 按秒数归一化」与「未引号 3723 不在容错语义内」矛盾（3723 < 6000）。M:SS 上界 59:59=3599s，正确阈值 `<3600`。fold dev 实施 prompt 一并订正，非安全面，不阻断闭环。

### 验收清单 §6 可执行性（复审核对项 5）

8 项验收 + test_sync_videos 10 用例 + 回归面 1:1 映射无漂移，均保留可执行。

### Positives

- 3 个 🟡 RIG（安全面：safe_load / subprocess list-form / 路径基准）全部一句话级精确补齐，措辞直接覆盖初审要求
- 🟢 057..060 全落地且三处（§2/§5/§7）同步，无半落地/单处更新
- git mv v1.0→v1.1 保留历史（`git log --follow` 显示 24b9cbc + 431c1df），修订记录 §8 完整
- 唯一新发现为规格精度矛盾（阈值边界），非安全/架构缺陷

- 报告: `documents/review/table-videos-syncer-design-rereview-v1.1-20260829.md`
- dev 实施 prompt: `cache/review-prep/prompt-table-videos-syncer-dev-20260829.md`
- 处理: PASS → 闭环 + auto-push（github/main）；dev 按实施 prompt 落地 CL002

---

## 2026-08-29 — table/knowledge JSON 顶层 output 字段设计 v1.0 评审（CONDITIONAL PASS 75/B）

- **Reviewer**: Security Reviewer
- **Level**: L2（design-document-review）
- **Scope**: `e76bcde` docs@design: table/knowledge JSON 顶层 output 字段设计 v1.0（HTML-GEN-CL003）— `output` 字段内嵌渲染目标 + CLI `-o` 最高优先级 + 无输出中断 exit 1 + 批量文档化；决策 1A/2A/3/4A/5/6/7/8/9 全闭合
- **Verdict**: 🟠 **CONDITIONAL PASS 75/100（B）** — 修 v1.1 后复审
- **Score**: 75 / 100
- **Tracking**: HG-SEC-062（🔴 open）+ HG-SEC-063/064（🟡 open）+ HG-SEC-065/066（🟢 随 v1.1）
- **Findings**: 1 🔴 / 2 🟡 / 2 🟢

### Summary

4 点需求 + 9 项决策全部落位，优先级三态矩阵主路径无歧义，向后兼容零回归（grep tests/ 全部 table/knowledge 子进程调用均显式传 `-o`，doc/slide 无 JSON 分支，cmd_demo --rebuild L988 已传 output）。唯一 🔴 是实现落点遗漏：argparse L768/L779 自带 `default='index.html'`/`default='kb.html'`，未删则 `args.output` 恒真、JSON output 与中断分支不可达、特性空转。2 处 🟡（usage-guide.md 文档漂移 / D2 knowledge json_output 提取位置未指定）+ 2 处 🟢（`-o ""` 措辞 / `-g`+data output 测试缺口）。

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-062 | 🔴 | argparse `default='index.html'`/`'kb.html'`（L768/779）未纳入 D1/D2，三态步骤 2/3 不可达 | ⏳ OPEN |
| HG-SEC-063 | 🟡 | D5 遗漏 `demos/usage-guide.md`（:126「默认 index.html」将漂移） | ⏳ OPEN |
| HG-SEC-064 | 🟡 | D2 cmd_knowledge json_output 提取位置未指定（raw L475 最终化、items/data 键） | ⏳ OPEN |
| HG-SEC-065 | 🟢 | 矩阵「显式传入」未限定非空，`-o ""` 与 title/subtitle 空串语义不对称 | 随 v1.1 |
| HG-SEC-066 | 🟢 | §5 缺「`-g` + data 文件 output 生效」组合用例 | 随 v1.1 |

### Positives

- 需求覆盖完整，9 决策闭环，决策与 §3 细节逐条自洽无悬空
- 向后兼容论证到位且经实测复核（现有测试 0 依赖静默默认值、cmd_demo rebuild 已传 output、doc/slide 无 JSON 分支）
- 三态矩阵主路径（CLI > JSON > 中断）与 title/subtitle 优先级顺序自洽，空串/None 语义在 §3.1 显式声明「无清空语义」
- 零依赖约束遵守（纯 stdlib 三态解析）；错误处理对齐「数据文件不存在」的 stderr + exit 1 既有模式
- 测试规划正确声明纯 CLI 行为（subprocess 断言、无需 Selenium），主分支覆盖齐全

### RIG 清单（ops 修 v1.1）

| # | 项 | 修复 |
|:-:|:---|:---|
| RIG-1 (062) | D1+D2+§4 | L768/L779 删 argparse `default='index.html'`/`'kb.html'`（缺省 None）；§4「两处 cmd」更正为「两处 cmd + 两处 argparse default + 两处 JSON 分支」 |
| RIG-2 (063) | D5 | 增 `demos/usage-guide.md`：table 节 :126 改「必填（CLI -o 或 JSON output 二选一）」，knowledge 节 :186 同理 |
| RIG-3 (064) | D2 | 补「L475 raw 最终化后 `json_output = raw.get('output') if isinstance(raw, dict) else None`；knowledge 键为 items/data（非 columns）」 |

- 报告: `documents/review/table-knowledge-json-output-design-review-v1.0-20260829.md`
- 处理: CONDITIONAL PASS → 不 push；ops 修 v1.1 后复审（PASS 后生成 dev 实施 prompt 转 dev 按 D1-D6 实施）

---

## 2026-08-29 — table/knowledge JSON 顶层 output 字段设计 v1.1 复审（CONDITIONAL PASS 85/B）

- **Reviewer**: Security Reviewer
- **Level**: L2（design-document-review）
- **Scope**: `2454e37` docs@design: table/knowledge JSON output field design v1.1 — review fixes RIG-001/002/003（HTML-GEN-CL003）；v1.0 已删（HEAD 仅存 v1.1）；复审上轮 HG-SEC-062..066
- **Verdict**: 🟠 **CONDITIONAL PASS 85/100（B）** — 上轮 5 项全闭合，新发现 3 🟡 修 v1.2 后复审
- **Score**: 85 / 100
- **Tracking**: HG-SEC-062..066（✅ closed v1.1）+ HG-SEC-067/068/069（🟡 open）
- **Findings**: 3 🟡（新增）/ 0 🔴

### Summary

上轮 1 🔴 + 2 🟡 + 2 🟢 全数正确闭合：argparse L768/L779 默认值删除点（§3.4 点 1 + D1/D2）、knowledge json_output 提取位置（L475 raw 最终化后 isinstance(raw,dict)）、usage-guide.md 纳入 D5（:126/:186/:60 逐字核验）、§3.2 矩阵「CLI -o 非空」、§5「-g + data 带 output」用例——均实测落地无半落地。复审对影响面做系统性 grep 枚举，新发现 D5 仍漏 3 处表面：`features.md:23`（table -o 默认 index.html）、`skills/html-gen-cli-spec/SKILL.md:44`（默认 index.html / kb.html）、`src/html_gen/` pip 打包源（build-package.py 未纳入 D-list，已装 `html-gen` v3.3 入口将滞留旧默认）。无逻辑缺陷，均为文档/构建同步完整性缺口，且是 D5 完整性连续两轮的问题（v1.0 漏 usage-guide → v1.1 仍漏 3 处）。

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-062 | 🔴 | argparse `default='index.html'`/`'kb.html'`（L768/779）未纳入 D1/D2 | ✅ closed v1.1 |
| HG-SEC-063 | 🟡 | D5 遗漏 `demos/usage-guide.md`（:126「默认 index.html」） | ✅ closed v1.1 |
| HG-SEC-064 | 🟡 | D2 cmd_knowledge json_output 提取位置未指定 | ✅ closed v1.1 |
| HG-SEC-065 | 🟢 | 矩阵「显式传入」未限定非空 | ✅ closed v1.1 |
| HG-SEC-066 | 🟢 | §5 缺「-g + data output」组合用例 | ✅ closed v1.1 |
| HG-SEC-067 | 🟡 | D5 遗漏 `features.md`（:23「table -o 默认 index.html」将漂移） | ✅ closed v1.2 |
| HG-SEC-068 | 🟡 | D5 遗漏 `skills/html-gen-cli-spec/SKILL.md`（:44「默认 index.html / kb.html」） | ✅ closed v1.2 |
| HG-SEC-069 | 🟡 | D1-D6 未含 build-package.py 重生成 src/，已装 `html-gen` 入口行为漂移 | ✅ closed v1.2 |

### Positives

- 上轮 5 项意见逐条实测闭合，代码锚点（L441/L484/L768/L779/L473-475）与 usage-guide.md（:126/:186/:60）逐字一致，_demos-data.json 实测无 output 键
- 三态实现落点完整（6 处），knowledge json_output 提取位置（L474 raw 恒为 data 文件最终解析，有/无 -g 均成立）无歧义
- §3.2 空串语义（`-o ""` truthiness 视为未传）与 title/subtitle 的不对称已显式文档化、有意区分
- 向后兼容零回归（cmd_demo rebuild 已传 output / doc/slide md 派生 / 现有测试全部显式 -o）不变
- 测试规划 11 用例完整，纯 CLI subprocess 断言声明正确

### RIG 清单（ops 修 v1.2）

| # | 项 | 修复 |
|:-:|:---|:---|
| RIG-4 (067) | D5 | 增 `features.md`：L23「table -o 默认 index.html」改「必填（CLI -o 或 JSON output 二选一）」；顺带修 L10「doc -o 默认 index.html」既有错误（doc 实为 md 派生默认） |
| RIG-5 (068) | D5 | 增 `skills/html-gen-cli-spec/SKILL.md`：L44「默认 index.html / kb.html」改「必填（CLI -o 或 JSON output 二选一）」 |
| RIG-6 (069) | D-list | 补「`python3 scripts/build-package.py` 重新生成 src/html_gen/（含 skills 副本）；已 pip 安装（`~/.local/bin/html-gen` v3.3）需同步重装」；§4「代码 6 处」补注 src/ 打包源 |

- 兜底: dev 实施 D5 以全仓 `grep -rn "默认.*index.html\|默认.*kb.html\|default='index.html'\|default='kb.html'"` 结果逐项清点，避免第三轮遗漏
- 报告: `documents/review/table-knowledge-json-output-design-review-v1.1-20260829.md`
- 处理: ✅ RESOLVED → v1.2 (2026-08-29 re-review PASS 100/A，HG-SEC-067..069 闭合)

---

## 2026-08-29 — table/knowledge JSON 顶层 output 字段设计 v1.2 复审（PASS 100/A）

- **Reviewer**: Security Reviewer
- **Level**: L2（design-document-review）
- **Scope**: `0295e8f` docs@design: table/knowledge JSON output field design v1.2 — review fixes RIG-004/005/006（HTML-GEN-CL003）；复审上轮 HG-SEC-067..069
- **Verdict**: 🟢 **PASS 100/100（A）** — RIG-4/5/6 全部闭合，无新增 🔴/🟡，1 🟢 记录折入 D5
- **Score**: 100 / 100
- **Tracking**: HG-SEC-067..069（✅ closed v1.2）+ HG-SEC-070（🟢 record，折入 D5，非阻断）
- **Findings**: 1 🟢（记录）/ 0 🟡 / 0 🔴

### Summary

上轮 3 🟡（RIG-4/5/6）逐条实测闭合：features.md L10「doc -o 默认 index.html」+ L23「table -o 默认 index.html」逐字核验、skills/html-gen-cli-spec/SKILL.md L44「默认 index.html / kb.html」逐字核验、D7 build-package.py 同步 src/（实测 src 与根 byte-identical sha 459af1bf、`~/.local/bin/html-gen` v3.3 已装确认）。修订未引入新问题：D7 位于 D6 后（打包同步步骤）正确、§4「6 处」计数与 src/ 注记分离清晰、修订记录表完整。残留 1 🟢 HG-SEC-070：features.md 三条 `-o` 行中 L30（knowledge -o）未显式纳入 D5，且兜底 grep 模式（`默认.*`/`default=`）不会命中该行（L30 无「默认」字样）——非错误、非阻断，dev 实施 D5 时与 L23 对称改「必填」即可。

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-067 | 🟡 | D5 遗漏 `features.md`（:23「table -o 默认 index.html」将漂移） | ✅ closed v1.2 |
| HG-SEC-068 | 🟡 | D5 遗漏 `skills/html-gen-cli-spec/SKILL.md`（:44「默认 index.html / kb.html」） | ✅ closed v1.2 |
| HG-SEC-069 | 🟡 | D1-D6 未含 build-package.py 重生成 src/，已装 `html-gen` 入口行为漂移 | ✅ closed v1.2 |
| HG-SEC-070 | 🟢 | features.md:30（knowledge `-o`）未显式纳入 D5，兜底 grep 不命中；与 L23 对称改「必填」 | ⏳ 折入 D5（dev） |

### Positives

- RIG-4/5/6 三处修复锚点逐字实测核验通过（features.md L10/L23、cli-spec SKILL.md L44、build-package.py src 同步），无半落地
- src/html_gen/html-gen.py 与根 html-gen.py byte-identical（sha256 前缀 459af1bf）实测确认；已装 CLI `~/.local/bin/html-gen` v3.3 存在，D7 确为必要步骤
- 修订未引入新问题：D7 位置正确、§4 影响面计数一致、§0 修订记录表完整
- 兜底 grep 枚举已采纳（§4 D5 末条），连续三轮的「文档同步清单遗漏」问题得到机制性收敛

### 实现 prompt

- ✅ 已生成（dev 按 D1-D7 实施；D5 补 features.md L30 与 L23 对称改「必填」）

- 报告: `documents/review/table-knowledge-json-output-design-review-v1.2-20260829.md`
- 处理: PASS → 生成 dev 实施 prompt + auto-push；dev 按 D1-D7 实施

---

## 2026-08-29 — table/knowledge JSON 顶层 output 字段实现审计（PASS 100/A）

- **Reviewer**: Security Reviewer
- **Level**: L2（implementation-audit）
- **Scope**: `f6efacb` fix@html-gen（源码三态 + test_json_output 11 用例）→ `27a4470` docs@html-gen（D5 文档同步 13 文件）→ `1fae2fd` docs@html-gen（AGENTS 计数 224→235）（HTML-GEN-CL003）；设计 v1.2 PASS 0295e8f
- **Verdict**: 🟢 **PASS 100/100（A）** — D1-D7 全数落地，ops 8 项证据逐条实测复核通过，HG-SEC-070 闭合
- **Score**: 100 / 100
- **Tracking**: HG-SEC-070（✅ closed 本次 D5，features.md L30 对称改「必填」）+ HG-SEC-071..072（🟢 records，非阻断）
- **Findings**: 2 🟢（记录）/ 0 🟡 / 0 🔴

### Summary

实现链对设计 D1-D7 全数落地且逐条实测核验。三态逻辑 `CLI -o > JSON 顶层 output > 中断(exit 1)` 在 cmd_table（L447-450）与 cmd_knowledge（L496-499）正确实现；根因位 argparse 两处 `default='index.html'/'kb.html'` 已删（L790/L801，原设计锚点 L768/779 因 HELP 增行漂移，内容定位正确）；NO_OUTPUT_MSG 共用常量（L28）+ stderr + 写盘前中断；knowledge 决策 7（只认 data output、groups 忽略）经 test_08/test_09 锁定。11 用例覆盖设计 §5 全表，tempfile 每用例隔离 xdist 兼容。D5 文档同步 8 表面全齐，HG-SEC-070（features.md L30）对称修正闭合，兜底 grep（*.py/*.html/*.md 排除历史）0 残留。D7 打包源 src/html_gen/html-gen.py 与根 byte-identical（sha256 7e50ad87），已装 `~/.local/bin/html-gen` 为 exec 根源码 thin wrapper 无 stale 风险。全量 235 passed 无回归；3 commit 自洽，drama WIP（data/_drama-table-history-strategy.json + demos/drama/history-strategy-table.html）为另一会话 pre-existing 未提交修改，不在 commit 内。

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-070 | 🟢 | features.md:30（knowledge `-o`）未纳入 D5，兜底 grep 不命中 | ✅ closed 本次 D5（对称改「必填」） |
| HG-SEC-071 | 🟢 | 设计 argparse 行号锚点 L768/779 → 实际 L790/801（HELP 增行漂移），内容定位正确 | ✅ record（非缺陷） |
| HG-SEC-072 | 🟢 | test_05 未单独覆盖「CLI 空串+皆无 JSON→中断」子分支（等价 test_03 truthiness 路径） | ✅ record（可选补断言） |

### Positives

- 根因位修复到位：不删 argparse default 则 `args.output` 恒真、三态步骤 2/3 不可达——两处 default 已删，特性非空转
- ops 8 项证据逐条实测复核通过（含 demo --rebuild 幂等、src byte-identical、235 passed），无「声称已测实未发生」
- HG-SEC-070（设计评审 🟢 残留）由 dev 在 D5 中与 L23 对称修正，闭环完整
- 打包源双保险：src/ gitignored 生成物已同步 + 已装 CLI exec 根源码，优于设计评审时的 stale 担忧
- 兜底 grep 全仓清点 0 残留，连续三轮的「文档同步清单遗漏」问题收敛

### 处理

- ✅ PASS → 审计三件套 + commit + auto-push（github + gitee 双 remote）

- 报告: `documents/review/table-knowledge-json-output-impl-audit-v1.0-20260829.md`

---

## 2026-08-29 — html-gen favicon + URL状态 + syncer参数 设计评审（PASS 85/A）

- **Reviewer**: Security Reviewer
- **Level**: L2（design-document-review）
- **Scope**: `9a9c608` docs@design: html-gen favicon 默认注入 + table URL 状态分享 + syncer 参数体系 设计 v1.0（HTML-GEN-CL004）；决策 A1..L1 + 1B 2A 3A 4A 5A
- **Verdict**: 🟢 **PASS 85/100（A）** — 无 🔴；3 🟡 非阻断规格收紧 + 4 🟢 记录
- **Score**: 85 / 100
- **Tracking**: HG-SEC-073..075（🟡×3 非阻断）+ HG-SEC-076..079（🟢 records）
- **Findings**: 3 🟡（非阻断）/ 4 🟢 / 0 🔴

### Summary

设计 v1.0 三项需求（favicon 默认注入 / table URL 状态分享 / syncer 参数体系）架构正确、范围适中，行号锚点全部实测命中（corner_args L98-102、四子命令 argparse L773-803、四处 cmd_* inject L314/384/439/489、syncer run_apply L173-219、layout-table 状态/分栏函数 L351-364/L1011-1042/L1287/L1294、四模板 head L6、缺省 yaml 路径存在、countries 195 行含 tabs）。安全面完整：URL 参数无 innerHTML 注入（tab 白名单 + split parseInt 越界 + q 仅 input.value）、favicon 注入源为 operator 受控（与既有 github/home 一致）、syncer subprocess 保持 RIG-002 shell=False + yaml safe_load。三处 🟡 均为「一处一行即可在实施中折叠」的规格收紧，不阻塞实施启动。无 🔴。

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-073 | 🟡 | `--favicon ""` 禁用未钉死 None/"" 区分，corner_args `or` 链照搬会失效 | ⏳ 折入实施 |
| HG-SEC-074 | 🟡 | URL q 编解码对称性 + malformed % 编码 URIError 未钉死 | ⏳ 折入实施 |
| HG-SEC-075 | 🟡 | split=<n>（filtered 下标）与 sort/quickFilter 交互未说明，分享可能错行 | ⏳ 折入实施 |
| HG-SEC-076 | 🟢 | 恢复流程 init() 挂钩点 + defaultFilter 优先级未指定 | ⏳ 折入实施 |
| HG-SEC-077 | 🟢 | §3.1 render_* 实为 cmd_* 命名漂移 | ⏳ 折入实施 |
| HG-SEC-078 | 🟢 | rebuild 三键空串语义；demo --rebuild 归一化存量 cache-busting favicon | ⏳ 折入实施 |
| HG-SEC-079 | 🟢 | test_10 HTML_GEN_STUB 仅识别 --github-url，需锁「[执行] 打印行」断言 | ⏳ 折入实施 |

### Positives

- 行号锚点零漂移（设计引用 L 与源码逐一命中，含 layout-table 9 处 + syncer 3 处 + html-gen 4 处）
- 需求→决策映射 1:1 完整（§一 三需求 ↔ §二 决策 A-L+1-5 ↔ §三/四/五），无跨节不一致
- 安全面显式覆盖（§4.5 白名单/越界/无 innerHTML + 零写盘），favicon/syncer 注入源均为 operator 受控，无新增攻击面
- 向后兼容闭合（§5.3 现有调用不变、URL 无参不变、favicon 默认与 34 个存量产物对齐）
- 修订日志登记 FIND-001（共享文件污染，推送前由归属 CL 登记）与 FIND-002（favicon 闭合）清晰

### 实现 prompt

- ✅ 已生成（PASS → dev 按 §三/四/五实施；实施时折叠 HG-SEC-073..079 七项收紧/记录）

- 报告: `documents/review/html-gen-favicon-urlstate-syncer-design-review-v1.0-20260829.md`
- 处理: PASS → 审计三件套 + commit（仅 commit 不 push，AGENTS.md 约定 + 本任务约束）

---

## 2026-08-29 — html-gen favicon + URL状态 + syncer参数 实现审计（PASS 100/A）

- **Reviewer**: Security Reviewer
- **Level**: L2（implementation-audit）
- **Scope**: HTML-GEN-CL004 实现 commit 链 8 个（`9a9c608` docs@design → `43c5ffd` docs@review → `872593e` feat@html-gen → `b97ca54` feat@template → `33707e7` feat@script → `ae606f3` test@script → `0b95c2b` docs@html-gen → `1d864b1` data@demo，全部未 push）；设计 v1.0 PASS 85/A
- **Verdict**: 🟢 **PASS 100/100（A）** — 三项需求全数落地且源码级+实测双重核验通过，HG-SEC-073..079 七项全部折入并闭合
- **Score**: 100 / 100
- **Tracking**: HG-SEC-073..079（✅ closed 本次实现验证）+ HG-SEC-080（🟢 record 非阻断）
- **Findings**: 1 🟢（记录）/ 0 🟡 / 0 🔴

### Summary

实现链对设计 §三/四/五 三项需求全数落地。favicon：DEFAULT_FAVICON 默认注入（html-gen.py L106）+ `favicon_args` 三层优先级（L122-123 用 `is not None` 判断，HG-SEC-073 空串禁用生效）+ 四子命令 argparse `--favicon`（L797/807/817/829）+ 四处 inject（L337/408/467/516）+ 四模板 `<!--FAVICON-->`（L7），四模板产物实测均注入默认 favicon。URL 状态：`syncUrlState` 统一封装（layout-table L1016-1027）+ 五同步点（switchTab L1351/搜索 debounce L1339/activateSplit L1043/splitNav/closeSplit L1063）+ 恢复顺序 tab→q→split（L1440-1484，HG-SEC-076）+ URLSearchParams 读写对称（HG-SEC-074）+ sort/quickFilter closeSplit（L728/741/797，HG-SEC-075）+ 🔗 shareBtn（clipboard + execCommand fallback + toast）。syncer：yaml_path 缺省路径（L40）+ 三向互斥 exit 2（L299-303）+ --empty-video 只读（L219-239）+ rebuild 三键配置（L188-216，空串禁用 HG-SEC-078）+ [执行] shlex.quote 完整命令 + shell=False（L282-283，RIG-002）。测试：test_url_state 5 / test_sync_videos 13 / test_json_output 14 / test_corner_privacy 6，专项 32 passed，全量 246 collected。治理：8 commit 全 type@scope、未 push、4 个 drama WIP 文件未混入、AGENTS.md 计数 246 一致。

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-073 | 🟡→✅ | `--favicon ""` 禁用 None/"" 区分 | ✅ closed（`L122-123` `is not None`，实测空串禁用） |
| HG-SEC-074 | 🟡→✅ | URL q 编解码对称 + malformed % URIError | ✅ closed（`L1018/1441-1449` 统一 URLSearchParams） |
| HG-SEC-075 | 🟡→✅ | split 下标 vs sort/quickFilter 交互 | ✅ closed（`L728/741/797` closeSplit） |
| HG-SEC-076 | 🟢→✅ | 恢复 init() 挂钩 + defaultFilter 优先级 | ✅ closed（`L1440-1484` + `L1479` `!quickFilter`） |
| HG-SEC-077 | 🟢→✅ | render_* 实为 cmd_* 命名 | ✅ closed（按 cmd_* 定位正确） |
| HG-SEC-078 | 🟢→✅ | rebuild 三键空串语义 | ✅ closed（`L197-215` 空串=禁用，实测 [执行] 无对应参数） |
| HG-SEC-079 | 🟢→✅ | test 锁「[执行] 打印行」断言 | ✅ closed（test_11 assertRegex 三参数打印行） |
| HG-SEC-080 | 🟢 | favicon/home URL 未 HTML 转义（operator 受控，与既有 github-corner 同模式） | ✅ record（非阻断，仅未来引入非受控 URL 才需转义） |

### Positives

- 设计评审 7 项 findings 全部折入实现并逐条验证闭合，无「折入即忘」——每项均有源码行号 + 实测证据（含 HG-SEC-078 rebuild 空串禁用临时 yaml 实测、HG-SEC-073 空串禁用 grep=0）
- 三处 🟡（073/074/075）均按设计评审建议的「一处一行」收紧，非绕过或含糊处理
- 安全面保持设计评审确认：URL 参数无 innerHTML、tab 白名单、split 越界、syncer shell=False + safe_load
- 12 项验证证据全属实（专项 32 passed + favicon 三态 + 四模板 + empty-video 173 条 + 互斥 exit 2 + [执行] 三参数 + 全量 246 collected），无「声称已测实未发生」
- commit 治理干净：8 commit 全 type@scope、drama WIP 未夹带、AGENTS.md 计数 246 与 `246 collected` 精确一致

### 处理

- ✅ PASS → 审计三件套 + commit（`docs@review: html-gen favicon+URL状态+syncer参数 实现审计 PASS (HTML-GEN-CL004)`）；仅 commit 不 push（AGENTS.md 约定 + 本任务约束）

- 报告: `documents/review/html-gen-favicon-urlstate-syncer-impl-audit-v1.0-20260829.md`

---

## 2026-08-30 — table-videos-syncer 设计评审 v1.2（PASS 90/A）

- **Reviewer**: Security Reviewer
- **Level**: L2（design-document-review）
- **Scope**: table-videos-syncer-design v1.2（commit `29bdbd2`）— 增量模型两态→三态（新增/更新/跳过）+ title 变更全字段覆盖 + 全包含统计（HTML-GEN-CL006）
- **Verdict**: 🟢 **PASS 90/100（A）** — 三态模型 + 幂等闭环成立，7 决策全数落入设计，无 🔴，2 🟡 折叠进 dev prompt
- **Score**: 90 / 100
- **Tracking**: HG-SEC-081..082（🟡×2 折叠进 dev）+ HG-SEC-083..085（🟢 记录）
- **Findings**: 2 🟡 / 3 🟢 / 0 🔴

### Summary

v1.2 三态增量模型（new_items/updates/skipped）是 v1.1 additive 语义的最小扩展：url 已存在 + yaml title 非空 + title ≠ json 既有 title → 全字段覆盖更新（title 覆盖 / duration 空保留 / platform detect 兜底空保留）。7 项决策（1B/2A/3A/4A + platform/duration/触发判据三子决策）全数落入 §2，无遗漏无矛盾。幂等闭环成立（更新写盘 → W 镜像带新 title → 下次 url+title 相同跳过）。G 判定修订（new_items 与 updates 双空才中断）正确修复「仅更新无新增误判中断」。实测数据核验：cache yaml 现 59 条/31 国、json 31 条视频，28 条新增候选 + 土耳其 1 条 title 不一致（更新候选）——设计 §1「31/24/31 已包含」已漂移（HG-SEC-082）。

### Findings

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-081 | 🟡 | duration 空/缺省判空谓词未 pin 在 raw yaml 值（normalize_duration(None)→'None' 会误判非空而覆盖） | ⏳ 折叠 dev prompt |
| HG-SEC-082 | 🟡 | §1/§4.3/§6 数据印证漂移（31/24/31已包含 → 实测 59/31/28新增+1更新） | ⏳ 折叠 dev prompt |
| HG-SEC-083 | 🟢 | 4A「同 url 取首条」vs 实现「同 country+url 取首条」措辞不一致 | 记录 |
| HG-SEC-084 | 🟢 | test_05 第三条「（重复）」title 由 skip 语义漂移为 update | 记录 |
| HG-SEC-085 | 🟢 | 缺「title 空 → 不触发更新」(2A) 显式用例 | 记录 |

### Positives

- 三态模型是最小扩展，未触碰 v1.1 的 W 回写 / E 重建 / F 校验 / 路径解析等已闭环决策，改动面收敛
- 幂等闭环经源码级验证成立（build_mirror_countries 读 json 现值回写，更新后自动带新 title）
- 触发判据收敛唯一（title 不同），避免把 yaml 未维护的 duration/platform 误当权威（§7 风险已显式声明）
- 'None' 防护风险被 U2 显式点名，t18 作为回归护栏可兜底朴素实现缺陷
- 安全面完全沿用已审计路径（safe_load / shell=False / json.dump + escapeHtml），零新增攻击面

### 实现 prompt

- ✅ 已生成（已存在 `documents/review/table-videos-syncer-v1.2-dev-impl-prompt-20260830.md`；实施时折叠 HG-SEC-081/082：duration 判空 pin raw 值 + §验证 dry-run 预期改为「28 新增 + 1 更新」）

- 报告: `documents/review/table-videos-syncer-v1.2-design-review-v1.0-20260830.md`
- 处理: PASS → 审计三件套 + commit（仅 commit 不 push，AGENTS.md 约定 + 本任务约束）

---

## 2026-08-30 — table-videos-syncer v1.2 实现审计（PASS 100/A）

- **Reviewer**: Security Reviewer
- **Level**: L2（implementation-audit）
- **Scope**: table-videos-syncer v1.2 实现审计 — dev 实施（`df2e28c`）+ ops 修复（`7dbaf4c` 更新步变量遮蔽 target → rebuild 配置丢失 + test_21）；设计 v1.2 PASS 90/A（HTML-GEN-CL006）
- **Verdict**: 🟢 **PASS 100/100（A）** — 三态增量模型源码级 + 实测双重核验通过，HG-SEC-081..085 五折叠项全数闭合，ops 遮蔽缺陷已修复并带回归测试
- **Score**: 100 / 100
- **Tracking**: HG-SEC-081..085（✅ closed 本次实现验证）+ 遮蔽缺陷修复 t21
- **Findings**: 0 🟢 / 0 🟡 / 0 🔴

### Summary

三态增量模型实现与设计 §4.2 逐条一致：build_increments（L126-180）新增（url 不在 existing_map）/ 更新（url 已存在 + yaml title 非空 + ≠ json 既有 title，携带 old_title + raw_duration）/ 跳过（其余），yaml 内部同 country+url 去重（seen 集合）。run_apply 更新步（L293-310）：title 直接覆盖、duration 以 raw yaml 值判空（HG-SEC-081，L301 杜绝 normalize_duration(None)→'None' 覆盖）、platform yaml→detect→保留既有（U1）。G 判定（L411）改 new/updates 双空才中断，正确修复「仅更新无新增误判中断」；全包含统计 N/M（L412-414）与 build_increments 同口径（去重 + 畸形条目排除）。ops 核查发现的 df2e28c「循环局部变量 target 遮蔽 run_apply target 参数 → resolve_rebuild_args 拿到视频条目 → rebuild 三键配置静默丢弃」缺陷，已由 7dbaf4c 修复（target→existing_entry）+ test_21 回归护栏。实测：专项 21 passed、全量 255 passed、dry-run 28 新增 + 1 更新（土耳其 title 变更）+ 30 跳过（零写盘）。

### Findings

无（0 🔴 / 0 🟡 / 0 🟢）。附注：df2e28c 引入的 target 遮蔽缺陷已在审计链内（7dbaf4c）闭环，不计 findings。

### Positives

- 5 项评审折叠项（HG-SEC-081..085）全部折入实现并逐条闭合，均有源码行号 + 回归测试（t17/t18/t19/t20 + test_05 fixture）+ 实测证据，无「折入即忘」
- HG-SEC-081（duration 判空 pin raw 值）的 t18 护栏 + HG-SEC-085（title 空）的 t20 护栏均落地，杜绝清空/None 覆盖两类回归
- ops 发现的 target 遮蔽缺陷（rebuild 配置静默丢失，属正确性级回归）带回了 test_21 透传断言，锁死同类回归
- 三项实测证据精确吻合设计预期（28+1+30），安全面沿用 safe_load / shell=False / json.dump，零新增攻击面
- 提交治理干净：2 实施 commit 只含 syncer + tests，未夹带 data/_countries-data.json 他人 note 编辑

### 处理

- ✅ PASS → 审计三件套 + commit（`docs@review: syncer v1.2 实现审计 (HTML-GEN-CL006)`）；仅 commit 不 push（AGENTS.md 约定 + 本任务约束）

- 报告: `documents/review/table-videos-syncer-v1.2-impl-audit-v1.0-20260830.md`

---

## 2026-09-02 — html-gen prompt 在线阅读站点 设计 v1.0 评审（PASS 85/A）

- **Reviewer**: Security Reviewer
- **Level**: L2（design-document-review）
- **Scope**: html-gen prompt --site 在线阅读站点（prompts/ 静态目录 + {skill}.md/.json + all.md + index.html 合集，HTML-GEN-CL007 kind=independent）；commit fe2ee22；前置 CL004/CL006 已闭环
- **Verdict**: 🟢 **PASS 85/100（A）** — 架构正确，3 项 🟡 非阻断折叠实现（幂等口径 / h1 fence-aware / 清空 containment），无 🔴
- **Score**: 85 / 100
- **Tracking**: HG-SEC-086..088（🟡×3 折叠 dev 实施）+ HG-SEC-089..095（🟢 records）
- **Findings**: 7 🟢 / 3 🟡 / 0 🔴

### Summary

设计复用 cmd_doc + layout-doc.html（零新模板），9 决策（A1 B3 C1 D1 E1 F1 G1 H1 I1）→ §4/§5/§6/§9 逐节映射一致。数据实证：8 skills（1185 行）+ references（177 行）核验准确；frontmatter 剥离定论由 §3 Jekyll 实证支撑（SKILL.md→404 / README.md→200 text/markdown）；双形态差异（CLI 含 frontmatter vs 站点剥离）已 §6.5 文档化。命名 html-gen-prompts-site-design-v1.0-20260902.md + commit docs@html-gen 均合规；设计文档 header 式无 YAML frontmatter 与兄弟设计文档惯例一致（非 §2 违规）。三项 🟡：① cmd_doc 把 all.md 分钟粒度 st_ctime/st_mtime 注入 index.html meta → 幂等 diff 跨分钟 flaky；② 3 个 skill 正文含代码块内 `# ` 注释行 → h1 计数/删除须 fence-aware；③ `--dir` 清空目录无 containment（误删风险）。七项 🟢 记录：references 数 4→3 笔误 / index.html favicon·github env 兜底未指定 / test_02 未点名 html-gen-slide 2 references / all.md TOC 扁平 / 「同构」措辞 / HELP_PROMPT 遗漏 --site / YAML 多行 description 截断。

### Findings

- 🔴 0 / 🟡 3（HG-SEC-086..088，均非阻断，折入实施）/ 🟢 7（HG-SEC-089..095，记录）

### Positives

- 需求五项（在线+md+json+all.md+README）全覆盖，9 决策零矛盾
- frontmatter 剥离有 Jekyll 实证链（非臆断），双形态差异显式文档化
- 内存构建 fail-fast 先于清空写盘，防半成品；cmd_doc Namespace 直调对 github/home/favicon getattr 兜底，稳妥
- --dir 测试隔离（test_08 断言默认路径不写仓库）+ 验收清单命令级可跑

### 处理

- ✅ PASS → 审计三件套 + commit（`docs@review: prompt 在线阅读站点 设计评审 (HTML-GEN-CL007)`）；仅 commit 不 push（AGENTS.md 约定）
- ✅ 实现 prompt 已生成（折入 HG-SEC-086..088）

- 报告: `documents/review/html-gen-prompts-site-design-review-v1.0-20260902.md`

---
