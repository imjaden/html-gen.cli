---
title: html-gen 测试治理细则
topic: html-gen
type: reference
version: 1.0
date: 2026-11-09
author: ops
source: AGENTS.md 外移（HTML-GEN-CL023）
---

# html-gen 测试治理细则

> 由 `AGENTS.md` 外移（HTML-GEN-CL023）：细则只在本文件维护，`AGENTS.md` 只留指针，两处不重复同一段文本。

## 测试治理

- Selenium 测试：headless Chrome，`localStorage.clear()` setUp，`window.__testErrors` 跟踪
- Chromedriver: `/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver`
- 测试文件命名：`tests/test_{feature}.py`，继承 `unittest.TestCase`
- 每个测试方法独立加载页面，`_errors()` 检查 JS 错误

> 用例计数与全量命令以 `AGENTS.md` 的「测试计数」子节为唯一权威（本节只写细则，不重复计数）。

- 组成：42 文件，共 99 subtests（下表为旧快照，缺 `test_table_default_state 10` / `test_split_span_empty 10` / `test_media_columns 14`；总计以 AGENTS.md「测试计数」为准）；test_issue_feedback 37 / test_help_contract 22 / test_sync_videos 21 / test_templates 18 / test_index_landing 18 / test_aliases 17 / test_drama_knowledge 16 / test_hermes_skills 15 / test_table_features 14 / test_json_output 14 / test_provinces_table 13 / test_prompt_site 13 / test_countries_table 13 / test_clipboard_fallback 12 / test_table_default_state 10 / test_demo_cmd 10 / test_the_price_you_choose_demo 8 / test_videos 8 / test_knowledge_sidebar 8 / test_doc_width 8 / test_word_count 7 / test_render_summary 7 / test_rebuild_refs 7 / test_history_tables 7 / test_doc_sidebar 7 / test_xss_escape 6 / test_url_state 6 / test_sticky_width 6 / test_prompt_cmd 6 / test_md_highlight 6 / test_heading_levels 6 / test_doc_bare 6 / test_demos_index 6 / test_corner_privacy 6 / test_initial_hidden_split 5 / test_knowledge_width 5 / test_split_detail 5 / test_cli_version 5 / test_slide_h3_toggle 4 / test_datetime_clickmode 3）
- **全量命令**（pytest-xdist 并行，见 pytest.ini `addopts = -n 4`）：
  ```bash
  python3 -m pytest tests/ -q -n 4     # 并行全量 (~55s)
  python3 -m pytest tests/ -q -n 0     # 单线程调试
  ```
- **等待机制约定**：
  - setUp 页面加载 wait 用 `WebDriverWait`（主元素：table `.data-table` / knowledge `.kw-tab` / doc `.doc-body` / slide `.slide-sidebar`）
  - 交互 wait 用调低后的固定 sleep（0.3/0.4/0.5/0.6/0.8/0.9 → 减半；0.08/0.1/0.15/0.2/0.25 不动）
  - sleep 调低用 `skills/test-speed-optimization/scripts/speedup_sleeps.py`（--dry-run/--apply/--restore）
- 依赖：`pytest-xdist>=3.8.0`（见 requirements-dev.txt）
