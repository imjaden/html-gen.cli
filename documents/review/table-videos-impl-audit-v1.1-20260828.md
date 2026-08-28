# A 型表格 videos 视频字段 — 实现审计报告 v1.1

> 日期: 2026-08-28
> 项目路径: ~/CodeSpace/html-gen.cli
> 聚焦: HTML-GEN-CL001 ｜ 设计: `documents/solutions/table-videos-design-v1.1-20260828.md`（99cede3）｜ 设计评审: d02cfc5 CONDITIONAL 85/B → 2a49d6e 复审 PASS 95/A
> 实施 commit 链（5+1 个）: 45bf232 feat@table / a42331e sync@demos / a9e30fa test@table / 18199be fix@tests / 2b3c997 docs@table / a3f783e docs@table / 6b8a4c1 fix@data（ops 核查修正）
> review维度: 验收清单 §8 逐项 / 设计合规（v1.1 规格）/ 安全 / 治理 / 数据
> review者: Security Reviewer (L2, implementation-audit)

## 裁决

**PASS — 100/100 (A) — 闭环，转 push**

设计 v1.1 全部 8 项验收清单 + 4 项设计合规 + 安全 + 治理 + 数据全部核验通过：无 🔴/🟡，1 项 🟢 观察（HG-SEC-053，非阻断）。实施链 7 commits 类型规范、CLI 零改动、196 全量回归绿、巴西行 2 条 douyin 视频（含 ops 修正长标题）运行时实测可见。

## 一、验收清单 §8 逐项核对

| # | 验收项 | 证据（运行时观察） | 结果 |
|:-:|:---|:---|:---:|
| 1 | type=videos 列渲染 pill 组（图标+标题+时长） | test_01：pill.text == `🎵 巴西建国史 (8:37)`；countries 实载巴西行 pill text == `🎵 每天了解一个国家，巴西 (3:22)` | ✅ |
| 2 | maxShow 折叠 +N，点击展开（不折叠回/跨 re-render 重置/stopPropagation） | test_02：maxShow=2+3 视频 → `+1`；点击后 3 pill 全显、+N 消失（不折叠回）；搜索 re-render 后回到 2 pill + `+1`；代码 `expandVideos` onclick 带 `event.stopPropagation()`，展开隐藏 +N 显示 `.video-rest` | ✅ |
| 3 | 点击 pill 新标签页打开（noopener,noreferrer；onclick 转义 JSON.stringify+&quot;） | test_03：拦截 window.open 断言 (url, `_blank`, `noopener,noreferrer`) 精确匹配；代码 `renderVideoPill` 用 `JSON.stringify(String(url)).replace(/\"/g,'&quot;')`；countries 实载 onclick 含 `event.stopPropagation();window.open("https://v.douyin.com/8KyFzcfoH68/",'_blank','noopener,noreferrer')` | ✅ |
| 4 | 平台图标映射（douyin/bilibili/youtube/默认📹 + 归一化 trim().toLowerCase()） | test_04：douyin→🎵 / 其他平台→📹 / 抖音(别名)→🎵 / YouTube(大小写)→▶️ / bilibili→📺；代码 `videoPlatformIcon`：`String(platform).trim().toLowerCase()` + VIDEO_PLATFORM_ICONS 映射 | ✅ |
| 5 | 空/缺失 videos 渲染空单元格 | test_05：无字段行与 videos=[] 行 td.text == `''` 且无 pill；有 videos 行正常渲染 | ✅ |
| 6 | countries-table 巴西行 2 条 douyin 视频可见（title 完整，含 ops 修正后的长标题） | Selenium 实载 demos/countries-table.html 搜索「巴西」：1 行，videos 列 2 个可见 pill —— `🎵 每天了解一个国家，巴西 (3:22)` + `🎵 巴西建国史——巴西如何从创业成功走向贫穷漩涡 (8:37)`；生成 HTML grep 双 title/双 url 各 1 命中 | ✅ |
| 7 | test_videos.py 8 用例 + 回归全绿 | `pytest tests/test_videos.py tests/test_countries_table.py -q -n 0` → **21 passed**（8+13）；全量 `pytest tests/ -q -n 4` → **196 passed in 35.33s** | ✅ |

## 二、设计合规（对照 v1.1 规格）

| # | 规格项 | 实现证据 | 结果 |
|:-:|:---|:---|:---:|
| 1 | searchKeys 排除 videos 列（无 searchFields 表） | layout-table.html:432-433：`COLUMNS.filter(c => c.type !== 'actions' && c.type !== 'videos' && c.key)`；test_08：仅命中 videos title 的词不筛出、数组 String 噪音不误匹配、普通字段正常筛出 | ✅ |
| 2 | split/expand Array.isArray 特判（勿 [object Object]） | `renderSplitPreview`（layout-table.html:1071-1075）与 expand detail（:600-606）均 `Array.isArray(v) && c.type === 'videos'` → `renderVideoListHtml` 逐条渲染；test_07：分栏预览出现双 title 文本、断言无 `[object Object]`、url 链接带 noopener,noreferrer | ✅ |
| 3 | .video-pill 独立类（max-width:180px + white-space:normal + word-break:break-all） | layout-table.html:42-44 `.data-table .video-pill`：`max-width:180px; white-space:normal; word-break:break-all`；与 .cell-pill nowrap 独立；生成 HTML 内联 CSS 同样命中 | ✅ |
| 4 | CLI 零改动 | 实施链 7 commits 无一触碰 html-gen.py（`git log -8 -- html-gen.py` 无 videos 提交）；45bf232 仅 layout-table.html +92/-4 | ✅ |

## 三、安全

| 项 | 结论 |
|:---|:---:|
| window.open noopener,noreferrer（pill + split/expand url 链接两处） | ✅ 与 :591 actions 先例一致，无 reverse tabnabbing |
| escapeHtml 文本路径 | ✅ title/duration/platform 经 `escapeHtml(videoPillLabel(v))`；url title 属性经 escapeHtml |
| onclick 转义 | ✅ `JSON.stringify(url).replace(/\"/g,'&quot;')`（pill 与 split/expand 链接两处均沿用） |
| 无新执行面 | ✅ 无子进程/无新依赖/CLI 零改动；videos 数据来自项目自维护数据文件 |
| XSS 面 | ✅ url 注入面与既有 actions 先例等价；`renderVideoPill` 对非对象/缺 url 直接返回空串 |

## 四、治理

| 项 | 结果 |
|:---|:---:|
| commit 规范 type@scope | ✅ 7/7：feat@table / sync@demos / test@table / fix@tests / docs@table ×2 / fix@data，全小写 |
| features.md 同步 | ✅ L120 Videos 视频列功能行 + L156 col.type 枚举含 videos |
| AGENTS.md 同步 | ✅ L228「当前 196 tests（21 文件…test_videos 8）」+ L253 目录注释 196 tests；实测 21 文件 / 196 defs 一致 |
| 196 tests 数一致 | ✅ `grep -c 'def test_'` = 196，全量 196 passed |
| 数据漂移 3 断言已同步 | ✅ 18199be：塞尔维亚 region_tags 3 值 / history-strategy 7 列表头 + tds[7]→tds[5] / test_12 数据源换 _countries-data.json；另同步 test_provinces_table backfill 列索引（len(tds)-1→-2、-3→-4，videos 追加影响）；全量回归验证修复真实生效 |
| git 状态 | ✅ clean，6b8a4c1 为 HEAD，ahead github/main 12（含设计评审 2 commits） |

## 五、数据（G 联动）

| 项 | 验证 |
|:---|:---|
| 列配置 | data/_countries-data.json columns 末尾 `{"key":"videos","label":"视频","type":"videos","width":"260px","preview":true,"videos":{"maxShow":2}}`；18 列 / 195 行 |
| 巴西行 2 视频 | title/url/duration/platform 四项完整：`每天了解一个国家，巴西`(v.douyin.com/8KyFzcfoH68/, 3:22, douyin) + `巴西建国史——巴西如何从创业成功走向贫穷漩涡`(v.douyin.com/Y6VCrD4QQg8/, 8:37, douyin) —— 第 2 条为 ops 6b8a4c1 修正后的完整长标题 |
| 其余 194 行 | 0 行含 videos 字段 → 空单元格（test_05 语义覆盖） |
| 产物同步 | demos/countries-table.html 已重生成（title 与 JSON 顶层一致「全球国家速查表（195 国）」）；demos/demos-index.html 同步 |

## 六、发现项

| # | Severity | 问题 | 位置 | 状态 |
|:---|:---:|:---|:---|:---:|
| HG-SEC-053 | 🟢 | test_countries_table.py（13 用例）无巴西行 videos 断言 —— countries 页面巴西行 2 pill 渲染仅靠本次审计运行时抽查，无提交级回归护栏；未来若从旧 data JSON 重生成 countries-table.html 且丢失 videos 列，全量测试仍绿 | tests/test_countries_table.py | record（建议后续补 test_15：搜索巴西 → 末列 2 个可见 pill + 长标题断言） |

附注（不计发现）：test_videos.py 临时文件写入 tests/ 目录（`_tmp_videos_{ts}.json/.html`，tearDown 清理，本次实测无残留）——与 test_table_features.py `_tmp_desc_empty.html` 项目既有惯例一致，不视为缺陷。

## 七、评分

```
基准分: 100
  （无 🟡/🔴 扣分项）
  HG-SEC-053  🟢 观察项（不计分）
────────────────────────
得分: 100 → A → PASS
```

## 八、结论

**PASS（100/A）— 闭环。**

- 设计 v1.1 验收清单 §8 7/7 全部运行时核验通过（Selenium + 全量回归），无一项依赖源码分析背书
- 4 项设计合规精确命中：searchKeys 排除 / split+expand Array.isArray 特判 / .video-pill 独立类 / CLI 零改动
- 安全路径与 :591 actions 先例完全一致（noopener,noreferrer + JSON.stringify &quot; 转义 + escapeHtml），无新执行面
- 治理 6/6：commit 规范、features.md/AGENTS.md 同步、196 tests 一致、漂移断言真实修复、git clean
- 唯一 🟢 观察（HG-SEC-053）为测试覆盖建议，非缺陷，不阻断闭环

**后续**：PASS → 完成闭环信号，复盘 md 由 ops 生成；push 授权由 review profile 执行（github/main）。
