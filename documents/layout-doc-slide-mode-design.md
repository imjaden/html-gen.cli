# layout-doc Slide Mode 设计方案

## 版本

v2.1 (2026-07-13) — 安全审查修订

## 概述

为 `layout-doc.html`（B 型文档模板）新增 slide 幻灯片模式。在现有 doc 平铺阅读模式基础上，增加按 h2/h3 标题分页的滑动切换体验，适配课件演示、会议记录回顾、长文档分段阅读等场景。

## 模式切换

侧边栏顶部增加模式切换按钮，一键在 doc/slide 间切换，动画过渡 0.3s。

- 切换至 slide 模式时：保存 doc 模式当前滚动位置到内存
- 切换回 doc 模式时：恢复至缓存的滚动位置（`scrollTo`）
- 页面初次加载时默认 doc 模式

```
┌──────┬──────────────┐        ┌──────┬──────────────┐
│ TOC  │  全部内容     │  →→→   │ TOC  │   Page N     │
│      │  连续滚动     │        │      │   单页内容    │
│      │              │        │  ←   │   →          │
└──────┴──────────────┘        └──────┴──────────────┘
    doc 模式（现有）               slide 模式（新增）
```

## 分页策略

### h2 分页（默认）

每个 `##` 二级标题作为一页。h1 标题作为封面页。

**封面页内容**: h1 标题 + 副标题（`<!--SUBTITLE-->`）+ 元信息（路径/日期/字数） + h2 页数统计（如 "共 12 节"）。

```
Page 1 (封面)      Page 2               Page 3              ...
┌──────────┐  ┌──────────────┐  ┌──────────────┐
│  # h1    │  │ ## Section A │  │ ## Section B │
│  副标题  │  │  内容...     │  │  内容...     │
│  元信息  │  │              │  │              │
│ 共 12 节 │  │              │  │              │
└──────────┘  └──────────────┘  └──────────────┘
```

### h3 分列模式

h2 作为页容器，h3 在该页内并列为卡片。适用于对比分析、多方案展示。

```
       ← Page N →
┌──────────────────────────────────┐
│         ## h2 标题                │
├──────────┬──────────┬────────────┤
│ ### h3-A │ ### h3-B │ ### h3-C   │
│ 内容A    │ 内容B    │ 内容C      │
│          │          │            │
└──────────┴──────────┴────────────┘
```

- 2-3 列均分宽度
- 4+ 列切换为 2×N 网格
- 列内内容超长时 `overflow-y: auto`
- 点击列或 Tab 键切换焦点列，焦点列亮边框

> ⚠️ **待确认**: 单个 h2 下只有 1 个 h3 时，分列模式降级为平铺还是保持单列？

## 边界情况处理

| 情况 | 行为 |
|:-----|:-----|
| 文档无 h2 | slide 模式下仅显示封面页，底部提示 "本文档无二级标题，无法分页" |
| 空文档（无内容） | 封面页显示 h1 + 元信息，"暂无内容" 占位 |
| 单页内容超长（超过 viewport） | slide-page 容器 `overflow-y: auto`，允许页内滚动 |
| 代码块/表格超宽 | 水平 `overflow-x: auto`，不截断内容 |

边界情况由 `html-gen.py` 生成 HTML 时通过注入 `data-` 属性或内联提示处理，不影响 slide 模式的正常功能。

## 性能策略

| 文档规模 | 策略 |
|:---------|:-----|
| ≤50 h2 节 | 全量 DOM 渲染，无性能问题 |
| >50 h2 节 | 生成 HTML 时在封面页注入黄色提示条："⚠️ 本文档共 N 节，slide 模式下可能加载较慢" |
| >200 h2 节 | 同上 + 建议拆分为多个文档 |

当前方案为全量渲染（v1），后续版本可考虑虚拟分页（只渲染当前页 ±2 页的 DOM）。提示条不影响 slide 模式正常功能，仅为用户知情。

## 安全约束

**所有 DOM 内容注入必须遵守以下规则，违反即阻断合入：**

### 1. 页面内容渲染 (`renderPage`)

```
✅ 允许: cloneNode + textContent / appendChild 操作现有 DOM 节点
❌ 禁止: innerHTML / insertAdjacentHTML 直接注入从 DOM 提取的内容
```

实现方式：从 doc 模式的 DOM 中提取对应 h2 区块的 DOM 子树，使用 `cloneNode(true)` 深拷贝后 `appendChild` 到 slide 容器。不经过字符串序列化。

### 2. 演讲者备注

```
提取管道: HTML comment → textContent → 转义 → textContent 注入
```

```javascript
// 从 DOM 中定位 <!-- notes ... --> 注释节点
var noteText = commentNode.textContent;
// 新窗口中仅使用 textContent 设置，禁止 innerHTML
noteWindow.document.getElementById('notes').textContent = noteText;
```

备注内容在 Markdown→HTML 环节已由 `_md_escape()` 转义特殊字符（`<` `>` `&`），新窗口渲染时使用 `textContent` 设置，双重保护。

### 3. localStorage 恢复

```javascript
restoreProgress: function() {
  try {
    var n = parseInt(localStorage.getItem('layoutdoc_slide_page'), 10);
    if (isNaN(n) || n < 0 || n >= this.pages.length) n = 0;  // 边界校验
    this.goTo(n);
  } catch(e) { this.goTo(0); }  // localStorage 不可用时回退
}
```

### 4. 底部导航标题

```javascript
// ✅ 使用 textContent — 浏览器自动解码 HTML 实体
document.getElementById('slidePageTitle').textContent = currentPageTitle;

// ❌ 禁止 innerHTML — 若标题含 &lt; 会字面显示而非渲染为 <
```

### 5. 全屏模式 URL

`F` 键进入全屏使用 `Element.requestFullscreen()` 标准 API，不涉及 `window.open()` 或 URL 跳转。无需处理 URL 参数。

## 导航交互

| 操作 | 行为 | 适用 |
|:---|:---|:---|
| `←` / `→` | 上/下一页 | 键盘 |
| `Space` / `Shift+Space` | 下/上一页 | 键盘 |
| `Home` / `End` | 首页/末页 | 键盘 |
| 左右滑动 | 上/下一页 | 触控板、移动端 |
| TOC 点击 | 跳转到对应 h2/h3 页 | 侧边栏 |
| 底部圆点点击 | 跳转到对应页 | 导航条 |

## 进度与定位

### 底部导航条

```
 ● ● ● ● ○ ○ ○ ○
 Page 3 / 54 — General Requirements for Journal Paper Submission
```

- 圆点表示每页：已读/当前/未读（三色区分）
- 当前页标题显示在圆点下方
- 鼠标悬停圆点时显示该页标题 tooltip

### 页码显示

- 当前页内容区右上角浮动：`3 / 54`
- 3 秒无操作后渐隐，鼠标移动时重新显示

### 阅读进度保存

- `localStorage` key: `layoutdoc_slide_page`
- 每次翻页自动保存
- 下次打开时恢复到上次阅读页

### 侧边栏同步

- TOC 中当前 h2 项高亮
- 当前页对应项始终在可视区内（scrollIntoView）

## 全屏演示模式

`F` 键进入全屏演示，`Esc` 或 `F` 退出。

```
┌─────────────────────────────────────┐
│          Page 12 / 54               │  ← 页码栏（3s 无操作渐隐）
│                                     │
│      ## General Requirements        │
│                                     │
│   - 每种期刊都有各自的投稿指南...     │
│   - 大多数期刊在收到稿件后会...       │
│                                     │
│         ● ● ● ● ○ ○ ○ ○            │  ← 圆点导航（始终可见）
│                                     │
│  ⏱ 12:34          ← → 翻页          │  ← 信息栏
└─────────────────────────────────────┘
```

特性：
- 隐藏侧边栏（TOC），内容区全屏
- 页码栏 3s 渐隐，鼠标移动重现
- 底部圆点导航始终可见
- 底部信息栏显示时间和操作提示

## 演讲者备注

Markdown 中使用 HTML 注释标记备注内容：

```markdown
## Page 12 — General Requirements

<!-- notes
- 提醒：此处可补充数据唯一性的实际案例
- 下一张图：展示 iThenticate 检测界面截图
-->

- 每种期刊都有各自的投稿指南...
```

- slide 模式下备注不显示在主页
- `N` 键打开演讲者视图新窗口：左半屏当前页 + 右半屏备注 + 底部下一页预览

## 附加创意（可选扩展）

| 功能 | 描述 | 快捷键 |
|:---|:---|:---|
| 演讲计时器 | 全屏底部显示已用时间 | 自动 |
| 激光笔模式 | 鼠标变为高亮圆点 | `L` |
| 画布缩放 | 缩放内容区适配分辨率 | `Cmd + / -` |
| 暗/亮切换 | slide 模式下切换背景色 | `D` |
| 导出 PDF | 按分页生成 PDF 布局 | 按钮 |
| 自动播放 | 设定每页秒数自动翻页 | `A` |
| 逐条淡入 | 列表项 step-by-step reveal | 空格触发 |

## 样式设计

### Slide 容器

```css
.slide-container {
  flex: 1; overflow: hidden;
  display: flex; flex-direction: column;
  position: relative;
}
.slide-page {
  flex: 1; overflow-y: auto;
  padding: 32px 40px;
  animation: slideFadeIn 0.25s ease;
}
@keyframes slideFadeIn {
  from { opacity: 0; transform: translateX(8px); }
  to   { opacity: 1; transform: translateX(0); }
}
```

### H3 分列

```css
.slide-columns { display: flex; gap: 20px; }
.slide-columns.cols-2 > div { flex: 1; min-width: 0; }
.slide-columns.cols-3 > div { flex: 1; min-width: 0; }
.slide-column { max-height: 70vh; overflow-y: auto; }
.slide-column:focus-within {
  outline: 1px solid var(--cobalt-500);
  border-radius: var(--radius-md);
}
```

### 底部导航

```css
.slide-nav { display: flex; gap: 6px; justify-content: center; padding: 12px; }
.slide-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #3a3a5e; cursor: pointer; transition: all 0.2s;
}
.slide-dot.active { background: var(--cobalt-400); width: 24px; border-radius: 4px; }
.slide-dot.visited { background: #555; }
```

## HTML 结构增量

```html
<!-- Slide 模式切换按钮（侧边栏头部） -->
<div class="mode-toggle">
  <button class="mode-btn active" data-mode="doc">📄 文档</button>
  <button class="mode-btn" data-mode="slide">🎞️ 幻灯片</button>
</div>

<!-- Slide 底部导航条 -->
<div class="slide-nav" id="slideNav" style="display:none">
  <div class="slide-dots" id="slideDots"></div>
  <div class="slide-page-title" id="slidePageTitle"></div>
</div>
```

## JS 模块概要

```javascript
var slideMode = {
  active: false,
  currentPage: 0,
  pages: [],        // [{h2, h3s: [{title, content}]}]
  isFullscreen: false,
  _docScrollPos: 0,  // doc 模式滚动位置缓存

  init: function() { /* 解析 DOM，按 h2/h3 建 pages 数组 */ },
  enter: function() { /* 保存 doc 滚动位置 → 切换 slide 布局 */ },
  exit: function() { /* 恢复 doc 布局 → scrollTo 缓存位置 */ },
  goTo: function(n) { /* 边界校验后渲染第 n 页 */ },
  next: function() { /* 下一页，末尾循环到首页 */ },
  prev: function() { /* 上一页 */ },

  // 安全渲染：cloneNode 深拷贝 DOM 子树，禁止 innerHTML
  renderPage: function(n) { /* cloneNode + appendChild，见安全约束 §1 */ },
  toggleFullscreen: function() { /* requestFullscreen API */ },
  openNotes: function() { /* 新窗口，textContent 注入，见安全约束 §2 */ },

  // localStorage（边界校验，见安全约束 §3）
  saveProgress: function() { try { localStorage.setItem('layoutdoc_slide_page', this.currentPage); } catch(e) {} },
  restoreProgress: function() { /* parseInt + 边界校验，NaN/越界回退 0 */ }
};
```

## 实现优先级

### v1 — 最小可行
1. doc/slide 模式切换（侧边栏按钮）
2. h2 分页
3. 键盘 ← → Space Home End 翻页
4. 底部圆点导航 + 页码显示
5. localStorage 进度保存

### v2 — 增强体验
6. h3 分列模式
7. 全屏演示 `F` 键
8. 触控板/移动端滑动
9. 页面切换动画

### v3 — 演示增强
10. 演讲者备注 `N` 键
11. 演讲计时器
12. PDF 导出
13. 自动播放
