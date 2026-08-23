# 落地页回归测试 + 文档同步实现审计 — review报告 v1.0

## 审计概况

- **审计类型**: Implementation Audit (L2)
- **审计对象**: 未 push commits（github/main..HEAD，3 个）
  1. `221be4a` test@html-gen: 落地页回归测试 test_index_landing (hero 100vh/github-corner/滑屏/上箭头 A+B/案例区统一, 8 tests)
  2. `402fe29` docs@html-gen: AGENTS/features 同步 — 落地页说明 + 测试数 154 + 双源漂移备注 + github-corner 差异文档化 (P2/P3/P4)
  3. `68d2734` docs@html-gen: review-log HG-SEC-014 文档化关闭 (P4)
- **需求来源**: P1-P6 清单（P1 回归测试固化 / P2 双源漂移备注 / P3 文档信息同步 / P4 github-corner 差异文档化 + HG-SEC-014 关闭 / P5 线上复验 / P6 skill 补测试信息）
- **审计方法**: 逐 commit diff 独立复核（git show 3 commits + github/main..HEAD 全 diff）→ test_index_landing.py 逐断言对照 index.html 现状 → pytest --collect-only 逐文件核对 154 → 新测试文件独立复跑 → AGENTS.md/features.md/review-log.md 准确性核验 → HG-SEC-015 关闭来源追踪（git log -S）→ 线上 7 URL curl 复验 → 凭证/XSS 扫描
- **审计日期**: 2026-08-23

## 数据验证

| # | 验证项 | 结果 |
|:--:|:---|:---|
| 1 | 未 push commit 数 | `git log github/main..HEAD` = **3**（221be4a/402fe29/68d2734）；working tree clean；双 remote（github/gitee）✅ |
| 2 | 变更范围 | 221be4a 仅 `tests/test_index_landing.py`（+138）；402fe29 仅 `AGENTS.md`(+6/-3) + `features.md`(+2/-2)；68d2734 仅 `review-log.md`(+17) — 无越界文件 ✅ |
| 3 | 测试收集数 | pytest --collect-only = **154**；18 个测试文件逐文件计数与 AGENTS.md 列表**逐一匹配**（templates 16 / drama_knowledge 16 / hermes_skills 15 / countries_table 13 / table_features 11 / demo_cmd 10 / knowledge_sidebar 8 / index_landing 8 / doc_width 8 / history_tables 7 / doc_sidebar 7 / sticky_width 6 / heading_levels 6 / doc_bare 6 / prompt_cmd 5 / initial_hidden_split 5 / slide_h3_toggle 4 / datetime_clickmode 3，求和 154）✅ |
| 4 | test_index_landing 实测 | 独立复跑 **8 passed in 6.83s**（headless Chrome，file:// 加载）✅ |
| 5 | 断言真实性（对照 index.html 现状） | `.github-corner` 无 pointer-events 设置（默认 auto）+ href=github.com/imjaden/html-gen.cli + 无 `.github-corner-hit` 元素（grep = 0）；`.octo-arm` 动画 `octocat-wave 560ms`（CSS :hover 触发）；scroll-hint `href="#templates"` + `<section id="templates">`；back-top-link/back-to-top `href="#top"` + `<html id="top">`（b940b3b 已修）；四卡 `.demos-title` 全「案例演示」+ demo-item icon/info-name/arrow 结构齐全 ✅ |
| 6 | file:// 兼容 | 测试用 `driver.get('file://' + str(INDEX))`，无 http 假设；skill 记录的 hash 规范化坑（`split('#')[-1]`）已在断言中处理 ✅ |
| 7 | HG-SEC-015 关闭属实 | `git log -S 'href="#top"'` = b940b3b（fix@html-gen, 已在 github/main 顶端）；HEAD index.html:216,360 均为 `#top`。**本次同步 .review-level.yaml 前置条目 findings_open 1→0** ✅ |
| 8 | AGENTS.md 双源漂移备注准确 | 「根 index.html 与 demos/index.html 两份独立副本、demos/index.html 是 --rebuild featured 数据源、github-corner 两模式差异」与事实（模板层双层穿透 + 根落地页全可点）一致 ✅ |
| 9 | features.md 同步准确 | 测试用例 154（含落地页 8）、GitHub Corner 行双模式表述 均准确 ✅ |
| 10 | review-log HG-SEC-014 关闭记录 | 68d2734 条目合规（处置决定 + 依据 + 复核）；但「五 🟢」与所列 4 个 ID（012/013/014/015）不符，且与前置尾项处置条目（L350）重复关闭 — 见 HG-SEC-016 🟢 |
| 11 | commit 分组规范 | 221be4a test@ / 402fe29 docs@ / 68d2734 docs@ — 类型职责分离，消息 `type@scope: subject` 格式符合约定 ✅ |
| 12 | 线上复验（P5） | curl 7 URL（/ + demos 系列 5 + style-guide.css）全 **200**；线上 drama-knowledge 页 github-corner 指向 html-gen.cli ✅ |
| 13 | 旧链接残留 | `git grep 'github.com/imjaden/html-gen[^.]' -- demos/` = **0**；index.html 双后缀/旧域名 0 ✅ |
| 14 | P6 skill 核查 | ops profile `~/.hermes/profiles/ops/skills/devops/html-gen-workflow/SKILL.md` 已含 test_index_landing 信息（commit 221be4a、file:// href 规范化坑、1.2s smooth scroll 等待依据）— 跨 profile 只读核查 ✅ |
| 15 | 凭证/注入扫描 | 3 commits 全 diff 无 secret 模式；本批无 JS/模板代码变更，测试文件纯 Selenium 断言无注入面 ✅ |

## 实现评估（对照 P1-P6）

### P1. 落地页回归测试固化 — ✅

`tests/test_index_landing.py` 8 用例覆盖 P1 全部要点，**断言真实行为**（非属性快照）：

| 用例 | 断言 | 真实性 |
|:---|:---|:---:|
| test_01_no_js_errors | browser console SEVERE/ERROR = 0 | ✅ |
| test_02_hero_100vh | `.hero` offsetHeight / innerHeight > 0.95（非硬编码像素） | ✅ |
| test_03_github_corner_clickable | pointer-events auto + href 含 html-gen.cli + `.github-corner-hit` = 0 + hover 后 octo-arm animationName=octocat-wave | ✅ |
| test_04_scroll_hint_to_templates | href hash=templates + 点击后 `#templates` 距顶 < 60px | ✅ |
| test_05_back_top_a | A 形式 href=#top + 点击 scrollY==0 | ✅ |
| test_06_back_top_b | B 形式初始隐藏 → 滚底 .show+visible → 点击回顶 → 回顶后隐藏 | ✅ |
| test_07_case_demos_unified | 四卡标题全「案例演示」+ demo-item 结构 icon/name/arrow | ✅ |
| test_08_local_links_no_old_repo | 文本层扫描：无旧仓库/双后缀/旧域名 + 有新链接 | ✅ |

- **无脆弱等待**：主元素用 WebDriverWait（`.hero` presence），交互等待用固定 sleep（0.2/0.4/0.6/1.2）；1.2s 为 smooth scroll 完成所需，html-gen-workflow skill 已显式记录该依据
- **file:// 兼容**：纯本地页面加载，无 http 依赖
- 8/8 实测通过（6.83s），无 flaky 复现

### P2. 双源漂移治理备注 — ✅

AGENTS.md 目录结构末尾新增备注：根 `index.html`（落地页）与 `demos/index.html`（模板展示首页）为两份独立副本、`demos/index.html` 是 `html-gen demo --rebuild` featured 数据源、根 index.html 不参与、github-corner 两模式差异。与 1C 决策及事实一致。

### P3. AGENTS.md/features.md 信息同步 — ✅

- AGENTS.md：测试数 146→154（18 文件逐一列举且与 collect-only 完全一致）；目录结构补 `index.html` 落地页行 + tests 计数 73→154；根目录名 `html-gen/`→`html-gen.cli/`
- features.md：测试用例 154（含落地页 8）；GitHub Corner 行更新为「demo 页双层可点区防遮挡；根落地页全图标可点 + hover 波浪动画」
- 除需求项外无其他漂移（diff 仅 4 个主题区）

### P4. 模板层 github-corner-hit 差异文档化 + HG-SEC-014 关闭 — ✅（含 1 🟢 记录）

- AGENTS.md 备注明确两模式：layout 模板层「pointer-events:none 穿透 + hit 36px」防遮挡工具栏（有意设计，commit 204f9e1）；根落地页无工具栏全图标可点 + hover 波浪动画
- review-log 68d2734 以「处置方: ops」条目记录文档化关闭（不改模板代码），依据充分、复核到位
- **HG-SEC-016 🟢**：条目「五 🟢 全部关闭」与所列 4 个 ID（HG-SEC-012/013/014/015）不符，应为「四」；且该条目与前置「HG-SEC-014 尾项处置」条目（L350）重复关闭同一 finding（前置条目已含"接受现状，不迁移"决定）

### P5. 生成物链接线上复验 — ✅

7 个代表性 URL 全 200（/、demos 系列 5、style-guide.css）；线上 demo 页 github-corner 指向 `github.com/imjaden/html-gen.cli`；本地 demos/ 旧链接 0 残留。

### P6. html-gen-workflow skill 补测试信息 — ✅（跨 profile）

ops profile skill 已含 test_index_landing 条目（8 tests 覆盖点 + file:// href 规范化坑 + 1.2s 等待依据），非 repo 变更，只读核查通过。

### 尾项处置链闭合

HG-SEC-015（#top 优化）由 b940b3b 修复且已在 github/main；本次同步 `.review-level.yaml` 前置条目 findings_open 1→0，与 review-log「四 🟢 全部关闭」一致。

## 安全事项

无 🔴 HIGH / 🟡 MEDIUM 发现。2 个 🟢 LOW 记录（不计分）：

- **HG-SEC-016** 🟢 — review-log 68d2734 条目「五 🟢」计数与所列 4 个 ID 不符（应为「四」），且与前置尾项处置条目重复关闭 HG-SEC-014。`review-log.md:435`
- **HG-SEC-017** 🟢 — test_index_landing 仅 test_01 调用 `_errors()`（1/8 覆盖），后续测试方法若触发 console 错误将漏检；项目约定「每个测试方法独立加载页面，`_errors()` 检查 JS 错误」，建议后续测试补充或文档化豁免。`tests/test_index_landing.py`

## 评分

| 项 | 值 |
|:---|:---|
| Base | 100 |
| 🔴 HIGH × 0 | −0 |
| 🟡 MEDIUM × 0 | −0 |
| 🟢 LOW × 2 | −0（记录） |
| **Score** | **100 / 100** |
| **Rating** | **A** |
| **Verdict** | **PASS** |

## 结论

**PASS** — 3 commits 与 P1-P6 逐条一致：P1 回归测试 8 用例断言真实行为（hero 100vh 比例 / github-corner 可点+动画+无 hit 区 / 滑屏到位 / A+B 回顶显隐 / 四卡统一 / 无 JS 错误 / 无旧链接），实测 8/8 通过，pytest 全量收集 154 与 AGENTS.md 逐文件一致；P2 双源漂移备注准确；P3 AGENTS/features 同步仅覆盖需求主题无额外漂移；P4 github-corner 两模式差异文档化 + HG-SEC-014 关闭记录合规（1 🟢 计数瑕疵）；P5 线上 7 URL 全 200 + 旧链接 0 残留；P6 skill 已补测试信息（跨 profile 核查）。commit 分组 test@/docs@ 职责分离。HG-SEC-015 关闭属实且 YAML 已同步。2 个 🟢 记录（review-log 计数瑕疵 / _errors() 覆盖），均不阻断，由 ops 尾项处置。PASS 后由 ops 推双远程（github 推 3 commits + 本次 review commit；gitee 同步）。

## 待确认清单

| # | 项 | 建议 | 状态 |
|:--:|:---|:---|:---:|
| 1 | HG-SEC-016: review-log「五 🟢」计数修正 + 重复关闭条目去重 | 改「四 🟢」（或补全 5 个 ID 的清单），或合并前置尾项处置条目 | □ |
| 2 | HG-SEC-017: test_index_landing _errors() 覆盖 | 各测试方法补 `_errors()` 断言，或在 AGENTS.md 注明豁免 | □ |
