# html-gen favicon 默认注入 + table URL 状态分享 + syncer 参数体系 — design review v1.0

> 日期: 2026-08-29
> 文件: documents/solutions/html-gen-favicon-urlstate-syncer-design-v1.0-20260829.md
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 待 push commit: 9a9c608（设计 v1.0，HTML-GEN-CL004）
> review维度: 合理性 / 严格性 / 安全性
> review类型: design-document-review（L2）

## 数据验证

逐条实测核对设计文档的行号锚点与可行性声明（非空谈）：

| 验证项 | 方法 | 结果 |
|:-------|:-----|:-----|
| corner_args 位置 | read_file html-gen.py:98-102 | ✅ 精确命中（gh/home 两键 env 兜底） |
| argparse --github-url/--home-url | grep html-gen.py | ✅ 四子命令 doc L773-774 / slide L782-783 / table L791-792 / knowledge L802-803（设计写 "L767-800 附近"，内容定位正确） |
| 四处 inject 调用 | read_file html-gen.py | ✅ cmd_doc L314-315 / cmd_slide L384-386 / cmd_table L439-445 / cmd_knowledge L489-494（设计写 "L315/386/445/494 附近"） |
| inject() 空串替换语义 | read_file html-gen.py:42-49 | ✅ `template.replace('<!--KEY-->', str(value))`，空串 → 占位符移除，`favicon=''` 可正确禁用 |
| 四模板 head 结构 | grep layout-*.html | ✅ 四模板均 L6 `<title><!--TITLE--></title>` + L7 stylesheet；FAVICON 占位插在 L6 后可行 |
| syncer run_apply / argparse / yaml 解析 | read_file syncer.py | ✅ run_apply L173-219（重建 cmd L209-218）、argparse L222-231、yaml safe_load L233-251（设计行号精确） |
| parse_target 兼容 rebuild 子键 | read_file syncer.py:58-67 | ✅ list/dict 均 `out.update(item)` 合并，`{rebuild: {...}}` 作为第三列表项 → `target.get('rebuild')` 可取 |
| layout-table 状态/函数行号 | grep + read_file layout-table.html | ✅ 状态变量 L351-364、applyFilters L420、activateSplit L1011、splitNav L1027、closeSplit L1032、searchInput input L1287、switchTab L1294-1295、header 工具栏 L262-281（searchInput L269）全命中 |
| 缺省 yaml 路径存在性 | ls cache/data/_countries-data.videos.yaml | ✅ 存在（4458 字节，2026-08-29） |
| 需求 2 目标数据形态 | python3 -c 读 data/_countries-data.json | ✅ 195 行，tabs（all/asia/europe/americas/africa/...）+ 搜索 + 分栏均具备，URL 状态分享可行 |
| DEFAULT_FAVICON 与存量产物一致 | grep demos/*.html | ✅ 34 文件含 `rel="icon"`；URL 三变体：干净 11 / `?=20260706` 4 / `?=20260705` 2（设计选干净 URL 为默认，方向正确并顺带归一化） |
| 测试文件现状 | ls tests/ | ✅ test_sync_videos.py（10 用例）、test_json_output.py（11 用例）、test_table_features.py 存在；test_url_state.py 不存在（新建，符合 5A） |
| 测试断言风格 | read_file test_sync_videos.py / test_json_output.py | ✅ subprocess + assertIn（存在性断言，非精确全文比对），favicon 新增不影响既有用例；test_sync_videos 用 HTML_GEN_STUB 桩 |
| 设计文档命名与 frontmatter | ls documents/solutions/ + head 兄弟文档 | ✅ 命名 kebab-case `{topic}-design-v1.0-20260829.md`；兄弟 CL003 设计文档同为「# 标题 + 内联元数据」无 YAML frontmatter，属项目既定风格，非违规 |

## 合理性评估

设计整体架构自然、范围适中，三项需求与决策一一对应：

1. ✅ favicon 三层优先级（CLI > env > DEFAULT）与现有 github-url/home-url 的 corner_args 模式对齐，复用 `inject()` 注入机制，最小侵入。
2. ✅ syncer 重建显式传三参数 + 打印 `[执行] shlex.quote` 命令行，直接闭合 FIND-002（favicon）与既有 corner 透传，`subprocess.run(cmd, shell=False)` 保持 RIG-002。
3. ✅ URL 状态分享采用 `history.replaceState`（不污染历史栈，刷新/分享均恢复）+ `syncUrlState()` 统一封装，切面清晰。
4. ✅ 需求→决策映射完整：需求 1→§3（A1 B1 C1 D1 + 1B 2A）、需求 2→§4（E1 F1 G1 H1）、需求 3→§5（I2 J1 K1 L1 + 3A 4A）、测试→§6（5A）。无跨节不一致。

## 严格性评估

| # | 项 | 评估 |
|:-:|:---|:---|
| 1 | 优先级 / 禁用语义 | ❌ HG-SEC-073（🟡）——`--favicon ""` 禁用未钉死 None vs "" 区分 |
| 2 | 边界 / 异常态 | ❌ HG-SEC-074（🟡）——URL q 编解码对称性与 URIError 未钉死 |
| 3 | 状态管理 | ❌ HG-SEC-075（🟡）——split 下标与 sort/quickFilter 交互未说明 |
| 4 | 初始化挂钩 | ⚠️ HG-SEC-076（🟢）——恢复流程未指定 init() 挂钩点与 defaultFilter 优先级 |
| 5 | 命名一致性 | ⚠️ HG-SEC-077（🟢）——render_* 实为 cmd_* |
| 6 | CLI 签名 | ✅ --favicon 三态（URL/空串/缺省）在 §3.1 明确；--empty-video 在 §5.1 明确 |
| 7 | 向后兼容 | ✅ §5.3 现有调用不变；URL 无参数行为不变；favicon 默认注入与存量产物对齐 |

## 安全事项

🟡 HG-SEC-073 — `--favicon ""` 禁用语义依赖 None/"" 区分，未显式指定

`corner_args`（L98-102）现有 `getattr(args,'github_url',None) or os.environ.get(...)` 的 `or` 链若照搬到 favicon（含非空 DEFAULT_FAVICON），`--favicon ""`（falsy）会落到 env/DEFAULT，禁用失效——与设计 A1「传空串禁用」承诺冲突。建议明确 `favicon = args.favicon if args.favicon is not None else (os.environ.get('HTML_GEN_FAVICON') or DEFAULT_FAVICON)`。

🟡 HG-SEC-074 — URL q 编解码对称性与 malformed 编码异常未钉死

§4.1 写「encodeURIComponent 编码」，§4.3 写「解析 location.search（URLSearchParams）」+「decodeURIComponent 后」：URLSearchParams.get() 已自动解码，再 decodeURIComponent 会二次解码（q 含字面 `%` 时损坏）；且畸形 % 编码使 decodeURIComponent 抛 URIError（未捕获 → 恢复中断）。建议读写统一走 URLSearchParams（`set` 写入 / `get` 读取，自动编解码、不抛异常），删除手工 encode/decode。

🟡 HG-SEC-075 — split=<n>（filtered 下标）与 sort/quickFilter 交互未说明

`filtered` 被 sort 就地重排（layout-table.html L459 `filtered.sort`）且被 quickFilter 收窄（L440），而排序/quickFilter 均明确不入 URL（§二 记观察）。「排序找行 → 开分栏 → 分享」是常见路径，分享方在排序/筛选态拿到的 `split=<n>` 在接收方默认态会指向不同行。建议三选一：(a) sort/quickFilter 时 closeSplit；(b) split 改用稳定标识（DATA 下标或 row 主键）；(c) 设计显式声明「split 仅在默认排序 + 无 quickFilter 下语义有效」。

🟢 HG-SEC-076 — 恢复流程 init() 挂钩点未指定

§4.3 列出恢复步骤但未指明在 init()（L1388-1416）的插入点与 defaultFilter（quickFilterBy L1412）先后：tab 须在 buildTabs（L1405）前、q 须在 render（L1408）前、split 须在 render 后（需 filtered + DOM rows）。defaultFilter 仅 drama 历史表使用，非 countries 主目标，风险低，但 URL 状态 vs defaultFilter 的优先级应明确。

🟢 HG-SEC-077 — 函数命名漂移

§3.1 写「render_doc/slide/table/knowledge」，实际函数名为 cmd_doc/cmd_slide/cmd_table/cmd_knowledge（L258/327/397/461）。非功能缺陷，实施时按 cmd_* 定位。

🟢 HG-SEC-078 — rebuild 三键空串语义未定义

2A/L1 仅定优先级（rebuild > extract > 默认），未定 rebuild.github_url="" 是「禁用 corner（传 --github-url ""）」还是「回落下一优先级」。建议与 html-gen.py 隐私语义对齐：空串 = 禁用。另注：demo --rebuild / 下次重建会将存量 cache-busting favicon URL（`?=20260705/06`）归一化为干净 DEFAULT_FAVICON，属正向收敛。

🟢 HG-SEC-079 — test_10 桩需扩展或改断言路径

test_sync_videos.py 的 HTML_GEN_STUB 仅识别 `--github-url`（L39-41），5A-2 说「mock subprocess 或断言打印行」二选一未定。建议锁定「断言 `[执行]` 打印行含 `--github-url` `--home-url` `--favicon` 三参数」路径，免改桩。

## 评分

| 编号 | 严重度 | 扣分 |
|:---|:---:|:---:|
| HG-SEC-073 | 🟡 | -5 |
| HG-SEC-074 | 🟡 | -5 |
| HG-SEC-075 | 🟡 | -5 |
| HG-SEC-076..079 | 🟢 | 0（记录） |

得分: 100 - 15 = **85 / 100 → A**

## 结论

**PASS（85/A）** — 设计架构正确、范围适中、行号锚点全部实测命中，安全面（URL 参数无 innerHTML 注入、tab 白名单、split 越界、shell=False、safe_load）完整。3 项 🟡 为非阻断的规格收紧项（一处一行即可在实施中折叠），4 项 🟢 为记录。无 🔴 阻塞项，可进入实现阶段。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | `--favicon ""` 禁用：明确 `args.favicon is not None` 判断，勿用 `or` 链 | 严格性 🟡 HG-SEC-073 |
| □ | URL q 读写统一 URLSearchParams，删除手工 encode/decode | 严格性 🟡 HG-SEC-074 |
| □ | split 下标 vs sort/quickFilter：三选一（closeSplit / 稳定标识 / 显式声明限制） | 严格性 🟡 HG-SEC-075 |
| □ | 恢复流程 init() 挂钩点 + defaultFilter 优先级 | 严格性 🟢 HG-SEC-076 |
| □ | 设计文档 render_* → cmd_* 命名更正 | 严格性 🟢 HG-SEC-077 |
| □ | rebuild 三键空串语义（空串=禁用） | 严格性 🟢 HG-SEC-078 |
| □ | 测试锁定「[执行] 打印行断言」路径 | 测试 🟢 HG-SEC-079 |
