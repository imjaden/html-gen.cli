# 表格文本列 XSS 转义 — ops 独立核查 v1.0

> 日期: 2026-09-17
> 闭环: HTML-GEN-CL010（HG-SEC-134）
> 设计: `documents/solutions/table-text-xss-escape-design-v1.0-20260911.md`（决策 A2+B1+C1+D1+E1+F2）
> 实现: `5f447fc`（`feat@table: default HTML escape for text cells`，已在 github/main）
> 口径: 不采信 dev 自报，全部由 ops 独立实测（CLI + 浏览器 + 全量回归 + 产物比对）

## 0. 结论

**PASS** — 设计 §2 六项决策（A2/B1/C1/D1/E1/F2）与 §5 测试计划逐项落地且可复核；
四渲染路径默认转义有效，HTML 依赖列零回归，产物重建幂等，全量 312 passed、工作区零残留。
非阻断说明 2 项（见 §7）。

## 1. OV-1 默认转义（静态）

`layout-table.html` 主单元格渲染分支顺序正确 —— **豁免先于默认转义**：

```
588:  else if (col.escape === false) { /* 显式豁免: raw HTML（如 <a> 链接列） */ }
590:  else val = escapeHtml(String(val));  // HG-SEC-134: 默认转义，防止 stored XSS
```

判定: 语义与设计 A2 一致（默认转义；仅显式 `escape: false` 放行）。✅

## 2. OV-2 HTML 列豁免（静态）

- 数据侧: `data/_demos-data.json:28` 「文档链接」列 `"escape": false` ✅
- 生成器侧: `html-gen.py` cmd_demo 的 `idx_columns` 同列补 `'escape': False`（5f447fc 内 1 行）✅
- 设计 D1（列级豁免）无遗漏面。

## 3. OV-3 四路径运行时转义（真实浏览器）

```
pytest tests/test_xss_escape.py -q -n 0  →  6 passed in 3.56s
```

覆盖: 主表格单元格（test_01）/ HTML 链接列不转义（test_02）/ 无 JS 错误（test_03）/
分栏预览（test_04）/ 弹窗（test_05）/ 行内展开（test_06）；载荷 `<img src=x onerror=alert(1)>`。
chromedriver = `/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver`（实存）。✅

## 4. OV-4 全量回归与工作区

```
pytest tests/ -q -n 0  →  312 passed in 130.60s
```

运行前后 `git status --short` diff = 空 → 测试零残留。✅

## 5. OV-5 产物一致性与数据面

- `data/_countries-data.json`: 195 行；text 字段含 `<`/`>` = **0 处** → 转义后视觉零变化（设计 §4 论断成立）。
- 重建幂等: 按 `scripts/feedback-targets.yaml` 的 `rebuild.args` 复跑
  （`--github-url/--home-url/--favicon/--feedback-repo`）→ `diff` 与入库 `demos/countries-table.html` **字节一致**。✅

## 6. OV-6 变更面核对（5f447fc）

```
AGENTS.md(2) data/_demos-data.json(3) demos/countries-table.html(3) demos/demos-index.html(5)
documents/solutions/table-text-xss-escape-design-v1.0-20260911.md(118)
features.md(2) html-gen.py(2) layout-table.html(3) scripts/countries-issue-sync.py(4)
tests/test_xss_escape.py(148)
```

- 入库防护（C1）实测在位: `scripts/countries-issue-sync.py` `plan_issues()` 内
  `if '<' in new or '>' in new: skips.append(...); continue`（字符串字段，含 `--value` 路径）。✅
- 无新增依赖、无新增外部资源、无凭证面变化。

## 7. 非阻断说明

| # | 项 | 说明 |
|:--|:--|:--|
| N-1 | 设计评审未单独执行 | CL010 的设计随实现同一 commit（`5f447fc`）落地，无 `docs@design` 独立提交、无设计评审报告；已转由本轮**实现审计**覆盖设计决策 A2/B1/C1/D1/E1/F2 的落地复核 |
| N-2 | 历史步骤 JSON 缺 | `cache/closed-loop` 无 CL010 步骤 JSON；`hm loop sync` 已从 commit 补齐 `dev 实施` 步，其余步骤由本次闭环补记 |

## 8. 复跑指令（含预期）

```bash
pytest tests/test_xss_escape.py -q -n 0        # expect 6 passed
pytest tests/ -q -n 0                          # expect 312 passed
grep -n "escape === false\|默认转义" layout-table.html   # expect L588/L590
python3 -c "import json;d=json.load(open('data/_countries-data.json'));r=d['data'] if isinstance(d,dict) else d;print(len(r), sum(1 for x in r for v in x.values() if isinstance(v,str) and ('<' in v or '>' in v)))"   # expect 195 0
```
