# html-gen

零依赖 Python CLI 工具：将 Markdown/JSON 注入 HTML 模板，输出自包含单文件 HTML。深色主题，中文优先。

- 站点首页（四型模板展示 + 安装使用）: https://html-gen.lab.jaden.tech/
- 模板源码: `layout-table.html` (A 型表格) / `layout-doc.html` (B 型文档) / `layout-knowledge.html` (C 型知识库) / `layout-slide.html` (D 型幻灯片)
- 生成器: `html-gen.py`（仅 Python 3 标准库，零外部依赖）
- 主题基座: `style-guide.css`（--cobalt-* 深色变量）

## 本地开发

```bash
python3 -m http.server 8089   # 项目根目录起服务
# 访问 http://localhost:8089/ （根落地页）/ http://localhost:8089/demos/ （demo 目录）
```

## 快速开始

```bash
bash install.sh install                 # 注册 html-gen 到 ~/.local/bin
html-gen doc -i report.md -o report.html          # B 型文档
html-gen table -d data.json -o index.html         # A 型表格
html-gen knowledge -d data.json -o kb.html        # C 型知识库
html-gen slide -i slides.md -o slides.html        # D 型幻灯片
```

完整使用说明见站点首页与 `html-gen help`。
