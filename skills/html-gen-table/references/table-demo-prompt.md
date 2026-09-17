# html-gen 数据表格生成模板

## 任务

使用 `html-gen table` 命令将 JSON 数据转为自包含 HTML 数据表格页。

## 数据规范

四个顶层分区: `columns`（列定义）/ `data`（数据行, 别名 `rows`）/ `tabs`（标签页）/ `options`（选项）。
**键名、取值与默认值一律以 `html-gen help table` 的键规范段为准**（单一事实源: `html-gen.py` 的
`TEMPLATE_CONTRACT['table']`）。下列仅为写法示例 —— 示例可含键名, 规范以 help 为准:

```
columns: [{key, label, type, width, preview, onCellClick}]
data:    [{<字段名>: <值>}]
tabs:    [{key, label, field}]
options: {pageSize, exportCSV, search, columnsSplit}
```

## 列类型

文本(默认) / 数值 / 日期 / 标签 / 视频 / 操作按钮 六类; 取值名与排序口径见
`html-gen help table` 的「列类型」段。

## 默认行为须知

- 标签点击筛选默认开、单元格快速筛选默认关（两者均可在列属性覆盖, 键名与默认值见 help「列属性」段）
- 第 1 列默认分栏预览（无显式单元格点击配置时）

## 生成命令

```bash
html-gen table -d data.json --title "标题" -o index.html
```

## 质量要求

- 所有数据列显式设列宽（Cinema 宽度模型要求; 默认值见 help「列属性」段）
- 操作列表取 `actions`、标签列表取 `pills`（列类型取值见 help）
