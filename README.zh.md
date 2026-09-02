<p align="center">
  <a href="README.md">🇬🇧</a> · <a href="README.zh.md">🇨🇳</a>
</p>

<h1 align="center">html-gen</h1>

<p align="center">
  <a href="https://github.com/imjaden/html-gen.cli"><img src="https://github.com/favicon.ico" width="16" height="16" alt="GitHub"> GitHub</a>
  <span> · </span>
  <a href="https://pypi.org/project/html-gen-cli"><img src="https://pypi.org/static/images/favicon.35549fe8.ico" width="16" height="16" alt="PyPI"> PyPI</a>
</p>

> Markdown / JSON → 自包含单文件 HTML。零外部依赖。
>
> 深色主题，中文优先。四型模板：B 文档（侧边栏 TOC）、A 表格（搜索/排序/分页）、C 知识库（标签栏 + 章节）、D 幻灯片（h2 分页）。
>
> html-gen 是独立工具 —— 与 npm 包 "html-gen" 无关。

- [x] **零外部依赖** — 纯 Python 标准库；输出为自包含单文件 HTML（CSS 内联）
- [x] **四型模板** — doc / table / knowledge / slide（`html-gen doc|table|knowledge|slide`）
- [x] **表格功能丰富** — 搜索 / 多字段排序 / 分页 / 列可见性 / CSV 导出 / 批量操作 / 分栏预览 / 视频列
- [x] **知识库** — 顶部标签栏 + 侧栏章节 + iframe/内联内容，URL 同步与状态恢复
- [x] **AI 对接** — `html-gen prompt` 输出项目 skills（供 AI agent 读取使用说明）
- [x] **默认隐私** — 生成物默认不含个人信息链接，显式入参才带（`--github-url` / `--home-url`）
- [x] **默认 favicon** — 默认注入 favicon 图标到 `<head>`；`--favicon <url>` 覆盖，显式空串禁用

## 安装

```bash
pip install html-gen-cli        # 安装 `html-gen` 命令
```

或源码运行（免安装）：

```bash
git clone https://github.com/imjaden/html-gen.cli
cd html-gen.cli
python3 html-gen.py version     # html-gen v3.3 (2026-08-28)
```

## 快速开始

```bash
# B 型 — Markdown → 文档（侧边栏 TOC + 阅读）
html-gen doc -i report.md -o report.html

# D 型 — Markdown → 幻灯片（h2 分页 + 键盘翻页）
html-gen slide -i slides.md -o slides.html

# A 型 — JSON → 数据表格
html-gen table -d data.json -o index.html

# C 型 — JSON → 知识库（顶部标签栏 + 侧栏章节）
html-gen knowledge -d kb.json -g groups.json -o kb.html
```

## 命令速查

| 命令 | 说明 |
|:--|:--|
| `html-gen doc` | Markdown → B 型文档 |
| `html-gen slide` | Markdown → D 型幻灯片 |
| `html-gen table` | JSON → A 型数据表格 |
| `html-gen knowledge` | JSON → C 型知识库 |
| `html-gen version` | 显示版本（vX.Y + 发版日期） |
| `html-gen help [topic]` | 总览 + 分主题帮助（doc/slide/table/knowledge/prompt/demo） |
| `html-gen prompt [skill]` | 输出项目 skills（AI 对接说明） |
| `html-gen demo list` | demo 清单与 registry |

> 输出: table/knowledge 的 `-o/--output` **必填**（CLI `-o` 或 JSON 顶层 `output` 二选一；均无 → 提示中断 exit 1）

## AI 对接

```bash
html-gen prompt                   # 列出全部 skills（名称 + 描述）
html-gen prompt html-gen-table    # 单篇完整使用说明
html-gen prompt html-gen-table --brief
html-gen prompt --json            # 机器可读信封
```

### 在线阅读 & curl 获取（`--site`）

生成 `prompts/` 站点（18 文件），供 GitHub Pages 原样服务——在线阅读页 + 每 skill
的纯 markdown / JSON 信封下载：

```bash
html-gen prompt --site                        # → prompts/（仓库根）
html-gen prompt --site --dir <path>           # 输出目录覆盖
```

| 文件 | URL | 内容 |
|:--|:--|:--|
| `prompts/index.html` | https://html-gen.cli.jaden.tech/prompts/ | 合集阅读页（B 型 doc 渲染） |
| `prompts/all.md` | https://html-gen.cli.jaden.tech/prompts/all.md | 8 skills 全量（一次拉取） |
| `prompts/{skill}.md` | https://html-gen.cli.jaden.tech/prompts/{skill}.md | 单 skill 纯 markdown（正文 + references） |
| `prompts/{skill}.json` | https://html-gen.cli.jaden.tech/prompts/{skill}.json | 单 skill JSON 信封（`{status,error,data}`） |

```bash
curl -s https://html-gen.cli.jaden.tech/prompts/                # 阅读页
curl -s https://html-gen.cli.jaden.tech/prompts/all.md          # 全量合集
curl -s https://html-gen.cli.jaden.tech/prompts/html-gen.md     # 单篇 markdown
curl -s https://html-gen.cli.jaden.tech/prompts/html-gen.json   # 单篇 JSON 信封
```

> 站点产物一律剥离 YAML frontmatter（GitHub Pages 原样服务），与终端
> `html-gen prompt <skill>`（保留 frontmatter）差异仅此一段。`prompts/` 勿手改，
> 由 `html-gen prompt --site` 重新生成。`--site` 与 `skill` / `--brief` / `--json` 互斥。

## 数据目录

- `data/*.json` — 源数据（表格 / 知识库）
- `demos/*.html` — 生成物（勿手改，由数据重新生成）
- `layout-*.html` / `style-guide.css` — Layer 2 模板 / Layer 1 CSS 基座

## 本地开发

```bash
# 预览（根落地页 + demos）
python3 -m http.server 8089

# 跑测试（pytest-xdist，约 36s）
python3 -m pytest tests/ -q -n 4
```

## 测试

- Selenium headless Chrome 回归套件（`tests/test_*.py`，246 用例）
- 每个用例断言页面加载零 JS 错误
