  ────────────────────────────────────────
验证 prompt — html-gen 文档模板修正 & 知识库表格化
────────────────────────────────────────

对 html-gen 项目 ~/CodeSpace/html-gen 验证 D1-D9 文档模板修正 + drama 知识库表格化改造。

聚焦:
- documents/html-gen-doc-fix-design-v1.0-20260806.md (commit 5520c71)
- documents/drama-kb-table-design-v1.0-20260806.md
- documents/review/drama-kb-table-review-v1.0-20260806.md (CONDITIONAL PASS, 90/A)
- 本 session commit 记录: 09903e0 (D1-D9) + 5595f42 (drama)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项 — 文档模板修正 (D1-D9)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D1 · Sidebar sticky (layout-doc.html L21)
  □ .doc-sidebar { position: relative; } 已删除
  □ L11-17 的 position: sticky 保留
  □ .doc-sidebar.open { position: fixed } (mobile) 不受影响

D2 · Sidebar sticky (layout-slide.html L35)
  □ .slide-sidebar { position: relative; } 已删除
  □ position: sticky 定义保留

D3 · strip_frontmatter() (html-gen.py L168-175)
  □ 函数签名: strip_frontmatter(text) → (body, frontmatter)
  □ --- 开头的 YAML 块正确剥离
  □ 无 frontmatter 时直通 (fm='', body=text)
  □ 单行 --- 不误剥离 (正则 ^---\n.*?\n--- 要求闭合)

D4 · cmd_doc 接线 (html-gen.py L201-210)
  □ text, fm = strip_frontmatter(text) 调用
  □ title 优先级: --title > fm title > body # > stem
  □ content = md_to_html(text) 基于剥离后 text
  □ h1 提取: 剥离后 content.startswith('<h1') 重新匹配

D5 · cmd_slide 接线 (html-gen.py L261-270)
  □ 同样 frontmatter 剥离 + title 优先级
  □ 封面 h1_html 正确 (frontmatter 剥离后提取)

D6 · 测试 (tests/test_templates.py)
  □ test_doc_frontmatter_stripped: FM→body, title=<title>, 无泄漏
  □ test_slide_frontmatter_stripped: FM→body, 无 YAML 泄漏
  □ test_doc_no_frontmatter_regression: 无 FM 的 md 正常
  □ test_sidebar_sticky: Selenium scrollTo 后 sidebar 可见, 0 JS errors

D7 · SKILL.md → 2.3.0 (skills/html-gen/SKILL.md)
  □ version: 2.3.0
  □ doc 命令说明含 "自动剥离 YAML frontmatter"
  □ 变更记录: v2.3.0 (2026-08-06)

D8 · features.md 同步
  □ CLI doc 行: "frontmatter 自动剥离"
  □ 侧边栏: "sticky 修复"
  □ 行数统计与实际一致

D9 · 测试回归
  □ 全量: 60→64 tests, 0 regression
  □ pytest tests/ -q --tb=short

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项 — drama 知识库表格化 (K1-K3, T1-T4, D2-1, D3-D5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

K1 · selectItem 双参数 (layout-knowledge.html)
  □ window.selectItem = function(group, title) 签名
  □ ITEMS.find 改为 (i.group === group && i.title === title)
  □ switchGroup: selectItem(activeGroup, firstItem.title)
  □ renderSidebar onclick: selectItem(group, title) 双参
  □ localStorage 恢复: selectItem(savedGroup, savedItem)

K2 · section 一级菜单 (layout-knowledge.html)
  □ section 标题 onClick: selectSection(group, sec)
  □ window.selectSection 函数: 查找匹配 item → call selectItem
  □ 单条目 section (title===sec, count===1): 跳过 kw-item 行
  □ CSS: cursor: pointer, hover color, active color

K2-1 · 剧中设定标注 (D2-1)
  □ T2 剧情节点: 改稻为桑/毁堤淹田 source="剧中设定"
  □ T2 剧情节点: 海瑞赴任淳安 source="史实"
  □ T4 大明计谋: 李代桃僵/将计就计 source="剧中设定"
  □ T3 千古名计: 七擒孟获 source="史载有争议" (与空城计"演义"对称)

K2-2 · 列定义 JSON (D2-2)
  □ T1-T4 各表含完整 columns/tabs/options 结构化 JSON
  □ T2 大明时间轴: tabs=[年号总览, 剧情节点]

D3 · 6 个内容页
  □ history-timeline-table.html / daming-timeline-table.html
  □ history-strategy-table.html / daming-strategy-table.html
  □ history-overview.html / daming-overview.html

D4 · _drama-kb-data.json
  □ 6 条数据, 2 组 (中国历史 3 + 大明王朝1566 3)
  □ title === section (单条目 per section)
  □ url 指向对应内容页

D5 · drama-knowledge.html
  □ 知识库页面生成, 2 个 tab, 每组 3 个 section
  □ section 点击 → iframe 加载对应 URL

D6 · Selenium 测试 (tests/test_drama_knowledge.py)
  □ test_01: 2 tabs 顺序
  □ test_02: 3 sections, 0 kw-item rows
  □ test_03-05: section 点击 → iframe src 正确
  □ test_06: 「概述」跨组不串 (K1 dual-param)
  □ test_07: 刷新恢复 group+section
  □ test_08: iframe 内表格 tabs 渲染
  □ test_09: 0 JS errors

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
产出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 按治理规范逐项验证（实现是否与设计与审计一致）
2. 报告验证结果（功能/测试/质量）
3. 若 PASS → 提示切 ops role 做实现验证

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
关键路径
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  D1-D9:
    layout-doc.html:L21            sticky override 删除
    layout-slide.html:L35          sticky override 删除
    html-gen.py:L168-175           strip_frontmatter()
    html-gen.py:L201-210           cmd_doc 接线
    html-gen.py:L261-270           cmd_slide 接线
    tests/test_templates.py        TestDocSlideFrontmatter (4 tests)
    skills/html-gen/SKILL.md       v2.3.0

  Drama:
    layout-knowledge.html:L328     selectItem(group, title)
    layout-knowledge.html:L314     section onclick + selectSection
    layout-knowledge.html:L38-41   CSS cursor/hover/active
    data/_drama-table-*.json       4 table JSONs (+ D2-1/D2-2)
    data/_drama-kb-data.json       6 items (2 groups × 3 sections)
    demos/drama/                   6 generated pages + 2 overview MDs
    tests/test_drama_knowledge.py  9 Selenium tests (section-as-menu)

  全量: pytest tests/ -q → 73 passed
