# html-gen

零依赖 Python CLI 工具：将 Markdown/JSON 注入 HTML 模板，输出自包含单文件 HTML。深色主题，中文优先。

## 四型模板

| 类型 | 指令 | 输入 → 输出 | 特性 |
|:---|:---|:---|:---|
| A 型表格 | `html-gen table` | JSON → 表格页 | 搜索/排序/分页/列隐藏/分栏预览/视图预设 |
| B 型文档 | `html-gen doc` | Markdown → 文档页 | 侧边栏 TOC/搜索/折叠/宽屏模式 |
| C 型知识库 | `html-gen knowledge` | JSON → 知识库 | 顶部标签栏/左侧章节/iframe 加载/记忆恢复 |
| D 型幻灯片 | `html-gen slide` | Markdown → 幻灯片 | h2 分页/键盘翻页/全屏 |

## 安装与注册

```bash
bash install.sh             # 显示帮助（无参默认 help）
bash install.sh install     # 注册 html-gen 到 ~/.local/bin（wrapper 指向本项目 html-gen.py）
bash install.sh status      # 查看注册状态（wrapper / PATH / 源码）
bash install.sh uninstall   # 移除注册
bash install.sh -p ~/bin install   # 自定义安装目录
bash install.sh -n install  # 预览命令（dry-run，不实际执行）
```

需 `~/.local/bin` 在 PATH（zshrc: `export PATH="$HOME/.local/bin:$PATH"`）。
运行仅需 Python 3 标准库，零外部依赖。

## 快速开始

```bash
# B 型文档
html-gen doc -i report.md -o report.html --title "标题"

# A 型数据表格
html-gen table -d data.json --title "标题" -o index.html

# C 型知识库
html-gen knowledge -d data.json -g groups.json --title "标题" -o kb.html

# D 型幻灯片
html-gen slide -i slides.md -o slides.html
```

输出为自包含单文件 HTML，无外部资源引用（CSS 生成时内联）。

## 指令速查

```
html-gen help                 总览
html-gen help doc              Markdown 语法规范 (B/D 型)
html-gen help table            JSON 数据格式 (A 型)
html-gen help knowledge        JSON 数据格式 (C 型)
html-gen help slide            slide 功能说明
html-gen help prompt           skills 输出
html-gen help demo             demo 清单与规范
html-gen demo list             按模板类型列出案例（--all 含引用子页 / --json）
html-gen demo <name>           案例详情 + 预览 URL（--open 打开浏览器）
html-gen demo --rebuild        重建案例清单 _registry.json
html-gen prompt <skill>        skills/ 项目 skill 摘要与全文
```

## 案例演示

[demos/index.html](demos/index.html) — 模板展示首页（三型案例精选 + 模板指南）

案例清单（40 个 demo，按模板分组）命令行查看：`html-gen demo list`

- 📚 知识库：以剧读史（影视历史知识库：中国历史/大明王朝1566/雍正王朝 3 组）、长亭科技商业分析
- 🗂 表格：Hermes Skills 列表、全球国家速查表、功能 demo 系列
- 📄 文档：四型模板指南、Markdown 规范、使用指南

## 测试

```bash
python3 -m pytest tests/ -q -n 4     # 并行全量 (139 tests, ~26s)
python3 -m pytest tests/ -q -n 0     # 单线程调试
```

依赖：`pytest-xdist>=3.8.0`（见 requirements-dev.txt）；Chromedriver 路径见 AGENTS.md。

## 零依赖

- 全部 Python 标准库（json/re/sys/os/argparse/subprocess/pathlib/datetime）
- 模板/CSS 通过 `Path(__file__).resolve().parent` 自定位
- 输出自包含单文件 HTML，无 CDN/外部链接
