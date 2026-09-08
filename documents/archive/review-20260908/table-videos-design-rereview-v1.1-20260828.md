# A 型表格 videos 视频字段设计 — 复审报告 v1.1

> 日期: 2026-08-28
> 文件: `documents/solutions/table-videos-design-v1.1-20260828.md`（git mv 自 v1.0，保留历史）
> 项目路径: ~/CodeSpace/html-gen.cli
> 初审: `d02cfc5` review@html-gen: table videos design v1.0 audit — CONDITIONAL PASS 85/B（HG-SEC-043..045 open，046..052 OBS）
> 复审 commit: `99cede3` docs@table: videos design v1.1 — RIG-001..003 fix (HG-SEC-043..045) + OBS spec + drift assertion sync (HTML-GEN-CL001)，1 文件 rename +35/-14
> review维度: 合理性 / 严格性 / 安全性 / 治理规范（git mv 历史 / commit 规范 / 漂移断言真实性）
> review者: Security Reviewer (L2, design-document-review)

## 裁决

**PASS — 95/100 (A) — 闭环，转 dev 实施**

初审 3 项 🟡（HG-SEC-043..045）全部按 RIG-001..003 闭合，7 项 🟢（046..052）全部规格落地，3 个数据漂移断言同步方案经实跑核实为真。复审仅发现 1 项新增 🟡 N1（§8 验收清单第 7 条用例数 6→8 未随 §7 同步，纯文档文本陈旧，不影响实施路径），有明确修复路径（dev prompt 已内嵌），不阻断闭环。

## 一、复审核对表（对照初审 RIG/🟢 逐项核验）

| # | v1.0 初审项 | 状态 | v1.1 证据 |
|:--|:-------------|:----:|:---------|
| RIG-001 (HG-SEC-043) | §5 split/expand 明确 Array.isArray(v) 特判，勿 String(v)；§7 补 test_07 | ✅ | §5 L73-76「分栏预览（split）与行内展开（expand）：videos 列 `Array.isArray(v)` 特判（勿用 String(v) 否则 [object Object]）：逐条渲染 [平台图标] title (duration) + url 链接；splitFull 整行宽 / 非 splitFull 普通 kv-item」；§7 test_07 L100「split 预览 videos 渲染：分栏预览中出现视频标题文本，非 [object Object]」（HG-SEC-043/049 双闭环） |
| RIG-002 (HG-SEC-044) | §5 平台映射含归一化 trim().toLowerCase() + 别名表 | ✅ | §5 L64-68：归一化 `String(platform).trim().toLowerCase()`；映射 douyin/抖音→🎵、bilibili/B站/b站→📺、youtube/YouTube→▶️、其他→📹；别名经归一化后命中（抖音→🎵、b站→📺），语义等价 RIG-002 别名表 {抖音→douyin, b站→bilibili, youtube→youtube}；test_04 覆盖大小写/别名归一化 |
| RIG-003 (HG-SEC-045) | §5/§9 定义 .video-pill 独立类 | ✅ | §5 L69-71：`.video-pill`：`max-width:180px; white-space:normal; word-break:break-all;`，声明不与 .cell-pill nowrap 冲突；§9 L123 同步「maxShow 控制行高，超长 title 多行内截断」 |
| HG-SEC-046 | +N 状态机（折叠回？re-render？stopPropagation） | ✅ | §5 L61：「点击展开全部（DOM 追加剩余 pill），不折叠回；跨 re-render 重置（回到 maxShow 折叠态）；点击 stopPropagation 防触发行点击」 |
| HG-SEC-047 | onclick 转义机制 | ✅ | §5 L60：沿用 actions 先例 `JSON.stringify(url).replace(/\"/g,'&quot;')` |
| HG-SEC-048 | col.videos 与 row.videos 键名混淆说明 | ✅ | §9 L125：列配置/行数据两套命名空间，规格已明确 |
| HG-SEC-049 | split 预览 videos 测试缺失 | ✅ | §7 test_07（随 RIG-001 一并闭合） |
| HG-SEC-050 | 跑法改回 -n 4 | ✅ | §7 L105：全量 `python3 -m pytest tests/ -q -n 4`（若环境并发卡死则分三组兜底） |
| HG-SEC-051 | title 必填约定 | ✅ | §5 L58：「title 与 platform 均缺省 → [📹] (duration)（数据质量约定：title 建议必填）」 |
| HG-SEC-052 | 默认搜索排除 videos | ✅ | §7 test_08 L101「搜索词命中 title 不应筛出该行」；§9 L124「videos 不加入默认搜索字段；无 searchFields 的表默认搜索也排除」 |

### 数据漂移断言同步方案（134e3c6，实跑核实）

| 测试 | v1.1 修复方案 | 实跑核实（python3.12 -m pytest，3 failed 复现） |
|:-----|:-------------|:-----------------------------------------------|
| test_countries_table.py::test_01_region_pills_dundun_split | 期望改 ['欧洲','南欧','前南斯拉夫']（3 值） | ✅ 实际 pills = ['欧洲','南欧','前南斯拉夫']（L76 断言 2 值 FAIL，diff 精确一致）；数据源 _countries-data.json 塞尔维亚 region_tags='欧洲、南欧、前南斯拉夫' |
| test_history_tables.py::test_01_strategy_headers_and_index | 期望改 7 列 ['序号','计名','分类','别名','衍生成语','兵法','人物'] + tds[7]→tds[5] | ✅ 实际表头 = ['序号','计名','分类','别名','衍生成语','兵法','人物']（L61 断言 9 列旧表头 FAIL，diff 精确一致）；COLUMNS 10 列中 detail/source/event/outcome 4 列 initialHidden:true → 默认可见 6 列 + 序号 = 7；兵法(battle) 位于 index 5 → tds[7]→tds[5] 推导正确；首行 battle 含「备周则意怠」已核实 |
| test_table_features.py::test_12_description_empty_hidden | 改用 data/_countries-data.json（无 subtitle） | ✅ 现 history-strategy JSON 顶层 subtitle=《孙子兵法》描述（L295 desc.text 非空 FAIL）；_countries-data.json 顶层 subtitle=None、title='全球国家速查表（195 国）' 已核实 → 生成页 desc 空 + display:none 成立 |

方案合理：3 个修复均为「断言同步数据现状」，与 134e3c6（update@data 2026-08-28 00:15，早于本设计）漂移方向一致，无新增耦合。

## 二、新增发现（v1.1 复审）

| # | Severity | 问题 | 修复路径 |
|:-:|:---:|:-----|:---------|
| N1 | 🟡 | §8 验收清单第 7 条「test_videos.py **6 用例** + 回归全绿」未随 §7 同步 —— §7 已扩至 8 用例（test_01..08，含新增 test_07/08），计数陈旧（v1.0 为 6） | 改 §8.7 为「test_videos.py **8 用例** + 回归全绿（test_01..08，见 §7）」；已内嵌 dev prompt 核心变更 #8 |

非阻塞：§7 为测试计划权威源，dev 按 §7 实施 8 用例不受 §8.7 计数影响；仅验收核对时会造成「6 vs 8」歧义，须在实施周期一并修正。

## 三、评分

```
基准分: 100
  N1  🟡 -5  §8.7 用例数陈旧（6→8 未同步）
  （初审 RIG-001..003 / 🟢 046..052 全部闭合，不计分）
────────────────────────
得分: 95 → A → PASS
```

## 四、结论

**PASS（95/A）— 闭环。**

- 初审 10 项发现（3 🟡 + 7 🟢）全部闭合：RIG-001/002/003 精确命中初审缺陷（split/expand 数组渲染、platform 归一化、.video-pill 截断类），🟢 046..052 逐项规格落地且 §7 测试计划 8 用例与风险边界一一对应
- 数据漂移 3 断言同步方案经实跑核实为真（3 failed 复现，diff 与设计描述精确一致），dev 按 §7 修复后全量应回绿
- 治理合规：git mv 保留双 commit 历史（`git log --follow` → b0896c1 + 99cede3）、commit 规范 `docs@table:`、文件命名 Style A v1.1 正确
- 唯一新增 N1（§8.7 计数）纯文档文本陈旧，dev prompt 已内嵌修复项，验收清单 §8 其余 6 条可执行

**后续**：dev 实施 prompt 已落盘 `cache/review-prep/prompt-table-videos-dev-20260828.md`（核心变更 8 项 + 验收清单 + 强制报告字段）；实施完成后按 ops 核查 → review 实施审计 → push 流程闭环。
