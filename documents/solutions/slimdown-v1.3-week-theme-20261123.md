# slimdown 方案页 v1.3：按星期 / 按主题双视图 + 点击态记忆 · 2026-11-23

> 状态：**已实施**（本批一条龙；落点见 §4）。真值以 `git log` / `data/_slimdown-plan.json` / `tests/test_slimdown_plan.py` 为准，本页只记「为什么这样定」。
> 来源：用户两份参考页（`居家训练计划（按星期）-v1.3-20261123.html`、`…（按主题）…`，Downloads 只读）+ 「所有点击动作刷新后不要重置」的追加要求。

## 1. 决策记录（D1–D8 用户「全采推荐」关闭，S1–S9 同）

| 项 | 决策 |
|---|---|
| D1 视图承载 | plan.html 单页双视图（顶部 `按星期 / 按主题` 分段），出图/换肤/打印只有一份实现 |
| D2 旧方案 | 保留为 preset：`presets[home(v1.3 居家七日), strength(v1.2 力量版)]`，面板上方下拉切换，按预设分开存编辑稿 |
| D3 主题视图 | 只读（不进编辑面板、不进分享链接）；动作序列与跟练视频绑死，编辑无意义 |
| D4 动作库 | append `ex73`–`ex80`（居家自重 8 条），库 72→80；分享链接编码库内序号 ⇒ **只许 append** |
| D5 出图 | 主题视图：合并长图（720×3002 实测）+ 逐张 4 张；周视图维持今日卡 / 本周速览 / 逐日；>4000–6000px 等比缩放 |
| D6 别名 | 短链本批**撤回**（用户明确），`html-gen.py` / `_aliases.json` / `test_aliases.py` 未动 |
| D7 抖音外链 | 保留 4 条（`target=_blank rel=noopener`，不嵌播放器、不引第三方脚本），出图只写视频标题 |
| D8 周六标签 | 参考页把周六标「恢复日」却仍排 9 个动作 ⇒ 判笔误；本站周六=训练日，恢复日只给周日 |
| S1–S4 | 合并长图默认 + 逐张次按钮；`plan` 版本升 v1.3 / 2026-11-23（旧 preset 内标 v1.2）；库新增条目沿用参考页名称与肌群；参考页原件不入仓（只记哈希与条数断言） |
| S5 状态存储 | 单键 `slimdown:ui:v2` 管全部点击态；旧键 `slimdownPlanTheme` / `slimdownPlanFx` / `slimdown:v1` 首次加载搬入并删除 |
| S6 分享 vs 记忆 | `#p=` 优先一次且**不回写** localStorage；顶部提示条给「恢复我的方案」 |
| S7 记忆边界 | 记：视图 / 预设 / 配色 / 动效 / 日签 / 面板分段 / 筛选+搜索词 / 打卡；不记：弹层开合、滚动像素 |
| S8 打卡颗粒 | 按日期存（`'2026-11-23': ['wed']`，可补练别的天），保留 28 天，本机不传 |
| S9 复位入口 | 面板底部「清除本机记忆」（清 `slimdown:*` 并重载） |

## 2. 数据映射（参考页动作 → 库 id）

| 参考页动作 | 库 id | 说明 |
|---|---|---|
| 深蹲 / 卷腹 / 开合跳 / 弓步蹲 / 靠墙静蹲 / 仰卧起坐 / 后踢腿 / 马步蹲 | ex73–ex80 | v1.3 新增（主题「居家自重」） |
| 平板支撑 / 俯卧撑 | ex47 / ex51 | 复用既有条目 |

校验口径（`scripts/slimdown-import-v13.py` 内置断言）：52 条动作 / 5 条恢复 / 4 套 41 项 / 库 80 条且 `ex01`–`ex72` 顺序不变。

## 3. 关键技术点

- **首屏防闪烁**：`plan.tpl` 在 `<style>` 之前内联一段极小的读 `slimdown:ui:v2` 脚本，先写 `data-theme` / `data-view` 再渲染。
- **编辑稿分预设**：`slimdown:edits:v2 = {v:2, byPreset:{home:[…], strength:[…]}}`；旧 `slimdown:v1`（力量版时代）首次加载迁进 `byPreset.strength`。
- **分享 v3**：`v3|<preset>|<天号>=<主题>!<时长>!<动作表>`，动作 `序号*sets~reps`（`sets` 可空），解码兼容 v1/v2。
- **出图**：`_src/shot.js` 抽出 `collectCss / themeVarsInline / nodeToBlob / download`；`nodeToBlob` 按 `maxH` 等比缩放，避免 iOS canvas 面积上限。
- **隐藏属性陷阱**：`#weekRow` / `.p-tabs` / `#themeRow` 都显式设了 `display`，`hidden` 会失效 ⇒ CSS 里补 `[hidden]{display:none!important}`。

## 4. 落点与验收

- 落点：`demos/slimdown/_src/{plan.tpl,plan.css,state.js,shot.js,plan.js}`、`scripts/build-slimdown.py`（JS 三段拼接 + 预设摘要）、
  `scripts/slimdown-import-v13.py`、`data/_slimdown-{plan,exercises}.json`、`tests/test_slimdown_plan.py`、`documents/testing.md`（49 文件）。
- 验收（真跑）：`build-slimdown.py --dry-run/--apply` 幂等；1440 下 7 卡各 194px 无横向溢出；1100/390 横滚；主题视图 4 卡；
  出图 720×643（日卡）/ 720×3002（主题长图）/ 4 张逐图，像素采样与 `--bg` `--acc` 同色；刷新后配色/视图/预设/日签/打卡全保持；
  `#p=` 分享不回写本机；`pytest tests/ -q -n 4` 500 passed / 103 subtests；`baseline.py --check` 50/50（slimdown 目录仍是 SKIP）。
- 待授权：`AGENTS.md` 测试计数 486 → 500（受保护文件，待批件 `.Agents.md-ops-htmlgen-demo`）。
