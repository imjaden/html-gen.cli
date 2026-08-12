────────────────────────────────────────
验证 prompt — quickFilter 默认关 & 第1列默认分栏
────────────────────────────────────────

对 html-gen 项目 ~/CodeSpace/html-gen 验证 quickFilter 默认关 (D1) / pillFilter 显式声明 (D2) / 第1列默认分栏 (D3) 实现。

聚焦:
- documents/solutions/table-quickfilter-default-design-v1.0-20260806.md (设计方案)
- documents/review/table-quickfilter-default-review-v1.0-20260808.md (审计报告, PASS 100/A)
- 本 session commit: 65c32c1 (dev 实现)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D1 · quickFilter 默认关
  □ layout-table.html L525: col.quickFilter !== false → col.quickFilter === true
  □ 注释: "quickFilter 默认关: col.quickFilter === true 才启用单元格点击筛选"
  □ 未配 quickFilter:true 的列点击 → 无 quickFilterBy 调用
  □ test_06b Selenium 验证: name 列(无 quickFilter) → 打开 split, 非 filter pill

D2 · pillFilter 默认开 + 显式声明
  □ layout-table.html L501: pillFilter !== false 逻辑不变 (默认开)
  □ 注释: "pillFilter 默认开: 标签点击筛选, pillFilter: false 可关闭"
  □ data/_skills-table-config.json: category + profiles 列加 "pillFilter": true
  □ data/_countries-data.json: region_tags 列加 "pillFilter": true

D3 · 第1列默认分栏
  □ layout-table.html L481: var firstKeyCol = cols.find(c => c.type !== 'actions')
  □ L527-530: col === firstKeyCol → openSplitAt(rowIdx)
  □ 优先级: onCellClick='split' > quickFilter === true > firstKeyCol > 无 onclick
  □ test_06b Selenium 验证: name 列点击 → wrapper.split-mode 激活

D5 · phase2-demo 数据适配
  □ data/_phase2-demo.json: stars 列加 "quickFilter": true
  □ test_06 Selenium 验证: stars 列(quickFilter:true) → filter pill 出现

D6 · Demo 重新生成 (6 个)
  □ demos/drama/daming-timeline-table.html
  □ demos/drama/daming-strategy-table.html
  □ demos/drama/history-strategy-table.html
  □ demos/hermes-profile-skills-list.html
  □ demos/phase2-demo.html
  □ demos/countries/countries-table.html

D7 · 文档同步
  □ features.md: "默认关, col.quickFilter:true 启用" + "pillFilter:false 关闭"
  □ AGENTS.md: col.quickFilter 说明更新 + 补 pillFilter

Step7 · 测试
  □ test_06: stars 列(quickFilter:true) → filter pill (适配新默认)
  □ test_06b: name 列(无 quickFilter) → split 打开 (D1+D3)
  □ select_click_mode JS close 替代 body.click (避免 clickMode=modal 时误触)
  □ 全量: 73 → 84 tests, 0 regression (84/84 PASS)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
产出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 按治理规范逐项验证（实现是否与设计一致）
2. 报告验证结果（功能/测试/质量）
3. 若 PASS → 提示切 review role 做最终审计

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
关键路径
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  layout-table.html:L525       quickFilter 默认关 (=== true)
  layout-table.html:L481       firstKeyCol 计算
  layout-table.html:L527-530   onclick 优先级链
  layout-table.html:L501       pillFilter 注释
  data/_skills-table-config.json   pillFilter:true
  data/_phase2-demo.json           quickFilter:true
  tests/test_table_features.py     test_06 + test_06b
────────────────────────────────────────
