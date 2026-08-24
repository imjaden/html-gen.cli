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
