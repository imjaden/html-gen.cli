---
title: html-gen 数据格式（table / knowledge / groups 输入）
topic: html-gen
type: reference
version: 1.0
date: 2026-11-09
author: ops
source: AGENTS.md 外移（HTML-GEN-CL023）
---

# html-gen 数据格式（table / knowledge / groups 输入）

> 由 `AGENTS.md` 外移（HTML-GEN-CL023）：细则只在本文件维护，`AGENTS.md` 只留指针，两处不重复同一段文本。

## 数据格式

### table 输入

**简单格式**（JSON 数组，向后兼容）：
```json
[{"列名1": "值1", "列名2": "值2"}, ...]
```

**结构化格式**（v2.0 新增）：
```json
{
  "title": "项目速查表",          // 可选，页面标题（默认 "数据表格"，CLI --title 覆盖）
  "subtitle": "共 N 条记录\n按需换行", // 可选，h1 下方段落描述（CLI --subtitle 覆盖，显式传空串清空）
  "output": "demos/xxx.html",   // 可选，渲染目标（CLI -o 覆盖；均无 → 中断 exit 1）
  "columns": [
    {"key": "name", "label": "项目", "sortable": true, "locale": "zh"},
    {"key": "stars", "label": "Stars", "type": "number"},
    {"key": "actions", "label": "操作", "type": "actions", "actions": [
      {"label": "复制", "icon": "📋", "copyKey": "name"},
      {"label": "打开", "icon": "🔗", "hrefKey": "url"}
    ]}
  ],
  "data": [{"name": "hermes-agent", "stars": 50200, "url": "https://..."}],
  "tabs": [
    {"key": "all", "label": "全部"},
    {"key": "AI框架", "label": "🤖 AI框架", "field": "group"}
  ],
  "options": {"exportCSV": true, "rowSelect": true, "pageSize": 30}
}
```

> **键表不在本文档**：列类型（6）/ 列属性（22）/ Tab 属性（6）/ 选项（13）/ `options.feedback`（5）/
> `actions[]`（7）/ `videos`（5）的完整定义（取值、默认值、语义差异）见 `html-gen help table` 的键规范段
> （单一事实源：`TEMPLATE_CONTRACT['table']`）。以下仅保留渲染要点，键名以 help 为准：

- **Videos 视频列**：行字段为对象数组（地址必填 + 标题/时长/平台可选），每视频渲染 pill `[平台图标] 标题 (时长)`；
  超出条数折叠 "+N" 点击展开全部（不折叠回，re-render 重置）；平台图标映射（归一化 trim().toLowerCase()）：
  douyin/抖音→🎵、bilibili/B站/b站→📺、youtube→▶️、其他→📹；点击 pill 新标签页打开
  （window.open noopener,noreferrer，onclick 转义 JSON.stringify+&quot;）；默认搜索排除 videos 列；
  split 预览 / expand 展开对 videos 数组 Array.isArray 特判逐条渲染 + url 链接（勿 String(v) → [object Object]）
- **转义默认开启**（CL010）：列级关闭转义是唯一豁免口（键名见 help「列属性」段）
- **两种隐藏语义**不可混用：「永不可见」与「默认收起·可开启」—— help「列属性」段并列写明

### knowledge 输入（JSON 数组）

> item / groups 键与数据源三态见 `html-gen help knowledge` 的键规范段。

```json
[{
  "title": "条目名称",      // 必填
  "group": "所属类目",      // 必填，对应顶部 Tab
  "section": "子分类",      // 可选，侧栏分组
  "badge": "标记",          // 可选，如熟练度
  "desc": "<p>HTML内容</p>", // 与 url 二选一
  "url": "detail.html"      // 与 desc 二选一，iframe 加载
}]
```

输出目标：结构化 dict 顶层可带 `"output"`（渲染目标；仅 data 文件识别，groups 文件忽略；CLI `-o` 覆盖；均无 → 中断 exit 1）

### groups 输入（JSON 数组）

> 类目键见 `html-gen help knowledge` 的「groups 类目键」段。

```json
[{"key": "类目key", "label": "显示名", "icon": "🏢"}]
```
