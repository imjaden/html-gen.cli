---
name: html-gen-slide
description: Use when generating slide-style presentation HTML from Markdown with
  the html-gen slide command. Covers layout-slide.html template, h2 pagination, cover
  page, dot navigation, keyboard shortcuts, fullscreen mode, and performance warnings.
version: 1.0.0
author: dev
license: MIT
metadata:
  hermes:
    tags:
    - html-gen
    - slide
    - presentation
    - markdown-to-html
    - template
    related_skills:
    - html-gen-doc
    - html-gen-table
quality:
  coverage: 0.8
  depth: 0.75
  maintainability: 0.8
  cross_profile: 0.65
---

# html-gen · 幻灯片模板 (slide)

## 概述

`layout-slide.html` 是 html-gen 的独立幻灯片模板 — 将 Markdown 文件按 h2 标题分页，渲染为可逐页演示的 HTML。支持封面页、圆点导航、键盘翻页、全屏模式、localStorage 进度保存和性能警告。

> 文档平铺阅读使用 `html-gen doc` 命令（`layout-doc.html`）。详见 `html-gen-doc` skill。

## 何时使用

- 将 Markdown 课件/讲稿渲染为逐页幻灯片
- 需要键盘翻页演示的长文档
- 会议记录/课程笔记的分段回顾
- 演讲时配合全屏模式 `F` 键

## CLI 用法

```shell
html-gen slide -i lecture.md -o lecture.slide.html --title "课件标题" --subtitle "副标题"
```

## 分页规则

- **封面页**（Page 1）：h1 标题 + 副标题 + 元信息 + 节数统计
- **内容页**（Page 2+）：每个 `##` h2 为一页，包含标题及其后续内容直到下一个 h2

## Phase 3/4 — TOC 搜索 + 侧边栏宽度拖拽 (v1.1)

### TOC 搜索

侧边栏底部 🔍 按钮 → 切换 TOC 顶部搜索输入框 `.slide-toc-search`：
- 150ms 防抖，输入 ≥2 字符触发过滤
- 不匹配条目 `.filtered-out` (display:none)
- Enter → 跳转到第一个匹配项 + 关闭搜索
- Esc → 关闭搜索，清除过滤
- 点击搜索框外部 → 自动关闭
- 激活时 🔍 按钮变 `var(--cobalt-400)` 高亮

### 侧边栏宽度拖拽

侧边栏右边缘拖拽调整宽度：
- `.slide-sidebar-resize`: 8px handle，hover/active 时 cobalt 高亮
- 拖拽范围 200–400px
- 实时更新 `sb.style.width` 和 `sb.style.minWidth`
- localStorage 持久化 key: `html-gen:slide:sidebar-width`

### 侧边栏底部工具栏

- 🔍 — TOC 搜索开关
- ◀◀ / ▶▶ — 折叠/展开侧边栏 (48px collapsed)
- `[` 快捷键仅在非 input/textarea 聚焦时触发

## 导航操作

| 操作 | 行为 |
|:---|:---|
| `←` / `→` | 上/下一页 |
| `↑` / `↓` | 上/下一页 |
| `Space` | 下一页 |
| `Shift+Space` | 上一页 |
| `Home` | 首页（封面） |
| `End` | 末页 |
| `F` | 全屏演示切换 |
| 底部圆点点击 | 跳转对应页 |
| 侧边栏 TOC 点击 | 跳转对应 h2 页 |

## 进度系统

- 底部圆点导航：未访问(暗灰) / 已访问(灰) / 当前(蓝)
- 页码浮层 `N / M` 右上角显示，3s 无操作渐隐
- localStorage 进度保存（key: `layoutslide_page`），下次打开自动恢复

## 性能提示

当 Markdown 含 >50 个 h2 时，封面页顶部显示黄色警告条：

```
⚠️ 本文档共 N 节，幻灯片模式下可能加载较慢
```

## 侧边栏 H3 开关（v2.2+）

侧边栏头部包含 H3 子标题开关，默认隐藏 `.toc-h3` 项：

- 开关位于 sub 行右侧，显示 `H3`（关闭）/ `H3 ✓`（打开）
- `.toc-h3` 默认 `display: none`
- 点击开关切换所有 `.toc-h3` 的显示状态

### CSS 优先级（重要）

`.slide-toc a { display: block; }` 优先级高于 `.toc-h3 { display: none; }`。

**正确写法**:
```css
.toc-h3 { display: none; }
.toc-h3.show { display: block; }
/* 必须用更高优先级覆盖 .slide-toc a */
.slide-toc .toc-h3 { display: none; }
.slide-toc .toc-h3.show { display: block; }
```

## 侧边栏头部显示（v2.2+）

- **logo**: 文档标题超过 30 字自动截断 + `…`
- **sub**: 显示副标题（如 `Slide 演示`） + 节数统计（`共 N 节`），如无副标题则仅显示节数

```javascript
// logo 截断
var txt = logoEl.textContent.replace(/^🎞️\s*/, '');
if (txt.length > 30) txt = txt.substring(0, 30) + '…';
logoEl.textContent = '🎞️ ' + txt;

// sub 节数
var base = subEl.textContent.trim();
subEl.textContent = (base ? base + ' · ' : '') + '共 ' + (pages.length - 1) + ' 节';
```

## 安全实现

### DOM 渲染

- 页面内容使用 `cloneNode(true)` 深拷贝 DOM 子树，不经过字符串序列化
- 禁止 `innerHTML` 直接注入用户内容
- 侧边栏标题使用 `textContent` 设置

### Null Guard（关键规范）

**所有 `getElementById()` 调用必须添加 null guard。** 即使 HTML 结构正确，生成的模板在不同浏览器/环境可能出现元素不存在的情况。

```javascript
// ✅ 正确 — null guard
var el = document.getElementById('slideDots');
if (!el) return;
el.innerHTML = '';

// ❌ 错误 — 直接访问 null 属性导致 TypeError
document.getElementById('slideDots').innerHTML = '';
```

受影响的方法：`buildDots`、`_updateDots`、`_showPageNum`、`enter`、`exit`、`_syncToc`、`renderPage`、TOC click handler。

详见 `references/slide-mode-null-guards.md`。

### localStorage

```javascript
// ✅ 正确 — parseInt + 边界校验
try {
  var n = parseInt(localStorage.getItem('layoutslide_page'), 10);
  if (isNaN(n) || n < 0 || n >= this.pages.length) n = 0;
  this.currentPage = n;
} catch(e) { this.currentPage = 0; }
```

### XSS 防护

- 所有 `<!--KEY-->` 注入值自动转义 `</` → `<\/`（防止 script 标签闭合）
- Markdown 纯文本 `<` `>` `&` 自动转义（`_md_escape` 在 `inline_format` 前调用）

## 与 doc 模板的区别

| | `layout-doc.html` | `layout-slide.html` |
|:---|:---|:---|
| 命令 | `html-gen doc` | `html-gen slide` |
| 渲染模式 | 平铺连续滚动 | h2 逐页分页 |
| TOC 点击 | 滚动到锚点 | 跳转到对应页 |
| 进度条 | 顶部 2px 线 | 底部圆点 |
| 页码 | 无 | 右上角 `N / M` |
| 全屏 | 无 | `F` 键 |
| 代码复制 | ✅ | ❌ |
| 代码行号 | ✅ | ❌ |
| 图片灯箱 | ✅ | ❌ |
| 输出后缀 | `.html` | `.slide.html` |

## 常见问题

### 键盘翻页不响应
确保未聚焦在 input/textarea 元素中。模板会跳过表单元素内的键盘事件。

### 页面内容为空
检查 Markdown 的 h2 标题是否被正确解析。`## Title` 必须有空格。

### localStorage 恢复失败
所有 localStorage 操作包裹 `try/catch`，失败时回退到封面页（page 0）。

### 切换全屏后布局错乱
按 `F` 或 `Esc` 退出全屏。全屏使用 `Element.requestFullscreen()` 标准 API。

## 验证清单

- [ ] 运行 `html-gen slide -i input.md -o output.html` 正常生成
- [ ] 封面页显示 h1 标题、副标题、元信息、节数
- [ ] 所有 h2 正确分页，内容无丢失
- [ ] 键盘 ← → Space Home End 翻页正常
- [ ] 底部圆点导航正常，当前/已访问状态正确
- [ ] `F` 全屏进入/退出正常
- [ ] >50 h2 时性能警告显示
- [ ] 浏览器 Console 无 TypeError（所有 DOM null guard 生效）
