# html-gen 数据表格生成模板

## 任务

使用 `html-gen table` 命令将 JSON 数据转为自包含 HTML 数据表格页。

## 数据规范

```
columns: [{key, label, sortable, type, width, freeze, preview, quickFilter, onCellClick}]
data:    [{key: value}]
tabs:    [{key, label, field}]
options: {pageSize, exportCSV, rowSelect, search, clickModes, columnsSplit}
```

## 列类型

`string`(默认) / `number` / `datetime`(Date.parse) / `pills`(逗号分隔 tag) / `actions`(按钮)

## 默认行为须知

- quickFilter 默认关 (`col.quickFilter: true` 显式启用)
- pillFilter 默认开 (`col.pillFilter: false` 关闭)
- 第 1 列默认分栏 (无显式 onclick 时打开 split)

## 生成命令

```bash
html-gen table -d data.json --title "标题" -o index.html
```

## 质量要求

- 所有数据列设 `width`
- 操作列 `type: "actions"`
- 标签列 `type: "pills"`
