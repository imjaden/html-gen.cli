# A 型表格 videos 视频字段设计 v1.1 (2026-08-28)

> 闭环: HTML-GEN-CL001 ｜ 探讨确认: A1 B1 C1 D1 E3 F1 G（2026-08-28 拍板）
> v1.1: 评审 CONDITIONAL 85/B（d02cfc5）修复 —— RIG-001/002/003（HG-SEC-043..045）+ 🟢 规格落地（046..052）+ 数据漂移断言同步

## 1. 背景与需求

table 模板需要"视频字段"：每行数据可关联 1 个或多个视频（链接、标题、时长、平台）。
目标场景：drama 36 计 → 影视片段；国家速查表 → 每国介绍视频。

## 2. 决策记录

| 项 | 决策 | 说明 |
|:---|:---|:---|
| A 粒度 | 数组多视频 | 1 字段 = 视频对象数组，0/1/多 天然表达 |
| B 数据结构 | url/title/duration/platform 四项 | url 必填，其余可选 |
| C 点击行为 | 新标签页打开 | window.open(url, '_blank', 'noopener,noreferrer') |
| D 折叠 | maxShow 可配（默认 3） | 超出折叠 "+N" |
| E 平台图标 | 预设映射 + 默认 emoji | douyin🎵 bilibili📺 youtube▶️ 默认📹 |
| F 实现方式 | 独立新类型 col.type="videos" | 数据驱动，CLI 零改动 |
| G 联动 | countries-table 巴西行 2 条 douyin 视频 | data/_countries-data.json |

## 3. 数据格式

行内字段（可选，缺省/空数组 = 无视频）：

```json
"videos": [
  {"title": "每天了解一个国家，巴西", "url": "https://v.douyin.com/8KyFzcfoH68/", "duration": "3:22", "platform": "douyin"},
  {"title": "巴西建国史", "url": "https://v.douyin.com/Y6VCrD4QQg8/", "duration": "8:37", "platform": "douyin"}
]
```

字段语义：
- `url`：必填，视频链接
- `title`：可选，标题；缺省时用 platform+duration 兜底显示
- `duration`：可选，时长文本（如 "3:22"）
- `platform`：可选，平台标识（douyin/bilibili/youtube…），用于图标映射

## 4. 列配置

```json
{"key": "videos", "label": "视频", "type": "videos", "width": "260px", "preview": true,
 "videos": {"maxShow": 2}}
```

- `type: "videos"`：新渲染类型
- `videos.maxShow`：单元格最多显示视频数（默认 3），超出折叠 "+N" 标签（点击展开全部）
- 复用现有列属性：`preview`（分栏显示）、`width`、`initialHidden` 等

## 5. 渲染设计

单元格（pills 风格，每视频一个 pill）：
```
[🎵] 每天了解一个国家，巴西 (3:22)  [🎵] 巴西建国史 (8:37)  +1
```

- pill = `[平台图标] title (duration)`；title 缺省 → `[平台图标] platform (duration)`；title 与 platform 均缺省 → `[📹] (duration)`（数据质量约定：title 建议必填，HG-SEC-051）
- 点击 pill → 新标签页打开 url（window.open(url, '_blank', 'noopener,noreferrer')）
- onclick 转义沿用 actions 先例：`JSON.stringify(url).replace(/"/g,'&quot;')`（HG-SEC-047）
- "+N" 折叠标签：点击展开全部（DOM 追加剩余 pill），不折叠回；跨 re-render 重置（重新渲染时回到 maxShow 折叠态）；点击 stopPropagation 防触发行点击（HG-SEC-046）
- 空/缺失 videos → 空单元格
- 平台图标映射表（JS 常量）：
  - 归一化：`String(platform).trim().toLowerCase()`（HG-SEC-044）
  - douyin / 抖音 → 🎵
  - bilibili / B站 / b站 → 📺
  - youtube / YouTube → ▶️
  - 其他 → 📹（默认）
- 长标题截断：videos pill 独立类 `.video-pill`（HG-SEC-045）：
  - `max-width: 180px; white-space: normal; word-break: break-all;`
  - 不与 .cell-pill 的 nowrap 冲突；maxShow 控制行高，超长 title 在多行内截断显示

分栏预览（split）与行内展开（expand）：
- videos 列 `Array.isArray(v)` 特判（HG-SEC-043，勿用 String(v) 否则 [object Object]）：
  - 逐条渲染 `[平台图标] title (duration)` + url 链接（可点击新标签页打开）
  - splitFull 时整行宽；非 splitFull 时普通 kv-item

## 6. countries 联动（G）

data/_countries-data.json：
- columns 末尾追加：`{"key": "videos", "label": "视频", "type": "videos", "width": "260px", "preview": true, "videos": {"maxShow": 2}}`
- 巴西行追加 videos 数组（2 条 douyin，见 §3）
- 其余 194 行无 videos 字段 → 空单元格

重新生成：
```
python3 html-gen.py table -d data/_countries-data.json --title "<现有 title>" -o demos/countries-table.html
```
（title 与现 demos/countries-table.html 的 <title> 一致）

## 7. 测试计划

新建 tests/test_videos.py（Selenium，参照 test_table_features.py 结构）：
1. test_01 单元格渲染：videos 列出现 pill，含平台图标/标题/时长
2. test_02 折叠：maxShow=2 + 3 个视频 → "+1" 标签；点击展开 3 个
3. test_03 点击新标签页：pill click → window.open 调用（js 检查）/ 链接 target=_blank
4. test_04 平台图标映射：douyin→🎵、未知平台→📹、平台大小写/别名归一化（抖音→🎵）
5. test_05 空单元格：无 videos 行渲染空
6. test_06 无 JS 错误
7. test_07 split 预览 videos 渲染（HG-SEC-043/049）：分栏预览中出现视频标题文本，非 [object Object]
8. test_08 无 searchFields 表默认搜索排除 videos（HG-SEC-052）：搜索词命中 title 不应筛出该行

回归：
- tests/test_countries_table.py（13 用例，无表头/列数硬断言，videos 列追加 index 17 不破坏）
- 全量 `python3 -m pytest tests/ -q -n 4`（若环境并发卡死则分三组兜底，HG-SEC-050）
- 数据漂移同步：134e3c6（update@data 2026-08-28）导致 3 个测试断言过期，v1.1 一并修复：
  - test_countries_table.py::test_01_region_pills_dundun_split：塞尔维亚 region_tags 现 ['欧洲','南欧','前南斯拉夫']（3 值）
  - test_history_tables.py::test_01_strategy_headers_and_index：history-strategy 现 10 列结构，可见列 ['序号','计名','分类','别名','衍生成语','兵法','人物']
  - test_table_features.py::test_12_description_empty_hidden：_drama-table-history-strategy.json 顶层已含 subtitle（《孙子兵法》描述），改用无 subtitle 数据源或临时 JSON

## 8. 验收清单

1. [ ] type=videos 列渲染 pill 组（图标+标题+时长）
2. [ ] maxShow 折叠 +N，点击展开
3. [ ] 点击 pill 新标签页打开（noopener,noreferrer）
4. [ ] 平台图标映射（douyin/bilibili/youtube/默认📹）
5. [ ] 空/缺失 videos 渲染空单元格
6. [ ] countries-table 巴西行 2 条 douyin 视频可见
7. [ ] test_videos.py 6 用例 + 回归全绿

## 9. 风险与边界

- 单元格宽度：maxShow 控制行高；长标题用 `.video-pill`（max-width:180px + word-break:break-all，HG-SEC-045）
- 搜索：videos 不加入默认搜索字段；无 searchFields 的表默认搜索也排除 videos 列（HG-SEC-052）
- 配置键名：col 配置 `{"key":"videos",...,"videos":{"maxShow":2}}` 与行数据 `row.videos` 同名，属列配置/数据两套命名空间，规格已明确（HG-SEC-048）
- 向后兼容：videos 空/缺省 → 空单元格，现有表不受影响；CLI 零改动

## 10. 修订记录

- v1.0 (2026-08-28)：初始设计，评审 CONDITIONAL 85/B（d02cfc5）
- v1.1 (2026-08-28)：RIG-001（split/expand Array.isArray 特判 + test_07）、RIG-002（platform 归一化 + 别名表）、RIG-003（.video-pill 截断类）；🟢 规格落地（+N 状态机/onclick 转义/键名说明/title 必填约定/搜索排除/跑法）；同步 3 个数据漂移断言（134e3c6）
