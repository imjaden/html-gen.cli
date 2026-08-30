# HTML-GEN-CL006 dev 实施 Prompt（2026-08-30）

你是 dev profile 的实施会话，在 /Users/jadenli/CodeSpace/html-gen.cli 项目目录内工作。
请以中文回复。只修改本需求范围内的文件，不做无关重构。

## 背景

HTML-GEN-CL006：scripts/tool-table-videos-syncer.py 增量模型两态→三态（新增/更新/跳过），
url 已存在且 yaml title 非空且不同 → 全字段覆盖更新；全包含提示补充「yaml 检查 N 条 / 涉及 M 个国家」统计。

设计文档：documents/solutions/table-videos-syncer-design-v1.2-20260830.md（已评审 PASS 90/A）
评审文档：documents/review/table-videos-syncer-v1.2-design-review-v1.0-20260830.md

## 评审折叠项（必须落实，见评审文档 §三）

- HG-SEC-081（🟡）：duration 判空须针对 **raw yaml 值**（`entry.get('duration') is None or == ''`），
  勿以 normalize 后 item 值判空——`normalize_duration(None)` 返回字面量 `'None'`（truthy）会错误覆盖 json 现值。
  建议 build_increments 为 updates 保留 raw duration，更新步按 raw 判空。
- HG-SEC-082（🟡）：cache yaml 为手工草稿随时漂移（实测 59 条/31 国，json 31 条：28 新增候选 + 土耳其 1 条 title 更新）。
  验证预期 = 「28 新增 + 1 更新」，勿硬编码。
- HG-SEC-083（🟢）：去重口径统一措辞「同 country+url 取首条」（源码 L135 已如此）。
- HG-SEC-084（🟢）：test_05 第三条「中东为何永不团结（重复）」v1.2 下由 skip 漂移为 update；
  显式调整 fixture（相同 title 保持 skip 语义，或改名体现 update 语义），断言随之明确。
- HG-SEC-085（🟢）：补「yaml title 空 → 保留 json 既有 title（跳过）」用例（2A 回归护栏）；
  N 统计口径排除畸形条目（缺 country_zh/url 被 warn+continue 的条目不计入 N）。

## 实现规格（来自 v1.2 设计 §4）

### 1. build_increments（scripts/tool-table-videos-syncer.py）
返回三态：new_items（url 不在该行 videos url 集合）/ updates（url 已存在且 yaml title 非空且 ≠ json 既有 title）/ skipped（其余）。
yaml 内部同 country+url 只取首条（去重，维持现状）。

### 2. run_apply（新增更新步，位于 append 之后、写 json 之前）
对 updates 按 url 定位既有 videos 条目：
- title：直接覆盖为 yaml 值（触发条件已保证非空）
- duration：yaml 非空才覆盖；空/缺省 → 保留 json 现值（防 normalize_duration(None) 写 'None'）
- platform：yaml 有值用 yaml 值；缺省 → detect_platform(url) 兜底；detect 空 → 保留既有值
输出 `[同步] 更新 N 条视频（title 变更）` 明细（国家: 旧 title → 新 title）。

### 3. G 判定（main 中）
`if not new_items` → `if not new_items and not updates`；双空才打印
`[提示] 所有 videos 均已包含，无需同步（yaml 检查 N 条 / 涉及 M 个国家）` 并 exit 0。
N = 去重后 yaml 有效条目数（与 build_increments 同口径），M = 去重国家数。

### 4. dry-run 预览
新增 `[预览] 更新 N 条（url 已存在, title 变更）:` 明细段（国家: 旧 title → 新 title + url）；
skipped 段措辞微调为「跳过 N 条（url 已存在, title 相同）」。

### 5. 测试（tests/test_sync_videos.py）
新增用例（v1.2 设计 §5 六例）：
- t14 title 更新 apply：yaml 同 url 新 title → json 既有条目 title 覆盖；yaml 镜像回写带新值；行数不变
- t15 仅更新无新增不早退：所有 url 已存在但 1 条 title 不同 → apply 执行写盘（非「均已包含」）
- t16 dry-run 更新预览：含 `[预览] 更新 N 条（url 已存在, title 变更）` 与旧→新 title；零写盘
- t17 全包含统计：输出 `（yaml 检查 N 条 / 涉及 M 个国家）`，N/M 与去重口径一致；零写盘
- t18 duration/platform 缺省保留：更新条目 yaml 缺 duration/platform 或 duration 空 → json 既有值保留，不写 'None'（HG-SEC-081 回归护栏：duration 判空用 raw 值）
- t19 platform 缺省 detect 兜底：更新条目 yaml 缺 platform 但 url 可识别 → json platform 更新为识别值
- t20 title 空不触发更新（HG-SEC-085）：yaml title 为空且 url 已存在 → 跳过，json 既有 title 保留
- 调整 test_05 fixture（HG-SEC-084）：第三条改为「相同 title」保持 skip 语义，或改名体现 update 语义
- N 统计口径：畸形条目（缺 country_zh/url）不计入 N（HG-SEC-085）

## 验证

1. cd /Users/jadenli/CodeSpace/html-gen.cli && python3 -m pytest tests/test_sync_videos.py -q -n 0（全过）
2. 确认 247 → 254 tests（test_sync_videos 13 → 20）
3. 真实数据 dry-run：`python3 scripts/tool-table-videos-syncer.py --dry-run`
   应显示「28 新增 + 1 更新（土耳其 title 变更，旧→新）」（N 随 yaml 草稿漂移，以三态行为为准）；
   **不要执行 --apply**（验证归 ops 步）

## 收尾

1. git add scripts/tool-table-videos-syncer.py tests/test_sync_videos.py（只加本需求文件；工作区
   data/_countries-data.json 的 note 改动为他人数据编辑，**不要 add 也不要 commit**）
2. git commit -m "feat@html-gen: syncer 三态增量更新 — title 变更全字段覆盖 + 全包含统计 (HTML-GEN-CL006)"
3. 打印实现摘要与测试结果（简短）

注意：不要 git push；不要修改设计文档；不要动 data/_countries-data.json 的 note 字段。
