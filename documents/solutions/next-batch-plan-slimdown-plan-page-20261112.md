# 下一批方案：slimdown 方案页改版（七列 / 拖拽 / 等宽出图）· 2026-11-12

> **v2（2026-11-22 已实施，本页下半部分为 v1 存档）**
> 用户新指令：整页按 `居家训练计划-v1.2-20261122.html` 源码重做，并加右下角悬浮按钮组 + 统一面板，
> 再参考 `lock-screen-plugin@1.4.js` 加左上角主题色切换。下表 v1 的 D3/D5/D6 与工具条已被 v2 取代。
>
> | 项 | v2 决策 |
> |---|---|
> | V1 视觉骨架 | 照抄参考页：深色暖调、居中 masthead（kicker/渐变标题/副标题）、七卡等宽、红色刀旗（星期/主题/时长）、虚线 chip、编号动作行 + 次数徽章、卡底口号、百叶窗展开 |
> | V2 宽度 | 回到参考页的 100%（sheet 左右 16px，1440 下每卡 194px），**不再用 90vw** |
> | V3 数据 | 沿用 slimdown 七日方案（每天 3–5 项），`_slimdown-plan.json` 每天补 `slogan`；周六按 `rest` 判定，不抄参考页把周六标成「恢复日」的笔误 |
> | V4 徽章 | 徽章只放次数（`8–10`），组数进 chip：全等→`建议 N 组`，不等→`建议 min–max 组`，`sets≤1` 的单次有氧不参与统计 |
> | V5 入口 | 右下角 FAB 两个：`✎` 编辑、`⤓` 保存图片；卡片点击 = 该日编辑，`⠿` 手柄仍是拖拽 |
> | V6 面板 | 同一弹层四段：标题 / 七天页签（默认今天，自动滚到可见）/ 功能区（`编辑方案`｜`预览方案图片` 分段切换）/ 底部（分享链接·复制图片·打印 ＋ 保存方案·下载图片，按视图启用） |
> | V7 保存 | 改动即写 localStorage（静默）；`保存方案` = 显式落盘 + toast（幂等） |
> | V8 出图 | 深色卡、宽度 = 预览实际宽（1x）；克隆前把主题变量内联到克隆根，保证 PNG 与屏幕同色 |
> | V9 主题 | `data-theme` + 四套成套变量（赤金默认 / 墨绿 / 靛蓝 / 暖橙），左上角 🎨 下拉，`localStorage.slimdownPlanTheme` 持久化；分享链接不带主题 |
> | V10 打印 | 只翻底色与文字色，保留当前主题强调色；隐藏 FAB / 主题条 / 面板 |
> | V11 文件拆分 | 新增 `_src/plan.css`（只服务 plan 页）；`base.css` 继续只服务 archive，避免深色改版波及档案页 |
> | V12 版本 | `v1.2` / 2026-11-22 |
> | V13 卡片行（2026-11-22 追加，全采推荐） | 拖拽手柄移到卡顶水平居中（36×20 热区，刀旗下移 4px）；动作名两行（中文 11.5px + 英文 10.5px 斜体，纯中文单行居中）；行高 35px、间隔 3px、行悬停 `rgba(255,255,255,.045)`；徽章 56→自适应（`min-width:56`，长值不截断，实测 56/58/60/76）；名称列 79→87~93px；出图卡同步两行；打印行高 26px + 隐藏 masthead/chip/手柄 ⇒ 7 卡一页（body 900px） |
>
> 实施落点：`demos/slimdown/_src/{plan.tpl,plan.css,plan.js}`、`scripts/build-slimdown.py`（plan 页改用 plan.css）、
> `data/_slimdown-plan.json`（slogan + 版本）。实测：1440 下 7 卡各 194px、行宽 1408；出图 720×245 == 预览；
> 墨绿主题 PNG 与屏幕同色；拖拽交换整天方案（主题/时长/口号/动作一起走）。
>
> ---

> 状态（v1）：**方案已落，等指示实施**（本次不动源码）。
> 决策来源：用户「全采推荐」——D1–D6 全按本文件推荐项执行。
> 真值来源：本轮实测（1440×900 探针）——7 卡 90vw ⇒ 每卡 171px；预览卡实测 379×457；
> 导出实测 1440×870（720 CSS × 2）；`text-overflow: ellipsis` 在 foreignObject 光栅化后仍生效。

---

## 1. 决策记录（已定，不再讨论）

| 项 | 决策 |
|---|---|
| D1 顶部 | 只删三页菜单（动作库 / 训练方案 / 档案），保留标题 + 版本小字 |
| D2 02–04 三节 | 迁到 `archive.html`，plan 页只留方案本身 |
| D3 宽度 | `.sheet` 保持 980；卡片行 full-bleed 到 90vw（居中溢出） |
| D4 拖拽语义 | 交换两天**内容**，星期标签固定（周一 ↔ 周五 换的是练什么） |
| D5 窄屏 | ≥1100px 七列；<1100px 横向滚动，卡固定 168px |
| D6 预览/出图 | 预览卡固定 720 逻辑宽；导出 1x ⇒ PNG 宽 == 预览宽；2x 留作后续开关，不默认开 |

---

## 2. 结构改动

### 2.1 `plan.tpl`

- 删除 `<nav class="case-nav">`；（动作库/档案入口改为页脚一行小字，可点）
- 保留 `.masthead`（标题 + 版本/日期）；
- 工具条保留：`分享链接` / `打印`；删除 `今日卡片` / `整周卡片` 两个全局按钮（改为卡片级 `▣`）；
- 删除 `02 运动量区间` / `03 一天节奏` / `04 止损线` 三节 → 迁到 archive；
- `#weekGrid` 改名 `#weekRow`（语义：一行七天）。

### 2.2 `archive.tpl`

- 把上述三节插到「01 基线与目标」之后，成为 02 / 03 / 04；
- 原 02–07 顺延为 05–10；A–D（FAQ）编号不变；
- `{{SAFETY}}` 占位符随「止损线」一起搬过去（build 脚本已对两页都替换，无需改）。

---

## 3. 七列布局（`base.css`）

```css
/* 一整行七天，总宽 90vw，从 980 容器里居中溢出 */
#weekRow{
  display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:10px;
  width:90vw;position:relative;left:50%;transform:translateX(-50%);
}
#weekRow .day-card{display:flex;flex-direction:column;min-width:0;}  /* 等高 + 页脚吸底 */
#weekRow .day-card .d-foot{margin-top:auto;display:flex;align-items:center;gap:6px;
  padding-top:6px;border-top:1px dashed var(--rule);font-size:10.5px;color:var(--muted);}
#weekRow .day-card .d-acts{margin-left:auto;display:flex;gap:2px;}

/* 窄屏：横滚，卡固定宽 */
@media (max-width:1100px){
  #weekRow{display:flex;overflow-x:auto;width:100%;left:0;transform:none;
    scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;padding-bottom:4px;}
  #weekRow .day-card{flex:0 0 168px;scroll-snap-align:start;}
}

/* 打印：七列压成 3 列 */
@media print{#weekRow{display:grid;grid-template-columns:repeat(3,1fr);width:100%;left:0;transform:none;}}
```

卡内清单每行两端对齐、名字单行省略：

```css
.day-card li{display:flex;gap:4px;white-space:nowrap;overflow:hidden;}
.day-card li .nm{flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;}
.day-card li .v{flex:0 0 auto;font-variant-numeric:tabular-nums;}
```

**卡脚**：左「5 个动作 共 17 组」，右 `✎`（编辑方案）/ `▣`（预览卡片），
均 24×24 触摸区，`aria-label` + `title` 齐全；`type="button"`。

---

## 4. 拖拽（`plan.js`）

**用 Pointer Events，不用 HTML5 DnD**（后者在 iOS 不触发）。

- 入口：卡头 `⠿` 手柄 `pointerdown`（`setPointerCapture`），卡体点击不再进编辑；
- 触屏：手柄 `touch-action:none`；卡体保持 `touch-action:pan-x`（横滚优先）；
- 拖动中：跟随指针的 ghost（`position:fixed` 半透明克隆 0.9 透明 / 1.02 缩放），
  用 `elementFromPoint` 找目标卡并高亮（`.drop-target` 虚线框）；
- 松手：`swapItems(fromKey, toKey)` —— 只换 `days[i].items`，不换 `label/theme/duration`；
  写 `localStorage` 并 toast「已交换 周一 ↔ 周五」；
- 取消：`pointercancel` / `Esc` 复原，无副作用；
- 键盘兜底：聚焦卡后 `Alt+←/→` 交换相邻两天（无鼠标也能改）。

数据层：

```js
function swapItems(aKey, bKey){
  var a = dayBy(aKey), b = dayBy(bKey);
  var t = a.items; a.items = b.items; b.items = t;
  markDirty(); saveLocal(); renderWeek();
}
```

---

## 5. 预览与出图（修「PNG 比预览大」）

根因：`.preview-inner` 是 flex 居中 ⇒ 卡片收缩到内容宽（实测 379）；导出却写死 720 CSS × 2 = 1440。

改动：

1. `.card{width:720px;max-width:100%;}`（预览与 `?card=` 模式一致）；窄屏不足时
   `transform:scale(w/720)`（只在预览层做视觉缩放，不影响逻辑宽）。
2. 动作行单行截断：
   ```css
   .card table{table-layout:fixed;}
   .card td.nm{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
   ```
3. 导出按预览逻辑宽 × 1：删掉 `cardToBlob()` 里「stage 720 重排 + scale=2」，
   改为 `scale=1`、`w = node.offsetWidth`；`?card=day` 页同样按 720。
4. 下载/复制共用同一个 blob；`imgNote` 显示实际像素宽（如「已复制 · 720×N」），
   让「预览尺寸 == 文件尺寸」肉眼可验。

> 若后续要高清：加「2x」勾选，勾选后 1440，仍标在按钮上（默认不勾）。

---

## 6. 验收清单（实施后逐条跑）

| # | 判据 | 期望 |
|---|---|---|
| 1 | 1440 视口 `.day-card` 数 / 行宽 | 7 张一排；行宽 = 1296（90vw） |
| 2 | 1024 视口 | 每卡 ~118px，仍七列 |
| 3 | 375 视口 | `#weekRow` 可横滚，卡 168px，页面无横向溢出（`scrollWidth == innerWidth`） |
| 4 | 卡脚文案 | 「5 个动作 共 17 组」与数据一致（周一 5/17） |
| 5 | 拖拽 周一 ↔ 周五 | 刷新后仍是交换后的内容；「今天」标签仍在周四 |
| 6 | `✎` / `▣` | 分别打开该日编辑器 / 该日预览卡（不是今天） |
| 7 | 预览宽 vs PNG 宽 | `getBoundingClientRect().width` 与下载 PNG 像素宽**相等**（同时打印两个数） |
| 8 | 预览长名字 | 单行 + `…`；导出的 PNG 里同样有 `…` |
| 9 | print media | 导航/工具条隐藏，七列压 3 列 |
| 10 | 回归 | `python3 -m pytest tests/ -q -n 4` ⇒ 473 passed |

---

## 7. 影响面

- 改：`demos/slimdown/_src/{plan.tpl,plan.js,base.css,archive.tpl}`；
  产物 `demos/slimdown/{plan,archive}.html`；必要时 `scripts/build-slimdown.py` 占位符。
- 不动：动作库页、两个数据 JSON、分享编码格式（老链接继续可用）。
- 风险：
  - 90vw 行在大屏（≥1920）会明显宽于标题条 —— 已选 full-bleed，接受；
  - 七列下卡内名字截断较重（171px 卡宽 ≈ 8~10 个汉字）—— 这是需求本身的取舍，不再回退；
  - 已存本机的方案（`slimdown:v1`）schema 不变，交换只是重排 `items`，兼容。

## 8. 明确不做

- 不引第三方拖拽库（零依赖铁律）；
- 不加「2x 高清」开关（本批）；不加训练打卡 / 完成度；
- 不改 `plan.html#p=` 分享编码；不动 demos 索引的 3 条登记。
