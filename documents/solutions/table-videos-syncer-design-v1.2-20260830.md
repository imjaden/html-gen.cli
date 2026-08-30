# A 型表格 videos 同步辅助脚本设计 v1.2 (2026-08-30)

> 闭环: HTML-GEN-CL006 · 探讨确认: 1B 2A 3A 4A + 1A 2A 3A（2026-08-30）
> 前置: HTML-GEN-CL002 / CL004（v1.1 已实现）
> v1.2: 在 v1.1 additive 语义上扩展「url 已存在 + title 变更 → 全字段覆盖更新」；
>       全包含提示补充统计数字（yaml 检查 N 条 / 涉及 M 个国家）

## 1. 背景与需求

v1.1 语义为 **additive**（只 append 不删除不覆盖）：yaml 增量中 url 已存在于 json
的条目一律跳过。实际使用中发现：

- 视频标题可能事后修订（如《土耳其-凯末尔建立新秩序》→《土耳其-凯末尔建立新秩序#国父#第一任总统》），
  但 add-only 导致 json 中旧 title 永不更新，同步脚本无法修复；
- 全包含提示「所有 videos 均已包含，无需同步」无统计信息，无法快速确认本次检查范围。

本版需求（HTML-GEN-CL006）：

1. url 已存在时同时判断 title：若 yaml title 非空且与 json 既有 title 不同 → 触发
   覆盖更新（全字段：title / duration / platform 以 yaml 为准，空值保留既有）；
   title 相同 → 仍为跳过（维持幂等）。
2. 全包含提示补充统计：`[提示] 所有 videos 均已包含，无需同步（yaml 检查 N 条 / 涉及 M 个国家）`，
   统计口径与增量模型一致（yaml 内部同 country+url 只取首条，去重）。

实时数据印证：yaml 31 条 / 24 国，json 31 条视频全部已包含（31/31），其中
土耳其 1 条 title 不一致 → 本版生效后下次同步自动修复。

## 2. 决策记录

| 项 | 决策 | 说明 |
|:---|:---|:---|
| U 更新触发 | url 已存在 + yaml title 非空 + title ≠ json 既有 title → 覆盖更新 | 触发判据唯一 = title 不同（3A）；url 相同 title 相同 → 跳过；title 空不触发（2A，防空 title 清空既有标题） |
| U1 platform | yaml 有值用 yaml；缺省 → detect_platform(url) 兜底（与新增条目一致）；detect 仍空 → 保留 json 既有值 | 不清除既有数据（1A） |
| U2 duration | yaml 非空才覆盖；空/缺省 → 保留 json 现值 | 防 normalize_duration(None) 写入 'None' 字符串（2A） |
| S 统计 | 全包含提示加「yaml 检查 N 条 / 涉及 M 个国家」 | 仅 yaml 输入侧（3A）；去重口径与增量模型一致，yaml 内部同 url 取首条（4A） |
| W 回写 | 维持全局镜像，零改动 | json 更新后 yaml 镜像自动带出新值，下次运行 url+title 相同 → 跳过，幂等闭环 |

其余 v1.1 决策（A 格式 / B 存放 / C platform 识别 / D 依赖 / E 重建 / F 校验 / G 无增量）
维持不变；v1.1「additive 语义：只 append 不删除不覆盖」修订为「append + 覆盖更新
（仅限 url 已存在且 title 变更），不删除」。

## 3. yaml 格式规格（A）

与 v1.1 完全一致（countries 平铺列表，字段 country_zh/title/url/duration/platform；
duration 引号包裹；url strip 尾部空白），本版不新增字段。

## 4. 脚本行为规格

### 4.1 CLI

```
scripts/tool-table-videos-syncer.py <yaml-path> [--dry-run] [--apply]
```

与 v1.1 一致（含 --empty-video 三向互斥），无新增参数。

### 4.2 执行流程（--apply）

1. 解析 yaml（yaml.safe_load），取 target.data / target.html 与 countries 列表【RIG-001 / HG-SEC-054】
2. 读 target.data json；建 country_zh → row 索引；路径以项目根为基准解析【RIG-003 / HG-SEC-056】
3. F3 校验：countries 每条 country_zh 必须在 json 行存在；任一缺失 → 清单 exit 1 零写盘
4. **逐条计算三态增量（v1.2 核心）**：url（strip）不在该行 videos url 集合中 → `new_items`；
   url 已存在且 yaml title 非空且 ≠ json 既有 title → `updates`；
   否则 → `skipped`。yaml 内部同 country+url 只取首条（去重口径与 S 统计一致）
5. **G 判定（v1.2 修订）**：`new_items` 与 `updates` 均为空 → 打印统计提示
   `[提示] 所有 videos 均已包含，无需同步（yaml 检查 N 条 / 涉及 M 个国家）`，exit 0 零写盘；
   任一非空 → 继续（仅更新、无新增也必须执行写盘，否则土耳其场景被误判中断）
6. 按 country_zh 分组补充：新增条目 append 至 json 行 videos（platform 缺省按 C1 识别）；
   **更新条目按 url 定位既有 videos 条目**：
   - title：直接覆盖为 yaml 值（触发条件已保证非空）
   - duration：yaml 非空才覆盖（U2）；空 → 保留现值
   - platform：yaml 有值用 yaml 值；缺省 → detect_platform(url) 兜底；detect 空 → 保留既有（U1）
7. W 回写：json 全部 videos 展平重建 yaml countries 段（target 保留原样）【零改动，自动带出新值】
8. E 重建：subprocess 调 html-gen.py table（列表参数、shell=False）【RIG-002 / HG-SEC-055】

### 4.3 输出形态

dry-run 预览（新增「更新」段，措辞区分 title 相同跳过）：

```
[预览] 新增 1 条:
  - 缅甸: 缅甸-散装缅甸 https://v.douyin.com/-IIdHuXNL0o/ (6:55)
[预览] 更新 1 条（url 已存在, title 变更）:
  - 土耳其: 土耳其-凯末尔建立新秩序 → 土耳其-凯末尔建立新秩序#国父#第一任总统
[预览] 跳过 1 条（url 已存在, title 相同）:
  - 伊朗: 中东为何永不团结 https://v.douyin.com/Ez_SJIkymk0/
[预览] 将回写 yaml countries 段（全局镜像）+ 重建 demos/countries-table.html
[提示] 使用 --apply 执行
```

--apply 同步段：

```
[同步] 新增 1 条视频
  - 缅甸: ...
[同步] 更新 1 条视频（title 变更）
  - 土耳其: 土耳其-凯末尔建立新秩序 → 土耳其-凯末尔建立新秩序#国父#第一任总统
```

全包含中断（v1.2 统计）：

```
[提示] 所有 videos 均已包含，无需同步（yaml 检查 31 条 / 涉及 24 个国家）
```

## 5. 测试计划

test_sync_videos.py（v1.1 的 13 例保持；新增用例）：

| 用例 | 断言 |
|:---|:---|
| t14 title 更新 apply | yaml 同 url 新 title → json 既有条目 title 被覆盖；yaml 镜像回写带新值；行数不变 |
| t15 仅更新无新增 → 不早退 | 所有 url 已存在但 1 条 title 不同 → apply 执行写盘（returncode 0 + json 更新），非「均已包含」 |
| t16 dry-run 更新预览 | 预览含 `[预览] 更新 N 条（url 已存在, title 变更）` 与旧→新 title；零写盘 |
| t17 全包含统计 | 全存在 → 输出 `（yaml 检查 N 条 / 涉及 M 个国家）`，N/M 与去重口径一致；零写盘 |
| t18 duration/platform 缺省保留 | 更新条目 yaml 缺 duration/platform 或 duration 空 → json 既有 duration/platform 保留，不写 'None' |
| t19 platform 缺省 detect 兜底 | 更新条目 yaml 缺 platform 但 url 可识别 → json platform 更新为识别值 |

预计 247 → 253 tests（+6）。

## 6. 验收清单

- [ ] build_increments 三态返回（new_items / updates / skipped），触发条件 = url 已存在 + yaml title 非空 + title 不同
- [ ] run_apply 更新步：title 覆盖 / duration 空保留 / platform detect 兜底空保留
- [ ] G 判定含 updates：仅更新无新增不早退
- [ ] 全包含提示含「yaml 检查 N 条 / 涉及 M 个国家」（去重口径）
- [ ] dry-run / --apply 输出含更新段
- [ ] test_sync_videos 新增 6 用例全通过；全量 pytest -n 4 通过（253）
- [ ] 真实数据验证：dry-run 显示土耳其更新 1 条 → --apply 后 json/yaml/html 三态复核
- [ ] 实现审计 PASS（review 子会话）

## 7. 风险与边界

- 幂等性：更新写盘后 yaml 镜像带出新 title，下次运行 url+title 相同 → 跳过，无重复写
- 'None' 防护：duration 空/缺省不覆盖（U2），杜绝 normalize_duration(None) → 'None'
- 清空防护：yaml title 空不触发更新（2A），不覆盖既有标题
- platform 保留：yaml 与 detect 均无值时不删除 json 既有 platform（U1），符合「不删除」原则
- 触发判据收敛：仅 title 不同触发，url 相同 title 相同仅 duration/platform 不同 → 不更新（3A），
  避免误把 yaml 未维护的 duration/platform 当作权威

## 8. 修订记录

- v1.1 (2026-08-29)：HTML-GEN-CL002/CL004，additive 语义 + rebuild 三参数 + --empty-video + 缺省 yaml 路径
- v1.2 (2026-08-30)：HTML-GEN-CL006，三态增量模型 + 全字段覆盖更新 + 全包含统计
