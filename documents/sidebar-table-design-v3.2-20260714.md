# 统一侧边栏 + 增强表格设计方案

## 版本

v3.3 (2026-07-14) — N1/N2 修正

## 决策记录

| # | 决策项 | 确认结果 |
|:---|:---|:---|
| 1 | 折叠态宽度 | 48px（仅图标） |
| 2 | 折叠按钮位置 | 侧边栏底部 |
| 3 | knowledge 适配 | 改为侧边栏+内容区，内容区顶菜单栏与左侧顶部标题栏对齐 |
| 4 | doc 标题复制 | 同 slide：点击 `.sidebar-title` 拷贝路径 |
| 5 | 默认点击模式 | 新标签页（现有） |
| 6 | 分栏比例 | 表格 40% + 预览 60% |
| 7 | 密度默认值 | 默认（34px） |
| 8 | 设置持久化 | localStorage 记忆 |
| 9 | 实施范围 | Phase 1 + Phase 2 全部 |
| 10 | 实施顺序 | 侧边栏优先 |

---

## 一、统一侧边栏 (slide / doc / knowledge)

### 1.1 当前状态

| 模板 | 侧边栏结构 |
|:---|:---|
| slide | 标题 + 副标题/页码 + H3 开关 + TOC |
| doc | 标题 + 副标题 + TOC |
| knowledge | 顶部 Tab 栏 + 左侧章节列表（非传统侧边栏） |

三者结构各异，无统一交互规范。

### 1.2 统一布局

```
┌─────────────────────┐
│ 🎞️ 文档标题...(30字) │  ← .sidebar-title (点击复制路径)
│ Slide 演示 · 3 / 38  │  ← .sidebar-sub (i18n 页码)
├─────────────────────┤
│ [🔍 搜索 TOC]        │  ← 可选搜索框 (点击 🔍 展开)
├─────────────────────┤
│ ▸ Section A         │  ← TOC (h2)
│   ▸ Sub A.1         │  ← TOC (h3, 默认隐藏)
│ ▸ Section B         │
│ ▸ Section C         │
├─────────────────────┤
│ 共 38 页    [🔍][H3][◀◀] │  ← 底部工具栏: 搜索/H3/折叠
└─────────────────────┘

收起态:
┌────┐
│ 🎞️ │  ← 图标
│    │
│    │
├────┤
│ ▶▶ │  ← 展开按钮 (底部)
└────┘
```

侧边栏底部工具栏统一放置：🔍 TOC 搜索、H3 开关、折叠按钮。

### 1.3 统一功能清单

| # | 功能 | 说明 | slide | doc | knowledge |
|:---|:---|:---|:---:|:---:|:---:|
| 1 | **折叠/展开** | ◀◀ 按钮切换，收起时仅显示图标列 | ✅ | ✅ | ✅ |
| 2 | **标题点击复制路径** | 统一 `.sidebar-title` 交互，使用 `textContent` | ✅ | ➕ | ➕ |
| 3 | **页码/进度** | `.sidebar-sub` 显示当前位置 | ✅ | ➕ | ➕ |
| 4 | **H3 子项开关** | 显示/隐藏 TOC 中的 h3 条目 | ✅ | ✅ | N/A |
| 5 | **TOC 搜索** | 🔍 按钮弹出搜索框，过滤 TOC 条目，150ms debounce，≥2 字符触发 | ✅ | ✅ | N/A |
| 6 | **当前章节高亮** | 滚动/翻页时 TOC 自动高亮当前项 | ✅ | ✅ | ✅ |
| 7 | **localStorage 状态记忆** | 折叠态、H3 开关、语言、主题 | ✅ | ➕ | ➕ |
| 8 | **侧边栏宽度拖拽** | 右边缘拖拽调整宽度 (200-400px) | ⬜ | ⬜ | ⬜ |
| 9 | **快捷键切换** | `[` 键折叠/展开侧边栏（输入框中不触发） | ⬜ | ⬜ | ⬜ |
| 10 | **底部统计** | 页数/字数/阅读进度 | slide | doc | ❌ |

> ✅ 已实现  ➕ 需新增  ⬜ 新功能  ❌ 不适用

### 1.4 knowledge 模板适配

知识库由顶部 Tab 栏改为侧边栏+内容区，内容区顶菜单栏与侧边栏标题行对齐：

```
┌─ sidebar ──┬─ tabs (aligned with title) ────┐
│ 📚 知识库   │ [Agent] [HTML] [hs CLI]        │  ← 标题行对齐
│ 共 15 条目  │                                 │
├────────────┼─────────────────────────────────┤
│ ▸ Codex    │  ┌──────────────────────────┐  │
│ ▸ Claude   │  │  内容区 (iframe/inline)   │  │
│ ▸ Hermes   │  │                          │  │
│ ▸ OpenCode │  └──────────────────────────┘  │
├────────────┤                                 │
│ [◀◀]       │                                 │  ← 折叠按钮在侧边栏底部
└────────────┴─────────────────────────────────┘
```

改动要点：
- 顶部 Tab 栏从全宽 → 仅内容区宽度，与侧边栏标题行水平对齐
- 左侧新增侧边栏（标题 + 条目数 + 章节列表）
- 侧边栏底部放折叠按钮

### 1.5 折叠态设计

```css
.sidebar { width: 260px; transition: width 0.25s; }
.sidebar.collapsed { width: 48px; }
.sidebar.collapsed .sidebar-title,
.sidebar.collapsed .sidebar-sub,
.sidebar.collapsed .toc { display: none; }
.sidebar.collapsed .sidebar-icon { display: flex; }
```

折叠按钮在侧边栏底部：
```
展开态                  收起态
┌─────────────┐        ┌────┐
│ 标题         │        │ 🎞️ │
│ 页码         │        │    │
│ TOC          │        │    │
│              │        │    │
├─────────────┤        ├────┤
│ [◀◀]        │        │ [▶▶]│  ← 底部
└─────────────┘        └────┘
```

收起态仅显示顶部图标 + 底部展开按钮。

### 1.6 TOC 搜索

点击 🔍 → 侧边栏顶部出现搜索输入框 → 150ms debounce + ≥2 字符触发过滤 → 选中跳转

```
┌─────────────────────┐
│ [🔍 search...     ] │  ← 搜索框（自动聚焦）
├─────────────────────┤
│ ▸ Section A         │  ← 匹配项高亮
│ ▸ Section C         │  ← 不匹配项隐藏
└─────────────────────┘
```

### 1.7 CSS 变量统一

```css
:root {
  --sidebar-width: 260px;
  --sidebar-collapsed: 48px;
  --sidebar-bg: var(--surface-900);
  --sidebar-border: #2a2a3e;
}
```

### 1.8 localStorage 命名空间

所有键使用 `html-gen:` 前缀，防冲突：

| 键 | 类型 | 默认值 |
|:---|:---|:---|
| `html-gen:sidebar:collapsed` | boolean | false |
| `html-gen:sidebar:h3-visible` | boolean | false |
| `html-gen:table:density` | string | "default" |
| `html-gen:table:click-mode` | string | "tab" |
| `html-gen:table:view-presets` | JSON array | [] (max 10) |

恢复逻辑统一模式：

```javascript
function restore(key, fallback, validate) {
  try {
    var v = JSON.parse(localStorage.getItem(key));
    return validate(v) ? v : fallback;
  } catch(e) { return fallback; }
}
// 示例
var collapsed = restore('html-gen:sidebar:collapsed', false, function(v) { return typeof v === 'boolean'; });
```

### 1.9 标题点击复制

统一使用 `textContent` 获取路径（不受 HTML 注入影响）：

```javascript
var m = el.textContent.match(/路径:\s*(.+)/);
if (m && /^(https?:|\/|~\/)/.test(m[1])) {
  var path = m[1].trim();
  try {
    navigator.clipboard.writeText(path).catch(function() {
      // clipboard API unavailable (non-HTTPS, permission denied) — silent fallback
    });
  } catch(e) { /* clipboard API not supported */ }
}
```

### 1.10 快捷键焦点检测

```javascript
document.addEventListener('keydown', function(e) {
  if (e.key === '[' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
    toggleSidebar();
  }
});
```

---

## 二、增强表格 (table)

### 2.1 设置面板增强

当前 ⚙️ 仅支持列可见性勾选。扩展为：

```
┌─ 表格设置 ──────────────────────┐
│ 显示列                           │
│ ☑ 名称  ☑ Stars  ☑ 语言  ☐ URL │
│ ─────────────────────────────── │
│ 密度                             │
│ ○ 紧凑  ● 默认  ○ 舒适          │
│ ─────────────────────────────── │
│ 点击行为 (操作列)                 │
│ ○ 新标签页打开                   │
│ ○ 弹出面板内嵌                   │
│ ○ 分栏模式 (表格+预览)           │
│ ─────────────────────────────── │
│ 排序                             │
│ 名称 ▲  ·  Stars ▼              │
│ [清除排序]                       │
│ ─────────────────────────────── │
│ [保存为默认]  [重置]             │
└────────────────────────────────┘
```

### 2.2 三种点击打开模式

#### 模式 1: 新标签页打开（默认）

```javascript
window.open(url, '_blank', 'noopener,noreferrer');
```

#### 模式 2: 弹出面板 (Modal Panel)

```
┌──────────────────────────────────┐
│  表格 (全宽)                      │
│  ┌────┬───────┬──────┬──────┐   │
│  │ #  │ Name  │ Type │ Size │   │
│  ├────┼───────┼──────┼──────┤   │
│  │ 1  │ doc.A │ PDF  │ 11K  │   │
│  │ 2  │ doc.B │ MD ▶ │ 9.5K │ ← │ 点击行
│  └────┴───────┴──────┴──────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │  ×     doc.B 详情         │   │  ← 弹出面板
│  │  ─────────────────────── │   │
│  │  类型: Markdown           │   │
│  │  大小: 9.5 KB             │   │
│  │  路径: ~/docs/doc.B.md    │   │
│  │  [📋 复制路径] [🔗 打开]  │   │
│  └──────────────────────────┘   │
└──────────────────────────────────┘
```

- 页面内弹出，居中，半透明遮罩
- 显示行的字段，尊重设置面板中的**列可见性**（隐藏列不出现在弹出面板中）
- Esc / 点击遮罩关闭
- 数据渲染规则见 §2.5

#### 模式 3: 分栏模式 (Split View)

```
┌──────────────────┬──────────────────────────┐
│ 表格 (preview列)  │  预览面板                  │
│ ┌────┬────┬────┐ │                          │
│ │ #  │Name│Typ │ │  📄 doc.B                │
│ ├────┼────┼────┤ │  ─────────────────────── │
│ │ 1  │A   │PDF │ │  类型: Markdown           │
│ │ 2▶ │B   │MD  │ │  大小: 9.5 KB             │
│ │ 3  │C   │PDF │ │  路径: ~/docs/doc.B.md    │
│ │ 4  │D   │XLS │ │                          │
│ └────┴────┴────┘ │  [📋] [🔗] [⬇️]         │
└──────────────────┴──────────────────────────┘
```

- 表格仅显示 `col.preview: true` 的列（无自动选择逻辑，完全由 col.preview 控制）
- 表格 40% + 预览 60%
- 拖拽分栏线调整比例：表格 min 25% / max 75%
- 点击行 → 右侧加载内容
- 数据渲染规则见 §2.5

### 2.3 额外增强功能

| # | 功能 | 说明 | 优先级 |
|:---|:---|:---|:---:|
| 11 | **密度切换** | 紧凑(28px)/默认(34px)/舒适(42px) | P1 |
| 12 | **行详情展开** | 点击行展开内嵌详情（手风琴），显示全部字段 | P2 |
| 13 | **快速过滤** | 点击单元格值 → 添加为该列的过滤条件 | P2 |
| 14 | **列冻结** | 左侧 1-2 列冻结（`position: sticky; left: 0`） | P2 |
| 15 | **多列排序** | Shift+点击第二列表头 → 二级排序 | P2 |
| 16 | **键盘导航** | ↑↓ 移动行高亮，Enter 打开详情 | P3 |
| 17 | **批量操作栏** | 选中行后顶部出现批量操作（删除/导出/标记） | P3 |
| 18 | **视图预设** | 保存/加载设置（最多 10 个预设，每个 ≤ 2KB） | P3 |
| 19 | **全屏表格** | 按钮或 F 键全屏表格 | P3 |
| 20 | **列拖拽排序** | 拖拽表头重新排列列顺序 | P3 |

### 2.4 分栏模式的列配置

```json
{
  "columns": [
    {"key": "name", "label": "名称", "preview": true},
    {"key": "type", "label": "类型", "preview": true},
    {"key": "size", "label": "大小", "preview": false},
    {"key": "url", "label": "链接", "preview": false},
    {"key": "desc", "label": "描述", "preview": false}
  ]
}
```

`col.preview: true` — 分栏模式下保留此列。`preview: false` 或不设置的列在分栏模式下隐藏（信息移至详情面板）。**不设自动列数选择逻辑**，完全由 `col.preview` 字段控制。

### 2.5 弹出面板 / 分栏面板的数据渲染（安全约束）

| 数据源 | 渲染方式 | 安全说明 |
|:---|:---|:---|
| `row.url` 存在 | `<iframe src="..." sandbox="allow-same-origin" loading="lazy" referrerpolicy="no-referrer">` | 禁止脚本执行，仅允许同源访问 |
| `row.desc` 存在 | `container.textContent = row.desc` | 纯文本渲染，禁止 innerHTML |
| 无 url/desc | 展示键值对列表（仅用户在设置面板中可见的列） | textContent 逐字段渲染 |

#### URL 白名单

所有 `row.url` 在进入 iframe 或 `window.open` 前校验：

```javascript
function isSafeUrl(url) {
  return /^(https?:|\/|~\/)/.test(url);
}
```

非白名单 URL → 静默忽略，展示降级键值对列表。

#### 安全强化规则

- `window.open(url, '_blank', 'noopener,noreferrer')` — 防止新页面访问 `window.opener`
- `row.desc` **绝不**使用 `innerHTML` 注入，统一使用 `textContent`
- 弹出面板中显示**所有字段**时，使用 `textContent` 设置每个字段值

---

## 三、实现优先级

### Phase 1 — 侧边栏统一（P1）

1. slide/doc 添加折叠/展开按钮 + 收起态
2. doc 添加标题复制路径 + 页码/进度
3. doc 添加 H3 开关
4. 三个模板统一 CSS 变量 + localStorage 命名空间
5. 快捷键焦点检测

### Phase 2 — 表格增强（P1）

6. 设置面板扩展（密度 + 点击模式选择）
7. 弹出面板模式（Modal Panel）+ 安全渲染
8. 分栏模式（Split View）+ min/max 比例 + sandbox iframe
9. 密度切换

### Phase 3 — 增强体验（P2）

10. 侧边栏 TOC 搜索（150ms debounce）
11. 行详情展开
12. 快速过滤
13. 列冻结 + 多列排序

### Phase 4 — 锦上添花（P3）

14. 侧边栏宽度拖拽（200-400px）
15. 键盘导航 + 批量操作
16. 视图预设（max 10, ≤2KB each）+ 全屏表格
