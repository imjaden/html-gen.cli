# 🖼 幻灯片（模板D）

---

## 一、使用场景

幻灯片模板适用于**演示与分页展示**场景，是三层模板中的演示层：每个 `## h2` 标题为一页，h1 为封面页。

| 场景 | 说明 | 典型篇幅 |
|:---|:---|:---:|
| **技术分享** | 架构讲解、方案评审、团队分享 | 10-30 页 |
| **方案演示** | 产品演示、代码 walkthrough | 5-20 页 |
| **培训课件** | 教学课件、操作指南 | 15-50 页 |
| **会议材料** | 周会/月会汇报、决策材料 | 5-15 页 |

### 与 B 型文档的关系

D 型与 B 型共用同一 Markdown 渲染器，区别在于排版与交互：
- B 型：长文滚动阅读（侧边栏 TOC）
- D 型：h2 分页演示（键盘翻页）

---

## 二、方案设计

### 架构

```
Layer 1: style-guide.css (CSS variables + component base)
Layer 2: layout-slide.html (template skeleton)
Layer 3: html-gen.py → slide subcommand (Markdown injection)
```

### 分页规则

```
# Title        → cover page (h1; slide-cover + page counter)
## Chapter     → one page per h2 (page unit)
### Subheading → in-page H3 section (collapsed by default)
```

### 关键设计决策

| 决策 | 选择 | 理由 |
|:---|:---|:---|
| **分页粒度** | h2 为页 | Markdown 天然语义，无需额外语法 |
| **渲染** | 与 B 型同源 | md_to_html 复用，特性一致（代码块/表格/Callout） |
| **交互** | 客户端 JS | 键盘翻页 + 全屏，零依赖 |
| **样式** | style-guide.css inline | 单文件嵌入 |

---

## 三、功能清单

### 已实现 ✅

| 功能 | 说明 |
|:---|:---|
| h2 分页 | 每个 ## h2 为一页，h1 为封面页 |
| 键盘导航 | ← → Space Home End 翻页 |
| 全屏 | F 键切换全屏 |
| 进度指示 | 底部圆点（已读/当前/未读） |
| 页码 | 当前页 / 总页数 |
| 阅读记忆 | localStorage 恢复上次阅读位置 |
| H3 子标题 | 默认隐藏，点击开关展开 |
| 性能警告 | >50 h2 时显示加载警告（perf-warning） |
| 零外部依赖 | 单文件 HTML，样式内联 |

### 待实现 🔜

| 功能 | 说明 |
|:---|:---|
| 演讲者备注 | 每页备注区（仅演示者可见） |
| 目录页 | 封面后自动生成可点击目录 |

---

## 四、快速开始

```shell
# 安装（三选一）
pip install html-gen-cli               # PyPI 包，命令 html-gen（短别名 htmlgen）
git clone https://github.com/imjaden/html-gen.cli && cd html-gen.cli   # 源码方式
python3 html-gen.py version            # 零依赖：不装也能直跑
```

```shell
# 从 Markdown 生成幻灯片
html-gen slide -i slides.md -o slides.html

# 指定标题
html-gen slide -i slides.md -o slides.html --title "方案评审"
```

### 命令行参数

```
html-gen slide -h
  -i, --input FILE   输入 Markdown 文件（必需）
  -o, --output FILE  输出 HTML 文件
  --title TEXT       覆盖标题
  --subtitle TEXT    副标题
```

### Markdown 分页约定

```markdown
# 方案标题          ← 封面页（h1）

## 背景与目标       ← 第 1 页

正文内容...

## 方案设计         ← 第 2 页

### 架构             ← 页内 H3（默认隐藏）

细分内容（点击 H3 展开）
```

---

## 五、模板案例

该模板的精选案例（html-gen demo list ★ featured，路径相对 demos/）：

| 案例 | 说明 | 文件 |
|:---|:---|:---|
| [Slide 幻灯片版](slide-features-demo.html) | h2 分页 · 键盘翻页 · 圆点导航 · 全屏演示 | slide-features-demo.html |

---

## 六、影响面说明

> 改本模板的能力/键/行为时按此表逐面清点；**单源权威是 `documents/templates.md` §影响面矩阵**（含判据命令与 1→8 标准流程），这里只列本模板落点。

| 面 | 本模板落点 |
|:---|:---|
| **指令面** | `html-gen help slide`（`TEMPLATE_CONTRACT['slide']`） |
| **Skills 面** | `skills/html-gen-slide/SKILL.md`、`skills/html-gen/SKILL.md`（D 型段） |
| **文档面** | 本文件（→ `slide-guide.html`）、`documents/templates.md`、`features.md` |
| **案例面** | `demos/slide-guide.html`（← `slide-guide.md`，`demo --rebuild`）、`demos/slide-features-demo.html`（手写页，无 md 源） |
| **测试面** | `tests/test_help_contract.py`、`tests/test_templates.py`（slide 段）、`tests/test_slide_h3_toggle.py` |
| **基线/门禁面** | `scripts/baseline.py`（`SLIDE_PRODUCTS`）、`data/_render-baseline.json`、`documents/docs-index.md` |
| **打包面** | `src/html_gen/layout-slide.html` → `scripts/build-package.py` |
| **跨仓/发布面** | script-miner `skills/html-templates/layout-slide.html`（+ 其 vendor 测试）、版本三件 |

> 反例参照 CL047（2026-11-23）：模板改完漏了 Skills 面、案例面、打包面三处，靠事后全量扫描才发现。

## 迭代记录

| 版本 | 日期 | 变更 |
|:---|:---:|:---|
| v1.0 | 2026-07-14 | 初版：h2 分页 + 键盘导航 + 全屏 + 进度圆点 + 页码 + 记忆 |
| v1.1 | 2026-07-22 | H3 子标题开关 + 性能警告（>50 h2）+ slide-cover 封面页 |
| v1.2 | 2026-08-23 | 新增「模板案例」章节（★ featured 精选） |