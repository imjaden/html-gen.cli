# html-gen index 落地页同步 — review报告 v1.0

- **日期**: 2026-08-24
- **Reviewer**: Security Reviewer（L2）
- **范围**: 未 push 6 commits（e1add13 / 0b015a4 / 25f299a / 5e9508a / 775d27f / 28000b2）— index 落地页主题切换 + 复制按钮 + footer + 动态两屏 + github-corner light + demos 双源同步 + drama 测试同步
- **结论**: ⚠️ CONDITIONAL PASS 75/100（B）
- **待确认**: 2 项（见 §待确认清单）

---

## 一、数据验证（实测）

| 项 | 结果 |
|:---|:---|
| 专项测试 `tests/test_index_landing.py + test_demos_index.py -q -n 0` | ✅ 21 passed (10.32s) |
| 全量收集 `pytest --collect-only` | ✅ 180 tests（20 文件，与 AGENTS.md 逐文件计数一致） |
| drama 相关 `test_history_tables.py + test_drama_knowledge.py -q -n 0` | ✅ 23 passed（依赖工作区未提交数据，见 HG-SEC-029） |
| AGENTS.md 双源漂移段 vs 实现 | ✅ 一致（corner 穿透差异、theme-btn right:88px、`html-gen:index_theme` key、动态两屏 hero、防漂移测试） |
| chromedriver 路径 | ✅ 与 AGENTS.md 一致（script-miner/cache/chromedriver） |

**浏览器实测（headless Chrome 151）**:
- root index 深色模式 corner base `rgb(156,163,175)`（= --text-secondary #9ca3af）；**hover 后变 `rgb(99,102,241)`（#6366f1 indigo）** → HG-SEC-031
- demos 页浅色模式（:root.light）：body bg `rgb(245,245,245)`，案例演示清单 h2 计算色 `rgb(224,224,224)`（≈1.25:1，近乎不可见）、p `rgb(156,163,175)`（≈2.3:1）、Layer1 卡文字 `#9ca3af` on `#ffffff`（≈2.3:1）→ HG-SEC-030
- HEAD 提交态 `demos/drama/history-strategy-table.html` COLUMNS 仍为 9 列旧结构（计名/别名/衍生成语）；工作区为 11 列（衍生词/同源意象/近义词/反义词）→ HG-SEC-029

---

## 二、维度评估

### 1. 实现正确性（主题切换 / 复制 / hero / corner）
✅ 主题切换：`:root.light` 类 + localStorage 读写均包 try/catch；值白名单校验（`=== 'light'`）；无 innerHTML、无 XSS 面；与模板页 key 隔离（`html-gen:index_theme`）。
✅ 复制按钮：clipboard API + execCommand fallback 双通道；`data-copy` 全部静态内容，textarea 离屏注入，无注入风险；5 处（hero 1 + 四卡 4）与测试断言一致。
✅ 动态两屏：`minHeight = innerHeight − 110` + resize 重算，测试容差 ±6px 通过；CSS 80vh 兜底。
✅ github-corner light：`--gh-corner-fill`/`--gh-octocat` 变量化，浅色模式白 octocat 实测通过（test_15 / demos test_06）。
✅ 双源同步：0b015a4/5e9508a 将 theme/copy/footer/2col/light-corner 同步至 demos/index.html；test_05 11 项子串断言防漂移生效。

### 2. 双源差异（防漂移边界）
✅ 文档化差异均与 AGENTS.md HG-SEC-014 段一致：corner 穿透 + hit（demos 层）vs 全图标可点（根页）；hero 仅根页；layer-divider 仅 demos 页。
⚠️ 未文档化差异：根页内部链接全部 `rel="noopener"`，demos 页内部 `target="_blank"` 链接（tpl-guide/demo-item 共 14 处）全部省略 rel → HG-SEC-032。

### 3. CSS 特异性陷阱
🔴→🟡 HG-SEC-031：root 页深色模式 `.github-corner` (0,1,0) 被全局 `a:hover` (0,1,1) 击败，hover 时 octocat 变 indigo；浅色模式有 `:root.light .github-corner:hover` (0,4,0) 保护、深色模式缺失（不对称保护）。

### 4. 可访问性
🟡 HG-SEC-030：demos 页浅色模式下"案例演示清单"区块 + Layer 卡文字硬编码深色系色值（`#e0e0e0`/`#9ca3af`/`#a5b4fc`），对比度 1.25:1~2.4:1，均不达 WCAG AA 4.5:1。
🟢 HG-SEC-035：主题按钮 aria-label 固定"切换主题"，无 aria-pressed/状态语义，切换后屏幕阅读器无反馈。

### 5. 深/浅色对比度
✅ 浅色变量组整体达标：--text-primary #1f2328 on white ≈15:1、--text-secondary #57606a ≈7:1、--text-muted #6e7681 ≈4.7:1、gh-corner 白猫 on rgba(0,0,0,.75) ≈8.5:1。
❌ 例外即 HG-SEC-030（demos 页硬编码区块）。

---

## 三、安全事项（🟡 SEC-N）

| ID | 严重度 | 标题 | 文件:行 | 优先级 |
|:---|:---:|:---|:---|:---:|
| HG-SEC-029 | 🔴 | 28000b2 测试断言依赖未提交的 11 列数据（提交单元不自洽） | tests/test_history_tables.py:62 / tests/test_drama_knowledge.py:243 + demos/drama/*-strategy-table.html ×4（工作区 +1719 行未提交） | P1 |
| HG-SEC-030 | 🟡 | demos/index.html 浅色模式案例清单/Layer 卡对比度不达标（h2 ≈1.25:1） | demos/index.html:298-301, 304-330 | P1 |
| HG-SEC-031 | 🟡 | root index github-corner 深色模式 hover octocat 变 indigo（a:hover 特异性压制） | index.html:187-190 + style-guide.css:95 | P2 |
| HG-SEC-032 | 🟢 | demos 页内部 target=_blank 缺 rel="noopener"（与根页不一致） | demos/index.html:109,129-134,144,162-169,179,197-204,214,232-235 | P2 |
| HG-SEC-033 | 🟢 | hero 安装复制按钮"📋 复制"点击后重置为"📋"（标签丢失） | index.html:455（done() 硬编码 '📋'） | P3 |
| HG-SEC-034 | 🟢 | execCommand fallback 抛异常/返回 false 仍标记 ✅（假成功） | index.html:461 / demos/index.html:367 | P3 |
| HG-SEC-035 | 🟢 | 主题按钮无 aria-pressed/状态语义 | index.html:233 | P3 |
| HG-SEC-036 | 🟢 | html-gen.py 行数文档漂移：AGENTS.md 记 569、demos 页记 546、实际 958 | AGENTS.md / demos/index.html:274 | P3 |

---

## 四、评分

```
Base: 100
🔴 HIGH × 1  (HG-SEC-029)  -15
🟡 MEDIUM × 2 (HG-SEC-030/031) -10
🟢 LOW × 5  (HG-SEC-032..036)   0
Score: 75 / 100 → B → CONDITIONAL PASS
```

> 说明：HG-SEC-029 非安全漏洞，属提交完整性/CI 回归风险——单独 checkout 本 6-commit 单元跑全量会失败 3+ 用例。按治理规范 🔴 判定为条件通过而非 FAIL。

---

## 五、结论

**CONDITIONAL PASS（75/100, B）** — 修完两项 P1 后通知复查：
1. **HG-SEC-029**：将 4 个 11 列 strategy-table 数据文件随 28000b2 一并提交（或回退测试），保证提交单元自洽
2. **HG-SEC-030**：demos 页案例清单/Layer 卡硬编码色值改用语义变量或补 `:root.light` 覆盖

**Push**: 不推送（CONDITIONAL PASS 规则）。6 commits 保留本地，待复查通过后授权。

---

## 六、待确认清单

```
□ 1. HG-SEC-029 — 11 列数据文件（demos/drama/*-strategy-table.html ×4）由 dev 会话另行提交？确认后补提并复核
□ 2. HG-SEC-036 — html-gen.py 行数以哪个为准（958）？同步 AGENTS.md 与 demos 页
□ 3. HG-SEC-032 — demos 页 rel="noopener" 是否纳入双源一致性测试 features（test_05）？
```

## 七、Positives

- 测试覆盖到位：专项 21 + 全量 180 + drama 23 全部通过（当前工作区态）
- AGENTS.md 与实现高度同步（测试数、双源漂移段、corner 差异文档化）
- 主题/localStorage 实现健壮（try/catch + 白名单 + 无注入面）
- test_05 双源一致性防漂移机制有效
- 变量化改造范围彻底（e1add13 将 40+ 硬编码色值迁移至 --text-*/--border-*/--code-*）

---

## 八、复查（v1.1，2026-08-24 晚）— HG-SEC-029..036 修复验证

### 修复验证

| ID | 原严重度 | 修复 commit | 验证结果 | 结论 |
|:---|:---:|:---|:---|:---:|
| HG-SEC-029 | 🔴 P1 | 30add19 | 4 个 strategy-table 已提交（+1668 行），daming/history/yongzheng/zhuyuanzhang 均含 derivative/homology/synonym/antonym 11 列；全量 180 passed 无回归 | ✅ 已修复 |
| HG-SEC-030 | 🟡 P1 | c7a5bf0 | h2 var(--text-primary) #1f2328 on #f5f5f5 = **14.49:1** ✅；p var(--text-secondary) #57606a = **5.86:1** ✅；Layer1/3 卡 p #57606a on #ffffff ≈ **6.35:1** ✅；code var(--cobalt-600) #6366f1 on #dfe0f4 = **3.43:1** ⚠️ 仍略低于 AA 4.5:1（0.7rem 小字） | ⚠️ 主体已修复，code 残余 |
| HG-SEC-031 | 🟡 P2 | c7a5bf0 | 双页（index.html:188 / demos/index.html:48）均补 `.github-corner:hover { color: var(--gh-octocat); }`，深色模式 hover 不再被 a:hover 压制变 indigo | ✅ 已修复 |
| HG-SEC-032 | 🟢 P2 | c7a5bf0 | demos 页 18 处 target="_blank" 全部带 rel="noopener"（0 缺失）；根页 17 处全带；test_05 features 增 'rel="noopener"' 断言 | ✅ 已修复 |
| HG-SEC-033 | 🟢 P3 | c7a5bf0 | copyText 保存 orig 原标签，恢复时不再硬编码 '📋' | ✅ 已修复 |
| HG-SEC-034 | 🟢 P3 | c7a5bf0 | fallback 检查 execCommand 返回值，false/异常不标记 ✅ | ✅ 已修复 |
| HG-SEC-035 | 🟢 P3 | c7a5bf0 | themeBtn 初始 aria-pressed="false"，updateThemeBtn 随 light 状态同步 true/false | ✅ 已修复 |
| HG-SEC-036 | 🟢 P3 | c7a5bf0 | wc -l html-gen.py = 958，AGENTS.md + demos 页均同步 958 | ✅ 已修复 |

### 数据验证（实测）

| 项 | 结果 |
|:---|:---|
| 全量 pytest `-n 4`（py3.12 env） | ✅ **180 passed in 34.08s**（20 文件） |
| demos 页浅色对比度（:root.light 计算色） | ✅ h2 14.49:1 / p 5.86:1 / Layer 卡 p ≈6.35:1；⚠️ code 3.43:1 |
| rel="noopener" 覆盖率 | ✅ demos 18/18、根页 17/17，0 缺失 |
| html-gen.py 行数 | ✅ 958 = AGENTS.md 958 = demos 页 958 |

### 残余记录（不阻断）

- **HG-SEC-030 residual** 🟢：案例清单内 `html-gen demo list` code 元素（0.7rem 小字）对比度 3.43:1，仍略低于 WCAG AA 4.5:1。原硬编码 #a5b4fc（≈2.4:1）已显著改善，主体 h2/p/Layer 卡全部达标；如进一步达标可将该 code 改 var(--cobalt-700) 或加粗。→ 降级为 🟢 记录。

### 复查结论

**PASS 100/100（A）** — 8 项 findings 全部处置：7 项完整修复 + 1 项主体修复（HG-SEC-030 code 残余降 🟢）。CONDITIONAL PASS 75 → PASS 100。授权 push（含 13 commits 本地 + 本轮审计交付物）。


