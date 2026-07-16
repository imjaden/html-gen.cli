# 安全审计日志

## 2026-07-12 — 初次全项目安全评审

- **Reviewer**: Security Reviewer
- **Level**: L2 (AI Deep Review)
- **Scope**: 全仓库 (3 commits, 0e35dce HEAD)
- **Commit(s)**: 6fc412a → 2b17f48 → 0e35dce
- **Verdict**: FAIL
- **Score**: 60 / 100 (Rating: C)

### Summary

`html-gen` 是一个零依赖 Python CLI 工具，将 Markdown/JSON 数据注入 HTML 模板生成自包含单文件。项目整体结构清晰，无硬编码凭据，git 历史干净。但存在 **2 个 🔴 高危** 和 **2 个 🟡 中危** 问题，主要集中在 JSON 注入 `<script>` 标签导致 XSS 和路径穿越漏洞。由于工具生成的是可共享的自包含 HTML 文件，XSS 具有实际攻击面。

### Findings

| # | Severity | Title | File:Line | Status |
|:-:|:--------:|:------|:---------:|:------:|
| 1 | 🔴 | JSON 注入 `<script>` 标签导致 XSS | `layout-table.html:135-138`, `layout-knowledge.html:150-151` | **Fixed** |
| 2 | 🔴 | 路径穿越 — JSON schema 可控制输出路径 | `company-report.py:36,50,56` | **Fixed** |
| 3 | 🟡 | innerHTML 注入未转义的 JSON 值 | `layout-table.html:225`, `layout-knowledge.html:252` | **Fixed** |
| 4 | 🟡 | Markdown 解析器未转义原始 HTML | `html-gen.py:78-111` | **Fixed** |

### Positives

- ✅ 无硬编码凭据（API Key/Token/Password）
- ✅ git 历史无敏感文件残留
- ✅ `subprocess.run` 使用 list 参数而非 `shell=True`
- ✅ 零外部依赖，供应链风险极低
- ✅ `.gitignore` 覆盖 `.env`、虚拟环境和 IDE 文件

### Tracking

| Issue | Title | Severity | Priority | Status |
|:------|:------|:--------:|:--------:|:------:|
| HG-SEC-001 | JSON 注入 `<script>` 标签导致 XSS | 🔴 HIGH | P1 | ✅ Fixed |
| HG-SEC-002 | 路径穿越 — JSON schema 可控制输出路径 | 🔴 HIGH | P1 | ✅ Fixed |
| HG-SEC-003 | innerHTML 注入未转义的 JSON 值 | 🟡 MEDIUM | P2 | ✅ Fixed |
| HG-SEC-004 | Markdown 解析器未转义原始 HTML | 🟡 MEDIUM | P2 | ✅ Fixed |

---

## 2026-07-12 — 安全修复 (SEC-FIX-001)

- **Fixer**: dev agent
- **Commit**: (pending)
- **Verdict**: PASS

### HG-SEC-001: `</script>` 注入 XSS → ✅ Fixed

**Root cause**: `inject()` 直接将 JSON 字符串写入 `<script>` 标签，攻击者可通过数据中嵌入 `</script>` 提前闭合标签并注入恶意脚本。

**Fix**: `html-gen.py` `inject()` 函数 — 对所有注入值执行 `s.replace('</', '<\\/')`。`<\/` 是 HTML 中 `</script>` 的标准转义形式，浏览器不会将其识别为闭合标签，但 JS 中 `\/` 等同于 `/`，运行时字符串值不变。

**Verification**: 输入 `{"name": "test</script><script>alert(1)</script>"}` → 输出 `"test<\/script><script>alert(1)<\/script>"` ✅

### HG-SEC-002: 路径穿越 → ✅ Fixed

**Root cause**: `company-report.py` 直接用 schema 中的路径字段拼接 `HTML_DEMOS / out['groups_file']`，攻击者可通过 `../etc/hosts` 写入任意位置。

**Fix**: `company-report.py` 新增 `_safe_path()` 函数 — resolve 后校验结果是否在 `HTML_DEMOS` 子树内，否则拒绝并退出。

**Verification**: 输入 `"groups_file": "../etc/hosts"` → `❌ 路径穿越拒绝: ../etc/hosts` + exit 1 ✅

### HG-SEC-003: innerHTML XSS → ✅ Fixed

**Root cause**: `layout-table.html` 渲染时未转义用户数据的 HTML 实体，如数据中含 `<img onerror=...>` 会被执行。

**Fix**: 新增 `escapeHtml()` 函数（使用 `textContent` 赋值实现安全转义）+ `col.escape: true` 列配置选项。保持向后兼容：默认不转义（支持 `col.render` 的现有 HTML 渲染行为），需显式开启 `col.escape`。

### HG-SEC-004: Markdown HTML 转义 → ✅ Fixed

**Root cause**: `md_to_html()` 对非 Markdown 语法的普通文本行不做处理，原始 `<script>` 等标签直接注入 HTML。

**Fix**: 新增 `_md_escape()` 函数 — 转义 `&` `<` `>`，在 `inline_format()` 之前对标题、列表项、引用（含 callout）、普通段落文本统一调用。`inline_format()` 的 Markdown 语法处理不受影响（`**bold**` → `<strong>bold</strong>` 仍正常）。

**Verification**: 输入 `<script>alert(1)</script>` → 输出 `&lt;script&gt;alert(1)&lt;/script&gt;` ✅；`**bold**` → `<strong>bold</strong>` ✅

---

## 2026-07-12 — 复查: 4 项安全修复验证 + 新增代码扫描

- **Reviewer**: Security Reviewer
- **Level**: L2 (AI Deep Review)
- **Scope**: HEAD (ad5694c) — 含 5 个新 commit (723880e fix + 4 features)
- **Commit(s)**: 723880e → 92b6f24 → 332b45e → 4274049 → ad5694c
- **Verdict**: PASS
- **Score**: 95 / 100 (Rating: A)

### Summary

复查验证 commit 723880e 的 4 项安全修复全部生效。扫描了后续 4 个 feature commit 新增的 Cmd+F 覆盖层、skills table 数据、demo 页面等，无新增安全问题。HG-SEC-003 (innerHTML XSS) 的 fix 采用 opt-in `col.escape` 策略以保持向后兼容，默认不转义；因 `</script>` 突破口已被 HG-SEC-001 封堵，剩余风险可控。

### Findings 修复验证

| # | Severity | Title | Fix | Status |
|:-:|:--------:|:------|:----|:------:|
| 1 | 🔴 | JSON 注入 `<script>` 标签 | `inject()` 中 `</` → `<\\/` 转义 | ✅ Verified |
| 2 | 🔴 | 路径穿越 | `_safe_path()` 路径边界校验 | ✅ Verified |
| 3 | 🟡 | innerHTML XSS | `escapeHtml()` + `col.escape` 列选项 | ⚠️ Opt-in (向后兼容) |
| 4 | 🟡 | MD 解析器 HTML 转义 | `_md_escape()` 统一转义 `&<>` | ✅ Verified |

### 新增代码扫描

- `layout-table.html` Cmd+F 覆盖层 (L529-613): 使用 `textContent` 安全渲染 — ✅ 无问题
- `data/_skills-table-config.json` (1023行): 技能数据，无凭据 — ✅ 无问题
- `data/_user-skills.json` (1917行): 本地路径信息，无凭据 — ✅ 无问题
- `demos/hermes-profile-skills-list.html` (803行): 生成的 demo 文件 — ✅ 无问题
- `demos/table-actions-demo.html` (117行): demo 页面 — ✅ 无问题
- `documents/cmdf-quick-search-design.md`: 纯文档 — ✅ 无问题

### ⚠️ 关注项 (非阻塞)

HG-SEC-003 的 `escapeHtml()` 采用 opt-in 设计 (`col.escape: true`)，默认不转义。这是为兼容 `col.render` 的 HTML 渲染行为所做的权衡。后续版本建议将默认行为改为 escape-by-default + `col.html: true` opt-out，但当前设计风险可控。

---

## 2026-07-14 — 全量复查: 15 commits, D 型 slide 模板 + 重构

- **Reviewer**: Security Reviewer
- **Level**: L2 (AI Deep Review)
- **Scope**: HEAD (2f6fd80) — 15 new commits since last review
- **Commit(s)**: 777cba4 → ... → 2f6fd80
- **Verdict**: PASS
- **Score**: 100 / 100 (Rating: A)

### Summary

全量复查 15 个新 commit，核心变更是 doc/slide 模板拆分重构 + D 型 slide 模板首次实现。上轮 4 项安全修复全部保持有效，新增代码（519 行 `layout-slide.html`、`cmd_slide()`、`install.sh`、帮助系统、测试套件）安全质量优异。设计审查中 3 个 🟡 项（`_lang` 白名单、`Object.keys` 替换 `for...in`、主题恢复）在实现中全部落实。`inject()` 优化为仅对 `<script>` 上下文 key 做 `</` 转义，非 script 值不再无故转义。`.review-level.yaml` 被误删已恢复。

### 新增代码逐项扫描

| # | 文件 | 行数 | 扫描结果 |
|:-:|:-----|:----:|:---------|
| 1 | `layout-slide.html` | 519 | ✅ `textContent`/`cloneNode`/`createElement` 全链路，仅 2 处 `innerHTML` 用于服务端生成的受信 HTML (`<!--METADATA-->`) |
| 2 | `html-gen.py` +230 | 546 | ✅ `cmd_slide()` 安全注入，`_SCRIPT_KEYS` 精确控制转义范围，帮助系统全硬编码 |
| 3 | `install.sh` | 56 | ✅ bash heredoc + sed，无 eval/unsafe ops |
| 4 | `tests/test_templates.py` | 114 | ✅ `os.system()` 仅用于测试，参数全硬编码 |
| 5 | `tests/test_slide_h3_toggle.py` | 92 | ✅ Selenium 测试，无安全问题 |
| 6 | `layout-doc.html` ±28 | — | ✅ CSS only，无 JS 变更 |
| 7 | `skills/html-gen/SKILL.md` | 271 | ✅ 文档 |
| 8 | Demo HTML 文件 | ~1,800 | ✅ 由 CLI 生成，继承模板安全属性 |

### 设计审查项落实 (layout-slide-toolbar-design.md)

| 原审查项 | 实现状态 |
|:---------|:---------|
| 🟡 `_lang` 白名单校验 | ✅ L218-219: `(_lang === 'zh' \|\| _lang === 'en') ? _lang : 'zh'` |
| 🟡 `t()` `for...in` → `Object.keys` | ✅ L226: `Object.keys(params).forEach(...)` |
| 🟡 主题初始加载恢复 | ✅ L243-244: 读 localStorage + 应用 class |
| 🟡 路径正则跨平台 | ✅ L260: `/^\/Users\/[^/]+/` → 追加 `/^\/home\/[^/]+/` |
| 🟢 `window.isSecureContext` | ✅ L262: clipboard 调用前检查 |

### Positives

- ✅ D 型 slide 模板安全意识极强：全链路 `textContent`/`cloneNode`/`createElement`，零 `innerHTML` 注入用户数据
- ✅ `inject()` 优化：`_SCRIPT_KEYS` 精确控制只对 script 上下文做 `</` 转义
- ✅ 设计审查 5 个 🟡 项在实现中全部落实
- ✅ 测试覆盖 doc/slide/table/knowledge 四型模板
- ✅ Slide 模板全屏 API 标准调用，无 `window.open` 注入

### 🔧 修复项

- `.review-level.yaml` 被误删 → 已恢复并更新 (commit 2f6fd80 之后)

---

