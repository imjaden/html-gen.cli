---
title: html-gen 目录结构与双源漂移
topic: html-gen
type: reference
version: 1.0
date: 2026-11-09
author: ops
source: AGENTS.md 外移（HTML-GEN-CL023）
---

# html-gen 目录结构与双源漂移

> 由 `AGENTS.md` 外移（HTML-GEN-CL023）：细则只在本文件维护，`AGENTS.md` 只留指针，两处不重复同一段文本。

## 目录结构

```
html-gen.cli/
├── index.html                 # 落地页（动态两屏 hero + 四模板网格 + 上箭头 A/B 返回首页 + 🌙☀️ 主题切换 + 📋 复制按钮 + footer）
├── html-gen.py                 # Layer 3 CLI 生成器
├── .github/ISSUE_TEMPLATE/      # data-fix-countries.yml（数据反馈表单）+ config.yml（关闭 blank issue）
├── scripts/                     # 脚本与 schema（company-report 生成器 / tool-table-videos-syncer.py videos 同步 /
│                                #   countries-issue-sync.py 反馈闭环 + feedback-targets.yaml 目标配置）
├── style-guide.css             # Layer 1 样式基座
├── layout-doc.html             # Layer 2 B 型文档模板
├── layout-table.html           # Layer 2 A 型表格模板
├── layout-knowledge.html       # Layer 2 C 型知识库模板

├── data/                       # 数据文件（*_data.json, *_groups.json, _cloudwise-news.json 公众号文章库,
│                                #   _aliases.json 根级短链配置, _*-kb-data.json 引用登记, _*-source.json 源件台账）
├── tests/                      # Selenium + 回归测试 (401 tests)
├── prompts/                    # prompt --site 生成物（在线阅读站点: index.html 合集 + {skill}.md/.json + all.md; 勿手改, 由 --site 重新生成）
├── skills/                    # 项目 skills prompt
    │   ├── html-gen/SKILL.md
    │   ├── html-gen-table/SKILL.md
    │   │   └── references/table-demo-prompt.md
    │   ├── html-gen-doc/SKILL.md
    │   ├── html-gen-knowledge/SKILL.md
    │   ├── github-issue-feedback/SKILL.md   # GitHub Issue 数据反馈闭环（跨页面 ✏️ + Issue Form + 配置 + 同步脚本; 跨项目复用）
    │   └── pages-index/SKILL.md   # pages index 落地页规范（hero+矩阵/主题/复制/两屏/corner/双源）
    └── demos/                      # 生成的 HTML 示例（独立案例根级扁平，URL=/demos/{name}.html）
    ├── index.html              # 模板展示首页
    ├── demos-index.html        # A 型文档索引（数据源 data/_demos-data.json）
    ├── usage-guide.html        # CLI 使用说明
    ├── table-guide.html        # A 型 · 数据表格方案
    ├── doc-guide.html          # B 型 · 文档阅读方案
    ├── markdown-spec.html      # Markdown 语法规范
    ├── knowledge-guide.html    # C 型 · 知识库方案
    ├── slide-guide.html        # D 型 · 幻灯片方案
    ├── slide-demo.html         # D 型 Slide 演示
    ├── hermes-profile-skills-list.html  # 主力 demo: Hermes Skills 列表
    ├── table-features-demo.html # 表格功能全演示（数据源 data/_table-features-demo.json）
    ├── table-actions-demo.html # 操作按钮 demo
    ├── knowledge-demo.html     # 知识库功能 demo
    ├── countries-table.html    # 全球 195 国速查表（数据源说明 countries-table.md）
    ├── provinces-table.html    # 中国 34 省速查表（数据源说明 provinces-table.md）
    ├── drama-knowledge.html    # 以剧读史影视历史知识库（中国历史 + 大明王朝1566）
    ├── chaitin-business-analysis.html  # 长亭科技商业分析知识库
    ├── cloudwise-business-analysis.html # 云智慧商业分析知识库
    ├── the-price-you-choose.html   # 人选天选论 · The Price You Choose（目录页；17 页正文在 demos/the-price-you-choose/；data/_the-price-you-choose-kb-data.json 引用登记 + …-source.json 源件 sha）
    ├── chaitin/                # 长亭内容子页（知识库引用）+ menu-design 菜单方案
    ├── cloudwise/              # 云智慧内容子页（知识库引用）
    ├── the-price-you-choose/   # 正文子页（chapter00..07 + highlights + 8 个旧 slug 跳转桩，均由 kb-data 标记 referenced）
    └── drama/                  # 以剧读史内容子页（知识库引用；时间轴 + 36计策，md 源 + html）

> **双源漂移（1C 决策，2026-08-23）**：根 `index.html`（落地页）与 `demos/index.html`（模板展示首页）为**两份独立副本**，非同一文件。改动落地页结构时需同步两处；`demos/index.html` 是 `html-gen demo --rebuild` 的 featured 数据源，根 index.html 不参与。github-corner 模式亦不同：layout 模板层（demo 页）用「pointer-events:none 穿透 + hit 36px」防遮挡右上角工具栏；根落地页无工具栏，用全图标可点 + hover 波浪动画（HG-SEC-014 文档化，2026-08-23）。两页共用主题按钮（right:88px 避让 corner，`html-gen:index_theme` localStorage key）与复制按钮/断点/footer；github-corner 浅色模式用深三角+白 octocat（`--gh-corner-fill`/`--gh-octocat` 变量，`:root.light .github-corner` 覆盖全局 a 链接色）；根页 hero 为**动态两屏**（JS: hero 高 = 视口高−55px，第二屏标题露出首屏底部；scroll-hint fixed 底部、滚动淡出），demos 页无 hero。**防漂移测试**：`tests/test_demos_index.py::test_05_dual_source_consistency` 断言双源关键功能特征一致（2026-08-24）。
```
