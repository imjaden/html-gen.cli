────────────────────────────────────────
Review prompt — html-gen doc meta 显示 md 路径（show-md）
────────────────────────────────────────

对 html-gen 项目 ~/CodeSpace/html-gen 审查 doc meta 显示 md 源文件路径设计方案。

聚焦:
- documents/doc-meta-path-showmd-design-v1.0-20260819.md (commit 3f456d3)

背景:
- history-overview.html meta 区不展示 md 路径; cmd_doc 已计算 rel 但组装 meta 时丢弃
- 需求: meta 显示 md 路径, 默认隐藏(隐私), ?show-md=1 显示, 路径脱敏(仅文件名)
- 决策: 方案 A (生成端输出路径行 + 运行时 body class 显隐); show-md=1; basename 脱敏

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

M1 · 需求覆盖
  □ meta 输出路径行 (cmd_doc + cmd_slide 两处)
  □ 默认隐藏 (隐私) — CSS display:none
  □ ?show-md=1 显示 — body class 驱动 (与 sidebar/toolbar/width 同机制)
  □ 脱敏: os.path.basename() 仅文件名, 不含目录

M2 · 实现正确性
  □ html-gen.py meta 组装加 span.meta-path (doc L249 / slide L308)
  □ layout-doc.html CSS: .meta-path hidden + body.show-md 显示
  □ layout-doc.html JS: params.get('show-md')==='1' → add class (与 width 同处)
  □ 与 width 实现模式一致性 (URLSearchParams → body class → CSS)

M3 · 脱敏与隐私
  □ basename 脱敏正确 (无完整路径泄露)
  □ HTML 源码仅含文件名, 不泄露目录结构
  □ layout-knowledge iframe 不自动追加 show-md (默认隐私)

M4 · 标题点击复制逻辑
  □ 模板 L306-311 match(/路径:\s*(.+)/) 恢复命中, 复制脱敏文件名
  □ 行为变化 (URL fallback → 复制文件名) 合理且已声明

M5 · slide 处理
  □ slide meta 同步输出路径行 (生成端统一)
  □ slide 无 URL 解析机制, 不做运行时显隐的决策合理

M6 · 测试设计
  □ 回归: meta 含 路径: 且为文件名 (无 /)
  □ Selenium: show-md=1 → inline / 无参 → none / 标题点击复制文件名
  □ 0 JS errors

M7 · 影响面
  □ 仅 html-gen.py + layout-doc.html (+ 重新生成 demos)
  □ features.md B 型 URL 入参节补 show-md
  □ 待确认项 (slide 运行时显隐 / 测试文件命名) 合理

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
产出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 按治理规范逐项审查
2. 报告审查结果 (PASS / CONDITIONAL PASS / REJECT + 评分 + 修改意见编号)
3. 若 PASS → 提示切 dev role 实现
