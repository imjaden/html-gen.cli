# html-gen 四模板字体倒挂修复 — review报告 v1.0

- 日期: 2026-08-27
- Reviewer: Security Reviewer
- 评审级别: L2 (commit-range-audit)
- 范围: 8079a28 feat@templates / 107affc sync@demos / 151a929 test@templates（位于已 PASS 的 7ed27bb 之后）
- 决策依据: 1A 容器基座 / 2A blockquote 紧凑 / 3A callout 保持 / 4A 两模板 / 5A 重新生成产物

## 一、数据验证

| 项 | 结果 |
|:---|:---|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → **185 passed in 32.66s**（基线 183 + test_templates 2 新用例） |
| 模板 font-size | layout-doc.html:84 `.doc-body { font-size: 0.88rem }` ✓；layout-slide.html:91-94 `.slide-page { font-size: 0.88rem }` ✓ |
| 模板 blockquote | 两模板 `.doc-body/.slide-page blockquote { margin: 0.1rem 0; padding: 2px 16px }` ✓ |
| callout 保持 (3A) | layout-doc.html:131 `.doc-body blockquote.callout { padding: 10px 16px; margin: 0.75rem 0 }` 特异性覆盖 base，未受紧凑化影响 ✓ |
| h/table/code 显式 rem | h1-h6 (1.5~0.82rem) / table 0.8rem / code 0.78rem 均显式声明，不受容器 0.88rem 继承影响 ✓ |
| doc 产物抽查 | core-products.html:317 font-size 0.88rem + 343 blockquote 紧凑 + 364 callout 保留；变量基座完整 (--cobalt-50:17) ✓ |
| 变量基座全量扫描 | 25 doc 产物 + slide-guide.html 全部含完整 `:root { --cobalt-* }`（37 定义）；**slide-demo.html 例外（见 SEC-041）** |
| git status | 仅 2 个非范围文件（demos/countries-table.html、demos/drama/history-strategy-table.html，未提交，其他 session 内容扩充）✓ |

## 二、维度评估

### 合理性
- 1A 容器基座方案（.doc-body/.slide-page 加 font-size 0.88rem，li 等继承统一）合理，避免逐元素声明；h/table/code 显式 rem 不受影响 ✓
- 2A blockquote 紧凑（0.75rem→0.1rem / 8px→2px）直接命中「间隔过大」痛点 ✓
- 3A callout 保持正确：callout 用更高特异性选择器覆盖，视觉不变 ✓
- 4A 两模板范围正确：doc/slide 是文档型模板；knowledge/table 不含正文排版 ✓

### 严格性
- 新增 TestDocTypography 2 用例：li==p 14.08px（0.88rem×16px 精确断言）+ blockquote margin/padding 紧凑 ✓
- 但测试用 markdown-spec.html（doc 型）覆盖，未覆盖 slide-demo.html，故 SEC-041/042 未被测试暴露 ✗

### 安全性
- 纯 CSS 排版改动，无脚本/注入/XSS 风险 ✓
- slide-demo.html 同步引入变量丢失回归（SEC-041）✗

## 三、安全事项

| # | Severity | 问题 | File:Line |
|:---|:---:|:---|:---:|
| HG-SEC-041 | 🔴 | slide-demo.html 丢失 `:root { --cobalt-* ... --radius-full }` 变量基座，深色主题完全失效（实测 body bg transparent / text black，code 块深底黑字不可读） | demos/slide-demo.html:8-216 |
| HG-SEC-042 | 🟡 | slide-demo.html 出现两个重复 `<style>` 块，旧副本（217-424）`.slide-page blockquote` 仍为 0.75rem/8px，覆盖新紧凑值 0.1rem/2px，blockquote 修复未生效 | demos/slide-demo.html:330 vs 122 |

### 验证证据（headless Chrome 实测）

| 指标 | slide-demo.html（当前） | layout-slide.html（模板对照） |
|:---|:---|:---|
| `--cobalt-400` | `''`（未定义） | `#818cf8` |
| `--surface-900` | `''`（未定义） | `#11111b` |
| `--font-mono` | `''`（未定义） | `'JetBrains Mono', monospace` |
| body background | `rgba(0,0,0,0)` 透明 | `rgb(10,10,20)` 深色 |
| body color | `rgb(0,0,0)` 黑 | `rgb(224,224,224)` 浅色 |

## 四、评分

| 项 | 分 |
|:---|:---:|
| 基线 | 100 |
| 🔴 HG-SEC-041 | -15 |
| 🟡 HG-SEC-042 | -5 |
| **合计** | **80 (B)** |

## 五、结论

**CONDITIONAL PASS（80/B）** — 不 push。

根因：107affc 对 slide-demo.html 的「从 layout-slide 提取替换」同步错误地替换了第一个 `<style>` 块的 `:root` 变量基座（而非更新第二个 slide 样式块），导致：(a) 变量基座整体丢失；(b) 出现两个重复 slide 样式块，旧块覆盖新块。

其余部分均正确：2 模板 + 25 doc 产物 + 185 tests 全绿。问题仅隔离于 slide-demo.html 单文件。

修复建议（二选一，均需保持「1 个变量基座块 + 1 个 slide 样式块」）：
1. 恢复 slide-demo.html 第一个 `<style>` 块为 style-guide.css 变量基座（` :root { --cobalt-* ... }`），并仅对第二个 slide 样式块应用 font-size 0.88rem + blockquote 紧凑两处改动（即正确重做同步）
2. 保留第一个块（已含修复），删除第二个旧副本块（217-424），再把变量基座补回第一个块前

修完后通知复查。

---

## 六、复查（8347dd8 修复验证）— PASS 100/A

- 日期: 2026-08-27
- Reviewer: Security Reviewer
- 评审级别: L2 (commit-range-audit recheck)
- 范围: 8347dd8 fix@demos（slide-demo single style block + style-guide 变量基座恢复）
- 上轮: CONDITIONAL PASS 80/B（HG-SEC-041 🔴 + HG-SEC-042 🟡）

### Fix Verification

| # | 原严重度 | 修复 | 验证证据 | 结论 |
|:--:|:---:|:---|:---|:---:|
| HG-SEC-041 | 🔴 | 8347dd8 恢复 `:root { --cobalt-* }` 变量基座（style-guide.css 全文 + :root.light 浅色组 + layout-slide 样式合并为单 `<style>` 块） | headless Chrome 实测 `--cobalt-500`=#6366f1 / `--cobalt-400`=#818cf8 / `--surface-900`=#11111b / `--font-mono`='JetBrains Mono' / body bg=rgb(10,10,20) 深色 / body color=rgb(224,224,224) 浅色（原 bg 透明 / text 黑） | ✅ 已修复 |
| HG-SEC-042 | 🟡 | 8347dd8 删除重复 `<style>` 块（2→1），blockquote 紧凑值 0.1rem/2px 16px 生效 | grep 计数 `<style>`=1 / `</style>`=1；`.slide-page blockquote { margin: 0.1rem 0; padding: 2px 16px }`（无旧 0.75rem/8px 副本残留） | ✅ 已修复 |

### 数据验证

| 项 | 结果 |
|:---|:---|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → **185 passed in 33.03s**（无回归） |
| style 块 | slide-demo.html 恰 1 个 `<style>` 块（1 开 1 闭） |
| 变量基座 | --cobalt-50..950 / accent / surface / text / border / code / hero / gh / font / radius 全套 37 定义恢复；:root.light 浅色组完整 |
| --cobalt-500 | getComputedStyle 计算值 **#6366f1** 生效 |
| slide-page 排版 | font-size 0.88rem（line 325）+ blockquote 紧凑（line 354）+ callout 特异性覆盖保留 |
| JS 错误 | window.__testErrors = []（加载 + refresh 两轮） |
| git status | 仅 2 个非范围文件（demos/countries-table.html、demos/drama/history-strategy-table.html，其他 session 内容扩充） |

### 评分

| 项 | 分 |
|:---|:---:|
| 上轮 80 → 本次 100（HG-SEC-041/042 全部关闭，0 🔴 / 0 🟡 / 0 🟢） | **100 (A)** |

### 结论

**PASS（100/A）** — 授权 push。

8347dd8 正确重做同步：单 `<style>` 块内依次为 style-guide.css 变量基座（`:root` + `:root.light`）+ layout-slide 样式。HG-SEC-041（变量基座丢失）与 HG-SEC-042（重复块覆盖）两项均完整修复，深色主题恢复，无 JS 错误，185 tests 全绿。问题仅隔离于 slide-demo.html 单文件，修复范围精确。
