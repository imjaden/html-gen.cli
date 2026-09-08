# A 型表格 videos 视频字段设计 — review报告 v1.0

> 日期: 2026-08-28
> 文件: `documents/solutions/table-videos-design-v1.0-20260828.md`
> 项目路径: ~/CodeSpace/html-gen.cli
> 聚焦 commit: `b0896c1`（docs@table: videos field design v1.0 (HTML-GEN-CL001)，1 文件 +110，未 push，ahead github/main 1）
> 决策依据: A1 B1 C1 D1 E3 F1 G（2026-08-28 用户拍板）
> review维度: 合理性 / 严格性 / 安全性 / 治理规范（commit + 命名）
> review者: Security Reviewer (L2, design-document-review)

## 裁决

**CONDITIONAL PASS — 85/100 (B) — 不 push**

方案完整、数据驱动、复用既有机制正确，countries 联动可验收，测试基线不受破坏。但 3 项 🟡 未闭环（其中 HG-SEC-043 为「设计承诺的行为当前模板无法交付」——split 预览会把 videos 数组渲染成 `[object Object]`）。85 达 PASS 分数线下限，但按项目先例（doc-meta-path-showmd 85/REJECT：open finding 不得 PASS）与「🟡 未闭环不得 PASS」原则，判 CONDITIONAL。RIG-001..003（全部 Bucket A，无需用户决策）修复为 v1.1 后复审 → PASS。

## 一、数据验证

| 验证项 | 方法 | 结果 |
|:-------|:-----|:-----|
| commit 范围 | `git show b0896c1 --stat` | ✅ 仅 1 文件（设计文档 +110），无代码/数据混入 |
| 提交规范 | 消息体 | ✅ `docs@table:` type@scope 小写；HTML-GEN-CL001 闭环编号；符合项目惯例 |
| 文档命名 | 文件名 | ✅ `table-videos-design-v1.0-20260828.md` 符合 Style A（topic-design-v{maj}.{min}-{date}） |
| 数据文件结构 | json 读 `data/_countries-data.json` | ✅ 17 列 / 195 行 / options{pageSize:50, exportCSV:true, searchFields:[country_zh,country_en,capital_zh,capital_en]} / 顶层 title="全球国家速查表（195 国）"；当前 0 行含 videos 字段 |
| title 一致性 | 现 demo `<title>` vs JSON 顶层 title | ✅ 均为「全球国家速查表（195 国）」；生成命令 `--title` 冗余但无害 |
| 列尾追加安全性 | 读 `tests/test_countries_table.py`（13 用例） | ✅ 无表头/列数硬断言；tds[] 索引断言仅 0-6（国家/英文名/首都/纬经度/大洲），videos 追加于 index 17 不破坏；test_11 中国行无 videos 不受影响；test_03/04（50 行/195 tab 计数）不依赖列数 |
| 模板现状 | grep `videos` layout-table.html | ✅ 0 命中 —— 新类型需在 renderRow 加分支（pills 分支先例 :529-544）；既有 escapeHtml(:367) / escapeAttr(:606) / window.open noopener,noreferrer 先例(:591) 可直接复用 |
| split 预览可达性 | countries columns 配置 | ✅ country_zh `onCellClick:'split'` + videos 列 `preview:true` → split 模式表格与预览体均会出现 videos 列（:382-388 预览过滤） |
| 搜索隔离 | layout-table.html:428-434 | ✅ searchFields 白名单限定 4 字段，videos 不参与 countries 搜索；无 searchFields 的表默认搜索所有非 actions 列（见 🟢 HG-SEC-052） |
| 巴西行 | 数据文件 巴西 | ✅ 现无 videos 字段，2 条 douyin 数据（url/title/duration/platform 完整，§3 样例）待追加 |
| CLI 零改动 | html-gen.py:340-370 | ✅ columns/data/options 数据驱动注入，新增 col.type 值无需 CLI 变更 |
| 测试基线 | `grep -c 'def test_' tests/*.py` + 实跑 | ⚠️ 188 defs / 20 文件（与 AGENTS.md 一致）；实跑 185 passed / 3 failed —— 3 项均为 134e3c6（update@data 2026-08-28 00:15，早于本设计）数据漂移未同步测试所致：test_01_region_pills_dundun_split（塞尔维亚 region_tags 现为 欧洲/南欧/前南斯拉夫，断言旧 2 值）、test_history_tables::test_01（history-strategy 数据重构 672 行删除）、test_table_features::test_12（table-features-demo subtitle 变更）。与本次评审无关，不扣分；v1.1 修复时应一并同步这 3 个断言 |

## 二、维度评估

### 合理性（✅ 无待确认项）

- A-G 决策记录完整闭环，六要素（数据格式/列配置/渲染/联动/测试/验收/风险）齐全，dev 可直接实施
- 复用既有机制正确：pills 视觉风格（.cell-pill :39）、actions hrefKey 的 window.open 新标签页先例（:591）、escapeHtml 安全路径（:367）、searchFields 白名单
- F 独立新类型（非 pills 扩展）正确：pills 语义是「字符串分隔筛选」，videos 是「对象数组链接组」，复用会污染 pillFilter/quickFilter
- 折叠 maxShow 默认 3 + 显式 2（countries）合理；「+N」计数语义清晰
- 巴西行 2 条 douyin 数据已由用户提供（url 为 v.douyin.com 短链），G 联动落地无歧义

### 严格性（3 项 🟡）

| # | 严重度 | 问题 | 详情 |
|:-:|:------:|:-----|:-----|
| 1 | 🟡 | split 预览 videos 渲染承诺无法交付 | 设计 §5「videos 走默认 kv-list 渲染…完整列出全部视频文本」—— 但 renderSplitPreview 对所有列执行 `escapeHtml(String(v))`（layout-table.html:986-991），对象数组 String() 得 `[object Object]`。countries 分栏可达，dev 按文实施必然产出损坏预览（HG-SEC-043） |
| 2 | 🟡 | platform 归一化机制未指定 | 映射表列了 douyin/抖音、bilibili/B站、youtube/YouTube 别名，但未规定 trim/lowercase/别名表规则；dev 若只做精确小写匹配，抖音/B站 数据静默落默认 📹（HG-SEC-044） |
| 3 | 🟡 | 长标题截断机制与现有 CSS 冲突 | 设计 §9「长标题截断（word-break）」—— 但 .data-table td 为 nowrap+overflow:hidden+ellipsis 单元格级截断（:99-100），.cell-pill 为 nowrap 行内块（:39）；word-break 在 nowrap 上不生效，长标题会被单元格裁剪在 pill 中间（HG-SEC-045） |

### 安全性（✅ 无新执行面）

- 点击打开：`window.open(url,'_blank','noopener,noreferrer')` 与既有 :591 一致，无 reverse tabnabbing ✓
- 文本渲染：title/duration/platform 走 escapeHtml 文本路径（与 pills :535 一致）✓
- url 注入 onclick 需沿用 `JSON.stringify(url).replace(/"/g,'&quot;')` 转义模式（:591 先例）—— 归入 🟢 HG-SEC-047
- 零新增依赖、CLI 零改动、无子进程 → 供应链/执行面无新增 ✓
- 数据面：videos 来自项目自维护数据文件，非外部用户输入 ✓

## 三、安全事项

| # | Severity | 问题 | 位置 | 状态 |
|:---|:---:|:---|:---|:---:|
| HG-SEC-043 | 🟡 | split 预览将 videos 渲染为 `[object Object]`；设计 §5「默认 kv-list」承诺与现模板不符 | layout-table.html:986-991（renderSplitPreview）；设计 §5 分栏预览段 | ⏳ OPEN |
| HG-SEC-044 | 🟡 | platform 归一化（trim/lowercase/别名表）未指定 | 设计 §5 平台图标映射表 | ⏳ OPEN |
| HG-SEC-045 | 🟡 | 长标题截断方案（word-break）与 .cell-pill nowrap CSS 冲突 | layout-table.html:39,99-100；设计 §9 | ⏳ OPEN |
| HG-SEC-046 | 🟢 | "+N" 展开状态机未指定（可折叠回？跨 re-render 保持？stopPropagation） | 设计 §5 | 随 v1.1 |
| HG-SEC-047 | 🟢 | pill 点击 onclick 转义机制未指定（应参照 :591 JSON.stringify+&quot;） | 设计 §5 | 随 v1.1 |
| HG-SEC-048 | 🟢 | 列配置键名混淆：`{"key":"videos",...,"videos":{"maxShow":2}}` col.videos 与 row.videos 同名 | 设计 §4 | 随 v1.1 |
| HG-SEC-049 | 🟢 | 测试计划 6 用例未覆盖 split 预览 videos 渲染（HG-SEC-043 关联） | 设计 §7 | 随 v1.1 |
| HG-SEC-050 | 🟢 | §7「全量分三组跑」非必要 —— 185 tests `-n 4` 并行已验证稳定（32.66s，2026-08-27） | 设计 §7 | 随 v1.1 |
| HG-SEC-051 | 🟢 | title 与 platform 均缺省时 pill 为「[📹] (duration)」空壳，边界可接受（数据质量约定建议 title 必填） | 设计 §5 | 随 v1.1 |
| HG-SEC-052 | 🟢 | 无 searchFields 的表默认搜索含 videos 列（String(array) 噪音 + 可能误命中 title 文本）；建议 videos 渲染分支从默认搜索键排除 | layout-table.html:430-431 | 随 v1.1 |

## 四、评分

```
基准分: 100
  HG-SEC-043  🟡 -5  split 预览 [object Object]（设计承诺无法交付）
  HG-SEC-044  🟡 -5  platform 归一化未指定
  HG-SEC-045  🟡 -5  长标题截断与 nowrap CSS 冲突
────────────────────────
得分: 85 → B → CONDITIONAL PASS
```

## 五、结论

**CONDITIONAL PASS（85/B）— 不 push。**

方案方向正确：数据驱动、复用既有机制、countries 联动可验收、CLI 零改动、向后兼容（videos 空/缺省 → 空单元格，现有表不受影响）、测试基线 188 无破坏（test_countries_table.py 无列数/表头硬断言，videos 列追加于末尾 index 17 安全）。

问题集中在「设计承诺的渲染行为」与「现模板实际能力」的 3 处缺口（split 预览数组渲染、平台归一化、长标题截断 CSS），全部为 Bucket A（可自决修复，无需用户决策），v1.1 补 3 行规格 + 1 个测试用例即可闭合。

## 六、RIG 清单（ops 修 v1.1，全部 Bucket A）

| # | 项 | 修复 |
|:-:|:---|:---|
| RIG-001 (HG-SEC-043) | 设计 §5 分栏预览段重写 | 明确 `Array.isArray(v)` 特判：split 预览与 expand detail（:573-576）对 videos 逐条渲染 `[icon] title (duration)` + url 链接（而非 String(v)）；§7 测试计划补 test_07（split 预览 videos 文本断言） |
| RIG-002 (HG-SEC-044) | 设计 §5 平台映射段补一行 | 归一化：`String(platform).trim().toLowerCase()`；映射键 {douyin, bilibili, youtube} + 别名表 {抖音→douyin, b站→bilibili, youtube→youtube}；未命中 → 📹 |
| RIG-003 (HG-SEC-045) | 设计 §5/§9 截断边界明确 | videos pill 独立类 `.video-pill`：max-width（建议 180px）+ white-space:normal + word-break:break-all（或 nowrap + max-width + ellipsis 二选一）；声明 maxShow 控制行高、超长 title 的视觉边界 |

修复后重命名 v1.1（git mv 保留历史）并通知复审。
