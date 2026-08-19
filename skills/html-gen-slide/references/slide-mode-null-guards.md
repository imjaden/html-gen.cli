# DOM Null Guard 规范

## 问题背景

2026-07-13，`layout-doc.html` 合并 doc/slide 模式时，在浏览器 Console 出现以下错误：

```
Uncaught TypeError: Cannot set properties of null (setting 'innerHTML')
    at Object.buildDots (template-B-markdown-spec-v1.0-20260707.html:1219:22)

Uncaught TypeError: Cannot read properties of null (reading 'classList')
    at Object.enter (template-B-markdown-spec-v1.0-20260707.html:1131:43)

Uncaught TypeError: Cannot read properties of null (reading 'scrollIntoView')
    at HTMLAnchorElement.<anonymous> (template-B-markdown-spec-v1.0-20260707.html:993:53)
```

## 根因

`document.getElementById()` 返回 `null` 时，直接访问 `.classList`、`.style`、`.innerHTML` 等属性导致 `TypeError`。即使在 HTML 中元素确实存在，不同浏览器/环境/解析顺序可能导致临时不可用。

## 解决方案

所有 `getElementById()` 调用必须添加 null guard：

```javascript
// buildDots
var dots = document.getElementById('slideDots');
if (!dots) return;
dots.innerHTML = '';

// _updateDots
var dotsEl = document.getElementById('slideDots');
if (!dotsEl) return;
var dots = dotsEl.children;

// _showPageNum
var el = document.getElementById('slidePageNum');
if (!el) return;

// _syncToc / slideNavTitle
var titleEl = document.getElementById('slideNavTitle');
if (titleEl) titleEl.textContent = ...;

// enter
var dm = document.getElementById('docMain');
var sm = document.getElementById('slideMain');
var sn = document.getElementById('slideNav');
if (!dm || !sm || !sn) return;

// exit
var sm = document.getElementById('slideMain');
if (sm) sm.classList.remove('active');

// TOC click
var target = document.getElementById(this.dataset.target);
if (target) target.scrollIntoView({ behavior: 'smooth' });

// perfWarning
var pw = document.getElementById('perfWarning');
if (pw && pw.textContent.trim()) pw.style.display = 'block';
```

## 影响范围

以下方法/位置必须添加 null guard：

| 位置 | 元素 | 风险 |
|:---|:---|:---|
| `buildDots()` | `slideDots` | innerHTML |
| `_updateDots()` | `slideDots`, `slideNavTitle` | children, textContent |
| `_showPageNum()` | `slidePageNum` | textContent, classList |
| `enter()` | `docMain`, `slideMain`, `slideNav` | style.display, classList |
| `exit()` | `slideMain`, `slideNav`, `docMain`, `perfWarning` | classList, style.display |
| TOC click handler | `this.dataset.target` | scrollIntoView |

## 测试验证

结构测试即可覆盖（无需 Selenium）：

```python
def test_null_guards_in_template(self):
    tmpl = (PROJECT / 'layout-slide.html').read_text()
    for pattern, desc in [
        (r'if\s*\(!?\s*dots?\s*\)\s*return', 'buildDots'),
        (r'if\s*\(!?\s*el\s*\)\s*return', '_showPageNum'),
        (r'if\s*\(!dm\s*\|\|\s*!sm\s*\|\|\s*!sn\s*\)\s*return', 'enter'),
        (r'if\s*\(target\s*\)\s*target\.scrollIntoView', 'TOC'),
    ]:
        self.assertIsNotNone(re.search(pattern, tmpl), f"Missing: {desc}")
```
