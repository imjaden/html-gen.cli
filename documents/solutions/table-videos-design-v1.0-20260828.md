# A 型表格 videos 视频字段设计 v1.0 (2026-08-28)

> 闭环: HTML-GEN-CL001 ｜ 探讨确认: A1 B1 C1 D1 E3 F1 G（2026-08-28 拍板）

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

- pill = `[平台图标] title (duration)`；title 缺省 → `[平台图标] platform (duration)`
- 点击 pill → 新标签页打开 url（noopener,noreferrer）
- "+N" 折叠标签：点击展开全部（DOM 追加剩余 pill）
- 空/缺失 videos → 空单元格
- 平台图标映射表（JS 常量）：
  - douyin/抖音 → 🎵
  - bilibili/B站 → 📺
  - youtube/YouTube → ▶️
  - 其他 → 📹（默认）

分栏预览（split）：videos 走默认 kv-list 渲染（splitFull 时整行宽），完整列出全部视频文本。

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
4. test_04 平台图标映射：douyin→🎵、未知平台→📹
5. test_05 空单元格：无 videos 行渲染空
6. test_06 无 JS 错误

回归：
- tests/test_countries_table.py（13 用例，检查列数/表头断言是否需要同步）
- 全量分三组跑（避免 xdist 并发卡死）

## 8. 验收清单

1. [ ] type=videos 列渲染 pill 组（图标+标题+时长）
2. [ ] maxShow 折叠 +N，点击展开
3. [ ] 点击 pill 新标签页打开（noopener,noreferrer）
4. [ ] 平台图标映射（douyin/bilibili/youtube/默认📹）
5. [ ] 空/缺失 videos 渲染空单元格
6. [ ] countries-table 巴西行 2 条 douyin 视频可见
7. [ ] test_videos.py 6 用例 + 回归全绿

## 9. 风险与边界

- 单元格宽度：maxShow 控制行高，长标题截断（word-break）
- 搜索：videos 不加入默认搜索字段（countries 已有 searchFields 白名单）
- 向后兼容：videos 为空/缺省 → 空单元格，现有表不受影响；CLI 零改动
