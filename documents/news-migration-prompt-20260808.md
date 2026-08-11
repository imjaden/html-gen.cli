---
title: 资讯迁移 prompt — html-gen demos
topic: html-gen
type: prompt
version: 1.0
date: 2026-08-08
tags: [html-gen, demos, migration, prompt]
---

# 资讯迁移 prompt

> 用途: 在其他 session 探讨/收集资讯后，将数据落地为 html-gen 的 demos 专题。
> 设计依据: documents/demos-news-migration-design-v1.0-20260808.md

────────────────────────────────────────
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
────────────────────────────────────────
