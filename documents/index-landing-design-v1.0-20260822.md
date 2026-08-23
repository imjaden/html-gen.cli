# GitHub Pages 落地页（根 index.html）— 设计文档

## 版本

v1.0 (2026-08-22)

## 背景与问题来源

GitHub Pages（html-gen.lab.jaden.tech，CNAME 已配置）当前站点首页为 README.md 的自动渲染：

- 根目录**无 index.html**，GitHub Pages 回退渲染 README.md
- README 为纯文字 Markdown 表格，**无主题色、无交互、观感生硬**
- 项目本身产出深色主题自包含 HTML，但站点首页反而不体现产品能力（dogfood 缺失）

**现状核实**：
- `demos/index.html`（22.6KB）已是 4 模板展示页：A/B/C/D 四卡（icon + 场景 pills + 6 条特性 + CLI 命令框 + 案例演示链接 + 模板使用说明 ↗），但位于 demos/ 子目录，非站点首页
- demos/index.html 用**相对路径**（`../style-guide.css`、`templates/*.html`、`demos-index.html`、`features/*.html`、`drama-knowledge.html` 等），直接复制到根目录需改 7 处
- demos/index.html 被 README、usage-guide、hermes-profile-skills-list 等多处引用（含本地 http://jaden.local:8089/demos/index.html），不能直接删除或移动

需求：
1. 站点首页（根 index.html）覆盖 README 渲染，带主题色、整屏落地页
2. 首屏展示 html-gen 指令定位（价值）与安装使用
3. 第二屏展示 4 模板能力（复用 demos/index.html 内容）

待确认清单（用户回复 2026-08-22）定稿：

| 项 | 确认 |
|:--|:--|
| 1 文件策略 | C=两份独立维护，接受漂移风险（根 index.html 新建，demos/index.html 不动） |
| 2 Hero 内容 | A 价值定位 + B 安装使用 + C 4 条快速开始命令（不含导航锚点） |
| 3 首屏形态 | A=真 100vh 整屏 hero，滚动进入模板区 |
| 4 README | B=精简为仓库说明，指向站点首页 |
| 5 案例演示区 | A=保留（四卡底部链接与现状一致） |
| 6 模板使用说明链接 | A=保留（相对路径改为 demos/templates/） |

## 目标形态

**现状**：
- 站点首页 = README.md 自动渲染（生硬、无主题色）
- 根目录无 index.html

**目标**：
- 根 index.html：深色主题落地页
  - 第一屏 Hero（100vh）：大标题 + 价值定位一句话 + ⚡ 安装（install.sh install + PATH）+ 🚀 快速开始 4 命令 + github-corner
  - 第二屏起：4 模板展示网格（A 表格 / B 文档 / C 知识库 / D 幻灯片），内容复制自 demos/index.html 的 template-grid，相对路径迁移到根
- README.md：精简为仓库说明（一句话定位 + 目录 + 指向站点首页 + 本地开发），四型表格与安装说明移交首页

## 实现方案

### 1. 新建根 index.html

结构：

```
<head>
  <title>html-gen · 零依赖 HTML 模板生成器</title>
  <link rel="stylesheet" href="style-guide.css">   ← 路径从 ../style-guide.css 改为 style-guide.css
  <style> 落地页自定义样式（hero + 复用 demos/index.html 网格样式）</style>
</head>
<body>
  github-corner（复制自 demos/index.html）
  <section class="hero">            ← 100vh 整屏
    <h1>html-gen</h1>
    <p>零依赖 Python CLI：Markdown/JSON → 自包含单文件 HTML · 深色主题 · 中文优先</p>
    <div class="install">⚡ 安装  bash install.sh install / export PATH=...</div>
    <div class="quickstart">🚀 快速开始  doc/table/knowledge/slide 4 命令</div>
    <div class="scroll-hint">↓ 模板展示</div>
  </section>
  <section class="templates">       ← 第二屏
    <div class="template-grid">    ← 复制 demos/index.html 网格（四卡 + 案例演示 + 使用说明链接）
      ...A/B/C/D 四卡...
    </div>
  </section>
</body>
```

### 2. 相对路径迁移清单（demos/index.html → 根 index.html）

| 原路径 (demos 下) | 新路径 (根) |
|:---|:---|
| `../style-guide.css` | `style-guide.css` |
| `templates/template-*-guide-v1.0-20260707.html` | `demos/templates/template-*-guide-v1.0-20260707.html` |
| `demos-index.html` | `demos/demos-index.html` |
| `features/hermes-profile-skills-list.html` | `demos/features/hermes-profile-skills-list.html` |
| `features/phase2-demo.html` | `demos/features/phase2-demo.html` |
| `drama-knowledge.html` | `demos/drama-knowledge.html` |
| `cloudwise-business-analysis.html` | `demos/cloudwise-business-analysis.html` |
| `chaitin-business-analysis.html` | `demos/chaitin-business-analysis.html` |

共 8 处引用点（7 个目标文件 + 1 个 CSS）。根目录已有 style-guide.css（6361 字节），复用不复制。

### 3. README.md 精简（4B）

保留：
- 一句话定位（与 hero 一致）
- 项目目录结构（简要）
- 站点首页链接：`站点首页: https://html-gen.lab.jaden.tech/`
- 本地开发：`python3 -m http.server 8089` 后访问 `http://localhost:8089/`

移除（移交首页）：
- 四型模板表格（A/B/C/D 特性）
- 安装与注册详细命令
- 快速开始命令
- 指令速查

### 4. 验证

- 生成后本地 `python3 -m http.server 8089` 冒烟
- 检查根 index.html 所有相对链接可解析（无 404）：style-guide.css、demos/*.html、demos/templates/*.html、demos/features/*.html
- 无 JS 错误（window.__testErrors 思路，手动 console 检查）
- 浏览器打开确认 100vh hero 形态与网格布局

## 风险与注意

- **漂移风险（1C 接受）**：根 index.html 与 demos/index.html 为两份独立副本，后续模板特性更新需同步维护两处。治理上可在 AGENTS.md 备注两文件关系
- **相对路径是唯一坑**：根 index.html 所有链接必须指 demos/ 前缀，复制时逐个核对，验证步骤兜底
- README 精简后 GitHub 仓库主页信息量下降，靠首页承接；如后续 README 需恢复完整信息，保留本设计文档可回滚

## 变更文件清单

| 文件 | 动作 |
|:---|:---|
| `index.html`（根，新建） | 落地页（hero + 模板网格） |
| `README.md` | 精简为仓库说明 |
| `documents/index-landing-design-v1.0-20260822.md` | 本设计文档 |
