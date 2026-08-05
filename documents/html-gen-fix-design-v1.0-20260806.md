# html-gen 底层修正完善 — 设计文档

## 版本

v1.0 (2026-08-06)

## 背景与来源

script-miner html-gen-docs skill 实践(personal cinema / MyVideos 项目反馈)确认的 html-gen 底层事项。html-gen-docs 侧已按评审优化数据层;本设计针对 html-gen 仓库 (`/Users/jadenli/CodeSpace/html-gen`) 需修正/完善的事项,输入为 `cache/html-gen-fix-prompt.md` 需求反馈,经待确认清单问答(用户回复 1A 2A 3A 4A 5A 6A)定稿。

## 需求反馈核查结论

| 项 | fix-prompt 要求 | 核查结果 | 结论 |
|:---|:---|:---|:---|
| CSV 导出中文列名 | 已满足 | exportCSV L1159-1160 / exportSelectedCSV L1371 表头均用 c.label | 无需改 |
| SKILL.md 列属性 quickFilter/freeze | 补 | 当前列配置表未含 | 需补 |
| SKILL.md 列类型 datetime/pills | 补 | SKILL.md 仅 string/number/actions | 需补(含模板实现) |
| SKILL.md options clickMode | 补 | options 表仅 pageSize/exportCSV/rowSelect/search | 需补 |
| SKILL.md 版本 bump 2.1.0→2.2.0 | 补 | 仍 2.1.0 | 需补 |
| html-gen/SKILL.md 四型总览提示 | 补 | 已有 "> A 型表格的详细列配置...参见 html-gen-table skill" | 已满足 |
| features.md 列类型/选项 | 补 | quickFilter/freeze/pills/clickModes 已有;缺 datetime、clickMode 单数 | 部分需补 |

## 设计决策 (D)

### D1 — datetime 列类型:补模板实现 (1A)

**现状**: `layout-table.html` 排序仅区分 `type === 'number'`(parseFloat)与其余(字符串 localeCompare)。html-gen-docs 数据层已用 `type: "datetime"`(mtime 列),模板无对应分支,按字符串排序;ISO 格式 `YYYY-MM-DD HH:MM` 字符串序恰好近似时间序,但语义不严谨(如 `2026-02-01` 与 `2026-1-1` 混排会错)。

**方案**: 在排序比较处增加 datetime 分支:
```js
var isDate = col && col.type === 'datetime';
// 比较时:
if (isDate) { va = Date.parse(va)||0; vb = Date.parse(vb)||0; cmp = va - vb; }
```
- 渲染不变(原样字符串展示)
- 二级排序同步支持(col2 同样判定 isDate2)
- 空值/解析失败按 0 处理,与 number 分支一致

**影响**: layout-table.html 排序逻辑;行为兼容(旧数据无 datetime 列不受影响)。

### D2 — clickMode 单数兼容 (2A)

**现状**: 模板仅读取 `OPTIONS.clickModes`(复数数组,默认 `['tab']`)。html-gen-docs 数据层实际使用 `"clickMode": "tab"`(单数),当前不生效(因默认 tab 视觉无差异,但配置被静默忽略)。

**方案**: OPTIONS 解析处兼容单数:
```js
var validModes = (OPTIONS && OPTIONS.clickModes) ||
                 (OPTIONS && OPTIONS.clickMode ? [OPTIONS.clickMode] : null) ||
                 ['tab'];
```
- 单数 clickMode 存在时视为单元素数组
- 复数 clickModes 优先(向后兼容)
- 设置面板 initColToggle(L1051)与点击模式判定共用此值

**影响**: layout-table.html OPTIONS 解析;兼容新旧两种配置。

### D3 — html-gen-table SKILL.md 文档同步 (3A)

补全内容:
1. 列配置表新增行:
   - `quickFilter` | bool | | 是否禁用该列点击筛选(默认 false 不禁用;true 时单元格点击不触发 quickFilter)
   - `freeze` | bool | | 列冻结(sticky,left 偏移基于 col.width 动态计算)
2. 列类型详情新增:
   - **type: "pills"** — 逗号分隔值渲染为 tag pills
   - **type: "datetime"** — 时间排序(Date.parse 比较;展示原样字符串)
3. options 表新增:
   - `clickModes` | array | ['tab'] | 允许的点击模式 [tab/modal/split/expand](兼容单数 `clickMode`)
   - 组合说明: `rowSelect` + `exportCSV` 可同时启用 → 批量工具栏出现"导出选中"
4. 版本号 `2.1.0` → `2.2.0`,新增变更记录段落
5. frontmatter description 补充 datetime/pills/clickModes 关键词(可选)

### D4 — features.md 同步 (4A)

补全条目(数据格式部分):
- `col.type: string/number/actions` → `string/number/datetime/pills/actions`
- options 列表补 `clickModes (可用点击模式列表, 兼容单数 clickMode)`
- 模板功能区补 datetime 排序、clickMode 单数兼容条目
- 同步 layout-table.html 行数(当前 1110 行,按实际改动后更新)与项目统计表

### D5 — Selenium 测试 (5A)

新增测试文件 `tests/test_datetime_clickmode.py`(或并入 test_table_features.py,按 dev 实施时选择;建议独立文件便于追溯):

**测试 1: datetime 列排序**
- 构造含 datetime 列的数据(混排顺序 + 非补零格式 `2026-2-1` 验证语义排序而非字符串序)
- 点击表头排序 → 断言首行/末行时间序正确
- 验证 `window.__testErrors` 为空

**测试 2: clickMode 单数兼容**
- 构造 `options: {"clickMode": "tab"}` 的生成页面
- 断言点击行在新标签页打开(或验证设置面板可切换模式、validModes 正确)
- 验证单数配置被正确解析(非静默忽略)

**测试 3(可选): 复数优先**
- 构造 `options: {"clickModes": ["modal","split"]}` → 设置面板不出现 tab 单选

依赖: 现有测试脚手架(webdriver/chromedriver/error_collector),沿用 `tests/test_table_features.py` 风格。

### D6 — html-gen/SKILL.md 四型总览

**结论**: 无需修改(6A)。已存在 "> A 型表格的详细列配置、操作按钮、Tab 过滤等高级功能参见 `html-gen-table` skill。" 提示。

## 影响范围

| 类型 | 文件 | 改动 |
|:---|:---|:---|
| 直接功能 | `layout-table.html` | 排序 datetime 分支;OPTIONS clickMode 单数兼容 |
| 说明性指令 | `skills/html-gen-table/SKILL.md` | 列属性/列类型/options 补全,版本 bump 2.2.0 |
| 说明性文档 | `features.md` | col.type/options 补全,行数统计更新 |
| 说明性文档 | `html-gen/SKILL.md` | 无需改(已满足) |
| 测试用例 | `tests/test_datetime_clickmode.py`(新) | datetime 排序 + clickMode 兼容 + 复数优先 |
| 无改动 | `html-gen.py` | HELP_TABLE 已覆盖 pills/quickFilter/clickModes(不含 datetime,维持现状可接受;如需可后续补) |

> 注: html-gen.py HELP_TABLE 未含 datetime 类型说明,本次不改(模板功能已完成,HELP_TABLE 属 CLI 内嵌文档,按 fix-prompt 约束"只改文档不改代码逻辑"保持;如需可在实施时评估补充)。

## 修改步骤

1. **dev 实施 (layout-table.html)**
   - D1: 排序比较 datetime 分支(主键 + 二级键)
   - D2: OPTIONS 解析 clickMode 单数兼容
   - 手动生成 demo 验证行为
2. **dev 实施 (skills/html-gen-table/SKILL.md)**
   - 列配置表 + 列类型 + options 补全
   - 版本 bump 2.1.0 → 2.2.0 + 变更记录
3. **dev 实施 (features.md)**
   - col.type/options/模板功能补全
   - 行数统计同步
4. **dev 实施 (tests/)**
   - 新增 datetime 排序 + clickMode 单数兼容测试
   - 运行全部测试确认无回归(当前 57 tests)
5. **ops 核查**
   - 对照本设计 TC/SC 验证
   - 确认文档与实现一致(datetime 有实现才写文档)
6. **review 审计**
   - 按治理规范 audit 后 push

## 验收清单 (TC)

- TC1: layout-table.html 含 datetime 排序分支,非补零日期 `2026-2-1` 与 `2026-02-01` 按时间语义排序
- TC2: `options.clickMode: "tab"`(单数)生效,设置面板可正常切换点击模式
- TC3: `options.clickModes`(复数)优先于单数,向后兼容
- TC4: html-gen-table SKILL.md 覆盖 quickFilter/freeze/datetime/pills/clickModes,版本 2.2.0 + 变更记录
- TC5: features.md 无缺失项(col.type 含 datetime/pills,options 含 clickModes)
- TC6: 新增 Selenium 测试通过,`window.__testErrors` 为空
- TC7: 全部测试通过(57 → 59/60,无回归)
- TC8: html-gen.py 与模板行为不受影响(纯文档 + 兼容性改动)

## 自检清单 (SC)

- SC1: datetime 分支与 number 分支逻辑对称(空值/undefined 处理一致)
- SC2: clickMode 单数兼容不破坏现有 clickModes 数组用法
- SC3: SKILL.md 文档描述的每一项均有模板实现支撑(无文档撒谎)
- SC4: features.md 行数与实际 layout-table.html 行数一致
- SC5: 变更记录日期正确(2026-08-06)
