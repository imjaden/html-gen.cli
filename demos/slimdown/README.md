# slimdown · 减脂训练方案案例

来源：用户 2026-11-11 的两份单页（`训练动作库 v1.1`、`薄肌减脂执行档案 v2.4`），
2026-11-12 由 ops 会话收敛成可重建的案例（三页 + 单一数据源 + 生成脚本）。
2026-11-23 接 v1.3：方案页拆成「按星期 / 按主题」双视图，点击态全部浏览器记忆（见 `## v1.3`）。
同日 v1.4 整改：页面迁到 `index.html`（`/demos/slimdown/` 直达）、面板 90vw×90vh、出图收敛单张下载（见 `## v1.4`）；
v1.5 小批：标题一行、副标题移除、Tab「主题、星期」默认主题、面板 100vh（head/foot 减半）——详见方案文档 §7。

## 结构

```
demos/slimdown/
  exercises.html    动作库 —— html-gen table 标准模板（深色数据工具页）
  index.html        训练方案 —— 按星期七日卡 / 主题四套 / 四套配色 / 面板（编辑·列表预览·单张出图）；目录首页
  plan.html         旧链接跳转桩（v1.4）：透传 ? 与 # 后跳 index.html，带 `slimdown:redirect auto` 标记
  archive.html      档案 —— 基线（本机填）/ 营养 / SOP / FAQ
  _src/             页模板与样式（不被 demo 扫描，只有 *.html 进 registry）
    plan.tpl        plan 页骨架（含首屏防闪烁内联脚本）
    plan.css        plan 页专用（深色 + 四套主题变量）；base.css 只服务 archive
    state.js        点击态记忆（slimdown:ui:v2：视图/预设/配色/页签/筛选/打卡）
    shot.js         出图管线（foreignObject → canvas，周视图与主题视图共用）
    plan.js         页面逻辑（双视图渲染 / 面板 / 分享 v3 / 拖拽 / 打卡）
    archive.tpl/archive.js  档案页
data/_slimdown-exercises.json   动作库单一源（80 条：原 69 + 计划引用 3 + v1.3 居家自重 8）
data/_slimdown-plan.json        presets[home（居家七日）] + themes[4]（v1.4：力量版预设已移除）
scripts/build-slimdown.py       一次重建三页（state.js + shot.js + plan.js 按序拼接）
scripts/slimdown-import-v13.py  v1.3 数据导入（两份参考页 → 上述两个 JSON，幂等）
```

## 重建

```bash
python3 scripts/build-slimdown.py --dry-run   # 先看将写哪些文件
python3 scripts/build-slimdown.py --apply
python3 scripts/slimdown-import-v13.py --dry-run   # 仅在需要重放 v1.3 参考页时
```

输出不含生成时间戳，同一份 JSON 重复构建逐字节一致（可直接 diff）。

## 数据契约

- 动作：`id` / `name` / `theme` / `equip` / `muscle` / `load`（展示用合并串）/ `sets` / `reps` / `alias`
  - `id` 形如 `ex18`，是分享链接与 localStorage 的唯一键；**不要改已发布条目的 id**，改 id 等于让旧链接失效。
  - 分享链接编码的是**库内序号**（`id` 的数字部分）⇒ 新增条目只能 append（`ex73`–`ex80` 即 v1.3 追加），插队会让历史链接全错位。
  - `load` 保留原样给人看；`sets`/`reps` 由它拆出，供编辑与出图使用。
- 方案：`presets[]`，每个 `{id, label, version, slogan?, days[]}`；v1.4 起只保留 `home`（力量版已按裁定移除，
  旧七日方案留在 git 历史与 `documents/solutions/slimdown-v1.3-week-theme-20261123.md`）。
  - `days[].key/label/short/theme/duration/slogan/items[]`，item 为 `{id, reps, muscle?, sets?, note?}`。
  - v1.3 居家七日：每天 `setsHint: "3–5"`（day 级建议组数，item 不带 `sets`）；周日是 `rest: true + recover[5]`（恢复清单）。
  - v1.2 力量版：item 带 `sets`，chip 由 min–max 计算（无 `setsHint` 时走该逻辑）。
- 主题：`themes[4] = {id, tag, name, time, pace, sets, video{title,url}, items[{cn,en,m,note?}]}`；
  动作序列与跟练视频绑死，**不挂库 id**（只读视图，不进编辑面板与分享链接）。
- 分享链接：`plan.html#p=v3|home|1=!!73*~20%20%E6%AC%A1,47*~15|...`
  （`v3|预设|` + 天序号从 1 起；每段 `主题!时长!动作表`，主题/时长与默认一致时留空；
  动作 = 库内序号 `*` `sets`（可空）`~` `encodeURIComponent(reps)`）。
  解码兼容 v1（只带动作）/ v2（主题!时长!动作）；未知 id 跳过并提示；非法片段静默忽略，不 eval。配色不进链接（观者偏好）。
  `preset` 段恒为 `home`；遇到已下线的预设（如旧 `strength` 链接）只 toast 一行并按当前方案渲染，不报错。
  `#p=` 优先级高于本机记忆，且**只生效一次**：不回写 localStorage，页面顶部给「恢复我的方案」。
- localStorage 键：`slimdown:ui:v2`（视图/预设/配色/动效/日签/面板分段/筛选/打卡）、
  `slimdown:edits:v2`（按预设分开存的方案改动）、`slimdown:baseline:v1`（档案页基线，只在本机）。
  旧键 `slimdownPlanTheme` / `slimdownPlanFx` / `slimdown:v1` 首次加载时搬入并删除。

## 方案页交互

- 顶部：`星期 | 主题` 分段（v1.4：预设下拉已移除，副标题并入同一行）。
- 周视图：七天一行铺满 100%（<1100px 横滚、卡 200px）；卡片 = 刀旗（星期/主题/时长）+ 组数 chip +
  编号动作行（35px，中文 + 目标肌群小字，英文进 `title` 与出图卡）+ 口号 + 打卡圆钮 `✓`；
  卡顶居中 `⠿` 拖拽或 `Alt+←/→` 交换**整天方案**（主题/时长/口号/动作/恢复清单一起来），星期标签不动。
- 主题视图：四张跟练卡（名称 + 部位标签 + 节奏 + 时长/建议组数 + 中英动作行 + 肌群 badge + 抖音跟练外链，`target=_blank rel=noopener`）。
- 面板（90vw×90vh，<760px 走底部抽屉满宽）：周视图 = 标题 + 七天页签（默认记忆中的日签）+ 编辑方案｜预览方案图片
  + 底部（分享链接·复制图片·打印·清除本机记忆 ＋ 保存方案·下载图片）；主题视图自动进预览（编辑与分享禁用）。
  预览区 = 左「方案列表」+ 右「预览（出图卡）」：周视图 8 项（本周速览 + 七天，默认今天）、主题视图 4 项（默认第 1 套）；
  点列表换预览，`↑/↓` 切换、`Enter` 下载；**下载图片 = 右栏预览这张**（合并长图/逐张已撤）。
- 打印：周视图 3 列、行高 26px、隐藏 masthead/chip/抓握条/打卡，7 卡压一页；主题视图 2 列。
- 配色：`<html data-theme>` 四套成套变量（赤金/墨绿/靛蓝/暖橙），左上角 🎨 下拉即时生效并记忆；
  出图与屏幕同色（克隆前把变量内联），打印翻浅色但保留主题强调色。
- 出图：PNG 宽 = 出图卡 CSS 宽（1x，720），单张；超过 6000px 自动等比缩放避免撞 canvas 上限。
- 卡片模式：`?card=day|week|theme`（`&d=mon` / `&t=1`），只留卡本身方便截图。
- 旧链接：`plan.html`（及带 `#p=` 的分享链接）经跳转桩直达 `index.html`，query 与 hash 均透传。

## 隐私

- 公开页不含个人身体数值：`archive.html` 基线表默认留空，填写值只存 `localStorage`（`slimdown:baseline:v1`），不上传。
- 分享链接只编码方案本身（动作 + 组次），不含体重/围度/昵称、不含配色与视图偏好。
- 打卡（`✓`）按日期存本机（保留 28 天），不上传、不进分享链接。

## 已知取舍

- 原库 69 条不含 `提踵` / `弓步走` / `锤式弯举`，但默认七日方案引用了它们 ⇒ 补 3 条（`ex70`-`ex72`）。
  v1.3 居家七日又用到 7 个库外动作（自重深蹲/卷腹/开合跳/弓步蹲/靠墙静蹲/仰卧起坐/后踢腿/马步蹲），
  再补 8 条（`ex73`-`ex80`，主题「居家自重」）⇒ 保住「方案动作都能在库里选到」这条链路。
- 主题四套的 41 个动作**不入库**：它们绑死跟练视频，属「跟练序列」而非「可查百科」；入库会让动作库变成半本跟练手册。
- 动作库走 table 模板（深色、可搜索/筛选/导出），方案页走参考页的深色暖调（可换肤、可出图），
  档案页仍走纸上质感（打印与长文阅读友好）；三者视觉不同源是刻意的：
  库是数据工具、方案是每天要看的卡、档案是要打印的册子。
- plan 页样式独立在 `_src/plan.css`，`base.css` 只服务 archive —— 深色改版不会波及档案页。
- `demos/slimdown/*.html` 在 `demos/` 子目录 ⇒ 不进 `scripts/baseline.py` 的 jobs/SKIP 覆盖（该门禁只扫 `demos/*.html` 顶层）；
  本案例的可重建性由 `scripts/build-slimdown.py` 与 `tests/test_slimdown_plan.py`（14 例）保证。
- 根级短链（如 `/demos-slimdown-plan.html`）本批**未做**：别名机制只认根级独立案例，嵌套页需扩 `_resolve_aliases`，另开一笔；
  `index.html` 化后 `/demos/slimdown/` 已足够短，优先级降低。
- `demo --rebuild` 的 registry 扫描跳过 basename=`index.html` ⇒ 登记面只留跳转桩行（标题「训练方案 · slimdown（已迁目录首页）」），计数不漂移（77 行）。

## v1.4 落地记录（2026-11-23）

- 移除「力量版」预设与下拉；视图标签改「星期 / 主题」；masthead 175px → 68px（1440 实测），副标题并入 view-bar。
- 面板 90vw×90vh（1440×900 实测 1296×810）；<760px 保留底部抽屉满宽。
- 出图收敛单张：左「方案列表」+ 右「预览」+ 「下载图片」（= 预览那张）；`↑/↓`/`Enter` 键盘；选中记忆 `shotWeek`/`shotTheme`。
- `plan.html` → `index.html`（`/demos/slimdown/` 直达），`plan.html` 留跳转桩保旧链接与 `#p=` 分享。

## v1.3 落地记录（2026-11-23）

- 数据来源：`居家训练计划（按星期）-v1.3-20261123.html`、`居家训练计划（按主题）-v1.3-20261123.html`（用户 Downloads，只读）。
- 搬运：`scripts/slimdown-import-v13.py`（正则取字面量，不 eval；断言 52 条动作 / 5 条恢复 / 4 套 41 项 / 库 80 条且前 72 条顺序不变）。
- 参考页把周六标成「恢复日」却仍排 9 个动作 ⇒ 判为笔误，本站周六按训练日渲染，恢复日只给周日。
- 点击态记忆（配色 / 视图 / 预设 / 日签 / 面板分段 / 筛选 / 打卡）全部存 `slimdown:ui:v2`，刷新不重置；
  首屏用内联脚本预置 `data-theme` / `data-view`，避免「先赤金后墨绿」闪一下。
