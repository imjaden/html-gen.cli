# layout-doc Slide Mode 设计方案

## 版本

v2.0 (2026-07-13)

## 概述

为 `layout-doc.html`（B 型文档模板）新增 slide 幻灯片模式。在现有 doc 平铺阅读模式基础上，增加按 h2/h3 标题分页的滑动切换体验，适配课件演示、会议记录回顾、长文档分段阅读等场景。

## 模式切换

侧边栏顶部增加模式切换按钮，一键在 doc/slide 间切换，动画过渡 0.3s。

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

```
Page 1 (封面)      Page 2               Page 3              ...
┌──────────┐  ┌──────────────┐  ┌──────────────┐
│  # h1    │  │ ## Section A │  │ ## Section B │
│  副标题  │  │  内容...     │  │  内容...     │
│  元信息  │  │              │  │              │
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

  init: function() { /* 解析 DOM，按 h2/h3 建 pages 数组 */ },
  enter: function() { /* 切换为 slide 布局 */ },
  exit: function() { /* 恢复 doc 布局 */ },
  goTo: function(n) { /* 渲染第 n 页 */ },
  next: function() { /* 下一页，末尾循环到首页 */ },
  prev: function() { /* 上一页 */ },
  renderPage: function(n) { /* 生成页面 HTML */ },
  toggleFullscreen: function() { /* 全屏切换 */ },

  // localStorage
  saveProgress: function() { localStorage.setItem('layoutdoc_slide_page', this.currentPage); },
  restoreProgress: function() { /* 读取并跳转 */ }
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
