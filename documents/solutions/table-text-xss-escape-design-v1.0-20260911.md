# 表格文本列 XSS 转义设计 v1.0（HG-SEC-134）

> 日期: 2026-09-11
> 状态: 实施中
> 闭环: HTML-GEN-CL010
> 决策: A2+B1+C1+D1+E1+F2

## 1. 问题

layout-table.html 主表格单元格渲染（line 529-605）对普通 text 列使用 raw innerHTML，未做 HTML 转义。
当可写文本字段（note / capital_zh / ethnic_groups 等）含 `<script>` 或事件处理器时，可注入 stored XSS。

现状:
- `col.escape: true` 显式标记才转义（opt-in），countries 18 列全部未设
- modal / split preview / expand 三条路径已 escapeHtml，无风险
- 唯一依赖 HTML 的 text 列: `_demos-data.json`「文档链接」（raw `<a>` 标签）

攻击路径: 反馈 Issue → --apply 写回 data JSON → 重建 HTML → 访客浏览触发脚本

## 2. 设计决策

### A. 转义机制（A2 模板侧默认转义）

主表格单元格渲染改为**默认转义**，`col.escape === false` 显式豁免。

```js
// 修改前 (line 586-589)
if (col.render) val = col.render(val, row);
else if (col.format === 'thousands' && typeof val === 'number') val = val.toLocaleString('en-US');
else if (col.escape) val = escapeHtml(String(val));
else if (val === undefined || val === null) val = '';

// 修改后
if (col.render) val = col.render(val, row);
else if (col.format === 'thousands' && typeof val === 'number') val = val.toLocaleString('en-US');
else if (col.escape === false) { /* 显式豁免: raw HTML */ }
else if (val === undefined || val === null) val = '';
else val = escapeHtml(String(val));
```

### B. 覆盖范围（B1 全局）

模板层改动，影响所有 A 型表格案例。扫描确认:
- countries / provinces / skills / features / drama 等所有数据文件均不含 `<` 字符（text 列）
- 唯一含 HTML 的列: `_demos-data.json`「文档链接」→ 加 `escape: false`
- `_skills-table-config.json` profiles 列已有 `escape: true`（pills 路径不受影响）

### C. 入库防护（C1 反馈脚本侧拦截）

`countries-issue-sync.py` 写盘前检查 string 字段值含 `<` 或 `>` → 拒绝并报错。

位置: `plan_issues()` line 261 后，数值列分支之后。

```python
# C1: XSS 入库防护 — 拒绝含 HTML 标签的建议值
if '<' in new or '>' in new:
    skips.append((no, f'字段 {field} 建议值含 HTML 标签字符（< 或 >），安全策略拒绝'))
    continue
```

覆盖: 所有 editable string 字段（含 --value 人工裁决路径）。
数值列已走 `to_number()`，不含 `<`/`>`，无需额外检查。

### D. HTML 列兼容（D1 列级 escape:false）

需 HTML 渲染的列在 JSON columns 定义里显式 `"escape": false`。

现有唯一案例: `_demos-data.json`「文档链接」列。

新增表格若需 HTML 列，同样在 columns 里声明 `"escape": false`。

### E. 无反馈页面（E1 防御性默认转义）

默认转义与 `--feedback-repo` 无关，所有 A 型表格页面均受保护。

## 3. 四条渲染路径安全矩阵

| 路径 | 位置 | 修复前 | 修复后 |
|:---|:---|:---|:---|
| 主表格单元格 | render() line 529-605 | ❌ raw innerHTML | ✅ 默认 escapeHtml |
| 分栏预览 | renderSplitPreview() line 1118-1156 | ✅ 已 escape | ✅ 不变 |
| 弹窗 modal | showModal() line 872-883 | ✅ 已 escape | ✅ 不变 |
| 行内展开 | expand grid line 610-626 | ✅ 已 escape | ✅ 不变 |

## 4. 影响面与回归评估

受影响页面（数据侧无 HTML，转义后视觉不变）:
- countries-table.html（195 行 × 18 列）
- provinces-table.html（34 行 × 11 列）
- hermes-profile-skills-list.html（98 行 × 6 列）
- table-features-demo.html / table-actions-demo.html
- 所有 drama 策略/时间轴表

需数据侧修复:
- demos-index.html: 「文档链接」列加 `escape: false`

视觉回归: `escapeHtml('<')` → `&lt;`，数据不含 `<` 则零变化。

## 5. 测试计划

1. 新增 test_xss_escape.py:
   - 生成含 `<img src=x onerror=alert(1)>` 的 table JSON → html-gen table → 加载 → 断言
     主表格 / split / modal / expand 四路径均无脚本执行 + payload 按纯文本呈现
2. 全量 pytest 回归 305 → 0 失败
3. demos-index.html 重建后「文档链接」仍为可点链接

## 6. 提交计划

```
feat@table: default HTML escape for text cells (HG-SEC-134, CL010)
```

文件变更:
- layout-table.html（模板）
- data/_demos-data.json（escape:false）
- scripts/countries-issue-sync.py（入库防护）
- tests/test_xss_escape.py（新增）
- documents/solutions/table-text-xss-escape-design-v1.0-20260911.md（本文件）
