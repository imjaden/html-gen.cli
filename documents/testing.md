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

- 组成：45 文件，共 102 subtests（下表为旧快照，缺 `test_table_default_state 10` / `test_split_span_empty 10` / `test_media_columns 14` / `test_link_safety 5` / `test_split_grid 13` / `test_baseline_gate 9`（3 例为 CL029 返工新增）；总计以 AGENTS.md「测试计数」为准）；test_issue_feedback 37 / test_help_contract 22 / test_sync_videos 21 / test_templates 18 / test_index_landing 18 / test_aliases 17 / test_drama_knowledge 16 / test_hermes_skills 15 / test_table_features 14 / test_json_output 14 / test_provinces_table 13 / test_prompt_site 13 / test_countries_table 13 / test_clipboard_fallback 12 / test_table_default_state 10 / test_demo_cmd 10 / test_the_price_you_choose_demo 8 / test_videos 8 / test_knowledge_sidebar 8 / test_doc_width 8 / test_word_count 7 / test_render_summary 7 / test_rebuild_refs 7 / test_history_tables 7 / test_doc_sidebar 7 / test_xss_escape 6 / test_url_state 6 / test_sticky_width 6 / test_prompt_cmd 6 / test_md_highlight 6 / test_heading_levels 6 / test_doc_bare 6 / test_demos_index 6 / test_corner_privacy 6 / test_initial_hidden_split 5 / test_knowledge_width 5 / test_split_detail 5 / test_cli_version 5 / test_slide_h3_toggle 4 / test_datetime_clickmode 3）
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

## 渲染基线门禁（CL029，v1.2 = CL032 扩容）

`scripts/baseline.py`：对**可判定子集**（5 个模板/样式源含 `layout-slide.html` + 2 个手写落地页 + `demos-index` 就地重建 + 15 个可 verify 产物 = 23 项）钉 sha256+字节数，
基线文件 `data/_render-baseline.json` 随仓入库（`version: 2`，带 `verified` 标记）。

```bash
python3 scripts/baseline.py --check          # 0 一致 / 1 漂移 / 2 无基线 / 3 基线损坏
python3 scripts/baseline.py --check --json   # {"ok","total","mismatches"}（错误分支也带 total+error）
python3 scripts/baseline.py --verify         # 重渲比 sha：产物是否由当前模板产出
python3 scripts/baseline.py --update         # 重建基线（默认先 --verify；落后则拒，--force 越权并标 verified=false）
```

- **两道门**：`--check` 证「文件没被改过」；`--verify` 证「产物是当前模板产出的」。
  后者用**从产物回收的参数集**（title/subtitle/welcome/corner/home 全从产物解析）重渲到临时目录比 sha，
  脚本里不维护第二份参数副本 —— 参数漂移是 CL002 FIND-002 的老坑。
- **覆盖清单（v1.2）**：table 5（countries / provinces / table-features / table-actions / hermes-skills）+ slide 1（slide-guide）
  + doc 5（usage-guide / doc-guide / table-guide / knowledge-guide / markdown-spec，md 源走**同目录同名约定**
  `demos/<name>.html` ← `demos/<name>.md`）+ knowledge 4（knowledge-demo / drama-knowledge / chaitin / cloudwise，
  台账逐页登记 `产物 → (kb-data, groups)`）= **15 件判定 + `demos-index` 就地重建**。
- **SKIP 五项逐条带理由（禁静默漏过）**：`demos/demos-index.html`（就地重建型）/ `demos/index.html`（半手写落地页）/
  `index.html`（仓根手写）/ `demos/slide-demo.html`（无 .md 源，手工同步）/ `demos/the-price-you-choose.html`
  （生成后注入层 rx-patch，CLI 直渲 ≠ 产物）。新增页面若不进 `build_jobs` 也不进 `SKIP_PRODUCTS`，`test_08` 直接红。
- **为什么不许 `--force` 常态化**：产物落后于模板时重建基线，等于把「模板已前进、产物没重刷」的漂移一次性拍成绿
  （复审实测就是这种状态：countries/provinces/table-features/table-actions/hermes-skills/slide-guide 六个产物都落后）。
- 测试：`tests/test_baseline_gate.py` 9 例，全部在 `--root` 临时副本上跑（真仓零写入）：
  未改绿 / 改一字节红且只报该项（含 stderr 漂移提示断言）/ JSON 形状 / 缺文件 / 无基线 exit 2 /
  基线损坏 exit 3 / 产物落后时 `--update` 拒绝且 `--force` 标 `verified=false` / `--update` 复原 /
  **无页面漏网（jobs ∪ SKIP 覆盖 `demos/*.html`，子集 ⊇ 全部 jobs）/ doc·kb 作业带单源与回收标题**。
  子集项数由测试 import `baseline.SUBSET` 现取，不再写死常数。
