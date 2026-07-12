# layout-table Cmd+F Quick Search 弹出框设计

## 版本

v2.2 (2026-07-12)

## 参考

`emoji2image.html` — Spotlight 风格搜索弹框：全局快捷键、blur 遮罩、聚焦输入、ESC 关闭

## 功能描述

在 `layout-table.html` 中添加 `Command+F` / `Ctrl+F` 全局快捷键，弹出 Spotlight 风格搜索框，快速定位表格数据。

## 交互流程

```
1. 用户在页面任意位置按 Cmd+F / Ctrl+F
2. 阻止浏览器默认搜索行为 (e.preventDefault())
3. 弹出半透明遮罩 + 居中搜索框 (Slide-in 动画)
4. 搜索框自动聚焦，内容为当前顶部搜索框已有内容 (双向同步)
5. 用户在弹出框中输入/修改搜索关键词 → 实时同步到顶部搜索框
6. 按 Enter 或点击「搜索」按钮 → 关闭弹框 → 表格执行搜索
7. 按 ESC 或点击遮罩外部 → 关闭弹框 (不触发搜索)
8. 关闭弹框时保留搜索关键词到顶部搜索框
```

## CSS 设计

### 遮罩层 (.quick-search-overlay)
- `position: fixed; inset: 0`
- `background: rgba(0,0,0,0.5); backdrop-filter: blur(6px)`
- `z-index: 9999`
- `display: none` → `.active { display: flex }`
- Flexbox 居中：`justify-content: center; align-items: flex-start; padding-top: 15vh`

### 搜索框 (.quick-search-modal)
- 宽度 `560px`，最大 `90vw`
- 背景 `var(--surface-900)`，深色主题适配
- `border: 1px solid var(--cobalt-700)`
- `border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.4)`
- 动画: `@keyframes qsSlideIn { from { opacity:0; transform:translateY(-16px) } }`

### 输入区 (.qs-input-row)
- `display: flex; align-items: center; padding: 14px 18px; gap: 10px`
- 搜索图标 `🔍`，`font-size: 1.1rem; color: var(--cobalt-400)`
- `<input>` 占满剩余空间，无边框无轮廓
- 字体 `1rem; color: #e0e0e0; background: transparent`
- Placeholder: `搜索...`

### 提示区 (.qs-hint)
- `padding: 4px 18px 12px; font-size: 0.65rem; color: #6b7280`
- 显示快捷键提示: `↑↓ 导航  ·  Enter 搜索  ·  Esc 关闭`

### 匹配预览 (可选扩展)
- 实时显示匹配条数: `找到 12 条匹配`
- 紧凑预览列表（3-5 条），点击直接定位
- 如果不实现预览，仅显示匹配计数

## JS 实现

### 状态管理
```javascript
var quickSearch = {
  overlay: document.getElementById('qsOverlay'),
  input: document.getElementById('qsInput'),
  active: false
};
```

### 键盘事件
```javascript
document.addEventListener('keydown', function(e) {
  // Cmd+F / Ctrl+F → 打开
  if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
    e.preventDefault();
    quickSearch.open();
  }
  // ESC → 关闭
  if (e.key === 'Escape' && quickSearch.active) {
    quickSearch.close();
  }
});
```

### open()
1. 读取顶部搜索框 `#searchInput` 的当前值 → 填入弹出框
2. 显示遮罩 `.active`
3. `setTimeout(() => input.focus(), 100)`
4. 如有匹配预览，触发实时计算

### close()
1. 将弹出框内容同步回顶部 `#searchInput`
2. 移除 `.active`
3. **不触发表格搜索** — 用户需按 Enter 明确提交

### submit()
1. 关闭弹框 `close()`
2. 调用 `doSearch()` 触发表格搜索

### 实时同步
弹出框 `input` 事件 → 同步写入顶部 `#searchInput`
（确保关闭弹框后，顶部搜索框保留最新输入）

## HTML 结构

```html
<div class="quick-search-overlay" id="qsOverlay" onclick="if(event.target===this)quickSearch.close()">
  <div class="quick-search-modal">
    <div class="qs-input-row">
      <span>🔍</span>
      <input id="qsInput" placeholder="搜索..." onkeydown="qsHandleKey(event)">
      <button class="qs-close-btn" onclick="quickSearch.close()">Esc</button>
    </div>
    <div class="qs-hint" id="qsHint">
      <span>↑↓ 导航  ·  Enter 搜索  ·  Esc 关闭</span>
      <span id="qsMatchCount"></span>
    </div>
  </div>
</div>
```

### 按键处理 (qsHandleKey)
- `Enter` → `quickSearch.submit()`
- `Escape` → `quickSearch.close()`
- `input` → 实时同步 + 匹配计数更新

## 匹配预览（可选扩展 v2）

如启用匹配预览（配置 `options.quickSearchPreview: true`）：

- 实时计算匹配条数：`DATA.filter(...).length`
- 显示「找到 N 条匹配」
- 显示前 3 条匹配结果的行预览（紧凑单行）

不启用时：仅显示快捷键提示。

## 不影响现有功能

- 顶部搜索框行为完全不变（实时搜索 debounce + Enter）
- 弹出框只是给顶部搜索框提供快速访问入口
- Column 排序完全替换了旧的：但 column 定义保持不变
- 分页/导出/列可见性不受影响

## 暗色主题适配

所有颜色使用 `--cobalt-*` / `--surface-*` CSS 变量，与现有 style-guide.css 完全一致。
