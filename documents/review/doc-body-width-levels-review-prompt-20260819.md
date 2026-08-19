────────────────────────────────────────
Review prompt — html-gen doc-body 三级宽度支持
────────────────────────────────────────

对 html-gen 项目 ~/CodeSpace/html-gen 审查 doc-body 三级宽度（URL 入参）设计方案。

聚焦:
- documents/doc-body-width-levels-design-v1.0-20260819.md (commit 11d2d84)

背景:
- demos/drama/history-overview.html 在 ?sidebar=0（知识库 iframe 嵌入）时正文仍锁
  max-width:960px，宽屏下右侧留白过大
- 需求: URL 入参 ?width=narrow|medium|wide 切换正文宽度，默认 medium=960px
- 决策: 纯 URL 驱动不持久化; body class 方案（与 show-sidebar/show-toolbar 一致）;
  narrow=720px / medium=960px / wide=1280px

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

W1 · 需求覆盖
  □ 3 级宽度 (narrow/medium/wide) 定义合理
  □ 默认 medium=960px 与现状一致 (向后兼容)
  □ 不持久化: 纯 URL 驱动, 无 localStorage

W2 · 实现正确性
  □ body class 方案与现有 show-sidebar/show-toolbar 模式一致 (L243-245)
  □ CSS: body.width-narrow/.width-wide 选择器正确覆盖 .doc-body max-width
  □ JS: URLSearchParams 解析 width, 与 sidebar/toolbar 同处 (L245 后)
  □ 移动端 @media (max-width:768px) 兼容性 (padding 覆盖, max-width 自然失效)

W3 · 取值与语义
  □ 参数名 width 无冲突 (页面无同名参数)
  □ narrow/medium/wide 语义清晰, 不引入 s/m/l 歧义
  □ wide=1280px 而非 max-width:none 的理由成立 (避免无限拉伸)

W4 · 测试设计
  □ 回归: 默认/narrow/wide 三态 max-width 断言
  □ Selenium: 计算样式 + 0 JS errors + 组合参数 (sidebar=0&width=wide)
  □ 不持久化断言 (localStorage 无写入)

W5 · 影响面
  □ 仅 layout-doc.html 模板改动 (CSS 2 条 + JS 3 行)
  □ 已生成页面需重新生成才能生效 (demos/drama/*.html)
  □ 文档同步: features.md B 型条目

W6 · 风险
  □ 纯增量, 无参数行为不变
  □ wide 1280+padding 160=1440px 与 doc-main 关系合理

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
产出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 按治理规范逐项审查 (设计是否完备、与项目约定一致)
2. 报告审查结果 (PASS / CONDITIONAL PASS / REJECT + 评分 + 修改意见编号)
3. 若 PASS → 提示切 dev role 实现
