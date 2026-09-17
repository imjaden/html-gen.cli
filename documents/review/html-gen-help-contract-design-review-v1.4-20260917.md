# help 契约治理设计 v1.4 — 设计评审报告 v1.0

> 日期: 2026-09-17 · 闭环: **HTML-GEN-CL014 [2/6] 设计评审** · 角色: review（独立复跑，不采信 ops 自报）
> 被审对象: `documents/solutions/html-gen-help-contract-design-v1.4-20260917.md`（commit `e6933aa` 主体 + `1e473c2` 实测补记）
> 上位基线: v1.3（`git mv` 推进，rename 检测 R072）
> 需求源（唯一）: `cache/draft/TODO-20260917.md` 闭环 HTML-GEN-CL014 条目（gitignored）
> 上游 finding: CL013 实现审计 HG-SEC-180（🟢 记录类）+ CL013 [6/6] 观察项 O1
> **结论: CONDITIONAL PASS（非阻断）—— 88/100（F1–F11 全成立 · F12/F13 部分成立 · A2/A3 满足 · §11 分级成立 · 1 🟡 + 3 🟢）**

---

## ① 前置取证原始输出

```bash
cd /Users/jadenli/CodeSpace/html-gen.cli
pwd && git rev-parse --show-toplevel && git rev-parse --short HEAD && git status --short && git rev-parse --short github/main
```

实测原始输出:

```
/Users/jadenli/CodeSpace/html-gen.cli
/Users/jadenli/CodeSpace/html-gen.cli
1e473c2
（git status --short 输出为空 = 工作树干净）
4e58407
```

锚点核验: `pwd` = `/Users/jadenli/CodeSpace/html-gen.cli` ✅ · HEAD = `1e473c2`（= `e6933aa` 主体 + `1e473c2` 补记）✅ · `github/main` = `4e58407`（本地领先 2）✅ · 工作树干净 ✅。

补充取证（评审结束时复跑 `git rev-parse --short github/main`）仍为 `4e58407`，无并行线推进（见 §⑥）。

---

## ② F1–F11 逐条复跑结论（命令 + 实测摘要 + 成立/不成立）

### F1 — doc URL 状态真实键集合 = 4 项（含 show-md）

```bash
grep -n "params.get(" layout-doc.html
```

实测: L263 `sidebar` / L264 `toolbar` / L267 `width` / L273 `show-md` —— 键集合 = {sidebar, toolbar, width, show-md}。
**结论: 成立。**

### F2 — v1.3 §D 正则漏捕 show-md

```bash
python3 -c "import re,pathlib;print(sorted(set(re.findall(r\"params\.get\('([a-z]+)'\)\", pathlib.Path('layout-doc.html').read_text()))))"
```

实测: `['sidebar', 'toolbar', 'width']`（3 项，漏 `show-md`）。
**结论: 成立** —— 连字符使 `[a-z]+` 在 `show` 后要求 `'` 而实得 `-` ⇒ `show-md` 无守卫覆盖。

### F3 — 放宽 `[a-z-]+` 后提取 = 4 项

```bash
python3 -c "import re,pathlib;print(sorted(set(re.findall(r\"params\.get\('([a-z-]+)'\)\", pathlib.Path('layout-doc.html').read_text()))))"
```

实测: `['show-md', 'sidebar', 'toolbar', 'width']`（4 项）。
**结论: 成立。**

**正则宽松度评估（任务 §2.1 附加判点）**:
- `[a-z-]+` 对当前 4 键（全 lowercase + 连字符）**已足够**。
- **误捕面 = 0**：`grep -n "params.get(" layout-doc.html` 显示本文件内 `params.get('…')` 形态**仅** L263/264/267/273 四处，均为 URL 键，无非 URL 键的 `params.get(...)` 形态会被吞入（本文件无 `_params` / `urlParams` 等其他变量名，见维度隔离）。
- 是否应更通用（如 `[a-z][a-z0-9-]*`）: 当前**非必需**，但属 🟢 健壮性建议（见 §④ HG-SEC-184）——若未来新增含数字键（如 `?tab2`），`[a-z-]+` 会整体漏捕该键；在「模板漏改契约」的场景下守卫仍绿（同 HG-SEC-180 的静默失效模式）。因守卫是 `提取 == 契约` 等式，若契约同步声明了数字键而正则漏捕，测试会**转红**（fail-safe），故不阻断，但收窄建议更稳。

### F4 — 契约 doc 现状 = 3 项

```bash
python3 -c "import importlib.util as u;s=u.spec_from_file_location('h','html-gen.py');m=u.module_from_spec(s);s.loader.exec_module(m);print([e[0] for e in m.TEMPLATE_CONTRACT['doc']['url_state']])"
```

实测: `['?sidebar', '?toolbar', '?width']`。
**结论: 成立**（缺 `?show-md`）。

### F5 — 节点顶层与 data.url_state 同一 list 对象

```bash
python3 -c "…;print(m.TEMPLATE_CONTRACT['doc']['url_state'] is m.TEMPLATE_CONTRACT['doc']['data']['url_state'])"
```

实测: `True`（`html-gen.py:896-897` 别名循环，单一真源）。
**结论: 成立** —— 追加 1 条即渲染 + 判据单次取用两处同时生效。

### F6 — help 现状无 show-md

```bash
python3 html-gen.py help doc | grep -c 'show-md'
```

实测: `0`（grep exit=1）；URL 状态段现为 3 行（?sidebar / ?toolbar / ?width）。
**结论: 成立。**

### F7 — 机制可达性（纯内存探针，零写盘）

```bash
python3 - <<'PY'
import importlib.util, re, pathlib
spec = importlib.util.spec_from_file_location('h', 'html-gen.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
doc = m.TEMPLATE_CONTRACT['doc']
doc['url_state'].append(('?show-md', 'meta 区源文件名显示开关 show-md=1 (默认隐藏, 仅显示 basename 脱敏文件名)', ''))
help_text = m.render_help('doc')
# … 提取两种正则与契约比对（完整脚本见报告落盘前 /tmp）
PY
```

实测（关键行）:
```
[P1] before: ['?sidebar', '?toolbar', '?width']
[alias] url_state is data.url_state: True
[P2] after: ['?sidebar', '?toolbar', '?width', '?show-md']
[P3] render_help('doc') URL 状态 lines:
      ?sidebar: Bare 模式: sidebar=0 隐藏侧边栏 (默认隐藏, 知识库嵌入自动降级)
      ?toolbar: Bare 模式: toolbar=0 隐藏工具栏 (默认隐藏)
      ?width: 正文宽度三级 width=narrow|medium|wide (默认 medium 即 960px; 不持久化)
      ?show-md: meta 区源文件名显示开关 show-md=1 (默认隐藏, 仅显示 basename 脱敏文件名)
[P4] new extraction set: ['?show-md', '?sidebar', '?toolbar', '?width']
[P4] contract set: ['?show-md', '?sidebar', '?toolbar', '?width']
[P4] new == contract: True
[P5] old extraction set: ['?sidebar', '?toolbar', '?width']
[P5] old != contract (would go red): True
```

**结论: 成立** —— 契约追加 ⇒ `render_help('doc')` 自动渲染第 4 行（能力可达）；新正则提取集 == 契约集（等式成立）；老正则 != 契约集（必红，证明放宽必要）。零写盘（仅内存 append + 只读 layout-doc.html）。

### F8 — 语义一致（默认隐藏 + 仅 basename 脱敏）

```bash
grep -n "meta-path\|show-md" layout-doc.html
grep -n "basename" html-gen.py
```

实测:
- `layout-doc.html` L81 `/* ── md 路径行: 默认隐藏, ?show-md=1 显示 (隐私) ── */` / L82 `.meta-path { display: none; }` / L83 `body.show-md .meta-path { display: inline; }` / L272-273 `if (params.get('show-md') === '1') document.body.classList.add('show-md');`（判定 `=== '1'`）。
- `html-gen.py` L385 / L455 `md_name = os.path.basename(str(md))`，注入于 L388 / L458 `<span class="meta-path"> · 路径: <code>{md_name}</code></span>`（设计 §9 F8 的「L385/L388 与 L455/L458」= basename 计算于 385/455、注入于 388/458，逐字吻合）。

**结论: 成立** —— 「默认隐藏」（L82 display:none）+「只显示 basename、不显示完整路径」（L385/455 只 `basename`，`rel` 全路径 L377/379 计算后**未注入** meta）两点均由实测支撑。§3.2 与 §9 F8 的语义文本与实测逐条吻合。

**第三行为面核对（任务 §2.4 附加判点）**:
- 存在第三行为面：`layout-doc.html:309-318` 标题点击复制逻辑，读 `.doc-header .meta` 的「路径:」值（`metaEl.textContent.match(/路径:\s*(.+)/)`），复制该 basename。
- 关键：`textContent` **不受** `display:none` 影响 ⇒ **无论 show-md 开关与否，标题点击始终可复制 basename**（隐藏时仍可复制）。
- 判点：该行为**不与**契约「仅 basename 脱敏」矛盾（复制值同为 basename，非完整路径，`rel` 未注入）。但属契约未登记的「第三行为面」；doc 契约**无 behaviors 段**（`section_order=['url_state','cli']`），标题复制路径未在任何 help 段登记。**是否需写进契约**：建议后续「doc behaviors 段补齐」批登记（🟢 HG-SEC-185，非本批）。本批 url_state 契约条目语义（显示开关/默认隐藏/basename 脱敏）**不受影响**，不阻断。

### F9 — 文档面现状缺 show-md

```bash
grep -c 'show-md' demos/doc-guide.md
```

实测: `0`（grep exit=1）。
**结论: 成立**（需补 1 行；.html 为生成物随 md 重生成）。

### F10 — 渲染器零改动即可

```bash
grep -n "section_order\|'url_state':" html-gen.py
```

实测: L814 `'section_order': ['url_state', 'cli']`（doc 节点）· L908 `'url_state': 'URL 状态'`（`_SPEC_TITLES` 已登记）。
**结论: 成立** —— 追加条目即渲染，本批**不碰** `render_help` / `render_help_spec` / `_SPEC_TITLES` / `section_order`，回归面最小（设计 §9 F10 的零改动判据成立，回归面未低估）。

### F11 — 测试基线 334

```bash
/usr/bin/python3 -m pytest tests/ -q -n0 --collect-only 2>&1 | tail -1
```

实测: `334 tests collected in 0.09s`。
**结论: 成立** ⇒ 计数不变 ⇒ 无需改 AGENTS.md（与 §11 自报一致）。

### 维度隔离（任务 §2.7 独立验证）

```bash
grep -rn "URLSearchParams\|params.get(" layout-*.html
```

实测:
- `layout-doc.html:261` `var params = new URLSearchParams(...)` → L263/264/267/273 `params.get('…')`（4 处）。
- `layout-knowledge.html:408` `var urlParams = new URLSearchParams(...)`（变量名 `urlParams`，**非** `params`；仅用于给 iframe 详情页追加 `sidebar=0&toolbar=0`，非配置键）。
- `layout-table.html:1499-1509` `var _params = ...` → `_params.get('tab'/'q'/'split')`（变量名 `_params`，**非** `params`）。

**结论: 成立** —— doc 维度提取正则 `params\.get\('([a-z-]+)'\)` **按文件隔离**（`tmpl_text('doc')` 只读 layout-doc.html，见 `test_help_contract.py:27/61-63`）。放宽 `[a-z-]+` **不影响** knowledge（`urlParams`）或 table（`_params`）维度，也不误吞 table 的 `?tab/?q/?split` 键（它们由 table 自身维度口径处理）。

### F12/F13 — 实测补记独立复算（重生成到 /tmp + 归类 diff）

```bash
python3 html-gen.py doc -i demos/doc-guide.md -o /tmp/cl014-regen-baseline.html   # 未改 md + 当前生成器
diff <(cat /tmp/cl014-regen-baseline.html) demos/doc-guide.html | wc -l
diff demos/doc-guide.html /tmp/cl014-regen-baseline.html
```

实测（原始 diff，未归一化时间戳）:
- `diff ... | wc -l` = **28**（含 hunk 标记），实质 **增 8 行 / 删 11 行**。
- 归类:
  - `<title>`/`<link rel="icon">` 行序 = **2 行**（L6/L7 互换）；
  - CSS `.home-link`（print/bare 隐藏选择器 + 新 `.home-link` 规则块）= **5 行**（L426/435 选择器改 + L438-440 新增规则）；
  - `github-corner` 硬编码元素（`<a class="github-corner">…svg…` + `<a class="github-corner-hit">`）= **8 行**（L455-462 整块删除，当前生成器无 `--github-url` 时不再输出该元素）。
- 无「meta 时间戳」diff（doc 的 meta 时间戳取自 md 文件 stat L380-384，非生成时刻 ⇒ 确定性，无漂移）。

```bash
grep -c "home-link" demos/*-guide.html
grep -c 'class="github-corner"' demos/*-guide.html
grep -c 'github.com/imjaden/html-gen.cli' demos/*-guide.html
```

实测:
```
home-link    : doc-guide 0 · knowledge-guide 4 · slide-guide 0 · table-guide 4 · usage-guide 4   （5 文件）
github-corner: doc-guide 1 · knowledge-guide 1 · slide-guide 1 · table-guide 1 · usage-guide 1   （5 文件）
硬编码 imjaden: 5 文件全部 2（github-corner + github-corner-hit 各引一次）
```

**结论: 部分成立（须按实测收窄）**:
- **成立面**：F12 漂移确为「CSS 5 + corner 8 + title 2」既有模板漂移（我独立复算与设计 §9 F12 逐类吻合）；F13「guide 产物均落后于当前模板（硬编码 imjaden corner）」方向正确。
- **不成立面（发现，见 §④ HG-SEC-182）**：
  1. **计数 4 ≠ 5**：`grep -c "home-link" demos/*-guide.html` 的 glob 实匹配 **5** 文件（含 `usage-guide.html`），设计 §9 F13 实测仅列 **4** 文件，漏 `usage-guide.html`（其 home-link=4 / 硬编码 corner=1，与 table/knowledge 同代）。
  2. **O-CL014-1「缺 home-link」列表自相矛盾**：§11 O-CL014-1 写「`table-guide.html` / `knowledge-guide.html` / `slide-guide.html` 缺 home-link」，与 §9 F13 自身实测（table=4、knowledge=4，**不缺**）冲突；实际「缺 home-link」集合 = `{doc-guide, slide-guide}`。
  3. **「生成物刷新批」范围被低估**：全量 `grep -c 'github.com/imjaden/html-gen.cli' demos/*.html` 实测 **16/18** 文件带硬编码 corner（含 `usage-guide` / `markdown-spec` / 各 demo / 落地页），远超 F13 的 4 文件样本。

---

## ③ §3 各评估项判定

| 评估项 | 判定 | 依据 |
|:--|:--|:--|
| 扩容口径是否最小充分 | ✅ 恰当 | 只补 `?show-md` 1 条 + 放宽 doc 正则 1 处 + doc-guide 文档面 1 处，是最小充分改动（§② F7 证「加条目 + 放宽正则」是同一变更的两半）。相邻键核: ① `layout-knowledge.html` 的 `urlParams` 仅用于 iframe `sidebar=0&toolbar=0` 追加（非配置键，L396），**无需守卫**；② `layout-table.html` 的 `_params.get('tab'/'q'/'split')` **确有同族缺口**（table url_state 无模板→契约提取守卫，见 §④ HG-SEC-183），但属**另批**（CL012/CL013 pre-existing，非 CL014 口径） |
| §0 errata 是否如实 | ✅ 如实 | `git show e6933aa^:…v1.3…` 独立复核: v1.3 §D doc URL 行为 `params\.get\('([a-z]+)'\)`、§3.2 缺 show-md、§4 矩阵 doc URL「契约目标」= 2 → v1.4 依次为 `[a-z-]+` / 补 `?show-md` / 3。订正表覆盖 §D 正则 / §3.2 清单 / §4 矩阵 / §9–§11 新增**全部改动面**；无「改了没登记」或「登记了没改」 |
| §10 验收是否满足 A2 | ✅ 满足 | E2E 为**真实使用路径** `html-gen help doc | sed | grep show-md && pytest test_help_contract.py`（cmd1 && cmd2，覆盖能力可达性）；V1–V6 均可复跑可证伪：V3 变异删 `?show-md` → 转红并指名（非恒真），V5 已订正为「归类 diff」（禁「仅新增行」表述，回应 F12） |
| §11 分级判定是否成立 | ✅ 成立 | 纯口径收敛 + 文档类；不触碰删除/`git rm`（`git mv` 为 rename，R072 保留历史，非数据/产物删除，自判定可接受）；不触碰授权面 / `~/.hermes/**` / 他 profile；**不触碰 AGENTS.md**（独立验证：测试计数不变 334，且「只改既有守卫用例」前提成立——`test_17_doc_url_state_matches_template` 已用 `_assert_topic_dim('doc','url_state')` 表达「模板提取 == 契约」等式断言，CL014 只改 `TOPIC_DIMENSIONS[('doc','url_state')]` 正则 `[a-z]+`→`[a-z-]+` + 契约 append `?show-md`，**无需新增用例**，V3 变异是手工验证非提交用例） |
| 出口判据（A3）是否与 §0/§9 一致 | ✅ 一致 | §11 出口判据实测**非**「遗留率 0/6」，而是「遗留率 = 1/6 ≈ 0.17」：O1（上游 HG-SEC-180）**就地闭合**（F1–F8 + V1–V3 四项齐），O-CL014-1 **显式升级**为「生成物刷新批」（编号/归属批/理由/优先级/无需授权 五要素齐）。与 §0 补记（L70-74）+ §9 F12/F13 一致 —— 补记 `1e473c2` 把「0/6 乐观预期」订正为「1/6 + O-CL014-1」，符合 A3「每条观察项给归宿」 |
| 不做清单是否明确 | ✅ 明确 | §0 口径说明（L66-68）显式写「不动 table/slide/knowledge 维度、不改渲染器形状（`render_help_spec`/`_SPEC_TITLES`/`section_order` 零改动）、不改模板（layout-doc.html 仅被读取）」；§8 文件变更 CL014 仅 html-gen.py（契约 1 条）+ test_help_contract.py（正则 + doc 断言）+ doc-guide.md/.html + 本档。不重开 CL012/CL013 已定决策 |

---

## ④ 新发现问题（编号自 max+1 = 182）

| # | 严重度 | 发现 | 落点 | 最小闭合方向 |
|:--|:--|:--|:--|:--|
| HG-SEC-182 | 🟡 | F13/O-CL014-1 计数与归因错误：① `demos/*-guide.html` glob 实匹配 **5** 文件，§9 F13 实测只列 **4**，漏 `usage-guide.html`（home-link=4 / 硬编码 corner=1）；② §11 O-CL014-1「table-guide / knowledge-guide / slide-guide 缺 home-link」与 F13 自身实测（table=4、knowledge=4 不缺）**自相矛盾**，实际「缺 home-link」= `{doc-guide, slide-guide}`；③「生成物刷新批」范围被低估——全量 16/18 `demos/*.html` 带硬编码 corner | 设计 §9 F13（L622-633）+ §11 O-CL014-1（L677） | 见下「可复跑判据」；订正 3 处：F13 改「五份 guide」并补 usage-guide 行；O-CL014-1「缺 home-link」列表改 `doc-guide / slide-guide`；「生成物刷新批」范围按全量 `grep -c 'github.com/imjaden/html-gen.cli' demos/*.html`（16/18）定义 |
| HG-SEC-183 | 🟢 | table URL 状态 `?tab/?q/?split`（契约 L775-779）无**模板→契约提取守卫**（`DIMENSIONS`/`TOPIC_DIMENSIONS` 无 table url_state 维度；模板 L1500/1504/1509 `_params.get(...)` 未被提取断言）。与 HG-SEC-180 同族（守卫盲区），但弱一档（table 键已在契约声明 + 渲染，仅缺「模板漂移提取」等式） | `tests/test_help_contract.py` DIMENSIONS / TOPIC_DIMENSIONS | **另批**「守卫面补全批」（可与 O5 table-demo-prompt / O3 prompts 重建合并）；理由: pre-existing CL012/CL013 缺口，非 CL014 口径 |
| HG-SEC-184 | 🟢 | doc URL 提取正则 `[a-z-]+` 对**未来含数字键**（如 `?tab2`）会整体漏捕，在「模板漏改契约」场景下守卫仍绿（同 HG-SEC-180 静默失效模式）。当前 4 键全 lowercase+hyphen，非阻断；建议收窄为 `[a-z][a-z0-9-]*` | 设计 §D doc URL 行（L274）+ `test_help_contract.py` TOPIC_DIMENSIONS | 折入 [3/6] dev 可选（一行正则），或留观察 |
| HG-SEC-185 | 🟢 | 标题点击复制为「第三行为面」：`layout-doc.html:309-318` 经 `textContent` 读「路径:」值，**无论 show-md 均复制 basename**（display:none 不影响 textContent）。不与契约「仅 basename 脱敏」矛盾，但 doc 契约**无 behaviors 段**登记该行为 | `layout-doc.html:309-318`；契约 doc 节点 `section_order=['url_state','cli']`（无 behaviors） | **另批**「doc behaviors 段补齐」批（可选，低优先级）；本批 url_state 条目语义不受影响 |

**HG-SEC-182 可复跑判据（最小闭合集）**:

```bash
grep -c "home-link" demos/*-guide.html                 # 期望 5 文件: doc 0 / knowledge 4 / slide 0 / table 4 / usage 4
grep -c 'github.com/imjaden/html-gen.cli' demos/*-guide.html   # 期望 5 文件全部 2
grep -c 'github.com/imjaden/html-gen.cli' demos/*.html | grep -v ':0'   # 期望 16/18 文件带硬编码 corner
```

闭合后判据: F13 文本含「五份 guide」+ usage-guide 行；O-CL014-1「缺 home-link」列表 = doc-guide/slide-guide；「生成物刷新批」范围覆盖全量 16 份带硬编码 corner 的 demos。

---

## ⑤ A2/A3 与 §11 分级判定复核结论

- **A2（端到端）**: 满足。E2E 为命令级 `cmd1 && cmd2` 真实使用路径（`html-gen help doc | … | grep show-md` + `pytest test_help_contract.py`），覆盖「用户视角可读 help」+「守卫同时成立」的能力可达性；V1–V6 全部可复跑、可证伪（V3 变异转红反证非恒真，V5 归类 diff 禁乐观表述）。
- **A3（出口判据）**: 满足。O1 就地闭合（F1–F8 + V1–V3 四证齐）、O-CL014-1 显式升级（编号/归属批/理由/优先级/无需授权五要素齐）、遗留率 1/6 如实登记；与 §0/§9 一致。唯 O-CL014-1 的「缺 home-link」列表需按 HG-SEC-182 订正（不改变「升级为生成物刷新批」的结论本身）。
- **§11 分级（§C2 低风险 ⇒ 单评审轮）**: **成立**。本批不触碰删除/`git rm`/授权面/`~/.hermes/**`/他 profile/AGENTS.md 等受保护指令文件；`git mv` 版本推进属 rename（R072 保历史）非数据删除，自判定可接受；「测试计数不变 ⇒ 无需改 AGENTS.md」与「只改既有守卫用例」均经独立验证成立（test_17 已表达等式断言，无新增用例）。**无机制类 ❌ ⇒ 维持单轮，不转三关**。

---

## ⑥ 结论 + 分数

- **结论: CONDITIONAL PASS（非阻断）**。F1–F11 逐条独立复跑**全成立**（含 F7 纯内存可达性探针、维度隔离、F10 渲染器零改动、F11 基线 334）；F12/F13 **部分成立**（漂移归类与「产物落后」归因方向正确，但 F13 计数 4≠5 + O-CL014-1「缺 home-link」列表自相矛盾 ⇒ 🟡 HG-SEC-182）；A2/A3 满足；§11 分级判定成立。
- **Score: 88 / 100**（L2 百分制；参考 CL013 实现审计 94/100、CL012 实现审计 93/100）。
- **扣分（非阻断）**:
  1. 🟡 HG-SEC-182: F13/O-CL014-1 计数与归因错误（4≠5、缺 home-link 列表自相矛盾、生成物刷新批范围低估 16/18）—— 事实卡（A1）与出口判据（A3）两处治理产物精度缺陷，须在 [3/6] dev 前订正；
  2. 🟢 HG-SEC-183: table url_state 无提取守卫（同族缺口，另批）；
  3. 🟢 HG-SEC-184: doc 正则健壮性（`[a-z][a-z0-9-]*` 建议）；
  4. 🟢 HG-SEC-185: 标题点击复制第三行为面未登记（doc 无 behaviors 段，另批）。

- **待处置编号（归属批 · 理由）**:
  - HG-SEC-182（🟡）: **本批 [3/6] dev 前由 ops 折入设计 v1.4 补记**（或下笔 `1e473c2` 同级补记）——理由: 影响事实卡与出口判据精度，但不触碰 CL014 核心机制（契约 3→4 + 正则放宽），非阻断，无需重开评审轮；
  - HG-SEC-183（🟢）: 归属「守卫面补全批」——理由: pre-existing CL012/CL013 缺口，非 CL014 口径；
  - HG-SEC-184（🟢）: 折入 [3/6] dev 可选（一行正则）——理由: 非阻断健壮性；
  - HG-SEC-185（🟢）: 归属「doc behaviors 段补齐」批（可选）——理由: pre-existing，非 CL014 引入。

---

## 处置动作

- ✅ 非阻断 CONDITIONAL PASS ⇒ 单笔提交（`git commit --only` 报告 + review-log + .review-level.yaml，严禁 `git add -A`）→ `git push github main`（ff-only，不推 gitee，不 force）。

## 前后 SHA 与推送核验

（提交/推送后回填，见回执）
