────────────────────────────────────────
验证 prompt — html-gen v2.2.0 底层修正 (D1-D6)
────────────────────────────────────────

对 html-gen 项目 ~/CodeSpace/html-gen 验证 datetime 排序 / clickMode 单数兼容 /
SKILL.md 文档同步 / features.md 同步 / Selenium 测试。

聚焦: documents/html-gen-fix-design-v1.0-20260806.md (commit 039f6c0)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D1 · datetime 排序 (layout-table.html L419-448)
  □ col.type === 'datetime' → var isDate = true (L421-422)
  □ 主键比较: isDate 分支 → Date.parse(va)||0, Date.parse(vb)||0 (L435)
  □ 二级排序: isDate2 同理 (L444)
  □ 空值/NaN 按 0 排序 (||0)
  □ SC1: 与 number 分支空值处理一致 (||0)

D2 · clickMode 单数兼容 (layout-table.html L1052-1060)
  □ 三级 fallback: clickModes → clickMode 包装 → ['tab'] (L1052-1054)
  □ 复数优先: 同时存在时 clickModes 优先, clickMode 被忽略
  □ 单数 auto-set: clickMode && !clickModes → 同步到全局变量 + localStorage (L1057-1059)
  □ SC2: 不破坏现有带 clickModes 的配置

D3 · SKILL.md → v2.2.0 (skills/html-gen-table/SKILL.md)
  □ 版本号: 2.1.0 → 2.2.0
  □ 列配置表: 新增 quickFilter、freeze 行
  □ 列类型详情: 新增 datetime(Date.parse 排序)、pills(逗号分隔标签)
  □ options 表: 新增 clickModes (兼容单数 clickMode)
  □ 变更记录段: "- v2.2.0 (2026-08-06): ..."
  □ SC3: 每项描述有模板实现对应

D4 · features.md 同步 (features.md)
  □ 行数统计: 1110 → 1436 (与实际一致)
  □ 排序描述: "locale/数字/字符串" → "locale/数字/日期/字符串"
  □ col.type: string/number/actions → string/number/datetime/pills/actions
  □ 新增属性行: stickyRight, quickFilter, onCellClick
  □ 新增功能行: Datetime 排序, 点击模式兼容单数
  □ SC4: 行数与实际一致

D5 · Selenium 测试 (tests/test_datetime_clickmode.py)
  □ test_01_datetime_ordering: 混排 + 非补零月 + 空值 → 排序正确, 空值首位
  □ test_02_clickmode_singular: clickMode:"split" → split 选中, 未静默忽略
  □ test_03_clickmodes_plural_priority: clickModes+clickMode 同时存在 → 复数优先
  □ 测试风格: 沿用 test_table_features.py (headless Chrome, __testErrors)
  □ localStorage.clear() 在页面加载后执行 (避免 about:blank 报错)

D6 · 测试回归
  □ 全量: 57 → 60 tests, 0 regression
  □ 运行: python3 -m pytest tests/ -q --tb=short

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
产出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 按治理规范逐项验证（实现是否与设计一致）
2. 报告验证结果（功能/测试/质量）
3. 若 PASS → 提示切换 review role 做实现审计

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
关键路径
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  layout-table.html: L419-448 (datetime), L1052-1060 (clickMode)
  skills/html-gen-table/SKILL.md: L2 (version), L66-78 (cols), L82-88 (types), L118-123 (options), L184-185 (changelog)
  features.md: L77 (line count), L80 (sort), L148 (types), L159-162 (new props), L87 (clickModes)
  tests/test_datetime_clickmode.py: 176 lines, 3 tests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
