---
title: table 模板手册
topic: html-gen
type: summary
version: 1.0
date: 2026-09-08
author: hermes-v0.20.6(2026.8.27)
profile: dev
provider: deepseek
model: deepseek-v4-flash
tags: [html-gen, table, layout-table, quickfilter, actions, videos, syncer, favicon, urlstate, handbook, summary]
---

# html-gen table 模板 v1.0

> 本文是 A 型表格模板（layout-table.html）与配套数据工具链的主题手册：交互层演进（Cmd+F 快捷搜索、操作按钮列、单元格筛选默认语义、URL 状态分享）、`col.type:'videos'` 视频字段渲染、以及 videos 数据同步脚本 tool-table-videos-syncer.py（CL001→CL002→CL004→CL006 闭环）。内容以 2026-09-08 当前实现为准（layout-table.html / html-gen.py table 子命令 / scripts/tool-table-videos-syncer.py / features.md 实测互证）。

## 1. 功能定位

table 命令把结构化 JSON 渲染为 A 型数据表格（搜索/排序/分页/导出/列可见性/分栏/点击模式）。本手册覆盖 layout-table.html 四轮交互与工具链演进：

- **交互默认语义**：普通单元格点击筛选、标签(pills)点击筛选、第 1 列默认分栏——「数据浏览型表格误触筛选」问题的三处决策链（族 B，quickfilter，无 CL 编号，L2 review PASS 100/A）。
- **数据驱动操作面**：Cmd/Ctrl+F Spotlight 快捷搜索弹框、`col.type:'actions'` 操作按钮列（族 A，设计级 2026-07-12，无审计）。
- **videos 内容类型与工具链**：`col.type:'videos'` 渲染（CL001）+ yaml 增量同步脚本（CL002 v1.1 additive → CL006 v1.2 三态增量）+ favicon 默认注入 / URL 状态分享 / syncer 参数体系（CL004）。
- **产物分享**：`?tab=<tabKey>&q=<搜索词>&split=<行下标>` URL 状态恢复 + 🔗/↗️ 拷贝按钮。

## 2. 演进主线与审计结论

| 节点 | 日期 | 内容 | 审计结论 | 测试基线 |
|:--|:--|:--|:--|:--|
| cmd-f-search / table-actions 设计 | 2026-07-12 | 快捷搜索 + 操作按钮列 | 设计级（无审计，features.md+源码兜底） | — |
| quickfilter 默认调整 | 2026-08-06~08 | 单元格筛选默认关 / pill 默认开 / 第 1 列默认分栏 | 设计 PASS 100/A + 实现 PASS 100/A（commit 65c32c1，无 CL） | 84 |
| CL001 | 2026-08-28 | videos 视频字段渲染 | 评审 85/B → 复审 95/A → 实现审计 PASS 100/A | 196 |
| CL002 | 2026-08-28~29 | syncer v1.1 additive | 评审 85/B → 复审 95/A → 实现审计 PASS 90/A（FIND-001/002） | 224 |
| CL004 | 2026-08-29 | favicon 默认注入 + URL 状态分享 + syncer 参数体系 | 设计评审 85/A → 实现审计 PASS 100/A（HG-SEC-073..079 closed） | 246 |
| CL006 | 2026-08-30 | syncer v1.2 三态增量 | 设计评审 90/A → 实现审计 PASS 100/A（0 findings） | 255 |

CL 前置：CL001 → CL002 →（CL004 参数扩展）→ CL006。族 A/B 无 CL/HG-SEC 体系。

## 3. 交互功能规格

### 3.1 Cmd+F 快捷搜索（族 A，layout-table.html）

- 页面任意位置 `Cmd+F`/`Ctrl+F` → `e.preventDefault()` 阻止浏览器默认搜索 → 弹半透明遮罩 + 居中搜索框（`.qs-overlay`/`.qs-modal`，Spotlight 风格，`qsSlideIn` 动画），自动聚焦并带入顶部搜索框现值。
- 弹框输入实时刷新「匹配 N 条」计数；Enter/「搜索」→ 关弹框并执行表格搜索；Esc 或点遮罩外部 → 关弹框**不触发搜索**；关闭时关键词保留到顶部搜索框。
- `options.quickSearchPreview: true`（可选扩展 v2）→ 实时「找到 N 条匹配」+ 前 3 条行预览。
- 边界：`showSearch=false`（隐藏搜索的页）时禁用快捷搜索；全部配色走 `--cobalt-*`/`--surface-*` CSS 变量（深色主题适配）。

### 3.2 操作按钮列（族 A，table-actions）

`col.type:'actions'` 操作列按钮，数据驱动（CLI 零改动）：

- 三种行为模式，**优先级 `copyKey` > `hrefKey` > `desc`（只生效第一个匹配）**：
  - `copyKey`：复制行数据指定字段到剪贴板（copyAction → clipboard + execCommand fallback + toast）；
  - `hrefKey`：`window.open(url, '_blank', 'noopener,noreferrer')` 新标签打开；
  - `desc`：点击弹 Toast 展示 `<icon> <label>: <desc>`，2.5s 自动消失（demo 模式）。
- ActionButton 字段：`icon`(emoji)/`label`(title 提示)/`copyKey?`/`hrefKey?`/`desc?`/`class?`；三模式可同列混合。
- 所有 onclick 必须 `event.stopPropagation()`（防触发行点击/分栏）；URL 入 onclick 用 `JSON.stringify(...).replace(/"/g,'&quot;')` 转义。
- demo 数据源 `data/_table-actions-demo.json`（顶层 `{columns,data,options}`）→ `demos/table-actions-demo.html`。

### 3.3 单元格点击默认语义（族 B，quickfilter）

点击优先级链（高→低，renderRows 内动态计算 `firstKeyCol`）：

1. `col.onCellClick === 'split'` → `openSplitAt(rowIdx)`（显式分栏）；
2. `col.quickFilter === true` → `quickFilterBy(key, value, ...)`（显式筛选；**默认关**）；
3. `col === firstKeyCol`（首个非 actions 有 key 数据列）→ `openSplitAt(rowIdx)`（**默认分栏**——无配置即得）；
4. 其余列无 onclick。

- **普通单元格点击筛选默认关**：`col.quickFilter: true` 才启用（精确匹配）。显式 `quickFilter:false` 也保留（旧配置兼容）。
- **标签(pills)点击筛选默认开**：`col.pillFilter !== false`（contains 匹配）；列级 `pillFilter:false` 可关。数据文件显式声明：skills category/profiles、countries region_tags 均配 `"pillFilter": true`。
- firstKeyCol 由 `visibleCols()` 动态计算 → 列可见性变化自动跟随，无 stale reference。
- 行为变化面（用户确认接受）：未显式配置的普通列点击从「筛选」变「无操作」（drama 全列、skills version/description 等）；第 1 列获得默认分栏能力（drama 元信息、countries 全字段）。

### 3.4 URL 状态分享（族 D，CL004）

- URL 参数：`?tab=<tabKey>&q=<搜索关键字>&split=<n>`（split = filtered 数组 0-based 下标）；默认值状态剔除（全 tab/空搜索/无分栏），URL 干净；无参时用纯净 location.pathname。
- 同步点 5 处 + quickSearch submit：switchTab / 搜索 input（300ms debounce 内）/ activateSplit / splitNav / closeSplit（剔除 split 参数）→ 统一 `syncUrlState()` → `history.replaceState`（不污染历史栈）。
- 恢复流程：URLSearchParams 解析 → tab 白名单校验（`TABS.find`，无效忽略）→ q 仅 `searchInput.value = q`（不走 innerHTML）→ split `parseInt` + 越界校验后 activateSplit（filtered 先按 tab+q 重建再定位）。
- 🔗（现行实现图标 `↗️`，class share-link）按钮：先 syncUrlState 再取 location.href → clipboard.writeText → execCommand fallback → toast「已复制链接」。
- 安全：tab key 白名单；split 越界忽略；q 仅 input.value 无 innerHTML 注入面；URL 参数只影响视图状态，不触发任何数据写入。
- **split 下标脆弱性**：sortBy/quickFilterBy/clearQuickFilter 均 `if (splitActive) closeSplit()`（下标语义随排序/筛选失效）；defaultFilter（drama 历史表专用）下 split 恢复跳过。仅「默认排序 + 无 quickFilter」下 split 参数语义稳定。
- 不做（记录）：排序/页码/quickFilter 状态不入 URL。

### 3.5 videos 视频字段（族 C，CL001）

- 列配置：`{"key":"videos","label":"视频","type":"videos","width":"260px","preview":true,"videos":{"maxShow":2}}`；行数据 `row.videos`（列配置键 `videos` 与行数据 `videos` 是两套命名空间）。
- 行数据格式：`videos: [{title, url, duration, platform}, ...]`——url 必填，title/duration/platform 可选；缺省/空数组 = 无视频。无 thumb 字段（封面图不存在于现行 schema，platform 承担图标语义）。
- 渲染：pill = `[平台图标] title (duration)`；title 缺省 → `[icon] platform (duration)`；双缺省 → `[📹] (duration)`；点击新标签页（noopener,noreferrer）；超出 `maxShow`（默认 3）折叠「+N」，点击展开全部 DOM、**不折叠回**、跨 re-render 重置、stopPropagation。
- 平台图标映射（归一化 `String(platform).trim().toLowerCase()` 后查表）：douyin/抖音→🎵、bilibili/B站/b站→📺、youtube/YouTube→▶️、其他→📹。
- videos 列从默认搜索字段排除（无 searchFields 时也排除，避免 String(array) 噪音）；split 预览/expand detail 必须 `Array.isArray(v)` 特判（勿 String(v) → `[object Object]`）。
- duration 恒为字符串（M:SS / H:MM:SS），int 容错仅 M:SS（<3600 秒归一化）。

## 4. videos 工具链（tool-table-videos-syncer.py）

### 4.1 数据流

```
cache/data/_countries-data.videos.yaml（手工增量草稿，gitignored，随时漂移）
   │ tool-table-videos-syncer.py <yaml> [--dry-run | --apply | --empty-video]
   │   F3 校验 → build_increments 三态（new_items/updates/skipped，url strip + country+url 去重）
   │   → append/覆盖 data/<target.data> 行 videos
   │   → build_mirror_countries 全局镜像回写 yaml（target 段保留）
   ▼   → subprocess html-gen.py table（--github-url/--home-url/--favicon 显式传入 + 打印 [执行]）
data/_countries-data.json（事实源）── html-gen table ──▶ demos/countries-table.html
```

### 4.2 用法

```shell
python3 scripts/tool-table-videos-syncer.py                     # 缺省 yaml + 预览（默认 dry-run，零写盘）
python3 scripts/tool-table-videos-syncer.py <yaml-path>         # 预览
python3 scripts/tool-table-videos-syncer.py <yaml-path> --dry-run
python3 scripts/tool-table-videos-syncer.py <yaml-path> --apply # 写盘：json → yaml 镜像 → html 重建
python3 scripts/tool-table-videos-syncer.py <yaml-path> --empty-video  # 只读列出 videos 为空的行（exit 0）
```

- `--dry-run/--apply/--empty-video` 三向互斥（同传 argparse exit 2）。yaml_path 缺省 = `cache/data/_countries-data.videos.yaml`（以项目根 PROJECT_ROOT 解析）。
- yaml 格式：`target: [{data: ...}, {html: ...}, {rebuild: {github_url, home_url, favicon}}]` + 每国条目 `country_zh/title/url/duration/platform`；country_zh 为外键（须匹配 json data[].country_zh）；**duration 必须引号包裹**（未引号 `6:55` 被 YAML 按 60 进制解析为 int 415）。
- 同步语义（v1.2 三态，源码命名）：`new_items`（url strip 后不存在 → append）/ `updates`（url 已存在 + yaml title 非空 + title 不同 → 全字段覆盖：title 直覆盖、duration **raw 判空**才覆盖、platform yaml→detect→保留既有）/ `skipped`（title 相同或空）。
- G 判定：new_items 与 updates 均空 → 统计提示 + exit 0 零写盘；任一非空继续（仅更新无新增也必须写盘）。
- 写盘安全三原则：F3 校验（任一 country_zh 缺失 → 清单 exit 1 零写盘）→ G 中断 → dry-run 为默认态；additive+覆盖不删除语义 + url 去重 = 幂等。
- E 重建：`subprocess.run([...html-gen.py, 'table', '-d', <data>, '-o', <html>, --github-url/--home-url/--favicon], shell=False)`；`[执行]` 先打印完整命令行。github_url 三级优先级：rebuild 配置 > extract_corner_url(旧 html) > 固定默认（https://github.com/imjaden/html-gen.cli）；空串 = 不传（禁用）。

### 4.3 favicon 默认注入（族 D，CL004）

- 四模板 head title 后 `<!--FAVICON-->` 占位；CLI 默认注入 `DEFAULT_FAVICON`（https://www.jaden.tech/static/img/favicon.png），`--favicon <url>` 覆盖，显式空串禁用。
- 优先级：CLI `--favicon` > env `HTML_GEN_FAVICON` > DEFAULT_FAVICON；**判断必须 `is not None`/truthy，勿 `or` 链**（空串回落 env/默认，HG-SEC-073）。
- table 子命令通用参数：`-d/--data`（required）、`--title`（优先级 CLI > JSON 顶层 title > '数据表格'）、`--subtitle`、`-o/--output`（CLI -o 或 JSON 顶层 output 二选一）、`--github-url/--home-url/--favicon`（env 兜底 + 显式空串禁用）。

## 5. 用法示例

```shell
# table 生成（JSON 顶层可含 title/subtitle/output）
html-gen table -d data/_countries-data.json -o demos/countries-table.html \
  --title "全球国家速查表（195 国）"

# videos 同步（三态增量）
python3 scripts/tool-table-videos-syncer.py                          # 预览（默认 dry-run）
python3 scripts/tool-table-videos-syncer.py cache/data/_countries-data.videos.yaml --apply
python3 scripts/tool-table-videos-syncer.py --empty-video            # 找 videos 为空的行
```

```yaml
# cache/data/_countries-data.videos.yaml（手工草稿示例）
target:
- data: data/_countries-data.json
- html: demos/countries-table.html
- rebuild: {github_url: "https://github.com/imjaden/html-gen.cli", home_url: "https://html-gen.cli.jaden.tech/", favicon: ""}

countries:
- country_zh: 缅甸
  title: 缅甸-散装缅甸
  url: https://v.douyin.com/-IIdHuXNL0o/
  duration: "6:55"        # 必须引号；int < 3600 按秒归一化（415 → "6:55"）
  platform: douyin        # 可省略 → detect_platform(url) 兜底
```

```jsonc
// data JSON 内嵌行数据示例（顶层 columns/data/options/title/subtitle/output）
{ "videos": [{ "title": "东帝汶-建国之路", "url": "https://v.douyin.com/ksBIqe1KmdM/", "duration": "6:02", "platform": "douyin" }] }
```

## 6. 关键决策（原文编号）

### 6.1 videos 字段（CL001，documents/archive/solutions-20260908/table-videos-design-v1.1-20260828.md，拍板 A1..G）

| 编号 | 决策 |
|:--|:--|
| A1 | 粒度 = 数组多视频：1 字段 = 视频对象数组 |
| B1 | 数据结构 = url/title/duration/platform，url 必填其余可选 |
| C1 | 点击行为 = 新标签 `window.open(url,'_blank','noopener,noreferrer')` |
| D1 | 折叠 = maxShow 可配（默认 3），超出「+N」 |
| E3 | 平台图标 = 预设映射 + 默认 emoji（douyin🎵 bilibili📺 youtube▶️ 默认📹） |
| F1 | 独立新类型 `col.type="videos"`，数据驱动，CLI 零改动 |
| G1 | countries 巴西行 2 条 douyin 视频入数据（联动） |
| RIG-001 | 分栏/expand 须 Array.isArray 特判（防 [object Object]） |
| RIG-002/003 | （并入 syncer：shell=False / 项目根路径基准） |
| HG-SEC-044 | platform 归一化 trim().toLowerCase() + 别名映射 |
| HG-SEC-045 | 长标题独立 `.video-pill` 类（截断不与 nowrap 冲突） |
| HG-SEC-046 | +N 展开不折叠回、跨 re-render 重置、stopPropagation |
| HG-SEC-047 | onclick url 转义 JSON.stringify + &quot;（沿用 actions 先例） |
| HG-SEC-052 | videos 从默认搜索键排除 |

### 6.2 syncer v1.1（CL002，documents/archive/solutions-20260908/table-videos-syncer-design-v1.1-20260829.md，拍板 A1..W1 + 决策 A..W）

| 编号 | 决策 |
|:--|:--|
| A1 | 格式 = 结构化 map，字段与 json 一致（country_zh/title/url/duration/platform） |
| B1 | yaml 留 cache/ 不入库（纯本地草稿）；入库仅同步后 json + 重建 html |
| C1 | platform = URL host 自动识别兜底（douyin/bilibili/youtube；回写写 json 现值） |
| D1 | PyYAML 入 requirements-dev.txt（仅 dev 依赖） |
| E2 | 重建 = 同步后自动 subprocess 调 html-gen.py table |
| F3 | 校验 = 国家键无匹配 → 清单报错 exit 1（写盘前全量校验，避免半写） |
| W1 | 回写 = 全局镜像：yaml countries 段整体重建为 json 全部 videos |
| G1 | 全存在 → 打印提示中断（幂等） |
| RIG-001/HG-SEC-054 | 必须 `yaml.safe_load`（禁 yaml.load，防任意代码执行） |
| RIG-002/HG-SEC-055 | subprocess 列表参数 shell=False |
| RIG-003/HG-SEC-056 | 相对路径以项目根为基准解析 |
| HG-SEC-058 | 脚本名修正 vides→videos 拼写（新建文件零迁移） |
| HG-SEC-061 | int 容错阈值 6000 → 3600（M:SS 上界 59:59） |
| FIND-001 | 共享文件污染（整文件 git add 纳入并行编辑）→ 有意保留，CL004 修订日志登记 |
| FIND-002 | E 重建丢 github-corner/favicon → extract_corner_url 透传 --github-url（0af421d + test_10） |

### 6.3 syncer v1.2（CL006，documents/archive/solutions-20260908/table-videos-syncer-design-v1.2-20260830.md，探讨确认 1B 2A 3A 4A + 1A 2A 3A）

| 编号 | 决策 |
|:--|:--|
| 3A/U | 更新触发判据唯一 = url 已存在 + yaml title 非空 + title ≠ json 既有 title → 全字段覆盖更新 |
| 2A | title 空不触发（防清空既有标题） |
| 1A/U1 | platform：yaml 有值用之；缺省 detect 兜底；detect 仍空 → 保留 json 既有值 |
| 2A/U2 | duration：yaml 非空才覆盖；空/缺省保留 json 现值（防 normalize_duration(None) 写 'None'） |
| 3A/4A/S | 统计：全包含提示加「yaml 检查 N 条 / 涉及 M 个国家」（去重口径与增量模型一致，畸形条目不计） |
| W | 回写维持全局镜像零改动（幂等闭环） |

### 6.4 favicon/URL/syncer 参数（CL004，documents/archive/solutions-20260908/html-gen-favicon-urlstate-syncer-design-v1.0-20260829.md）

| 编号 | 决策 |
|:--|:--|
| A1 | `<!--FAVICON-->` 占位 + 默认注入 + `--favicon` 覆盖/空串禁用 + env 兜底 |
| C1 | 默认 favicon = https://www.jaden.tech/static/img/favicon.png |
| 1B | rebuild 缺省 home_url = 站点根（https://html-gen.cli.jaden.tech/） |
| 2A | github_url 优先级 rebuild > extract_corner_url(旧 html) > 固定默认 |
| D1 | run_apply 显式传三参数 + `print('[执行] ' + join(shlex.quote...))` |
| E1 | URL 状态同步用 history.replaceState（不污染历史栈） |
| F1 | 分栏行标识 = filtered 下标 split=<n>（越界忽略） |
| G1 | 🔗 拷贝规范化 URL（navigator.clipboard + execCommand fallback + toast） |
| H1 | 搜索词随 300ms debounce 一起 replaceState |
| I2 | syncer 保留 positional yaml_path（nargs='?'）+ 加 --empty-video |
| J1 | empty-video 数据源 = yaml target.data 指向 json（无 yaml 参数用缺省路径） |
| K1 | empty-video 输出逐行「首字段 (次字段)」+ 底部计数 |
| 3A | --dry-run/--apply/--empty-video 三向互斥（exit 2） |
| 4A | 空字段显示 (空)，底部「共 N 条 videos 为空」 |
| L1 | yaml target 段可选 rebuild: {github_url, home_url, favicon} |

## 7. 已知坑

| # | 坑 | 出处/闭合 |
|:--|:--|:--|
| P1 | duration 缺失 → normalize_duration(None) 写字面 'None' 字符串 | OBS-002 → v1.2 U2 raw_duration 判空 + t18 护栏 |
| P2 | YAML duration 60 进制（未引号 6:55 → int 415） | int 容错仅 M:SS <3600（HG-SEC-061）；SyncerDumper 按需引号 |
| P3 | 数据快照漂移：cache yaml 手工草稿随时变；update@data 版本 bump 使多处断言过期 | HG-SEC-082；同步数据时一并同步测试断言（CL001 3 断言 + provinces backfill 列索引先例） |
| P4 | title 变更全字段覆盖三防 | title 空不触发 / 仅 duration·platform 不同不更新 / url+title 同跳过（幂等） |
| P5 | 循环变量命名 `target` 遮蔽 yaml target 段 → rebuild 配置静默丢弃 | df2e28c → 7dbaf4c（6 处）+ test_21 回归护栏 |
| P6 | split=<n> filtered 下标脆弱（sort/quickFilter 重排） | HG-SEC-075/076 → 两者触发时 closeSplit；defaultFilter 下跳过 |
| P7 | 空串禁用 vs None（`or` 链使空串回落 env/默认） | HG-SEC-073/078 → is not None / truthy 判断 |
| P8 | URL q 手工 decode 二次解码损坏字面 % + URIError | HG-SEC-074 → 统一 URLSearchParams set/get |
| P9 | split 预览/expand 渲染 videos 成 [object Object] | HG-SEC-043 → Array.isArray 特判 + test_07 |
| P10 | platform 未归一化（抖音/B站）落默认 📹 | HG-SEC-044 → trim().toLowerCase() + 别名表 |
| P11 | onclick URL 注入面 | actions 先例 → JSON.stringify + &quot; 转义（HG-SEC-047） |
| P12 | 无 searchFields 表默认搜索含 videos（String(array) 噪音） | HG-SEC-052 → 渲染分支排除 |
| P13 | body.click() 在 clickMode=modal 误触表格行 | quickfilter D5 impl fix → classList.remove('show') |
| P14 | E 重建丢 github-corner/favicon | FIND-002 → extract_corner_url + rebuild 三键（CL002 → CL004 闭合） |
| P15 | 共享文件污染（git add 整文件纳入并行会话编辑） | FIND-001 模式；提交前核 diff 范围 |
| P16 | countries demo 默认隐藏 6 列（含 videos） | FIND-001 有意保留；⚙️ 可开启/分栏全列渲染不受影响 |

## 8. 差异与待核记录

- `.video-pill` CSS 已从设计期 `word-break:break-all` 演进为现行 `white-space:nowrap; overflow:hidden; text-overflow:ellipsis`（成因待核）。
- shareBtn 图标设计写作 🔗，现行实现为 `↗️`（行为一致；成因待核）。
- `data/_phase2-demo.json` / `demos/phase2-demo.html`（quickfilter 测试载体）现仓已不在；现行 data/ 有 `_table-features-demo.json`（疑为后继，待核）。
- 设计 D6 一处路径 `demos/countries/countries-table.html` 为文档笔误（实际根路径 `demos/countries-table.html`）。

## 9. 参考文档

- 保留原位：features.md、layout-table.html、html-gen.py、scripts/tool-table-videos-syncer.py、data/_countries-data.json、demos/countries-table.html、review-log.md / .review-level.yaml（历史不追改）。
- **源码引用面（已随归档同步至 archive 路径，2026-09-08）**：scripts/tool-table-videos-syncer.py docstring L21-23 引 3 份设计（syncer v1.2/v1.1 + favicon §5）；tests/test_sync_videos.py docstring L4 引 table-videos-syncer-design-v1.1（§5 测试计划）；tests/test_url_state.py docstring L5 引 favicon 设计 §6。
- 本族过程文档（23 份）已归档（2026-09-08 执行） → `documents/archive/{solutions,root,review}-20260908/`：

| 素材 | 归档路径 | 归档桶 |
|:--|:--|:--|
| cmd-f-search / table-actions 设计（族 A） | documents/archive/root-20260908/cmd-f-search-design-v1.0-20260712.md · documents/archive/root-20260908/table-actions-design-v1.0-20260712.md | root |
| quickfilter 设计 / verify | documents/archive/solutions-20260908/table-quickfilter-default-design-v1.0-20260806.md · documents/archive/root-20260908/verify-prompt-quickfilter-20260808.md | solutions / root |
| quickfilter 设计评审 / 实现评审 | documents/archive/review-20260908/table-quickfilter-default-{review-v1.0,implementation-review-v1.0}-20260808.md | review |
| videos 设计 v1.1（CL001） | documents/archive/solutions-20260908/table-videos-design-v1.1-20260828.md | solutions |
| videos 设计评审/复审/实现审计 | documents/archive/review-20260908/table-videos-{design-review-v1.0,design-rereview-v1.1,impl-audit-v1.1}-20260828.md | review |
| syncer 设计 v1.1（CL002） | documents/archive/solutions-20260908/table-videos-syncer-design-v1.1-20260829.md | solutions |
| syncer v1.1 评审/复审/审计 | documents/archive/review-20260908/table-videos-syncer-{design-review-v1.0,design-rereview-v1.1,impl-audit-v1.1}-20260829.md | review |
| syncer 设计 v1.2（CL006） | documents/archive/solutions-20260908/table-videos-syncer-design-v1.2-20260830.md | solutions |
| syncer v1.2 评审 / 审计 / process prompt ×3 | documents/archive/review-20260908/table-videos-syncer-v1.2-{design-review-v1.0,impl-audit-v1.0,design-review-prompt,dev-impl-prompt,impl-audit-prompt}-20260830.md | review |
| favicon/urlstate/syncer 设计（CL004） | documents/archive/solutions-20260908/html-gen-favicon-urlstate-syncer-design-v1.0-20260829.md | solutions |
| favicon 设计评审 / 实现审计 | documents/archive/review-20260908/html-gen-favicon-urlstate-syncer-{design-review-v1.0,impl-audit-v1.0}-20260829.md | review |
