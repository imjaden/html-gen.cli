# layout-slide 右上角工具栏 + 标题交互设计方案

## 版本

v2.3 (2026-07-14)

## 参考

`~/.hermes/skills/software-development/static-site-portfolio/SKILL.md` — i18n 语言切换、dark/light theme、copy-to-clipboard 模式

## 1. 标题区域重构

### 重命名

`div.logo` → `div.slide-title`（无冲突，现有模板无 `.title` 类）

### 交互

| 操作 | 行为 |
|:---|:---|
| 鼠标悬浮 | 显示完整标题（`title` 属性，不受 30 字截断限制） |
| 鼠标点击 | 拷贝文件路径到剪贴板（`$HOME` → `~`），Toast 提示 |

### 路径获取

```javascript
// 从 <!--METADATA--> 中提取路径（格式: 路径: <code>~/path/file.md</code>）
var metaEl = document.querySelector('.doc-header .meta');
var pathMatch = metaEl ? metaEl.textContent.match(/路径:\s*(.+)/) : null;
var filePath = pathMatch ? pathMatch[1].trim() : document.title;
```

### 剪贴板

使用 `navigator.clipboard.writeText()` + `execCommand('copy')` 兜底。

## 2. .sub 页码格式

### 中文模式

| 位置 | 显示 |
|:---|:---|
| 封面页 | `共 38 页` |
| 第 3 页 | `3 / 38` |

### 英文模式

| 位置 | 显示 |
|:---|:---|
| Cover | `38 pages` |
| Page 3 | `3 / 38` |

### 实现

`goTo()` 中读取 `slide._lang` 变量选择文案。

## 3. 右上角工具栏

### 布局

```
┌──────────────────────────────────────────────┐
│  🎞️ Title...   3 / 38          [🇨🇳 🇺🇸] [🌙] │
│  slide-sidebar            top-right-toolbar  │
└──────────────────────────────────────────────┘
```

固定在浏览器视口右上角，`position: fixed; top: 12px; right: 16px; z-index: 900`。

### 样式（参考 static-site-portfolio）

```css
.top-toolbar {
  position: fixed; top: 12px; right: 16px; z-index: 900;
  display: flex; align-items: center; gap: 4px;
  background: rgba(17,17,27,0.88); backdrop-filter: blur(12px);
  border: 1px solid #2a2a3e; border-radius: 28px;
  padding: 3px 4px;
}
.tb-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: transparent; color: #9ca3af; cursor: pointer;
  font-size: 0.85rem; transition: all 0.2s;
  font-family: inherit;
}
.tb-btn:hover { background: rgba(79,70,229,0.15); color: #e0e0e0; }
.tb-btn.active { background: var(--cobalt-600); color: #fff; }
.tb-divider { width: 1px; height: 18px; background: #2a2a3e; margin: 0 2px; }
```

### 语言切换

两个独立按钮：

```html
<div class="top-toolbar" id="topToolbar">
  <button class="tb-btn active" id="langZh" onclick="setLang('zh')" title="中文">🇨🇳</button>
  <button class="tb-btn" id="langEn" onclick="setLang('en')" title="English">🇺🇸</button>
  <span class="tb-divider"></span>
  <button class="tb-btn" id="themeBtn" onclick="toggleTheme()" title="切换主题">🌙</button>
</div>
```

- 默认中文（🇨🇳 active），点击 🇺🇸 切换英文
- 语言选择保存到 `localStorage key: layoutslide_lang`
- 切换时更新 `.sub` 页码文案

### 主题切换

- 默认深色（🌙），点击切换浅色（☀️）
- `localStorage key: layoutslide_theme`
- 通过 CSS 变量覆写实现（`:root.light` 类名切换）

```css
:root.light {
  --surface-950: #f5f5f5;
  --surface-900: #ffffff;
  --surface-850: #f0f0f0;
  --surface-800: #e8e8e8;
  --cobalt-950: #eef2ff;
  --cobalt-900: #e0e7ff;
}
:root.light body { color: #333; }
:root.light .slide-page h2 { color: #222; }
:root.light .slide-page h3 { color: #333; }
:root.light .slide-page p { color: #444; }
/* ... 更多 light 变量映射 */
```

### i18n 影响范围（v1 最小）

仅 `.sub` 页码文案受语言切换影响：

```javascript
var LANG = {
  zh: { pages: '共 {n} 页', current: '{m} / {n}' },
  en: { pages: '{n} pages', current: '{m} / {n}' }
};
```

后续版本可扩展到全页面元素。

## 4. HTML 结构变更

```html
<!-- 删除旧的 sidebar-header sub 中的行内文案 -->
<div class="slide-sidebar-header">
  <div class="slide-title">🎞️ <!--TITLE--></div>
  <div class="sub-row">
    <div class="sub"><!--SUBTITLE--></div>
    <div class="slide-h3-toggle" id="h3Toggle" onclick="toggleH3()">H3</div>
  </div>
</div>

<!-- 新增: 右上角工具栏 -->
<div class="top-toolbar" id="topToolbar">
  <button class="tb-btn active" id="langZh" onclick="setLang('zh')" title="中文">🇨🇳</button>
  <button class="tb-btn" id="langEn" onclick="setLang('en')" title="English">🇺🇸</button>
  <span class="tb-divider"></span>
  <button class="tb-btn" id="themeBtn" onclick="toggleTheme()" title="切换主题">🌙</button>
</div>
```

## 5. JS 增量

```javascript
// ── i18n
var _lang = localStorage.getItem('layoutslide_lang') || 'zh';
var L = {
  zh: { pages: '共 {n} 页', current: '{m} / {n}' },
  en: { pages: '{n} pages', current: '{m} / {n}' }
};

function t(key, params) {
  var s = L[_lang][key];
  for (var k in params) s = s.replace('{' + k + '}', params[k]);
  return s;
}

window.setLang = function(lang) {
  _lang = lang;
  localStorage.setItem('layoutslide_lang', lang);
  document.getElementById('langZh').classList.toggle('active', lang === 'zh');
  document.getElementById('langEn').classList.toggle('active', lang === 'en');
  // Trigger sub update
  slide._updateSub();
};

// ── Theme toggle
window.toggleTheme = function() {
  var r = document.documentElement;
  var isLight = r.classList.toggle('light');
  localStorage.setItem('layoutslide_theme', isLight ? 'light' : 'dark');
  document.getElementById('themeBtn').textContent = isLight ? '☀️' : '🌙';
};

// ── Title click → copy path
document.querySelector('.slide-title').addEventListener('click', function() {
  var metaEl = document.querySelector('.doc-header .meta');
  var m = metaEl ? metaEl.textContent.match(/路径:\s*(.+)/) : null;
  var path = m ? m[1].trim() : document.title;
  // Replace $HOME with ~
  path = path.replace(/^\/Users\/[^/]+/, '~');
  if (navigator.clipboard) {
    navigator.clipboard.writeText(path).then(function() { showToast('已复制: ' + path); });
  } else {
    var ta = document.createElement('textarea'); ta.value = path;
    ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); document.body.removeChild(ta);
    showToast('已复制: ' + path);
  }
});

// ── Toast (simple inline, no dependency)
function showToast(msg) {
  var el = document.getElementById('slideToast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'slideToast';
    el.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);padding:8px 20px;background:var(--cobalt-950);color:#e0e0e0;border-radius:8px;font-size:0.78rem;z-index:9999;border:1px solid var(--cobalt-700);opacity:0;transition:opacity 0.2s;white-space:nowrap;pointer-events:none';
    document.body.appendChild(el);
  }
  el.textContent = msg; el.style.opacity = '1';
  clearTimeout(el._hide);
  el._hide = setTimeout(function() { el.style.opacity = '0'; }, 2500);
}
```

## 6. goTo() 修改

```javascript
// In goTo(), replace direct subEl.textContent with:
this._updateSub();

// New method:
_updateSub: function() {
  var subEl = document.querySelector('.slide-sidebar-header .sub');
  if (!subEl || this._subBase === undefined) return;
  var total = this.pages.length - 1;
  var text = this.currentPage === 0
    ? t('pages', {n: total})
    : t('current', {m: this.currentPage, n: total});
  subEl.textContent = (this._subBase ? this._subBase + ' · ' : '') + text;
}
```

## 7. 不影响的功能

- H3 开关、侧边栏 TOC、键盘导航、圆点导航
- 封面页渲染、h3 分列模式
- 所有 CLI 命令和参数
