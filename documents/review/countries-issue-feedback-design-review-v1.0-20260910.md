# A 型表格 GitHub Issue 反馈通道 设计 — review 报告 v1.0

> 日期: 2026-09-10
> 文件: documents/solutions/countries-issue-feedback-design-v1.0-20260910.md
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 待 push commit: 4e14795（docs@design: GitHub Issue 反馈通道设计 v1.0 · HTML-GEN-CL009）
> review 维度: 合理性 / 严格性 / 安全性
> 前置: HTML-GEN-CL002 / CL004 / CL006（table 模板 + videos 同步器 + rebuild 三参数）已闭环
> 模式: 独立（不入调度队列）；试点 demos/countries-table.html ← data/_countries-data.json

## 数据验证

| # | 验证项 | 方法 | 结果 |
|:-:|:-------|:-----|:-----|
| 1 | layout-table.html 占位符清单（§4 称 11 个） | grep `<!--[A-Z_]+-->` | ✅ 11 个：TITLE/FAVICON/GITHUB_CORNER/HOME_LINK/SEARCH_PLACEHOLDER/FILTERS/DESCRIPTION/COLUMNS/DATA/TABS/OPTIONS（TITLE 出现 2 次 L6/L274，唯一 key 数 11） |
| 2 | _SCRIPT_KEYS 含 `options`、inject() 转义 | read html-gen.py:39,42-49 | ✅ `_SCRIPT_KEYS={'columns','data','tabs','options','groups','items'}`；script 上下文 `</`→`<\/` 转义现成。§4.2「零新增占位符」成立 |
| 3 | cmd_table options 注入路径 | read html-gen.py:491 | ✅ `options = raw.get('options', {})` → json.dumps 注入。§5「写回 options.feedback.repo 随 OPTIONS 注入」可行 |
| 4 | argparse table 无 --feedback-repo | read html-gen.py:862-870 | ✅ 现仅 --github-url/--home-url/--favicon；需新增 --feedback-repo（§5） |
| 5 | renderSplitPreview | read layout-table.html:1076-1110 | ✅ 精确匹配；header 由 ▲▼ 标题 ✕ 构成（L1081-1084），§4.1 改动点准确 |
| 6 | activateSplit/openSplitAt/splitNav/closeSplit | read layout-table.html:1039-1074 | ✅ activateSplit(row,idx) L1039 / openSplitAt(idx) L1056 / splitNav L1057 / closeSplit L1062 精确；§4.3 形参/生命周期描述准确 |
| 7 | handleRowClick split 分支 | read layout-table.html:846 | ✅ `activateSplit(row, idx)`（split 模式行点击，§4.3「行点击入口不传列」所指） |
| 8 | URL 恢复 ?split=N + syncUrlState | read layout-table.html:1461,1489-1494,1030-1037 | ✅ `_params.get('split')` L1461；恢复 `activateSplit(filtered[n], n)` L1492（不传列）；syncUrlState L1030 |
| 9 | CSS .sp-nav/.sp-close | read layout-table.html:178-181 | ✅ .sp-close L178 / .sp-nav L179-181；无 .sp-feedback（新增，§4.1） |
| 10 | .github/ 目录现状 | ls .github | ✅ 不存在（0 文件），§6 全部需新建（data-fix.yml/config.yml/label） |
| 11 | data/_countries-data.json 顶层 + options | python3 json.load | ✅ 顶层 `[title,columns,data,tabs,options]`；options=`{pageSize:50,exportCSV:true,searchFields:[...]}`；无 `output` 无 `feedback`（§2.1 需新增 options.feedback） |
| 12 | 列 keys 与 editable/protected 覆盖 | python3 取 column keys | ✅ 18 列（country_zh…note + videos）；§8 editable 17 + protected[videos] 1 = 18，**精确全覆盖无遗漏列** |
| 13 | videos yaml 实际路径 + target 段 | read cache/data/_countries-data.videos.yaml | ✅ 路径为 `cache/data/`（非 `data/`）；顶层 `{target, countries}`；target=`[{data},{html}]` 无 rebuild 段（§2 V1/§12 用正确路径） |
| 14 | videos syncer rebuild 参数集 | read tool-table-videos-syncer.py:216-244,324-338 | ✅ resolve_rebuild_args 仅 github_url/home_url/favicon 三键（**不含 feedback-repo**）；subprocess 列表 + shell=False + [执行] 打印（RIG-002） |
| 15 | JSON 无尾换行 | od -c tail | ✅ 末字节 `}` 无 `\n`；videos syncer 用 `json.dump(indent=2)` 亦无尾换行 → §7.2 往返逐字断言成立 |
| 16 | 全量测试当前数 | pytest --collect-only | ✅ **268 tests**（0.09s），§9「268 → ~279」（TC-01..11）精确 |
| 17 | features.md CLI 参数清单 | grep features.md | ✅ 存在（16581B）；L23-30 列 table/knowledge `-o/--output` 等，L261「CLI 参数 | 15」——--feedback-repo 需同步（15→16） |
| 18 | html-gen-cli-handbook 隐私参数枚举 | grep L48 | ✅ L48「通用隐私参数（doc/slide/table/knowledge 共用）：--github-url/--home-url/--favicon」——table-only --feedback-repo 需补，§10 未列此手册 |

## 合理性评估

| # | 项 | 评级 | 说明 |
|:-:|:---|:----:|:-----|
| 1 | 需求闭环（页面→Issue→回写→重建） | ✅ | 静态站无后端的约束下，跳转 Issue Form 预填 + 本地脚本解析回写是最小可行闭环；H1 先人工跑再评估 cron 稳妥 |
| 2 | A1…V1 决策跨节一致 | ✅ | §2 → §3（D1 预填字段集/§3.2 URL 参数）、§4（A1/A0-1/O1/K1 模板与配置）、§5（K1 三级取值）、§6（C1/T1 表单）、§7（F1/G1/I1/H1/N1 脚本）、§8（S1 配置）、§12（L1/Q1/U1/V1 复用）。映射无矛盾 |
| 3 | case 配置落 options.feedback（§2.1） | ✅ | 复用即随案例自描述，零新增占位符；与 §5 JSON 三级取值自洽 |
| 4 | 复用分层（§12） | ✅ | 模板按钮/URL/CLI 参数零改动、数据 JSON 加一行、config 增 target、表单共用——分层成本递增清晰；doc/knowledge/slide 无「数据行」概念排除复用正确 |
| 5 | V1 不复用 videos yaml | ✅ | 实测 videos syncer run_apply 写 `{'target': doc.get('target'), 'countries': …}`，任何非 target/countries 顶层键必被丢弃；且 resolve_rebuild_args 不读/不发 feedback 键 → 塞进去也不生效。V1 理由充分且被源码佐证 |
| 6 | 行唯一定位（E1） | ✅ | join key=country_zh（195/195 唯一，实测 row0 含 country_zh）+ country_en 二次校验 + 0/多命中拒绝；无 ISO 码不新增（E2 二期）合理 |
| 7 | 重建参数漂移治理（§8 rebuild.args） | ✅ | 显式 flat list 固化 github-url/home-url/feedback-repo，比 videos syncer 的 dict 三级兜底更严（杜绝 FIND-002 同类丢失） |

## 严格性评估

| # | 项 | 评级 | 说明 |
|:-:|:---|:----:|:-----|
| 1 | 六项校验完备 | ✅ | page/dataset/row 唯一/field 白名单/类型/suggested 非空 + 幂等 + 冲突取最新——覆盖误写主路径；videos 永远拒绝（protected）双写风险堵死 |
| 2 | JSON 往返逐字 | ✅ | 实测现文件 indent=2 无尾换行（数据验证 #15）；`json.dumps(ensure_ascii=False, indent=2)` 与 videos syncer 同款，断言可执行 |
| 3 | 退出码三态 | ✅ | 0/1/2 语义清晰，与 argparse 互斥组（--list/--dry-run/--apply）自洽 |
| 4 | 一致性校验（§7.5） | ✅ | 启动比对 JSON options.feedback 与 config target，warning 不阻断——复用接入漂移点有护栏 |
| 5 | 测试计划 §9 可行性 | ✅ | TC-01..05（模板渲染/URL 构造）Selenium 可测（复用 test_corner_privacy 的 subprocess + test_countries_table 的 Selenium 基建）；TC-06..11（脚本解析/校验/写回）unittest + subprocess + mock gh（复用 test_sync_videos 的临时目录 + html-gen 桩模式）——全覆盖六校验 + 幂等 + 冲突 + dry-run 零写盘 |
| 6 | 文档同步面 §10 完整性 | 🟡 HG-SEC-113 | 漏 `documents/html-gen-cli-handbook-v1.0-20260908.md`（L48 隐私参数枚举，--feedback-repo 同语义需补）；features.md L261「CLI 参数 15」需 15→16（§10 仅「若有则同步」弱化措辞，实为已确认存在） |
| 7 | 跨重建漂移（videos syncer） | 🟡 HG-SEC-111 | 见下「安全/一致性」详述 |

## 安全事项

- **URL 构造安全** ✅：§3.2/§4.4 全值 encodeURIComponent、window.open 带 `noopener,noreferrer`、repo 经 json.dumps 注入（无法闭合 JS 字符串）；单字段约 160 字符远低于上限。
- **数据写回安全** ✅：白名单(editable)+类型校验+protected(videos)+行唯一定位(0/多命中拒绝)+冲突取最新+dry-run 先行——层层兜底，误写面收窄到「白名单字段+类型合法+人工 dry-run 确认」。
- **无凭据泄露** ✅：repo 三级取值、默认不注入（K1），与 --github-url 隐私语义对齐；脚本仅依赖本机 gh 登录态。
- **解析零新依赖** ✅：脚本仅标准库 + PyYAML（yaml.safe_load，RIG-001 同款）；运行时 html-gen 零依赖不受影响。

🟡 HG-SEC-110 — gh 调用 subprocess 形态未显式（shell 注入面）

§7.2 step 2（`gh issue list`）/ step 8（`gh issue comment`/`gh issue close`）未像 step 7 那样显式规定 list-form + shell=False。step 8 的 comment body 含用户可控数据（field 名、旧值、新值、建议值），若以 shell=True + 字符串拼接调用 gh，存在命令注入面。§13 风险表只提「gh 未登录 → exit 1」，未提 gh 的 shell 安全。

修复建议：实现统一 `subprocess.run([...], shell=False)`（list-form，与 videos syncer RIG-002 同款），comment body 作为独立 argv 元素传入（gh 自身会处理参数）；`--json` 输出用 `gh ... --json` 结构化读取而非文本解析。

🟡 HG-SEC-111 — 跨重建漂移：videos syncer 重建会丢失反馈按钮

实测 videos syncer 的 `resolve_rebuild_args`（tool-table-videos-syncer.py:216-244）仅发 `--github-url/--home-url/--favicon` 三键，**永不发 `--feedback-repo`**。而 §2.1 定义 options.feedback 仅 `{dataset,key,altKey}`（repo 不在 JSON），repo 由 CLI/env 注入。因此 videos syncer 每周重建 countries-table.html 时：cmd_table 读到的 options.feedback 无 repo → FEEDBACK=false → 反馈按钮消失。§12「任意 html-gen table 页面重建时加 --feedback-repo 即得」与 §13「重建参数漂移治理」均只覆盖 feedback syncer 自身，未覆盖 videos syncer 这一**独立重建路径**对反馈按钮的冲刷。

修复建议（三选一，推荐 a）：(a) 把 repo 也写进 data JSON 的 options.feedback（§5 已把 JSON 列为优先级 3，仅 §2.1 未列 repo——补上即可），使**任何**重建路径（videos/feedback/手工）都拾取 repo，从机制上根除漂移；countries 已是公开 demo（github-corner 已暴露 imjaden/html-gen.cli），无隐私回退；(b) videos syncer resolve_rebuild_args 增发 --feedback-repo（需读反馈配置，跨脚本耦合）；(c) 文档注明 videos 重建后须重跑 feedback 重建（脆弱，不推荐）。

🟡 HG-SEC-112 — TC-01「HTML 无 issues/new」与常驻 JS 字面量矛盾

§4.4 `buildFeedbackUrl` 在模板 `<script>` 中常驻定义（FEEDBACK=false 时返回 ''，但函数体含 `.../issues/new?...` 字面量）；§9 TC-01 却断言「HTML 无 `issues/new`」。按 §4.4 实现则 TC-01 必红（字面量在 JS 源码中，无论 FEEDBACK 取值）。

修复建议：二选一——(a) TC-01 断言收紧为「分栏 header 无 `.sp-feedback` 按钮 + 产物无被渲染的 feedback 链接/`github.com/…/issues/new` href」（不断言 JS 源码无该字面量）；(b) 实现将 URL 构造整体置于 `FEEDBACK` 门控之后（如 FEEDBACK=false 时 buildFeedbackUrl 不拼接含 issues/new 的字符串）。二者取一，避免实现期测试自相矛盾。

🟢 HG-SEC-114 — 「零变更」口径 = 视觉/行为零变更，非产物 byte-identical

A0-1/§4.2 的「既有页面零变更」是视觉/行为层面；实际新增 `FB/FEEDBACK/buildFeedbackUrl/openFeedbackIssue` 会常驻于生成 HTML（即使 FEEDBACK=false）。设计用词「视觉零变更」（A0-1）准确，未声明字节级一致；TC-01 也只断言按钮/URL 缺失。口径一致，仅记录——评审要求中的「逐字一致」应理解为「默认路径无行为/视觉变更」，非字节级。

🟢 HG-SEC-115 — issue body `### <label>` 切段歧义面

§7.2 step 3 按 `### <label>` 切段。若用户 suggested/note 值内出现 `### 来源` 等行（textarea 自由文本），会干扰切段（字段截断/错位）。三重兜底（白名单+类型+人工 dry-run）已缓解，但设计未显式声明该边界。建议实现按 `### ` 首现序切段 + 未知段丢弃 + 段内多行合并（值内偶发 `###` 行视为值的一部分而非新段）。

🟢 HG-SEC-116 — rebuild.args 缺 --favicon

§8 feedback-targets.yaml rebuild.args 仅 github-url/home-url/feedback-repo，无 favicon。当前 countries 用默认 favicon（favicon_args 兜底 DEFAULT_FAVICON），与 videos syncer 显式传 `--favicon DEFAULT_FAVICON` 结果一致，暂不漂移；但未来某案例换自定义 favicon 会静默回退默认。建议 rebuild.args 补 `--favicon`（与 videos syncer 对齐）或文档注明 favicon 走默认。

🟢 HG-SEC-117 — activateSplit 形参调用点枚举遗漏 skillSplit

§4.3 枚举 openSplitAt 调用点 3 处（L552/L588/L594，准确）+ activateSplit 入口（URL 恢复/▲▼/行点击）。遗漏 `skillSplit`（layout-table.html:883/885，`activateSplit(row, i)` / `activateSplit(row, 0)`，skills-list handler 模式）。新形参 colKey 缺省 `''` 可优雅降级，且 skills-list 属 U1 排除范围，不影响 countries 试点——仅记录。

🟢 HG-SEC-118 — title URL 参数覆盖表单固定 title 待实施实测

§3.2 用 `?title=[数据纠错] …` 预填，§6.1 data-fix.yml 同时声明 `title: "[数据纠错] "`。GitHub Issue Form 的 URL `?title=` 能否覆盖 YAML 固定 title 存在版本差异，需实施期实测确认（若不能覆盖，则 title 恒为固定值，§3.2 的 title 动态拼接需降级）。

## 评分

| 扣分项 | 严重度 | 分值 |
|:-------|:------:|:----:|
| HG-SEC-110 gh 调用 shell=False 未显式 | 🟡 | -5 |
| HG-SEC-111 videos syncer 跨重建漂移丢反馈按钮 | 🟡 | -5 |
| HG-SEC-112 TC-01 断言与常驻 JS 字面量矛盾 | 🟡 | -3 |
| HG-SEC-113 文档同步面遗漏 html-gen-cli-handbook + features.md 计数 | 🟡 | -2 |
| HG-SEC-114..118（5 项） | 🟢 | 0（记录） |

得分: 100 - 15 = **85 / 100 → A**

## 结论

**PASS（85/A，通过）** — 架构正确：静态站无后端约束下的「Issue Form 预填 + 本地脚本解析回写 + 重建」闭环成立；11 占位符/模板改动点/脚本锚点全部实测命中（renderSplitPreview L1076-1110、activateSplit 族 L1039-1074、inject/_SCRIPT_KEYS、videos syncer 风格、.github 待建、268 tests 精确）；安全面 URL 全编码 + noopener + json.dumps + 白名单/类型/protected/行唯一 层层兜底；复用分层（§12）与 config schema（§8）自洽，V1 不复用 videos yaml 理由被源码佐证。无 🔴 阻断项。4 项 🟡 均属实现前规格订正/一致性补强，折叠进 dev 实施即可，不阻塞开工。评审通过后由 dev role 按设计文档实施，折叠项以 HG-SEC-110..113 编号折入对应实现步。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | HG-SEC-110 §7.2 显式规定 gh 调用 list-form + shell=False（comment body 独立 argv 元素） | 安全 🟡 |
| □ | HG-SEC-111 决策跨重建漂移处置：repo 落 JSON options.feedback（推荐 a）/ 或 videos syncer 增发 --feedback-repo | 一致性 🟡 |
| □ | HG-SEC-112 TC-01 断言收紧（按钮/链接缺失，非 JS 字面量缺失）或 URL 构造 FEEDBACK 门控 | 测试 🟡 |
| □ | HG-SEC-113 §10 补 documents/html-gen-cli-handbook（L48 隐私参数）+ features.md（CLI 参数 15→16） | 文档 🟡 |
| □ | HG-SEC-114 「零变更」=视觉/行为零变更口径记录（非 byte-identical） | 记录 🟢 |
| □ | HG-SEC-115 body 解析按 `### ` 首现序切段 + 未知段丢弃 | 实现 🟢 |
| □ | HG-SEC-116 rebuild.args 补 --favicon（或文档注明走默认） | 文档 🟢 |
| □ | HG-SEC-117 activateSplit 形参覆盖 skillSplit（缺省 '' 降级即可，注明） | 记录 🟢 |
| □ | HG-SEC-118 title URL 覆盖表单固定 title 实施期实测 | 待验证 🟢 |
