# html-gen favicon 默认注入 + table URL 状态分享 + syncer 参数体系实现 — review报告 v1.0（实现审计）

- **日期**: 2026-08-29
- **审查人**: Security Reviewer（review role）
- **级别**: L2（implementation-audit）
- **对象**: HTML-GEN-CL004 实现 commit 链 8 个（`9a9c608` docs@design → `43c5ffd` docs@review → `872593e` feat@html-gen → `b97ca54` feat@template → `33707e7` feat@script → `ae606f3` test@script → `0b95c2b` docs@html-gen → `1d864b1` data@demo，全部未 push）
- **设计**: `documents/solutions/html-gen-favicon-urlstate-syncer-design-v1.0-20260829.md`（决策 A1..L1 + 1B 2A 3A 4A 5A）
- **设计评审**: `documents/review/html-gen-favicon-urlstate-syncer-design-review-v1.0-20260829.md`（PASS 85/A，findings HG-SEC-073..079 折入实现）
- **结论**: 🟢 **PASS 100/100（A）** — 三项需求全数落地且源码级 + 实测双重核验通过；HG-SEC-073..079 七项全部折入实现并逐条闭合；无新增 🔴/🟡；1 处 🟢 记录（非阻断）

---

## 一、数据验证（关键命令复跑，只读 + 临时目录）

| # | 验证项 | 命令 | 实测结果 | 结果 |
|:--|:--|:--|:--|:--:|
| 1 | 专项测试复跑 | `pytest tests/test_url_state.py tests/test_sync_videos.py tests/test_json_output.py -q -n 0` | `32 passed in 3.56s`（url_state 5 + sync_videos 13 + json_output 14） | ✅ |
| 2 | favicon 默认注入 | `/tmp` 临时 json → `table -d t.json -o t1.html` | `grep -c rel="icon" href=DEFAULT_FAVICON` = 1 | ✅ |
| 3 | favicon 覆盖 | `--favicon https://example.com/f.ico` | 含 example.com/f.ico，`grep -c jaden.tech/static/img/favicon` = 0 | ✅ |
| 4 | favicon 空串禁用 | `--favicon ""` | `grep -c rel="icon"` = 0（无任何 icon link） | ✅ |
| 5 | 四模板 favicon | doc/slide/table/knowledge 四产物 | 4 文件均 `grep -c rel="icon" href=DEFAULT_FAVICON` = 1 | ✅ |
| 6 | syncer --empty-video 缺省路径 | `syncer --empty-video`（无参） | 逐行「首字段 (次字段)」+ 底部「共 173 条 videos 为空」，只读 exit 0 | ✅ |
| 7 | 三向互斥 | `syncer --empty-video --apply` | argparse 报错，`exit=2` | ✅ |
| 8 | [执行] 打印三参数（rebuild 缺省默认） | `cache/_cl004_audit/` 临时 yaml → `--apply` | `[执行] … --github-url https://github.com/imjaden/html-gen.cli --home-url https://html-gen.cli.jaden.tech/ --favicon https://www.jaden.tech/static/img/favicon.png`（三参数全在，shlex.quote 完整命令） | ✅ |
| 9 | rebuild 空串禁用语义（HG-SEC-078） | rebuild `{github_url:"", home_url:自定义, favicon:""}` → `--apply` | `[执行]` 仅含 `--home-url https://custom.example.com/`，无 `--github-url`/`--favicon` | ✅ |
| 10 | 全量测试计数 | `pytest tests/ --collect-only -q` | `246 tests collected`（与 AGENTS.md 计数 246 一致） | ✅ |
| 11 | demos-index 产物再生 | `grep` demos/demos-index.html | `rel="icon"` = 1、`id="shareBtn"` = 1、`<!--FAVICON-->` = 0（占位符已注入） | ✅ |
| 12 | WIP 文件未混入 commit | `git status` + `git diff --stat HEAD` | 4 文件（countries-data.json / drama-table-history-strategy.json / countries-table.html / history-strategy-table.html）为 unstaged working-tree 修改，不在 8 commit 内 | ✅ |

**核验结论**：12 项证据全部属实，临时目录（`/tmp/cl004_audit`、`cache/_cl004_audit`）已用后清理，工作树仅余 4 个 pre-existing WIP 文件（未触碰）。

---

## 二、维度评估

### 1. 需求 1 — favicon 默认注入（决策 A1/C1 + HG-SEC-073）✅

| 项 | 设计锚点 | 实测 | 结果 |
|:--|:--|:--|:--:|
| DEFAULT_FAVICON 常量 | 新增常量 = https://www.jaden.tech/static/img/favicon.png | `html-gen.py:106` | ✅ |
| 优先级 CLI > env > DEFAULT | `--favicon` 覆盖 / env 兜底 | `favicon_args()` `html-gen.py:116-124` | ✅ |
| 空串禁用（HG-SEC-073） | 用 `is not None` 勿 `or` 链 | `L122-123` `args.favicon if getattr(args,'favicon',None) is not None else (os.environ.get('HTML_GEN_FAVICON') or DEFAULT_FAVICON)` — 空串走 `is not None` 分支，禁用生效 | ✅ |
| favicon_link_html | 空 → 空串 | `L109-113` `if not url: return ''` | ✅ |
| 四子命令 argparse `--favicon` | doc/slide/table/knowledge 四处 | `L797/807/817/829` | ✅ |
| 四处 inject 传 favicon | cmd_doc/slide/table/knowledge | `L337/408/467/516` 均 `favicon=favicon_args(args)` | ✅ |
| 四模板 `<!--FAVICON-->` | head 内 title 后 | 4 模板均 `L7` | ✅ |

### 2. 需求 2 — layout-table URL 状态分享（决策 E1/F1/G1/H1 + HG-SEC-074/075/076）✅

| 项 | 设计锚点 | 实测 | 结果 |
|:--|:--|:--|:--:|
| syncUrlState 统一封装 | ?tab&q&split，默认值剔除 | `layout-table.html:1016-1027`（tab 非首、q 非空、splitActive 才 set；无参用 `location.pathname`） | ✅ |
| replaceState 同步点 | switchTab/搜索 debounce/activateSplit/splitNav/closeSplit | switchTab `L1351`、搜索 debounce `L1339`（300ms 内 syncUrlState）、activateSplit `L1043`、splitNav→activateSplit、closeSplit `L1063`；quickSearch submit `L1520` | ✅ |
| URLSearchParams 读写对称（HG-SEC-074） | 删手工 encode/decode | 写 `p.set('q', q)`（自动编码，`L1021`）；读 `_params.get('q')`（自动解码，`L1446-1449`），无 decodeURIComponent 二次解码/URIError | ✅ |
| 恢复顺序 tab→q→split（HG-SEC-076） | tab buildTabs 前、q render 前、split render 后 | `L1440-1484`：tab 白名单 `L1443`、q 仅 `input.value` 赋值 `L1449`、split `parseInt`+越界校验 `L1479-1483`（render 后） | ✅ |
| defaultFilter 优先级（HG-SEC-076） | split 在 quickFilter 态下标语义失效跳过 | `L1479` `if (_urlSplit !== null && !quickFilter)` | ✅ |
| sort/quickFilter closeSplit（HG-SEC-075） | 三选一 → closeSplit | sortBy `L797`、quickFilterBy `L728`、clearQuickFilter `L741` 均 `if (splitActive) closeSplit()` | ✅ |
| 🔗 shareBtn + buildShareUrl + fallback | clipboard + execCommand fallback + toast | `L270` 按钮、`buildShareUrl` `L1212-1216`（先 syncUrlState 再取 location.href）、`shareLink` `L1217-1228`、`fallbackCopyUrl` `L1203-1210`（execCommand + showToast） | ✅ |
| 安全 | tab 白名单 / split 越界 / q 无 innerHTML | `L1443` `TABS.find`、`L1481` `n>=0 && n<filtered.length`、`L1449` 仅 value 赋值 | ✅ |

### 3. 需求 3 — syncer 参数体系（决策 I2/J1/K1/L1/1B/2A/3A/4A + HG-SEC-078/079）✅

| 项 | 设计锚点 | 实测 | 结果 |
|:--|:--|:--|:--:|
| yaml_path nargs='?' 缺省 | cache/data/_countries-data.videos.yaml（项目根解析） | `DEFAULT_YAML` `L40`、`argparse` `L296-298` | ✅ |
| 三向互斥 | --dry-run/--apply/--empty-video | `add_mutually_exclusive_group` `L299-303`，exit 2 实测确认 | ✅ |
| --empty-video 只读 | 读 target.data json，零写盘 exit 0 | `run_empty_video` `L219-239`、调用点 `L343-344`（F3 校验前） | ✅ |
| 行格式「首字段 (次字段)」+ 计数 | 按 json 首元素 keys 序取前两个非空字段 | `L229-238`（`keys = list(rows[0].keys())`；空字段 `(空)`；底部「共 N 条 videos 为空」） | ✅ |
| rebuild 配置节 | {github_url, home_url, favicon} 缺省默认 | `resolve_rebuild_args` `L188-216` | ✅ |
| github_url 优先级（2A） | rebuild > extract_corner_url > 默认 | `L197-203`：有 rebuild 键 → 用其值（空串禁用）；否则 `extract_corner_url(html_path) or DEFAULT_GITHUB_URL` | ✅ |
| 空串禁用（HG-SEC-078） | 任一键空串 = 不传该参数 | `L197-215` 三键均 `if rebuild[k]: extra += ...`（空串跳过），实测 [执行] 无 `--github-url`/`--favicon` | ✅ |
| [执行] 打印完整命令（D1） | shlex.quote + shell=False | `L282` `print('[执行] ' + ' '.join(shlex.quote(str(a)) for a in cmd))`、`L283` `subprocess.run(cmd, shell=False)`（保持 RIG-002） | ✅ |

### 4. 测试覆盖（决策 5A + HG-SEC-079）✅

| 设计 §6 用例 | 实测覆盖 |
|:--|:--:|
| 新建 test_url_state.py（?tab&q&split 打开/无效忽略/状态同步/拷贝 fallback） | `test_01..05` 5 例 ✅ |
| test_sync_videos 扩 3 例（[执行] 三参数 / empty-video+互斥 / 缺省路径） | `test_11`（assertRegex 三参数打印行，HG-SEC-079 锁定路径）、`test_12`（empty-video+exit 2）、`test_13`（无参缺省 yaml）✅ |
| test_json_output favicon 三态 | `test_12`（默认）/`test_13`（覆盖）/`test_14`（空串禁用，HG-SEC-073）✅ |
| test_corner_privacy 修正 | `test_01` 断言 `html.count('jaden.tech') == 1`（仅 favicon，无额外 home/github 泄露）✅ |

- test_url_state 用 Selenium + `tempfile` 唯一文件名防 file:// 缓存，`localStorage.clear()` setUp 隔离 ✅
- test_sync_videos 用 tempfile.mkdtemp + 脚本复制到临时目录（项目根推导），xdist 兼容 ✅

### 5. commit 治理 ✅

| commit | type@scope | 文件 | 夹带检查 |
|:--|:--|:--|:--:|
| 9a9c608 | docs@design | 设计 v1.0 | ✅ |
| 43c5ffd | docs@review | 设计评审 PASS | ✅ |
| 872593e | feat@html-gen | favicon 注入 | ✅ |
| b97ca54 | feat@template | layout-table URL 状态 | ✅ |
| 33707e7 | feat@script | syncer 参数体系 | ✅ |
| ae606f3 | test@script | 测试扩展 | ✅ |
| 0b95c2b | docs@html-gen | 文档同步（计数 235→246） | ✅ |
| 1d864b1 | data@demo | demos-index 产物再生 | ✅ |

- 8 commit 全部 `type@scope` 规范，subject 全英文 ✅
- 全部未 push（`git log origin/main..HEAD` = 8，`git status` 显示 ahead 8）✅
- AGENTS.md 计数 246 与实际 `246 collected` 一致 ✅
- 4 个 WIP 文件（data/_countries-data.json、data/_drama-table-history-strategy.json、demos/countries-table.html、demos/drama/history-strategy-table.html）为另一会话 pre-existing working-tree 修改，**不在** 8 commit 内（`git diff --stat HEAD` 复核确认，未触碰）✅

### 6. 文档同步 ✅

- AGENTS.md：四渲染子命令通用参数 `--favicon`、syncer 用法（--empty-video / 缺省路径 / rebuild 配置）、测试计数 235→246（`0b95c2b`）✅
- demos-index.html 产物再生含 favicon link + shareBtn（`1d864b1`）✅

---

## 三、安全事项

实现保持设计评审已确认的安全面，无新增攻击面：

- **URL 参数注入面**：syncUrlState 读写统一 `URLSearchParams`（自动编解码），tab 白名单（`TABS.find`）、split `parseInt` + 越界校验、q 仅 `input.value` 赋值 —— 无 innerHTML 注入路径，URL 仅影响视图状态不触发数据写入 ✅
- **favicon 注入源**：仅 CLI `--favicon` / env `HTML_GEN_FAVICON` / `DEFAULT_FAVICON` 常量，均为 operator 受控（与既有 github-corner/home-link 同信任模型）✅
- **syncer subprocess**：列表参数 + `shell=False`（RIG-002），`shlex.quote` 仅用于 [执行] 打印展示（非执行构造），`yaml.safe_load`（RIG-001）✅

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-073 | 🟡→✅ | `--favicon ""` 禁用 None/"" 区分 | ✅ closed（`L122-123` 用 `is not None`，实测空串禁用） |
| HG-SEC-074 | 🟡→✅ | URL q 编解码对称 + malformed % URIError | ✅ closed（`L1018/1441-1449` 统一 URLSearchParams，无手工 decode） |
| HG-SEC-075 | 🟡→✅ | split 下标 vs sort/quickFilter 交互 | ✅ closed（`L728/741/797` sort/quickFilter 均 closeSplit） |
| HG-SEC-076 | 🟢→✅ | 恢复流程 init() 挂钩 + defaultFilter 优先级 | ✅ closed（`L1440-1484` 顺序 tab→q→split + `L1479` `!quickFilter` 跳过） |
| HG-SEC-077 | 🟢→✅ | render_* 实为 cmd_* 命名 | ✅ closed（实现按 cmd_* 定位，四处 inject 正确） |
| HG-SEC-078 | 🟢→✅ | rebuild 三键空串语义 | ✅ closed（`L197-215` 空串=禁用，实测 [执行] 无对应参数） |
| HG-SEC-079 | 🟢→✅ | test 锁「[执行] 打印行」断言 | ✅ closed（test_11 assertRegex 三参数打印行） |
| HG-SEC-080 | 🟢 | favicon_link_html / home_link_html URL 未 HTML 转义（operator 受控，与既有 github-corner 同模式，防御性建议） | ✅ record（非阻断，仅当未来引入非受控 URL 输入时才需转义） |

---

## 四、评分

```
Base 100
  无 🔴 / 无 🟡
  7 项设计评审 findings（HG-SEC-073..079）折入实现并逐条闭合  -0
  🟢 HG-SEC-080  -0  (favicon/home URL 未转义，operator 受控，记录)
  ─────────────────────
  100 / 100（A）
```

---

## 五、结论

**PASS（A）**。HTML-GEN-CL004 实现链（8 commits，全部未 push）对设计 §三/四/五 三项需求全数落地，源码级 + 实测双重核验通过：

- 需求 1 favicon：DEFAULT_FAVICON 默认注入 + `--favicon` 覆盖 + 空串禁用（`is not None` 判断）+ env 兜底 + 四子命令 + 四模板 `<!--FAVICON-->`，四模板产物实测均注入 ✅
- 需求 2 URL 状态：`?tab&q&split` replaceState 五同步点 + 恢复顺序 tab→q→split + 白名单/越界/无 innerHTML 三安全项 + sort/quickFilter closeSplit + 🔗 shareBtn（clipboard + execCommand fallback + toast）✅
- 需求 3 syncer：yaml_path 缺省路径 + 三向互斥（exit 2）+ --empty-video 只读 + rebuild 三键配置（缺省默认/空串禁用/github_url 三级优先级）+ [执行] shlex.quote 完整命令 + shell=False ✅
- 测试：test_url_state 5 / test_sync_videos 13 / test_json_output 14 / test_corner_privacy 6，专项 32 passed，全量 246 collected ✅
- 治理：8 commit 全 `type@scope` 规范，未 push，WIP 文件未混入，AGENTS.md 计数 246 一致，文档同步完整 ✅

设计评审 7 项 findings（HG-SEC-073..079）全部折入实现并逐条验证闭合，无新增 🔴/🟡，1 处 🟢 记录（HG-SEC-080）非阻断。

**处理**：PASS → 写审计三件套（本报告 + review-log.md + .review-level.yaml）+ commit（`docs@review: html-gen favicon+URL状态+syncer参数 实现审计 PASS (HTML-GEN-CL004)`）。仅 commit 不 push（AGENTS.md 约定 + 本任务约束）。

---

## 六、dev 后续（非阻断，可选）

| 项 | 内容 | 优先级 |
|:--|:--|:--:|
| HG-SEC-080 | 若未来 favicon/home/github URL 接受非 operator 受控输入，`favicon_link_html`/`home_link_html` 应加 HTML 转义（现与既有模式一致，operator 受控无需处理） | P2 |
| — | 设计 §八 FIND-001（data/_countries-data.json columns 增 initialHidden/splitFull 共享文件污染）推送前由归属 CL 登记，本 CL 未触碰 | P2 |
