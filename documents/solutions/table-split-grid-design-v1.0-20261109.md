---
title: table 分栏详情「声明式行布局」设计（批2）
version: v1.0
date: 2026-11-09
status: design-only
closed_loop: HTML-GEN-CL027
source: daily-checker 转交件 20261111-to-html-gen-layout-table-lessons ④⑤⑧（只读，路径见 §8）
author: html-gen-ops
scope: 仅设计，不改源码
---

# table 分栏详情 · 声明式行布局（批2）

> 本文件只出设计，**不动源码**。实施另起一批（拟 CL031），本节末给分批建议与实施判据。

## 1. 为什么需要它（对端缺口,不是本仓臆测）

| 缺口 | 对端现象（只读引用） | 本仓现状 |
|:--|:--|:--|
| ④ 行边界不可声明 | 3 列布局里某行只有 1 项，`grid-auto-flow` 把下一项顶进第 3 列，出现「空格被占」的视觉错位 | 分栏详情是扁平 `repeat(auto-fill, minmax(200px,1fr))`（`layout-table.html:201`），行边界完全由流隐式形成 ⇒ **同样表达不了「第 N 行 M 列」** |
| ⑤ 动态行数写不进静态布局 | 逐仓/逐端口等数据驱动行，条数随数据变化 | 无 catch-all、无 hide 清单；现有 `hide` 只能「整列永不显示」，不能「保留数据、只在本布局里不占位」 |
| ⑧ 一套数据两套布局 | 主表与分栏预览各维护一套容器 CSS，同一 `.kv-row` 在两种容器里语义不同（对端现象；**`.kv-row` 在本仓是新类名**，`grep -rn kv-row layout-table.html` = 0） | 数据层已同源（分栏与表格都遍历同一 `COLUMNS`），但**容器仍是两套模型**：表格 `table-layout:fixed` 显式列宽 vs 分栏 auto-fill 栅格 |

批1（CL025）已交付 ②空值跳过 + ③`splitSpan` 权重 + ⑦几何判据；本设计补的是 ④显式行 + ⑤catch-all/hide + ⑧容器统一。

## 2. 键位决策（先解决冲突，再谈能力）

**禁用顶层 `rows`**：`html-gen.py:753`（`data = raw.get('data') or raw.get('rows') or []`）与 `:892`
（键表「`data` 数据行数组（别名 rows，二选一）」）已把它当**数据行**的别名。对端件建议的 `rows: [[...]]`
若照抄进顶层，会被当数据吃掉且**不报错**，只表现为页面变空/错位。

**选定键位**（全部挂在 `options` 下，顶层 schema 零变更）：

```jsonc
"options": {
  "splitGrid": {
    "grid": [                              // 行数组的数组：外层 = 行，内层 = 该行的格
      ["name", "status"],
      ["owner", "repo", { "key": "stats", "span": 2 }],
      ["*"]                                // catch-all：必须最后一行，至多一个
    ],
    "hide": ["cpuLimit", "repoCount"],     // 保留数据、仅在本布局里不渲染
    "skipEmpty": true                      // 等价现 hideEmptyCells:true（见 §4 F 行）
  }
}
```

格元素三态：
- `"key"`（字符串）—— 引用列 key；
- `{ "key": "k", "span": "full" | N }` —— 该格跨列（`full` = 整行，N ≤ 6）；
- `"*"` —— catch-all 占位（只能出现在最后一行、至多一次）。

**为什么叫 `splitGrid` 而不是 `splitRows` / `detailRows`**：`rows` 一词在本仓已被数据行占用，
即便嵌在 `options` 下也容易被配置者误读；`grid` 直指容器模型（二维栅格），且与 ⑧「容器统一」同名。

## 3. 两套容器模型（⑧ 的落点）

现在是**两个模型**：

| 面 | 容器 | 行边界 | 列宽 |
|:--|:--|:--|:--|
| 表格 | `<table>` + `table-layout:fixed` | `<tr>` 显式 | 每列强制显式 `width` |
| 分栏详情 | `.kv-list` = `repeat(auto-fill, minmax(200px,1fr))` | **隐式**（流决定） | 自动填充 |

设计：分栏详情新增**显式栅格模型**（有 `splitGrid.grid` 时启用）。**行边界必须由 JS 逐格写死坐标**：

```
.split-preview .kv-grid { display:grid; grid-template-columns:repeat(var(--kv-cols), minmax(0,1fr));
                          grid-auto-rows:auto; gap:6px; }
.split-preview .kv-item { /* 行/列坐标由 JS 写在 style 上，见下 */ }
.split-preview .kv-item.kv-item-full { grid-column: 1 / -1; }
```

```js
// 逐格写坐标（这是「显式行」唯一可靠的实现方式）
items.forEach(function (it, idx) {
  it.style.gridRow = String(it.__row + 1);      // 1-based
  it.style.gridColumn = it.__col + ' / span ' + it.__span;
});
```

- `--kv-cols`：该布局里「最宽行」的格数（`max(sum(span))`），JS 渲染时算出写到容器上。
- `minmax(0,1fr)` 显式写死 0 下限：避免内容撑破轨道（对端 ⑦ 判据 1「每行宽 ≈ 容器宽 ±2px」要求轨道可压缩）。
- ⛔ **不要用 `.kv-row{display:contents}` 表达行边界**：`display:contents` 只让子项参与父 grid，
  **不产生行边界**。Chromium 实测（3 轨，行 `[a,b]/[c]/[d,e,f]`）：`display:contents` 下得到
  a(top8,left8) b(8,210) **c(8,412)** d(44,8)…，`c` 被流顶到第 1 行第 3 列 —— 正是要修的 ④ 现象；
  改成逐格写 `grid-row/grid-column` 后为 a(8,8) b(8,210) **c(44,210)** d(80,8)…，三行成立。
- （备选）`.kv-row{display:grid;grid-column:1/-1;grid-template-columns:subgrid}` 亦可，但需 subgrid 支持
  （Safari ≥16 / Chrome ≥117），跨浏览器基线更高；除非有明确浏览器承诺，否则取逐格坐标写法。
- 无 `splitGrid` ⇒ 继续走现有 `.kv-list` auto-fill 分支，**一行代码都不改**（向后兼容硬承诺，见 §5）。

## 4. 优先级矩阵（现状键 × 有/无 splitGrid）

| 现状键 | 无 `splitGrid`（缺省） | 有 `splitGrid` | 理由 |
|:--|:--|:--|:--|
| 列 `hide` | 该列不出现在表格与分栏 | **仍然**排除（先 hide 后布局） | 「永不可见」是数据面语义，布局无权复活 |
| 列 `initialHidden` | 默认收起，可开启；分栏仍全列 | 同左（不受 `splitGrid` 影响） | 与 `hide` 语义不同，不进布局 |
| `options.columnsSplit` | 决定**分栏模式左侧表格**的列集，且**优先于** 列 `preview` | 同左 | 二者都只在表格侧生效，`splitGrid` 只管右侧详情面板 ⇒ 与它们零交叉 |
| 列 `preview: true` | 分栏模式下**表格列**的缺省白名单（有任一 `preview` 时表格只显这些列；无 `columnsSplit` 时生效） | 同左（**不受 `splitGrid` 影响**） | 现状 `renderSplitPreview` 明确「忽略列可见性与 preview 过滤」（`layout-table.html:1347`）⇒ preview 从来不是详情面板的键 |
| 列 `splitFull` | 详情面板：该格整行 | 被 `grid` 的 `span:"full"` 取代 | 显式布局优先，见下行 |
| 列 `splitSpan` | 详情面板：N 轨 / `"full"` | 同上，被 `{span}` 取代 | 有 `grid` 时列级权重忽略（避免双源） |
| `options.hideEmptyCells` | 空值不占格（CL025 ②） | 缺省继承；`splitGrid.skipEmpty` 显式设置时**以它为准** | 一个语义两个入口，后者更新更局部 |
| 行级 `url`（iframe 详情） | 整块详情交给 iframe | 与 `grid` 互斥：有 `url` 就不渲染栅格 | 现状即「有 url 则其他字段不显示」，不变 |
| `options.splitGrid.grid` 为空数组/全被 hide | — | 渲染空状态（零节点，不留空轨） | 对端 ⑤「没有剩余时不许渲染空轨」 |

**catch-all 展开规则**：
1. `*` 展开为「所有未被 `grid` 显式引用、未被 `hide`、非 `actions`」的列，按 `COLUMNS` 原顺序；
2. 展开集为空 ⇒ **该行不渲染**（零节点）；
3. 出现两个 `*` ⇒ 只有最后一个生效，`console.warn` 一次（不抛错、不白屏）；
4. `*` 不在最后一行 ⇒ 允许（但它之后的行照常渲染）；`*` 展开的格默认 `span: 1`。

## 5. 向后兼容承诺（对端迁移条件 4）

- 不写 `options.splitGrid` ⇒ 分栏详情走现有扁平 auto-fill，DOM 结构与 CSS 类名不变。
- **机器判据（可执行形态）**：在**临时副本**里用「实施前模板」与「实施后模板」各渲一次同数据、同 flags、且**都不写 `splitGrid`** 的页面，
  两者 sha256 必须相等；另加 `git diff --name-only <实施前>..<实施后> -- 'demos/*.html'` 为空。
  （CL029 `--update`/`--check` 不能直接当这条判据：实施批必然改 `layout-table.html`（在钉子子集里），
  一次 `--update` 会把「产物的意外改动」一并吸收；且 `--verify` 是「产物 vs 当前模板」，对「模板新旧的等价性」不敏感。）
- 老键（`splitFull` / `splitSpan` / `hideEmptyCells` / `preview` / `columnsSplit`）**不删除、不废弃**，
  仅在 `splitGrid` 存在时让位（`preview`/`columnsSplit` 属表格侧，与 `splitGrid` 零交叉、永不让位）。

## 6. 实施判据（下一批照这个验收）

1. **显式行**：3 行布局 `[["a","b"],["c"],["d","e","f"]]` ⇒ `distinct(top) == 3`，且 `c` 的 `top` 等于第 2 行 `top`、`c` 的 `left` 等于第 2 轨 `left`（±1px）——即 `c` **不得**被流顶到第 1 行第 3 列（对端 ④ 复现；±1px 容差因 `getBoundingClientRect` 取整）。
2. **权重与整行**：`{key,span:2}` 宽 ≈ 两倍单轨（±1px 容差下比值 ∈ [1.9, 2.1]）；`span:"full"` 恰等于容器宽（±2px，沿用 CL025 判据 3）。
3. **catch-all 零空轨**：`["*"]` 且展开集为空 ⇒ 该行零节点、不留空隙（`grid-auto-rows` 不产生空行，判据 = 容器高度不含该行）；展开集 3 项 ⇒ 一行 3 格。
4. **hide 不占位**：`splitGrid.hide` 里的列不出现在详情，但数据仍在表格与 CSV 里。
5. **几何三条**（沿用 CL025）：不出容器边界 / 行内不横向重叠 / 窄窗 `scrollWidth ≤ clientWidth`；补一条「同一逻辑行的格 `top` 差 ≤1px，不同行的 `top` 差 >1px」。
6. **向后兼容**：见 §5 的「临时副本双渲 sha 相等」判据（不写 `splitGrid` 的页面字节不变），外加 `git diff --name-only <pre>..<post> -- 'demos/*.html'` 为空。
7. **契约同步**：`help table` 键表新增 `options.splitGrid`（含 `grid`/`hide`/`skipEmpty` 三子键），`tests/test_help_contract.py` 双向守卫通过；计数变更写进 `documents/data-formats.md`。
8. **变异实证**：至少 5 条「改坏必红」（显式行失效 / catch-all 渲染空轨 / span 失效 / hide 复活 / 空值占位），全部拦住才算达标。

## 7. 分批与工作量

| 批 | 内容 | 预估 |
|:--|:--|:--|
| CL031 实施 | 模板 `splitGrid` 渲染分支 + CSS 显式栅格 + 契约/help/文档 + 新增 8 例守卫 + 变异实证 | 0.5–1 天 |
| CL032（可选） | 代表 demo 页示范 `splitGrid`（如 countries-table 分栏用 2 行显式布局），让能力可被眼见 | 0.2 天 |
| 对端迁移 | daily-checker 按 §6 判据替换 `dcKvRowsHtml`（~60 行）+ 删兼容层 CSS（~10 行）+ 判据瘦身（370 行） | 对端排期 |

## 8. 边界（本设计不做的事）

- **不做**任意嵌套布局（`grid` 只支持一层行数组；嵌套需求属过度设计）。
- **不做**响应式断点切换布局（`splitGrid` 是单一布局，窄窗靠 `minmax(0,1fr)` 压缩）。
- **不动**表格侧（`<tr>` 显式行本来就成立）、不动搜索/排序/quickFilter/CSV 面。
- **不改写**对端件；只读引用：`~/CodeSpace/daily-checker/documents/handoff/20261111-to-html-gen-layout-table-lessons.md`（④⑤⑧ 节 + §5 简化映射 + §6 迁移条件）。
- 对端迁移条件 ①（行级容器 + 占满声明）与 ⑧（同源列定义）在本设计里对应 §3 的 `.kv-row{display:contents}` 与「同一 `COLUMNS`」；
  ③ 空值/权重已由 CL025 交付，⑤ catch-all 见 §4 —— **§6 判据 1–6 全绿后，对端的迁移条件 1/2/3 才算齐**。

## 9. 修订记录

**v1.0（初稿）→ v1.0-r1（评审返工，2026-11-09）**

| 编号 | 问题（评审实测） | 处置 |
|:--|:--|:--|
| R1 🔴 | §3 用 `.kv-row{display:contents}` 表达行边界**不成立**：`display:contents` 只让子项参与父 grid，不产生行边界；Chromium 实测 `c` 被顶到第 1 行第 3 列（正是 ④ 现象），与 §6.1 判据自相矛盾 | 改为**逐格写 `grid-row`/`grid-column`**（实测得三行成立）；备选 `subgrid` 方案标注浏览器基线；§6.1 判据改为 `distinct(top)==3` + `c.left == 第 2 轨 left ±1px` |
| R2 🔴 | §4 把 `preview` 写成「详情面板白名单」与实现相反：`preview`/`columnsSplit` 都在**表格侧**，详情面板明确忽略 preview（`layout-table.html:1347`），且 `columnsSplit` 优先 | 该两行改为「表格侧、与 `splitGrid` 零交叉、永不让位」；§5 老键清单补 `columnsSplit` |
| R3 | §5「向后兼容」原判据不可执行：实施批必改 `layout-table.html`（在钉子子集内），`--update` 会把意外改动一并吸收；且 `--verify` 只比「产物 vs 当前模板」 | 改为「临时副本双渲（实施前/后模板，同数据同 flags 且不写 `splitGrid`）sha 必须相等」+ `git diff --name-only <pre>..<post> -- 'demos/*.html'` 为空 |
| R4 | §1 的 `.kv-row` 是对端类名，本仓 `grep -rn kv-row layout-table.html` = 0，易被读成既有结构 | 该行加注「`.kv-row` 在本仓是新类名」 |
| R5 | §6 判据 1/5 的「top 相同」缺容差口径 | 统一为「同行 top 差 ≤1px、异行 top 差 >1px」 |
