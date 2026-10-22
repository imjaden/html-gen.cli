# 会话轮转入口 — html-gen.cli

> 新会话开场只读本页：① 当前批次状态 ② 待执行清单（**串行，按序做**） ③ 关键指针。
> 维护纪律：状态变化只改本页对应格；条目真值仍以 `git log` / `cache/draft/` / `hm loop` 为准。
> 本页 2026-10-22 CL018 收尾时更新（CL015 批的完整记录见 `491c844` 之前的历史版本）。

---

## 〇、当前状态（一句话）

CL017（renxuan 案例）+ CL018（分栏 UI / 短链别名 / md 高亮 / knowledge item.width）已收尾；**github 与 gitee 双远端均同步**（`6d22253`），工作树 clean，`github_ahead=0 gitee_ahead=0`。

---

## 一、待执行清单（串行，按序执行；上一项不完成不开下一项）

| 序 | 任务 | 仓 | 前置 | 状态 |
|:--|:--|:--|:--|:--|
| **T1** | **AGENTS.md 文档同步**：测试计数 388→399、文件 37→39；补 `data/_aliases.json` 口径与短链说明；knowledge item 键 7→8（width） | html-gen.cli | — | ⛔ **写保护拦截**（审批提示超时，未落盘；AGENTS.md sha 仍 `3b737bc1…`）→ 需用户在场时重批，或手工套用 |
| **T2** | **AC2③ 转交 script-miner / site-patch**：注入层把 `.sidebar-title` 点击覆盖成「清记忆+回首页」，覆盖了 `layout-knowledge.html:278` 的「复制路径」语义 ⇒ 建议改为新增按钮；同时转达 item.width 约定（T2 已落地）与字数客户端重算双源问题。**prompt 已备**：`cache/handoff/prompt-script-miner-site-patch-20261015.md`（gitignored） | script-miner（他仓） | 用户手工转交 | 待转交 |
| **T3** | **产物 CSS 漂移重生成**（可选）：本次只重生成 `demos/demos-index.html`；其余 demo 页内联的 style-guide.css 仍无 `--hl-*` / `mark.hl`。若要站内一致，按 CL015 口径做一次「零改动基线重生成」并对 diff 逐页说明 | html-gen.cli | 用户决定范围 | 待定 |
| **T4** | **源站漂移复查**（条件触发）：比对 `data/_renxuan-source.json` 的 `source_index_sha256`（`d4c030ff…`）与 8 页哈希；若 script-miner 侧更新 → 重放 `landing_modifications`（98 处 `renxuan/` 前缀 + 版权声明 + canonical）并更新 source json | 双仓 | T2 有结论后 | 长期维护 |

> 串行理由：T1 是纯文档且被写保护卡住，需用户在场；T2 是他仓依赖；T3 是产物一致性（可延后）；T4 条件触发。

---

## 二、已完成 —— 仅供追溯，勿重做

### CL017（renxuan 案例）

- 案例纳入：`demos/renxuan.html`（目录页）+ `demos/renxuan/`（8 正文页）；清单行由 `demo --rebuild` 自动生成（📚 C 型）。
- 登记：`data/_renxuan-kb-data.json`（8 条 url → 标记 referenced）、`data/_renxuan-source.json`（源 sha / 8 页哈希 / landing_modifications）。
- 计数：registry 56→65（referenced 38→46，独立 18→19）；`data/_demos-data.json` 与 `demos-index.html` 各 18→19 行。
- 字数口径修复（独立 commit）：字数 = 汉字 + 西文词；阅读时长 = 汉字/400 + 西文/200。
- `demo --rebuild` 形状防护：非数组 / 混合数组 `*kb-data.json` 不再崩（`_collect_demo_refs`）。
- 提交：`32ffd60` 案例 / `b7f7b8b` 字数 / `b54f005` rebuild 防护 / `6862606` 版权声明 / `491c844` AGENTS 同步。

### CL018（分栏 UI + 短链别名 + md 高亮 + item.width）

- 分栏左表：`options.columnsSplit:['标题']`（`序号` 为行号工具列，仍显示）；`options.clickMode:'split'` 固化，新访客也默认分栏。
- 详情面板：kv-list 尊重列级 `escape:false` ⇒ 文档链接可点。
- 行高亮：`tr[data-idx]` 定位替代 `rows[idx]`，分页 ≥2 页不再错位。
- 短链：`data/_aliases.json`（`mode=list`，entries=[renxuan]）→ `demo --rebuild` 生成 `/renxuan.html`（200 + meta refresh + canonical + noindex），并给目标页注入 canonical；`mode=all` 可一次给全部独立案例开短链。
- md 行内高亮：`==文字==` → `<mark class="hl">`；`style-guide.css` 增 `--hl-bg/--hl-fg`（浅色另有覆盖）；help 语法段同步。
- knowledge `item.width`：`narrow|medium|wide` → iframe 追加 `?width=`；缺省 medium，url 含 `overview` 仍默认 wide；契约 item 键 7→8。
- 实测：短链 → `/demos/renxuan.html`；tab 4 / 亮点句 45 / 0 报错；分栏 thead=序号+标题、详情链接可点、高亮行 `data-idx=17`。
- 提交：`c606e88` 分栏+短链 / `98fe2d9` 入口页登记 / `e855667` md 高亮+item.width+help / `6d22253` demos-index 重生成。
- 全量 **399 passed / 83 subtests**；双远端已同步。

---

## 三、关键指针与判据（复跑用）

- 全量测试：`python3 -m pytest tests/ -q -n 4` → **399 passed / 83 subtests**（~49s）
- 分栏/短链回归：`python3 -m pytest tests/test_split_detail.py tests/test_aliases.py -q -n 0` → 21 passed
- 新增能力回归：`tests/test_md_highlight.py`（6）· `tests/test_knowledge_width.py`（5）
- 短链生成口径：`data/_aliases.json`（mode=list|all|none）；桩带 `<!-- html-gen:alias auto -->`，重建只清理带标记的桩；冲突（撞手写页/重名）exit 2
- 案例回归：`python3 -m pytest tests/test_renxuan_demo.py -q -n 0` → 7 passed（测试内自起 http，勿用 file:// 读 iframe）
- 清单重建幂等：`html-gen demo --rebuild && git diff --stat` → 输出为空
- 判据：亮点句 45 行（每章 6/6/5/5/5/5/6/7）、正文 `.rx-hl` span 合计 49（含 4 处跨行续行）、正文汉字 30696（按 docBody 文本节点复算 30706，差 +10）
- 入口页改写的 98 处 = 8 条目 url + 45 desc 内 href + 45 onclick `rxJump`；`demo --rebuild` 按 basename 跳过所有 `index.html` ⇒ 案例入口必须在根级、不能叫 index.html
- 源件（只读）：`~/CodeSpace/script-miner/projects/人选天选论/`（README / build.sh / site-patch.py / catalog.json / html/）
- 发布面：`github`=`imjaden/html-gen.cli`（发布面）；`origin`=gitee；两者本批均已同步；push 一律 ff-only、不 force
- AGENTS.md 受保护：写入需当场审批（本次审批超时被拦，文件未变，sha `3b737bc1…`）

---

## 四、未定案观察项（无编号，随批处置）

| # | 观察 | 处置建议 |
|:--|:--|:--|
| O1 | 正文汉字判据 30696 vs 复算 30706（+10，逐章 ±9） | 口径写死为「docBody 文本节点 CJK 计数」，避免回执无法精确对账 |
| O2 | renxuan 页内 site-patch 的客户端字数重算仍在覆盖显示值（如 3443） | 随 T2 转达：模板已给正确值，注入层可退化为「仅在不一致时修正」 |
| O3 | 交接单原写 `demos/renxuan/index.html` 不可行（rebuild 跳过 index.html） | 已按 D2(A) 落地根级入口；后续案例沿用此结论 |
| O4 | `html-gen.py` 中 `item.get(...)` 形态会被契约扫描器当作 knowledge item 键 | 别名/其它遍历代码避开 `item` 变量名（已改 `ent`） |
| O5 | 其它 demo 页内联 CSS 尚无 `mark.hl` 变量 | 见 T3 |
