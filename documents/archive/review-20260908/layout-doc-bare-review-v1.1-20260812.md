# layout-doc 嵌入降级 — 复审报告（v1.1）

## 版本

v1.1 复审 (2026-08-12)

## 审查对象

- documents/solutions/layout-doc-bare-design-v1.1-20260806.md (HEAD c80c4de)

## 复审结论

**PASS** — 上轮 5 项意见（N1-N5）全部正确闭合，可直接交付 dev 实施。

## 修正项核验

| 编号 | 上轮意见 | v1.1 修正 | 核验 |
|:--|:--|:--|:--:|
| N1 | 三 class（doc-full+no-*）改双独立 class | D2 改 `show-sidebar`/`show-toolbar`，CSS/JS 一一对应 | ✅ grep 无 `no-sidebar`/`no-toolbar`/`doc-full` 残留 |
| N2 | 产物清单漏 2 个 | D4 补全 22 个逐一列名 | ✅ grep `doc-wrapper` 实测 22（drama 15 + root 7）与清单完全一致 |
| N3 | "iframe 不带参"表述错误 | D3 补 `?t=` 时间戳事实 + 测试去 `?t=` 比对 | ✅ 与 layout-knowledge `frame.src = item.url + '?t=' + Date.now()` 一致 |
| N4 | 测试计数陈旧（写 103 实 100） | D5 改为 103 | ✅ `--collect-only` 实测 103 tests |
| N5 | collapsed 交互需明确 | D2 明确 show-sidebar 只控 display 不碰宽度 + D5 补折叠测试点 | ✅ 逻辑自洽 |

## 双 class 方案一致性核验

CSS（v1.1 D2）与 JS 一一对应，无死 class：

```css
.doc-sidebar { display: none; }        /* 默认隐藏 */
.top-toolbar { display: none; }        /* 默认隐藏 */
body.show-sidebar .doc-sidebar { display: flex; }
body.show-toolbar .top-toolbar { display: flex; }
```

```js
if (params.get('sidebar') === '1') document.body.classList.add('show-sidebar');
if (params.get('toolbar') === '1') document.body.classList.add('show-toolbar');
```

- 显示规则 `body.show-sidebar .doc-sidebar` 特异性 (0,2,1) > 隐藏规则 (0,1,0) ✅
- `flex-direction: column` 由原 L15 规则保留，`display:none` 不触碰该属性 ✅
- 四种形态（缺省/仅 sidebar/仅 toolbar/组合）天然成立 ✅

## 🟢 观察（非阻塞）

### N6 — CSS 级联顺序需在实施时明确

原模板 `.doc-sidebar`（L15）与 `.top-toolbar`（L142）**均已有 `display: flex`**。D2 新增的默认隐藏规则 `.doc-sidebar { display: none }` / `.top-toolbar { display: none }` 必须**放置在这两条原规则之后**（同特异性 0,1,0，靠后覆盖），否则级联顺序会使默认隐藏静默失效。

**建议**：实施时优先采用"改写原规则"而非"追加覆盖"——直接在 L15 `.doc-sidebar` 删除 `display: flex`、L142 `.top-toolbar` 删除 `display: flex`，再由 `body.show-*` 规则驱动显示；或在设计 D2 补一句"隐藏规则置于原 `display:flex` 声明之后"。此为实施细节，不构成驳回。

## 检查项结果

| 维度 | 结果 |
|:--|:--|
| 1. 需求覆盖 | ✅ 通过 |
| 2. 入参字段设计 | ✅ 通过 |
| 3. 实现安全性 | ✅ 通过（双 class 无死码；N6 为实施顺序提示） |
| 4. 布局影响 | ✅ 通过 |
| 5. 重新生成范围 | ✅ 通过（22 个完整） |
| 6. 测试规划 | ✅ 通过（4 组合 + 折叠 + 嵌入断言） |
| 7. 文档同步与风险 | ✅ 通过 |

## 结论

**PASS** — 5 项修正全部闭合，可切 dev role 按 D1-D6 实施。实施时注意 N6 级联顺序（改写原 `display:flex` 或置后隐藏规则），并在 test_doc_bare 中覆盖 4 种参数组合 + 折叠态。
