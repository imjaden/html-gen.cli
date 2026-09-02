
# html-gen B 型文档规范

## 概述
B 型文档模板从 Markdown 生成完整的文档页面。自动剥离 YAML frontmatter，提供侧边栏 TOC 导航、实时高亮、搜索等功能。

## 何时使用
- 需要将 Markdown 文档转为可分享的自包含 HTML 页面
- 需要带侧边栏导航的长文档（报告/手册/指南）
- 需要幻灯片模式（doc/slide 双模式）

## CLI 用法

```
html-gen doc -i report.md -o report.html [--title "标题"] [--subtitle "副标题"]
```

自动剥离 YAML frontmatter。标题优先级: `--title` > fm title > body h1 > stem。

## Markdown 语法规范
- h1-h3: 自动加 id 锚点
- **加粗** / *斜体* / `代码` / [链接](url)
- 围栏代码块 (变长 fence 嵌套)
- 表格 (pipe table)
- 无序/有序列表
- Callout: `> **Note/Warning/Tip/Danger/注意/警告/提示/危险**: 内容`
- 分隔线 `---` / 引用 `> 文字`
- 不解析图片 (安全限制)

## 文档页特性
- 侧边栏 TOC (h2/h3 自动生成) + 实时高亮当前章节
- TOC 搜索 (🔍 按钮, 150ms debounce, ≥2 字符)
- 折叠/展开侧边栏 (48px, `[` 快捷键)
- 侧边栏宽度拖拽 (200-400px, localStorage)
- H3 子项开关 / 中英双语 / 🌙☀️ 主题切换
- 标题点击复制路径 / 代码复制 (clipboard + fallback)
- 行号 / Callout 提示框 / 阅读进度条 / 图片灯箱

## 验证清单
- [ ] `html-gen doc` 命令执行成功
- [ ] 侧边栏 TOC 与正文 h2/h3 对应
- [ ] 搜索过滤正常
- [ ] 折叠/展开/拖拽功能正常
- [ ] 代码复制功能正常

## 变更记录
- v1.0.0 (2026-08-08): 首次提炼自 AGENTS.md
