---
title: html-gen CLI 参考（子命令与脚本）
topic: html-gen
type: reference
version: 1.0
date: 2026-11-09
author: ops
source: AGENTS.md 外移（HTML-GEN-CL023）
---

# html-gen CLI 参考（子命令与脚本）

> 由 `AGENTS.md` 外移（HTML-GEN-CL023）：细则只在本文件维护，`AGENTS.md` 只留指针，两处不重复同一段文本。

## CLI 子命令

```shell
# doc — Markdown 转 B 型文档
html-gen doc -i report.md -o report.html [--title "标题"] [--subtitle "副标题"]

# slide — Markdown 转 D 型幻灯片
html-gen slide -i slides.md -o slides.html [--title "标题"]

# table — JSON 转 A 型数据表格
html-gen table -d data.json [--title "标题"] [--subtitle "段落描述"] [-o index.html]
#   -o 必填二选一: CLI -o <out.html> 或 JSON 顶层 "output" (优先级 CLI > JSON; 均无 → 提示中断 exit 1)
#   --title    优先级: CLI > JSON 顶层 title > "数据表格"
#   --subtitle 页面级段落描述(纯文本, \n 换行); JSON 顶层 subtitle 兜底, 显式传空串清空
#   --feedback-repo <owner/repo> GitHub Issue 反馈通道开关 (仅 table; 默认不注入, 显式空串禁用; env HTML_GEN_FEEDBACK_REPO; case 级配置 data JSON options.feedback)
# 四渲染子命令通用参数: --github-url <url> 右上角 GitHub corner (默认不带, 隐私) / --home-url <url> demo 首页入口 / --favicon <url> favicon 图标 (默认注入 DEFAULT_FAVICON, 显式空串禁用) / --quiet 仅打印路径
#   环境变量兜底: HTML_GEN_GITHUB_URL / HTML_GEN_HOME_URL / HTML_GEN_FAVICON (CLI 参数优先)

# knowledge — JSON 转 C 型知识库
html-gen knowledge -d data.json [-g groups.json] [--title "标题"] [--welcome "欢迎语"] [-o kb.html]
#   -o 必填二选一: CLI -o <out.html> 或 JSON 顶层 "output" (仅 data 文件识别; groups 文件不带)

# demo — 案例清单与详情（按模板分组 / --json / --all / --open / --rebuild）
html-gen demo list
html-gen demo drama-knowledge
html-gen demo --rebuild

# prompt — 项目 skills 输出
html-gen prompt <skill> [--brief] [--json]
html-gen prompt --site [--dir <path>]   # 生成 prompts/ 在线阅读站点 (31 文件; --site 与 skill/--brief/--json 互斥; 产物勿手改)

# help — 6 主题（doc/slide/table/knowledge/prompt/demo）
html-gen help demo
html-gen help table --json   # CL036: 机器可读契约 (checkpoint 信封 {status,data,error}; 含 template_stamps)

# table --strict — CL036: 未知配置键从「stderr 告警」升级为 exit 2（缺省仍宽松, 向后兼容）
html-gen table -d data.json -o out.html --strict   # 仅 3 类键: columns[].* / columns[].type / options.*(含 feedback)

# version — 版本 (CL016: {name} v{ver} ({date}); --version flag 兼容同格式)
html-gen version
```

### 批量渲染场景（CL003，2026-08-29）

table/knowledge 输出目标三态：CLI `-o` > JSON 顶层 `output` > 中断（exit 1 + 「未指定输出文件」提示）。批量循环两种写法：

```shell
# 方式一: 循环显式传 -o（推荐，数据文件无需改动）
for f in data/*.json; do
  html-gen table -d "$f" -o "out/$(basename "$f" .json).html"
done

# 方式二: 结构化 JSON 顶层带 "output": "out/xxx.html"，循环免 -o
for f in data/*.json; do html-gen table -d "$f"; done
```

注意：`data/_demos-data.json` 无 output 字段——**手工** `html-gen table -d data/_demos-data.json`（不带 -o）从「静默写 index.html」变为「中断提示」（预期行为变更，防覆盖错文件）；`html-gen demo --rebuild` 直调 cmd_table 已传 output，不受影响。doc/slide 不受影响（md 派生默认）。

### videos 同步脚本（CL002 / CL004）

`scripts/tool-table-videos-syncer.py`：yaml 增量 → json videos 补充（按 url 去重）+ yaml 全局镜像回写 + html 重建。

```shell
scripts/tool-table-videos-syncer.py                            # 缺省 yaml (cache/data/_countries-data.videos.yaml) + 预览(dry-run)
scripts/tool-table-videos-syncer.py <yaml> --dry-run           # 预览, 零写盘
scripts/tool-table-videos-syncer.py <yaml> --apply             # 执行写盘 (json → yaml 回写 → html 重建)
scripts/tool-table-videos-syncer.py <yaml> --empty-video       # 列出 videos 为空的行 (只读, 零写盘)
```

- `--dry-run` / `--apply` / `--empty-video` 三向互斥（argparse mutually exclusive group）
- yaml `target` 段扩展 `rebuild: {github_url, home_url, favicon}`：缺省用固定默认；`github_url` 优先级 rebuild 配置 > 旧产物 github-corner 提取 > 固定默认；任一键显式空串 = 禁用（不传该参数）
- `--apply` 重建时打印 `[执行]` 完整 html-gen 命令（含 `--github-url`/`--home-url`/`--favicon` 三参数）

### GitHub Issue 反馈通道（CL009，2026-09-10；v1.4 2026-09-11）

`scripts/countries-issue-sync.py` + `scripts/feedback-targets.yaml`：A 型表格分栏预览 header 的 ✏️ 按钮 → GitHub Issue Form（`.github/ISSUE_TEMPLATE/data-fix-countries.yml`，预填 page/dataset/row/row_en + 模板名；**字段由下拉选择**，不含主键/匹配键/视频列）→ 脚本按 target 白名单校验 → 写回 data JSON → 调 `html-gen.py table` 重建 → **自动提交两文件（本地，`--no-commit` 关闭）** → 回评（`--close` 追加关闭）。

```shell
python3 scripts/countries-issue-sync.py --list          # 列待处理 issue（每条附 --issue N --dry-run 引导行）
python3 scripts/countries-issue-sync.py                 # 预览（默认 --dry-run，零写盘）
python3 scripts/countries-issue-sync.py --apply         # 写回 JSON + 重建产物 + 自动提交 + 回评
python3 scripts/countries-issue-sync.py --apply --close # 追加关闭已处理 issue
python3 scripts/countries-issue-sync.py --apply --no-commit  # 只写盘重建，不自动提交
```

- 页面侧开关：`html-gen table --feedback-repo <owner/repo>`（table 专属；env `HTML_GEN_FEEDBACK_REPO`；CLI > env > JSON `options.feedback.repo`；均无 → 不渲染按钮）；表单模板名由 `options.feedback.template` 指定（M1，案例自描述）
- **v1.3 表单改版（issue #2 驱动）**：`字段` 改为下拉（`标签｜key`，15 项，不含主键/匹配键/视频列）+ 值改为 textarea；主键 `country_zh` 与匹配键 `country_en` 双层硬保护（config 误列也拦）
- 校验链：page / dataset / 字段解析（`标签｜key` → key；O1/K1）/ 主键硬保护（A1）/ `editable` 白名单 / 行唯一定位 / 类型（数值可解析）/ 非空 + 幂等 + 冲突取最新；`protected` + `key_guard` 合并拦截
- `--issue N --field KEY --value TEXT | --value-file PATH`：人工裁决入口（N1），如 issue #2 处置
- `--check-template`：校验模板 dropdown 选项 ↔ config `editable` / 数据列标签一致性（L1）
- **v1.4 自动提交**：`--apply` 默认 `git commit`（**显式 pathspec**：仅数据文件 + 产物；`--no-commit` 关闭；只 commit 不 push）；写盘前预检目标文件无未提交改动（脏则拒绝 exit 1）；提交消息 `data@<scope>: apply #N <字段> 更新 (HTML-GEN-CL009)`，scope 取 `commit.scope`；无变化不空提交；提交失败不回滚并 exit 1；回评带本地短 sha（待推送）
- `--list` 引导行：每条 issue 后附 `python3 scripts/countries-issue-sync.py --issue N --dry-run`（不进 `--json`）
- 重建参数固化在 `targets.<name>.rebuild.args`（含 `--github-url`/`--home-url`/`--favicon`/`--feedback-repo`），apply 时打印 `[执行]`
- 复用：新增案例只需追加一份 target（join key：countries=country_zh、provinces=province、drama=strategy/era）

## 三层架构

```
Layer 1: style-guide.css        CSS 变量 + 基础组件（按钮/表格/弹窗/分页）
Layer 2: layout-*.html          模板骨架（A 型表格 / B 型文档 / C 型知识库）
Layer 3: html-gen.py            CLI 生成器（doc / table / knowledge）
```

## 核心文件（逐项用途）

| 文件 | 用途 |
|:---|:---|
| `html-gen.py` | 主 CLI，8 个子命令，2079 行 |
| `scripts/company-report.py` | 公司调研报告生成器，从 schema JSON 生成完整 C 型知识库（groups/data/html + content/metrics 内容页自动生成 + 📰新闻动态组自动附加，数据源 data/_cloudwise-news.json） |
| `scripts/cloudwise-news-sync.py` | 云智慧公众号周报同步器：读 web2md 索引 → 增量更新 data/_cloudwise-news.json → 重建知识库 → commit（每周六 10:00 cron 驱动；--dry-run/--rebuild/--no-rebuild/--no-commit） |
| `scripts/cloudwise-fetch.py` | 云智慧公众号新文章处理入口：web2md <URL> 自动 step1 全文+step2 智读，--sync 可选立即入库 |
| `style-guide.css` | Layer 1 深色主题 CSS 基座，241 行 |
| `layout-doc.html` | B 型文档模板：侧边栏 TOC + 内容区 |
| `layout-table.html` | A 型表格模板：搜索 + 排序 + 分页 |
| `layout-knowledge.html` | C 型知识库模板：顶部标签栏 + 左侧章节 + iframe/内联内容 |
| `scripts/company-research-schema.json` | 公司调研 schema 定义（company/groups/items/output） |

## 项目独立性与跨项目只读依赖

本项目完全自包含，零外部依赖：
- 所有 Python import 仅使用标准库（json, re, sys, os, argparse, subprocess, pathlib, datetime）
- 模板和 CSS 通过 `Path(__file__).resolve().parent` 自定位，无需外部配置
- `company-report.py` 调用同目录的 `html-gen.py knowledge`，通过 subprocess 运行；items 含 `content`（正文 md）+ `metrics`（数据卡表格）时自动生成内容页（doc 产物）
- 内容页数据卡模式：schema items.metrics → 内容页顶部"核心数据"表格（6 卡对齐：成立/客户/产品/专利/融资/荣誉）
- 数据采集：`scripts/qcc-cloudwise.py`（企查查 selenium 采集，登录态 30s 手工窗口）
- 公众号动态管线（2026-09-01 上线）：人工发现新文章 → `scripts/cloudwise-fetch.py <URL> --sync --rebuild-kb` → web2md 处理 → 每周六 10:00 cron（cloudwise-news-weekly，deliver 飞书）自动同步 → 知识库「📰新闻动态」组；文章源为 web2md 索引（候选链：env `WEB2MD_INDEX` > `~/CodeSpace/script-miner/cache/web2md/web2md_index.json`（现行）> 旧 `~/Documents/10-DataDrived/web2md_index.json`（已空置）；script-miner 项目，只读不修改）
- 输出均为自包含单文件 HTML，无外部资源引用
