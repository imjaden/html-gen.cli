# demos 资讯整合目录体系 + 迁移 prompt — 设计文档

## 版本

v1.0 (2026-08-08)

## 背景与问题来源

用户有临时资讯整合需求：在其他 session 中探讨/收集资讯后，用 html-gen 模板（A 表格 / B 文档 / C 知识库）展示，复用 `demos/` 目录。需要：

1. 一套清晰的 demos 目录体系（资讯类专题与现有模板 demo 隔离）
2. 一段可复用的迁移 prompt：把其他 session 探讨的资讯数据落地为本项目 data + 生成 html + 登记索引

待确认清单问答（用户回复 1A 2A 3A 4A）定稿：

| 项 | 确认 |
|:--|:--|
| 1 资讯数据形态 | A=按 html-gen demo prompt 生成数据及 html |
| 2 模板偏好 | A=单一信息罗列→A 表格；资讯整合展示→B 文档；多维度资讯整合→C 知识库 |
| 3 索引更新 | A=每次迁移都更新 demos-index.html |
| 4 生命周期 | A=README 标注日期，不需要过期自动清理机制 |

## 目标形态

**现状**：
- demos/ 根目录：单文件 demo（index.html 模板展示首页、skills 列表、guide 文档 html+md 成对）
- 子目录：chaitin/（公司分析专题）、drama/（知识库专题）
- 索引：demos-index.html（A 型表格，由 data/_demos-data.json 驱动）+ index.html（模板展示首页）
- 数据：data/_<topic>-*.json（下划线前缀 = 中间产物）

**目标**：
- 资讯类专题统一落入 `demos/<topic>/` 子目录，与根目录模板 demo 隔离
- 每个专题一套数据（data/_<topic>-*.json）+ 生成 html + README（日期/来源）
- 迁移流程可重复执行：其他 session 探讨 → 用迁移 prompt → 生成 + 登记
- 每次迁移更新 demos-index.html（_demos-data.json 追加一行 + 重新生成）

## 一、demos 目录体系

### 目录约定

```
demos/
├── index.html                # 模板展示首页（保持不变）
├── demos-index.html          # A 型索引（资讯类登记在此）
├── <topic>/                  # 资讯专题，小写 kebab-case
│   ├── <topic>-table.html    # A 型表格（单一信息罗列）
│   ├── <topic>-doc.html      # B 型文档（资讯整合展示）
│   ├── <topic>-knowledge.html# C 型知识库（多维度资讯整合）
│   ├── *.md                  # 源数据/草稿（可选）
│   └── README.md             # 专题说明：来源 session、日期、生命周期
data/
├── _<topic>-data.json        # table 数据
├── _<topic>-kb-data.json     # knowledge 数据
└── _<topic>-groups.json      # knowledge groups
```

### 命名规范

- 子目录：小写 kebab-case 主题名（tech-news / ai-roundup / dev-tools）
- 生成 html：`<topic>-<模板类型>.html`（table / doc / knowledge）
- 数据：`data/_<topic>-*.json`（沿用下划线前缀 = 中间产物约定）
- 版本化文档（可选）：`<topic>-<type>-vX.Y-YYYYMMDD.html` + `.md` 成对（现有 guide 风格）

### 模板选择规则

| 场景 | 模板 | CLI |
|:--|:--|:--|
| 单一信息罗列（清单/速览/链接集） | A 表格 | `html-gen table -d data/_<topic>-data.json` |
| 资讯整合展示（长文/分析/报告） | B 文档 | `html-gen doc -i <topic>.md` |
| 多维度资讯整合（分类/多组/嵌套） | C 知识库 | `html-gen knowledge -d data/_<topic>-kb-data.json -g data/_<topic>-groups.json` |

### 生命周期

- README.md 必含：来源 session、创建日期、主题说明
- 不需要过期自动清理机制；临时资讯保留在 demos/<topic>/ 由用户手动归档/删除
- 删除时：删子目录 + 删 data 文件 + 从 _demos-data.json 移除行 + 重新生成 demos-index.html

## 二、迁移 prompt

以下 prompt 供用户在**其他 session** 使用，或本 session 按需调用。输入为资讯主题 + 探讨记录/数据，输出为 html-gen 数据文件 + 生成的 html + 索引登记。

---

```
# 任务
你是 html-gen 项目的资讯迁移执行者。将用户提供的资讯内容转换为 html-gen 数据文件，
生成 demo 页面，并登记索引。工作目录 /Users/jadenli/CodeSpace/html-gen。

# 步骤

## 1. 输入
- 资讯主题 <topic>（小写 kebab-case，如 ai-roundup）
- 资讯条目：标题/来源/日期/摘要/链接/分类（或探讨 session 的原始记录）
- 模板偏好（未指定时按规则自选）：
  - 单一信息罗列 → A 表格
  - 资讯整合展示（长文/报告） → B 文档
  - 多维度资讯整合（多组/嵌套分类） → C 知识库

## 2. 产出数据文件（data/ 目录）
- A 型：data/_<topic>-data.json
  简单格式（JSON 数组）或结构化格式（columns + data + options）
  链接列用 type:"actions" + hrefKey，或 col.onClick:"url" 整行跳转
- C 型：data/_<topic>-kb-data.json（title/group/section/desc|url）+ data/_<topic>-groups.json
  title 必填、group 必填（对应顶部 Tab）、section 可选（侧栏分组）
- B 型：demos/<topic>/<topic>-doc.md（markdown 源）

## 3. 生成页面（输出到 demos/<topic>/）
- A 型: html-gen table -d data/_<topic>-data.json --title "..." -o demos/<topic>/<topic>-table.html
- B 型: html-gen doc -i demos/<topic>/<topic>-doc.md --title "..." -o demos/<topic>/<topic>-doc.html
- C 型: html-gen knowledge -d data/_<topic>-kb-data.json -g data/_<topic>-groups.json \
        --title "..." -o demos/<topic>/<topic>-knowledge.html

## 4. 登记索引
- data/_demos-data.json 追加一行：{"类型": "...", "文件": "<a href=...>", "说明": "...", "大小": "..."}
- 重新生成 demos-index.html（已验证命令）：
  html-gen table -d data/_demos-data.json --title "Demos Index" -o demos/demos-index.html
- 可选：长期保留专题在 demos/index.html 案例区加 demo-item 链接（不强制）

## 5. 写入 README.md（demos/<topic>/README.md）
  包含: 主题、创建日期、来源 session（如 @session:<profile>/<id>）、内容概述、模板类型

## 6. 验证
- 打开生成的 html 确认可正常展示、无 JS 错误
- 中文内容排序/搜索正常（column locale:"zh"）
- 链接列跳转正确

## 7. 收尾
- git add 相关文件 + git commit（治理规范: docs@html-gen 或 add@html-gen 前缀，subject 英文）
- 不 push（非 review profile）

# 约束
- 只使用 html-gen.py CLI 与 Python 标准库
- 数据文件字段名中文/英文均可，列名从首条 key 推导
- 不修改 default profile 配置；不读 .env/凭据文件
- 删除/覆盖任何现有文件前先确认
```

---

## 落地清单（本设计实施时）

1. 本设计文档 commit（docs@html-gen）
2. 将迁移 prompt 保存为 `documents/news-migration-prompt-20260808.md`（或 skills/ 内模板）
3. 首次试运行一个示例专题验证流程（可选，用户指定主题后执行）
4. demos-index.html 生成方式确认（_demos-data.json 的驱动命令）

## 待确认

- 迁移 prompt 存放位置：documents/ 独立文件 vs skill（如 script-miner 的 html-gen 子指令组）
- 是否需要首个小示例专题试跑
