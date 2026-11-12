# slimdown · 减脂训练方案案例

来源：用户 2026-11-11 的两份单页（`训练动作库 v1.1`、`薄肌减脂执行档案 v2.4`），
2026-11-12 由 ops 会话收敛成可重建的案例（三页 + 单一数据源 + 生成脚本）。

## 结构

```
demos/slimdown/
  exercises.html    动作库 —— html-gen table 标准模板（深色数据工具页）
  plan.html         训练方案 —— 周视图 / 编辑 / 本机保存 / 分享链接 / 截图卡 / 复制图片
  archive.html      档案 —— 基线（本机填）/ 营养 / SOP / FAQ
  _src/             页模板与样式（不被 demo 扫描，只有 *.html 进 registry）
data/_slimdown-exercises.json   动作库单一源（72 条：原 69 条 + 计划引用的 3 条）
data/_slimdown-plan.json        默认七日方案 + 文案
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
- 方案：`days[].key/label/short/theme/duration/items[]`，item 为 `{id, sets, reps, note?}`。
- 分享链接：`plan.html#p=v1|1=18*4~8%2D10,19*3~10%2F%E8%85%BF|...`
  （天序号 = 从 1 起，动作 = 库内序号，`sets` `*`，`reps` 走 `encodeURIComponent`）。
  解码时未知 id 会被跳过并提示；非法片段静默忽略，不 eval。

## 隐私

- 公开页不含个人身体数值：`archive.html` 基线表默认留空，填写值只存 `localStorage`（`slimdown:baseline:v1`），不上传。
- 分享链接只编码方案本身（动作 + 组次），不含体重/围度/昵称。

## 已知取舍

- 原库 69 条不含 `提踵` / `弓步走` / `锤式弯举`，但默认七日方案引用了它们 ⇒ 本次补 3 条（`ex70`-`ex72`），
  否则方案页选不到自己计划的动作。若上游库后续再发布，合并时保留这 3 条。
- 动作库走 table 模板（深色、可搜索/筛选/导出），方案与档案走纸上质感（打印与截图友好）；
  两者视觉不同源是刻意的：前者是数据工具，后两者是阅读与分享面。
- `demos/slimdown/*.html` 在 `demos/` 子目录 ⇒ 不进 `scripts/baseline.py` 的 jobs/SKIP 覆盖（该门禁只扫 `demos/*.html` 顶层）；
  本案例的可重建性由 `scripts/build-slimdown.py` 保证。
