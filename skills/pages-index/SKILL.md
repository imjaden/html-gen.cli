---
name: pages-index
description: Use when building or optimizing a GitHub Pages project landing/index page. Hero + product-matrix layout, light theme, copy buttons, dynamic two-screen hero, github-corner theming, dual-source sync.
version: 1.0.0
author: ops
license: MIT
metadata:
  hermes:
    tags: [pages-index, landing, github-pages, html, theme, hero, index]
    related_skills: [html-gen]
---

# pages-index — GitHub Pages 落地页规范（hero + 产物矩阵）

## 概述

沉淀自 html-gen.cli 落地页两轮迭代（2026-08-24，review 审计 PASS 100/A）。适用于"一仓多产物"项目（如 CLI 工具 + 多模板/多 demo）的 pages index 页。深色主题 + 浅色可切换，中文优先，零依赖单文件。

## 骨架（hero + 产物矩阵）

```
<body>
  <button class="theme-btn" id="themeBtn" aria-pressed="false">🌙</button>   ← 固定右上角 right:88px 避让 corner
  <a class="github-corner">…SVG…</a>
  <section class="hero">       ← 动态两屏（见下）
    h1 渐变标题 + tagline + 安装/快速开始 code block + scroll-hint
  </section>
  <section class="templates">  ← 产物矩阵: 每产物一张卡
    tpl-head: icon(四色 ia/ib/ic/id) + 名称 + guide 链接 + 文件行数
    tpl-body: scenarios pills + features 列表 + cli-box(带复制) + demos 列表
  </section>
  <footer class="site-footer">GitHub · Gitee · MIT</footer>
</body>
```

断点: 4 列 → `@media (max-width:1500px)` 2 列 → `@media (max-width:1100px)` 1 列。

## 主题系统

- style-guide.css `:root` 定义语义色变量: `--text-primary/--text-body/--text-secondary/--text-muted/--text-faint/--border-strong/--border-soft/--code-bg/--code-text/--code-cmd/--hero-title-from`；`:root.light` 覆盖全套
- 页面所有硬编码色一律 var() 引用（含 inline style），否则浅色下对比度失败（WCAG AA 4.5:1）
- 主题按钮: `document.documentElement.classList.toggle('light')` + localStorage key 规范 `html-gen:<page>_theme`（模板页用 doc_theme/kw_theme/layoutslide_theme，落地页用 index_theme 隔离）
- `aria-pressed` 随状态同步
- 陷阱: style-guide.css 的 `:root.light a { color: var(--cobalt-600) }` 特异性 (0,1,1) 会覆盖 `.github-corner` (0,1,0)，浅色下 corner 变 indigo——必须加 `:root.light .github-corner { color: var(--gh-octocat); }` (0,2,0) 且 hover 同样覆盖

## github-corner 浅色配色

- 变量: `:root { --gh-corner-fill: rgba(0,0,0,0.41); --gh-octocat: var(--text-secondary); }` / `:root.light { --gh-corner-fill: rgba(0,0,0,0.75); --gh-octocat: #ffffff; }`
- SVG: 三角 `fill="var(--gh-corner-fill)"`，octocat `fill="currentColor"` + `.github-corner { color: var(--gh-octocat); }`
- 浅色 = 深三角 + 白猫（经典 GitHub 形态）；深色 hover 也须保持 `var(--gh-octocat)`（加 `.github-corner:hover` 保护）
- 两种模式: 无工具栏页 = 全图标可点（pointer-events auto）；有工具栏页 = 穿透 `pointer-events:none` + hit 区（36px）

## 动态两屏 hero

目标: 首屏底部看到第二屏标题 + scroll-hint 固定视口底部。

```js
function updateHeroHeight() {
  var hero = document.querySelector('.hero');
  if (hero) hero.style.minHeight = (window.innerHeight - 110) + 'px';  // 110 ≈ 第二屏标题区
}
updateHeroHeight();
window.addEventListener('resize', updateHeroHeight);
```

- `.scroll-hint`: `position:fixed; bottom:24px; left:50%; translateX(-50%)` + `.hide { opacity:0; visibility:hidden }`，scrollY>8 淡出、回顶恢复
- CSS 保留 `min-height:80vh` 作无 JS fallback

## 复制按钮

```js
function copyText(text, btn) {
  var orig = btn ? btn.textContent : '';
  var done = function() { if (btn) { btn.classList.add('ok'); btn.textContent = '✅';
    setTimeout(function() { btn.classList.remove('ok'); btn.textContent = orig; }, 1500); } };
  var fallback = function() {
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.left = '-9999px';
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch(e) {}
    document.body.removeChild(ta);
    if (ok) done();   // 必须检查返回值，失败不标记 ✅
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done).catch(fallback);
  } else { fallback(); }
}
```

- 按钮 `data-copy` 存原文（不含 `$` prompt），恢复用保存的 orig（勿硬编码 📋，会丢"复制"标签）
- headless Chrome 兼容: clipboard API 不可用时走 execCommand

## 双源同步 + 防漂移测试

根 index.html 与 demos/index.html 为独立副本时: 功能特性必须同步，保留各自差异（corner 模式/链接前缀/hero 有无）。防漂移测试断言两文件关键功能特征一致:

```python
features = ['id="themeBtn"', 'html-gen:index_theme', 'class="site-footer"',
            'class="copy-btn"', 'max-width: 1500px', '--gh-octocat', 'rel="noopener"',
            'html-gen table -d data.json', ...]
missing_root = [f for f in features if f not in root]   # 同样查 demos
```

## 测试规范

- 沿用项目模式: headless Chrome + `window.__testErrors` JS 错误检查 + `WebDriverWait` 主元素
- 覆盖: hero 动态高度（`offsetHeight ≈ innerHeight-110 ±6`）、scroll-hint fixed+淡出、主题切换+localStorage 持久化、复制按钮数量+data-copy 非空、footer 链接、light 白猫（`rgb(255,255,255)`）、双源一致性
- 全量: `python3 -m pytest tests/ -q -n 4`

## Pitfalls

1. `:root.light a` 全局规则覆盖 corner/按钮颜色（特异性陷阱）——高特异性覆盖必须显式加
2. inline style 硬编码色不随主题——所有颜色走变量
3. `test_02_hero_100vh` 类断言随 hero 高度设计变更必须同步（80vh→动态两屏→断言 ≥0.75 或精确 vh−110）
4. 行数/文件数等元信息漂移（AGENTS.md vs 页面 tpl-file）——review 会抓（HG-SEC-036）
5. 双源只改一处导致防漂移测试红——同步时保留差异点，同步功能点
