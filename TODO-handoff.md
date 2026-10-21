# 会话轮转入口 — html-gen.cli

> 新会话开场只读本页：① 当前批次状态 ② 待执行清单（**串行，按序做**） ③ 关键指针。
> 维护纪律：状态变化只改本页对应格；条目真值仍以 `git log` / `cache/draft/` / `hm loop` 为准。
> 本页于 2026-10-15 CL017 收尾时**清空重写**（CL015 批的完整记录见本文件上一版，即 `491c844` 之前的历史版本）。

---

## 〇、当前状态（一句话）

CL017 已收尾并 push github：`08c1b08..491c844`（5 笔），工作树 clean，`ahead=0`，gitee(`origin`) 未推。

---

## 一、待执行清单（串行，按序执行；上一项不完成不开下一项）

| 序 | 任务 | 仓 | 前置 | 状态 |
|:--|:--|:--|:--|:--|
| **T1** | **AC2① md 高亮/下划线语法**：`md_to_html` 支持 `==文字==` → `<mark class="hl">`；`style-guide.css` 加 `--hl-*` 变量；新增 `tests/test_md_highlight.py`（3 例：单段 / 多段 / 转义不误伤） | html-gen.cli | **用户先定语法定稿**（`==…==` vs `<u>` vs `!!…!!`） | 待排期 |
| **T2** | **AC2② 条目级宽度声明**（可选）：knowledge 数据 items 增 `width: narrow\|medium\|wide`，模板拼到 iframe src；缺省行为不变（向后兼容）。现状靠数据侧 url 带 `?width=wide` 代偿（renxuan 8 页已如此） | html-gen.cli | T1 之后（同属模板小改，勿混批） | 待排期 |
| **T3** | **AC2③ 转交 script-miner / site-patch**：注入层把 `.sidebar-title` 点击覆盖成「清记忆+回首页」，覆盖了 `layout-knowledge.html:278` 的「复制路径」语义 ⇒ 建议改为新增按钮（`.kw-sidebar-footer` 已有 `sb-btn` 位）；同时转达 T2 宽度约定与 AC2④ 字数客户端重算双源问题。**prompt 已备**：`cache/handoff/prompt-script-miner-site-patch-20261015.md`（gitignored） | script-miner（他仓） | 用户手工转交 / 派发 | 待转交 |
| **T4** | **gitee 同步**：`git push origin main`（`origin`=gitee，现落后）。仓惯例 origin 不推，须明确授权后执行 | html-gen.cli | 用户授权 | 待授权 |
| **T5** | **源站漂移复查**（条件触发，非主动）：比对 `data/_renxuan-source.json` 的 `source_index_sha256`（`d4c030ff…`）与 8 页哈希；若 script-miner 侧更新 → 重放 `landing_modifications`（98 处 `renxuan/` 前缀 + 版权声明一行）并更新 source json | 双仓 | T3 有结论后 | 长期维护 |

> 串行理由：T1/T2 同属模板层小改，先定 T1 语法可一次性把样式基座（CSS 变量）改到位，T2 复用同一批；T3 是他仓依赖，不阻塞 T1/T2；T4/T5 属发布与维护面，最后做。

---

## 二、本批（CL017）已完成 —— 仅供追溯，勿重做

- 案例纳入：`demos/renxuan.html`（目录页）+ `demos/renxuan/`（8 正文页）；清单行由 `demo --rebuild` 自动生成（📚 C 型）。
- 登记：`data/_renxuan-kb-data.json`（8 条 url → 标记 referenced）、`data/_renxuan-source.json`（源 sha / 8 页哈希 / landing_modifications）。
- 计数：registry 56→65（referenced 38→46，独立 18→19）；`data/_demos-data.json` 与 `demos-index.html` 各 18→19 行。
- AC2④ 已实现（独立 commit）：字数 = 汉字 + 西文词；阅读时长 = 汉字/400 + 西文/200。
- `demo --rebuild` 形状防护：非数组 / 混合数组 `*kb-data.json` 不再崩（`_collect_demo_refs`）。
- AGENTS.md 同步：367 tests / 35 文件 + renxuan 目录条目。
- 提交：`32ffd60` 案例 / `b7f7b8b` 字数 / `b54f005` rebuild 防护 / `6862606` 版权声明 / `491c844` AGENTS 同步。

---

## 三、关键指针与判据（复跑用）

- 全量测试：`python3 -m pytest tests/ -q -n 4` → **367 passed / 82 subtests**（~49s）
- 案例回归：`python3 -m pytest tests/test_renxuan_demo.py -q -n 0` → 7 passed（测试内自起 http，勿用 file:// 读 iframe）
- 清单重建幂等：`html-gen demo --rebuild && git diff --stat` → 输出为空
- 判据：亮点句 45 行（每章 6/6/5/5/5/5/6/7）、正文 `.rx-hl` span 合计 49（含 4 处跨行续行）、正文汉字 30696（按 docBody 文本节点复算 30706，差 +10，口径待写死）
- 入口页改写的 98 处 = 8 条目 url + 45 desc 内 href + 45 onclick `rxJump`；`demo --rebuild` 按 basename 跳过所有 `index.html`（`f.name in ('index.html','_registry.json')`）⇒ 案例入口必须在根级、不能叫 index.html
- 源件（只读）：`~/CodeSpace/script-miner/projects/人选天选论/`（README / build.sh / site-patch.py / catalog.json / html/）
- 发布面：`github`=`imjaden/html-gen.cli`（发布面）；`origin`=gitee（本批未推）；push 一律 ff-only、不 force

---

## 四、未定案观察项（无编号，随批处置）

| # | 观察 | 处置建议 |
|:--|:--|:--|
| O1 | 正文汉字判据 30696 vs 复算 30706（+10，逐章 ±9） | 口径写死为「docBody 文本节点 CJK 计数」，避免回执无法精确对账 |
| O2 | AC2④ 修好后，renxuan 页内 site-patch 的客户端字数重算仍在覆盖显示值（如 3443） | 随 T3 转达：模板已给正确值，注入层可退化为「仅在不一致时修正」 |
| O3 | 交接单原写 `demos/renxuan/index.html` 不可行（rebuild 跳过 index.html） | 已按 D2(A) 落地根级入口；后续案例沿用此结论 |
| O4 | gitee（gitee.com/imjaden/html-gen.cli）落后 github 多笔 | 见 T4 |
