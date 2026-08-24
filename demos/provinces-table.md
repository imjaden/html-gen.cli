# 中国省份速查表（provinces）— html-gen table demo

- 主题：中国 34 个省级行政区（23 省 + 5 自治区 + 4 直辖市 + 2 特别行政区）速查表
- 创建日期：2026-08-24
- 来源：国家统计局 / 各省统计公报（面积、GDP 2023）/ 第七次全国人口普查 2020（人口）；关联国家数据复用 data/_countries-data.json（World Bank + UN M49）
- 模板类型：A 型表格（html-gen table）
- 数据文件：data/_provinces-data.json（columns + data + tabs + options）
- 页面：demos/provinces/provinces-table.html
- 特性：七大区域 Tab 分组、面积/人口/GDP 数值排序、千位符、CSV 导出、与全球国家速查表双向关联（面积/人口/GDP 相近国家 ↔ 相近省份）

字段：省份名称/简称/省会（首府）/区域/面积(万km²)/人口(万)/GDP(亿元)/面积相近国家/人口相近国家/GDP相近国家/备注

双向关联口径：国家侧面积按 `area_km2 ÷ 10000` 归一化为万km²，GDP 按 `gdp_yi × 7.08`（2023 年均汇率，国家统计局口径）归一化为亿元；匹配阈值面积 ≤30%、人口 ≤20%、GDP ≤30%；港澳台归"华南"区域，口径与内地有差异（备注注明）。
