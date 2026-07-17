# html-gen — Features

> 零依赖 Python CLI HTML 生成器。深色主题，中文优先。
>
> 文件命名: 固定为 `features.md`，小写，无版本号。
>
> 适用: 风格 B 文件（无版本号，持续更新），存放在项目根目录。

## 模板生成

1. A 型表格生成: `html-gen table <json>` ✅ — layout-table.html
2. B 型文档生成: `html-gen doc <md>` ✅ — layout-doc.html
3. C 型知识库生成: `html-gen knowledge <json>` ✅ — layout-knowledge.html
4. D 型幻灯片生成: `html-gen slide <md>` ✅ — layout-slide.html

## CLI 工具

1. 多级帮助系统: `html-gen help` / `html-gen <subcommand> help` ✅
2. 安装脚本: `bash install.sh` ✅
3. 演示服务器: `python3 -m http.server` 🟡 — 配合 demos/ 目录

## 辅助工具

1. 公司调研报告生成: `python3 company-report.py` ✅ — 从 schema JSON 生成知识库
2. Chromedriver 管理: `chromedriver-manager list / check` 🟡 — Selenium 测试依赖
3. Selenium 验收测试: `tests/selenium/test-*.py` ✅ — 4 模板覆盖测试

## 样式体系

1. style-guide.css: CSS 变量 + 基础组件（按钮/表格/弹窗/分页）✅
2. 深色主题统一设计: 所有模板共享 CSS 变量 ✅
3. 布局自适应: 移动端 + 桌面端 🟡

## 待定/规划

1. 模板市场 / 模板共享机制 🚧
2. 多语言输出支持 🚧
