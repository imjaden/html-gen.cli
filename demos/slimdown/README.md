# slimdown · 减脂训练方案案例

来源：用户 2026-11-11 的两份单页（`训练动作库 v1.1`、`薄肌减脂执行档案 v2.4`），
2026-11-12 由 ops 会话收敛成可重建的案例（三页 + 单一数据源 + 生成脚本）。

## 结构

```
demos/slimdown/
  exercises.html    动作库 —— html-gen table 标准模板（深色数据工具页）
  plan.html         训练方案 —— 深色七日卡 / 四套主题 / 右下角面板（编辑·预览·出图）
  archive.html      档案 —— 基线（本机填）/ 营养 / SOP / FAQ
  _src/             页模板与样式（不被 demo 扫描，只有 *.html 进 registry）
    plan.css        plan 页专用（深色 + 主题变量）；base.css 只服务 archive
data/_slimdown-exercises.json   动作库单一源（72 条：原 69 条 + 计划引用的 3 条）
data/_slimdown-plan.json        默认七日方案 + 文案 + 每日口号
scripts/build-slimdown.py       一次重建三页
```

## 重建

```bash
python3 scripts/build-slimdown.py --dry-run   # 先看将写哪些文件
python3 scripts/build-slimdown.py --apply
```

输出不含生成时间戳，同一份 JSON 重复构建逐字节一致（可直接 diff）。

## 数据契约

- 动作：`id` / `name` / `theme` / `equip` / `muscle` / `load`（展示用合并串）/ `sets` / `reps` / `alias`
  - `id` 形如 `ex18`，是分享链接与 localStorage 的唯一键；**不要改已发布条目的 id**，改 id 等于让旧链接失效。
  - `load` 保留原样给人看；`sets`/`reps` 由它拆出，供编辑与出图使用。
- 方案：`days[].key/label/short/theme/duration/slogan/items[]`，item 为 `{id, sets, reps, note?}`。
- 分享链接：`plan.html#p=v2|1=!!18*4~8%2D10,19*3~10%2F%E8%85%BF|...`
  （天序号从 1 起；每段 `主题!时长!动作表`，主题/时长与默认一致时留空；
  动作 = 库内序号，`sets` `*`，`reps` 走 `encodeURIComponent`）。
  解码兼容 v1（只带动作）；未知 id 跳过并提示；非法片段静默忽略，不 eval。主题不进链接（观者偏好）。
- 方案页交互：七天一行铺满 100%（<1100px 横滚、卡 200px）；
  卡片 = 刀旗（星期/主题/约时长）+ 组数 chip + 编号动作行（名 + 次数徽章）+ 口号；
  `⠿` 拖拽或 `Alt+←/→` 交换**整天方案**（主题/时长/口号/动作一起换，星期标签不动）；
  点卡片 / 右下角 `✎` 打开面板，`⤓` 直接进预览；面板 = 标题 + 七天页签（默认今天）+ 功能区
  （编辑方案｜预览方案图片）+ 底部（分享链接·复制图片·打印 ＋ 保存方案·下载图片）。
- 主题：`<html data-theme>` 四套成套变量（赤金/墨绿/靛蓝/暖橙），左上角 🎨 下拉即时生效，
  存 `localStorage.slimdownPlanTheme`；出图与屏幕同色（克隆前把变量内联），打印翻浅色但保留主题强调色。
- 出图：PNG 宽 = 预览实际宽（1x，720）；动作行含组数 + 次数；单行省略不压列。

## 隐私

- 公开页不含个人身体数值：`archive.html` 基线表默认留空，填写值只存 `localStorage`（`slimdown:baseline:v1`），不上传。
- 分享链接只编码方案本身（动作 + 组次），不含体重/围度/昵称。

## 已知取舍

- 原库 69 条不含 `提踵` / `弓步走` / `锤式弯举`，但默认七日方案引用了它们 ⇒ 本次补 3 条（`ex70`-`ex72`），
  否则方案页选不到自己计划的动作。若上游库后续再发布，合并时保留这 3 条。
- 动作库走 table 模板（深色、可搜索/筛选/导出），方案页走参考页的深色暖调（可换肤、可出图），
  档案页仍走纸上质感（打印与长文阅读友好）；三者视觉不同源是刻意的：
  库是数据工具、方案是每天要看的卡、档案是要打印的册子。
- plan 页样式独立在 `_src/plan.css`，`base.css` 只服务 archive —— 深色改版不会波及档案页。
- `demos/slimdown/*.html` 在 `demos/` 子目录 ⇒ 不进 `scripts/baseline.py` 的 jobs/SKIP 覆盖（该门禁只扫 `demos/*.html` 顶层）；
  本案例的可重建性由 `scripts/build-slimdown.py` 保证。
