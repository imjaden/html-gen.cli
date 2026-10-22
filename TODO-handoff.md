# 会话轮转入口 — html-gen.cli

> 新会话开场只读本页：① 当前批次状态 ② 待执行清单（**串行，按序做**） ③ 关键指针。
> 维护纪律：状态变化只改本页对应格；条目真值仍以 `git log` / `cache/draft/` / `hm loop` 为准。
> 本页 2026-10-22 CL019 收尾时更新（CL015 批的完整记录见 `491c844` 之前的历史版本）。

---

## 〇、当前状态（一句话）

CL017（案例接入）+ CL018（分栏/短链/md 高亮/item.width）+ CL019（更名重构接入 + 产物 CSS 同步）+ CL020（消费上游回执 bb3ae6e）全部收尾；**github 与 gitee 双远端同步**，工作树 clean。

---

## 一、待执行清单（串行，按序执行）

| 序 | 任务 | 仓 | 前置 | 状态 |
|:--|:--|:--|:--|:--|
| **T1** | **site-patch 转交收尾**：把 `cache/handoff/prompt-script-miner-site-patch-20261015.md` 发给 script-miner（三问：侧栏标题点击语义 / 宽度口径 / 字数双源）。注意该 prompt 里的案例名仍是旧 `renxuan`，发送前把标题与路径改为 `the-price-you-choose` | script-miner（他仓） | 用户手工转交 | 待转交 |
| **T2** | **源站漂移复查**（条件触发）：`data/_the-price-you-choose-source.json` 记 `upstream_commit=bb3ae6e`、`source_index_sha256=10bb35e4…` + 17 个子页哈希；上游再变 → 重拷 9 页 + 重放 35 处前缀 + 版权声明 + canonical，并换哈希 | 双仓 | 上游有新提交时 | 长期维护 |
| **T3** | ~~`demos/index.html` 样式同步~~ | html-gen.cli | — | ✅ 已办结：该页**外链** `../style-guide.css`，新变量/规则自动生效，无需注入 |
| **T4** | ~~handbook 补本案接入参数~~ | html-gen.cli | — | ✅ 已办结：`documents/pages-content-handbook` 新增 4.3 段 + registry 计数漂移记录 |

---

## 二、已完成 —— 仅供追溯，勿重做

### CL017（案例首次接入）
- `demos/renxuan.html` + `demos/renxuan/`（8 页）；`data/_renxuan-kb-data.json`（referenced 登记）+ `_renxuan-source.json`（源 sha）。
- 字数口径修复：字数 = 汉字 + 西文词；时长 = 汉字/400 + 西文/200。
- `demo --rebuild` 形状防护（非数组 kb-data 不再崩）。
- 提交 `32ffd60` / `b7f7b8b` / `b54f005` / `6862606` / `491c844`。

### CL018（分栏 UI + 短链别名 + md 高亮 + item.width）
- 分栏：`columnsSplit:['标题']` + `clickMode:'split'`；详情尊重列级 `escape:false`；高亮改 `tr[data-idx]`。
- 短链：`data/_aliases.json`（mode=list|all|none）→ rebuild 生成根级桩 + canonical + 孤儿清理 + 冲突 exit 2。
- `==文字==` → `<mark class="hl">`（style-guide.css 增 `--hl-*`）；knowledge `item.width`（契约 item 7→8）。
- 提交 `c606e88` / `98fe2d9` / `e855667` / `6d22253`；399 passed。

### CL019（上游重构接入：人选天选论 → The Price You Choose）
- 18 文件全量重拷（哈希逐个核对 == `57e191a`）：入口 `demos/the-price-you-choose.html` + 子页 `chapter00..07` / `highlights` + 8 个旧 slug 跳转桩。
- 入口页 35 处相对引用加 `the-price-you-choose/` 前缀（22 双引号 + 13 onclick 单引号）；补「非出版本」版权声明；canonical 由 rebuild 注入。
- 台账：`data/_the-price-you-choose-kb-data.json`（17 条 = 9 内容 + 8 桩，全部 referenced 隐藏）+ `…-source.json`（17 哈希 + upstream commit）。
- 别名：主短链 `/the-price-you-choose.html`（canonical 持有）+ 遗留 `/renxuan.html`（`canonical:false`，只跳转）。
- 计数：registry 65→74（referenced 46→55，独立 19→19）；索引 19 行不变。
- 测试：`test_renxuan_demo.py`（7）→ `test_the_price_you_choose_demo.py`（8，含旧 slug 桩跳转 + 亮点文章页 45 回链/8 h2 + 来源行尾部）；`test_aliases.py` 16→17；`test_split_detail.py` 断言改新名。
- 产物 CSS 同步：16 个既有 demo 页内联样式 +10 行（`--hl-*` + `mark.hl`），幂等。
- 提交 `03401c8`（接入）/ `5f7fce5`（CSS 同步）；401 passed / 83 subtests；双远端同步。

### CL020（消费 script-miner 回执 bb3ae6e）
- 重拷 9 页（`chapter00..07` + `highlights`），8 个旧 slug 桩字节未变、未重拷；入口页重做 35 处前缀 + 版权声明，canonical 重新注入（count 1）。
- 台账：`upstream_commit=bb3ae6e`、`source_index_sha256=10bb35e4…`、17 子页哈希全换（本地与台账逐项校验一致）。
- 上游三项结论：A1 侧栏标题**无绑定**（回首页在 `#rxHomeBtn`）；A2 已切 `item.width`（catalog url 去 `?width`，本仓模板自动拼 `?width=wide`）；A3 字数写死 **正文 30586 / docBody 30706**（本仓复算 30942 含 body 内其它文本，非来源行 120）。
- 实测：序 item → `chapter00.html?width=wide&sidebar=0&toolbar=0`（宽度来源于 item.width）· 正文 `width-wide` + `.rx-hl` 6 · 亮点页 45 回链 / 8 h2 / 末段来源行 · 旧链落 `hl-chapter00-1` · 0 SEVERE。
- 提交 `c2e890d`；全量 **401 passed / 83 subtests**（一次 `-n 4` 出现过 `test_index_landing::test_14` scroll-hint 时序 flake，串行 18 passed、复跑全量绿）。

---

## 三、关键指针与判据（复跑用）

- 全量：`python3 -m pytest tests/ -q -n 4` → **401 passed / 83 subtests**（~49s）
- 本案：`python3 -m pytest tests/test_the_price_you_choose_demo.py -q -n 0` → 8 passed（测试内自起 http）
- 短链/分栏：`tests/test_aliases.py`（17）· `tests/test_split_detail.py`（5）
- rebuild 幂等：`html-gen demo --rebuild && git diff --stat` → 空
- 判据（新结构）：tab 3（序 / 人之路 1~4 / 天权 5~7）· 条目 9 · 首页 `a.rx-ch`=8 / `a[data-rx-feat]`=5 / `#rxHomeBtn` · 亮点文章页 45 回链 + 8 个 h2 · 正文 8 页 `.rx-hl` 合计 49（含 4 处续行）· 旧深链 `01-xu.html#hl-01-xu-1` → `chapter00.html#hl-chapter00-1`
- 旧 slug 映射：01-xu→chapter00 / 02-heliu-shijie→chapter01 / 03-ren-zhi-lu→chapter02 / 04-yingbi-shijie→chapter03 / 05-pozhi-jian-shi-dingxin→chapter04 / 06-tianquan-shi-ruhe-bei-faxian→chapter05 / 07-tianquan-de-liehen→chapter06 / 08-zicheng-renjian→chapter07
- 源件（只读）：`~/CodeSpace/script-miner/projects/the-price-you-choose/`（README / build.sh / site-patch.py / catalog.json / html/）
- 发布面：`github`=`imjaden/html-gen.cli`（发布面）；`origin`=gitee；push ff-only、不 force
- AGENTS.md 受保护：写入需当场审批（本次已获授权并落盘）

---

## 四、未定案观察项

| # | 观察 | 处置建议 |
|:--|:--|:--|
| O1 | 正文汉字判据 30696 vs 按 docBody 复算 30942（+246） | 差来自「来源行已移到 docBody 末尾」；对账时以「排除来源行」为准 |
| O2 | site-patch 已按 CL017 口径改写字数逻辑（偏差 >20% 才重算）并默认 width-wide | 转交时确认其保留该实现 |
| O3 | `demo --rebuild` 按 basename 跳过所有 `index.html` | 案例入口必须根级且不叫 index.html（已在 CL017/CL019 验证两次） |
| O4 | `item.get(...)` 形态会被契约扫描器当作 knowledge item 键 | 遍历代码避开 `item` 变量名 |
| O5 | `demos/index.html` 无 CSS 锚点（手写页） | 见 T3 |
