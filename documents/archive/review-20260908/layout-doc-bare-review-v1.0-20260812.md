# layout-doc 嵌入降级：侧边栏/工具栏默认隐藏 — Review 报告

## 版本

v1.0 (2026-08-12)

## 审查对象

- documents/solutions/layout-doc-bare-design-v1.0-20260806.md (HEAD 5ac2e6d)

## 审查范围

按 7 个审计维度逐项核查，并对 layout-doc.html / layout-knowledge.html 源码与 demos 产物做了实证核验。

## 核验事实

| 项 | 核验结果 |
|:---|:---|
| `.doc-wrapper` 结构 | `display:flex; min-height:100vh`（L10），`.doc-main{flex:1; overflow-y:auto}`（L65）— sidebar 隐藏后 doc-body 自动全宽 ✅ |
| `.top-toolbar` 位置 | body 直接子元素（L197），`position:fixed`，非 `.doc-wrapper` 内 — 与 `.doc-sidebar`（wrapper 内）层级不同 |
| `.doc-sidebar` 已有规则 | L174 `display:none` 在 `@media(max-width:768px)` 内（移动端）；L175 `.doc-sidebar.open` 汉堡态；L181 print `!important` |
| localStorage 键 | `html-gen:doc_lang` / `html-gen:doc_theme` / `html-gen:doc:h3-visible` / `html-gen:doc:sidebar-collapsed`（设计写 "doc_lang/theme/collapsed" 略简） |
| knowledge iframe src | `frame.src = item.url + '?t=' + Date.now()` — **iframe 带 `?t=` 时间戳，非"不带参"** |
| doc-wrapper 产物总数 | **22 个**（drama 15 + root 7），设计 D4 列 root 仅 5+ |
| 当前测试总数 | **100**（100/100），设计写 "103" |

## 检查项结果

| 维度 | 结果 |
|:--|:--|
| 1. 需求覆盖 | ✅ 默认隐藏 + 两入参 + knowledge 降级 全覆盖 |
| 2. 入参字段设计 | ✅ sidebar/toolbar 命名自明，URLSearchParams 与 ?t= 正交 |
| 3. 实现安全性 | 🔴 D2 JS 三 class 方案自相矛盾（见 N1） |
| 4. 布局影响 | ✅ sidebar 隐藏后 doc-main 全宽正确；进度条/灯箱 body 级不受影响 |
| 5. 重新生成范围 | 🔴 D4 清单漏 2 个产物（见 N2） |
| 6. 测试规划 | ✅ 4 组合覆盖充分；knowledge 嵌入断言需注意 ?t= |
| 7. 文档同步与风险 | ✅ 默认行为变更已确认；旧产物过渡已列 |

## 🔴 阻断项

### N1 — D2 JS 三 class 方案自相矛盾，属未完成设计

**问题**：D2 提出 `doc-full` + `no-sidebar` + `no-toolbar` 三 class 机制，但设计只给出了 `doc-full` 的 CSS 规则（`.doc-wrapper .doc-sidebar {display:none}` / `body.doc-full ... {display:flex}`），`no-*` 两个 class **没有任何对应 CSS**。JS 里 `if (params.get('sidebar') !== '1') body.classList.add('no-sidebar')` 添加的是死 class，无法产生任何视觉效果。且设计第 54-55 行自认"具体实现以 dev 阶段简化为主，目标：参数驱动"，表明实现方案在设计阶段尚未收敛。

**建议改法**：废弃 `doc-full`/`no-*` 三 class，改为**两个独立 class，每个入参独立控制，CSS 与 JS 一一对应**：

```css
/* 默认隐藏 */
.doc-wrapper .doc-sidebar { display: none; }
.top-toolbar { display: none; }
/* 入参驱动显示 */
body.show-sidebar .doc-wrapper .doc-sidebar { display: flex; }
body.show-toolbar .top-toolbar { display: flex; }
```

```js
var p = new URLSearchParams(location.search);
if (p.get('sidebar') === '1') document.body.classList.add('show-sidebar');
if (p.get('toolbar') === '1') document.body.classList.add('show-toolbar');
```

两 class 方案每个参数独立、无组合爆炸、CSS 与 JS 完全对应，`?sidebar=1` / `?toolbar=1` / 组合 / 缺省四种形态天然成立。

### N2 — D4 重新生成清单不完整，漏 2 个产物

**问题**：实测 `grep doc-wrapper` 得 22 个产物，drama 15 个正确，但 root 实为 **7 个**，设计 D4 列 5+ 漏了：
- `demos/template-B-markdown-spec-v1.0-20260707.html`
- `demos/template-C-guide-v1.0-20260707.html`

设计第 68 行写了"如有遗漏，grep doc-wrapper 补全"作为兜底，但遗漏项应作为**明确待办**写进 D4 清单，而非模糊兜底（否则实施时可能漏生成，导致这两个页面仍显示完整 UI，与默认行为不一致）。

**建议改法**：D4 清单补全为 22 个（drama 15 + root 7，逐一列名），并在待办清单 D4 行明确"grep doc-wrapper 输出与清单核对一致"。

## 🟡 非阻塞观察

### N3 — D3 "iframe url 不带参"表述不准确

**问题**：layout-knowledge 的 `frame.src = item.url + '?t=' + Date.now()` 会给 iframe URL 追加 `?t=` 时间戳，D3 第 60 行"knowledge 的 item url 保持不带参"与事实不符。

**建议改法**：D3 表述改为"knowledge 的 item url 不带 sidebar/toolbar 参（仅带 `?t=` 缓存破坏参，URLSearchParams 已兼容）"。功能上无影响（默认隐藏仍生效），但需同步修正 test_drama_knowledge 嵌入断言的预期（iframe src 含 `?t=`，判断可见性而非 url 相等）。

### N4 — 测试计数陈旧

**问题**：D5 第 81 行写"现有 103"，实测当前 100（100/100）。

**建议改法**：更新为"现有 100，新增 test_doc_bare 后预期 104+"。

### N5 — collapsed 态与 show-sidebar 的交互

**问题**：侧边栏 `collapsed`（48px 态）由 localStorage `html-gen:doc:sidebar-collapsed` 恢复，init 时 `toggleSidebar()` 会无条件执行（L322）。当默认隐藏（无参）时，`[` 快捷键与 toggleSidebar 仍会运行，但 `display:none` 下无视觉反馈，属死交互；当用户曾折叠后访问 `?sidebar=1`，会以 48px 折叠态展示。均非 bug，但建议在 D2 明确"show-sidebar 不影响 collapsed 态（只控制 display，不触碰宽度）"以消除实施歧义。

## 修改意见（按 D1-D6 定位）

| 编号 | 定位 | 意见 |
|:--|:--|:--|
| N1 | D2 | 三 class → 两独立 class（show-sidebar/show-toolbar），CSS/JS 一一对应 |
| N2 | D4 | 清单补全为 22 个（root 7 逐一列名），grep 核对 |
| N3 | D3 | 修正"iframe 带 ?t="表述，同步 test 断言 |
| N4 | D5 | 测试计数 103 → 100 |
| N5 | D2 | 明确 show-sidebar 只控制 display、不触碰 collapsed 宽度 |

## 结论

**CONDITIONAL PASS** — 需求覆盖、入参字段、布局影响、测试规划、文档同步均达标；2 个 🔴 阻断项（N1 三 class 方案未完成、N2 产物清单漏 2 个）需修复后即可交付 dev 实施。N3-N5 为非阻塞观察，建议一并修正。

修复 N1/N2 后（N3-N5 建议同步），可切 dev role 按 D1-D6 实施。
