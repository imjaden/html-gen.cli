# table-videos-syncer v1.2 实现审计报告

> 审计对象: `scripts/tool-table-videos-syncer.py` + `tests/test_sync_videos.py`
> 闭环: HTML-GEN-CL006 ｜ 前置: HTML-GEN-CL002 / CL004（v1.1 已闭环）
> 审计日期: 2026-08-30 ｜ 审计者: Security Reviewer（L2 implementation-audit）
> 设计定稿: `documents/solutions/table-videos-syncer-design-v1.2-20260830.md`（评审 PASS 90/A）
> 设计评审: `documents/review/table-videos-syncer-v1.2-design-review-v1.0-20260830.md`（HG-SEC-081..085）

---

## 一、审计结论

**✅ PASS 100/100（A）— 三态增量模型源码级 + 实测双重核验通过，5 项评审折叠项全数闭合，ops 遮蔽缺陷已修复并带回测试**

| 维度 | 评级 | 结论 |
|:---|:---:|:---|
| 三态语义 (build_increments) | 🟢 | 新增/更新/跳过三态判定与设计 §4.2 step 4 逐条一致，updates 携带 old_title + raw_duration |
| 更新步 (run_apply) | 🟢 | title 覆盖 / duration raw 判空 / platform yaml→detect→保留既有 全落地；遮蔽 target 缺陷已修复 |
| G 判定 + 统计 | 🟢 | new/updates 双空才中断；N/M 去重口径正确，畸形条目排除 |
| 幂等 + 输出形态 | 🟢 | W 镜像带新 title → 下次跳过，闭环成立；dry-run/apply 三段输出符合 §4.3 |
| 测试覆盖 | 🟢 | t14-t21 覆盖设计 §5 + HG-SEC-081..085 全部折叠项；test_05 fixture 调整正确 |

- Findings: **0 🔴 / 0 🟡 / 0 🟢**
- 实测: 专项 21 passed ｜ 全量 255 passed ｜ dry-run 28 新增 + 1 更新 + 30 跳过（零写盘）
- 治理: 2 个实施 commit 只含 syncer + tests，未夹带 `data/_countries-data.json` 他人 note 编辑

---

## 二、逐项核验表（设计项 → 实现位置 → 符合性 → 意见）

| # | 设计项 | 实现位置 | 符合性 | 意见 |
|:-:|:---|:---|:---:|:---|
| 1 | 新增：url（strip）不在该行 videos url 集合 | `build_increments` L150-159（`existing_map` + `if url not in existing_map`） | ✅ | url strip 后建 `existing_map` 键，尾部空格不误判新增 |
| 2 | 更新：url 已存在 + yaml title 非空 + ≠ json 既有 title | L160-171（`yaml_title and yaml_title != existing_title`） | ✅ | 触发判据唯一 = title 不同；updates 携带 `old_title`（L166）+ `raw_duration`（L169） |
| 3 | 跳过：其余（title 相同 / title 空） | L172-179（else 分支） | ✅ | title 空落 skip（2A 清空防护，t20 护栏） |
| 4 | yaml 内部同 country+url 去重 | L138 + L145-148（`seen` 集合，`key=(cz,url)`） | ✅ | HG-SEC-083 措辞「同 country+url 取首条」已统一（源码原本即此） |
| 5 | 更新步 title 覆盖 | `run_apply` L300（`existing_entry['title'] = it['title']`） | ✅ | 触发条件已保证非空 |
| 6 | 更新步 duration raw 判空才覆盖（HG-SEC-081） | L301-302（`if it['raw_duration'] is not None and it['raw_duration'] != ''`） | ✅ | 判空针对 raw yaml 值，杜绝 `normalize_duration(None)→'None'` 覆盖现值 |
| 7 | 更新步 platform yaml→detect→保留既有（U1） | L303-305（`it['platform'] or detect_platform(...)` + `if platform:`） | ✅ | detect 空时不删 json 既有 platform |
| 8 | 无 target 参数遮蔽（ops 修复点） | L296（`existing_entry`，非 `target`）+ L332（`resolve_rebuild_args(target, ...)` 传参正确） | ✅ | 7dbaf4c 将循环局部变量 `target`→`existing_entry`，rebuild 配置不再被视频条目遮蔽 |
| 9 | 防御分支（url 已存在才进 updates） | L296-299（`existing_entry is None → continue`） | ✅ | 正常不会缺失，防御性兜底 |
| 10 | G 判定：new 与 updates 双空才中断 | `main` L411（`if not new_items and not updates`） | ✅ | 修复「仅更新无新增误判中断」 |
| 11 | 全包含统计 N/M（去重 + 畸形排除，HG-SEC-085） | L412-414（`all_items = new+updates+skipped`，`len` + `len(set(country))`） | ✅ | 畸形条目（缺 country_zh/url）在 build_increments 已 warn+continue，不进三态列表 |
| 12 | dry-run / --apply 输出三段 + 统计提示 | L420-434（dry-run）/ L285-310（apply） | ✅ | 措辞区分「title 变更」vs「title 相同」 |
| 13 | W 回写幂等 | `build_mirror_countries` L183-202 + `run_apply` L318-322 | ✅ | 读 json 现值回写，更新后带新 title，下次 url+title 相同 → 跳过 |

---

## 三、问题清单

### 🔴 严重（0 项）

无。

### 🟡 一般（0 项）

无。

### 🟢 建议（0 项）

无。

> 附注（非 finding，供记录）：实施链中 `df2e28c` 曾引入「更新步循环局部变量命名 `target` 遮蔽 run_apply 的 target 参数 → `resolve_rebuild_args(target)` 拿到视频条目而非 yaml target 段，rebuild 三键配置（github_url/home_url/favicon）被静默丢弃、回退固定默认」缺陷。该缺陷已由 ops 核查发现并于 `7dbaf4c` 修复（`target`→`existing_entry`），且带回 `test_21`（rebuild 配置透传断言）作为回归护栏。审计以 HEAD 终态为准（缺陷已闭环），不计入 findings。

---

## 四、测试与实测证据

| 验证项 | 命令 | 结果 |
|:---|:---|:---|
| 专项测试 | `python3 -m pytest tests/test_sync_videos.py -q -n 0` | **21 passed** (0.96s) |
| 全量测试 | `python3 -m pytest tests/ -q -n 4` | **255 passed**, 4 warnings (35.98s) |
| 真实数据 dry-run | `python3 scripts/tool-table-videos-syncer.py --dry-run` | **[预览] 新增 28 条 + [预览] 更新 1 条（土耳其 title 变更）+ [预览] 跳过 30 条**，零写盘（未执行 --apply） |
| 更新候选验证 | dry-run 更新段 | `土耳其: 土耳其-凯末尔建立新秩序 → 土耳其-凯末尔建立新秩序#国父#第一任总统 https://v.douyin.com/1ELCBlLmZBU/` — 与设计 §1 实时印证一致 |
| 提交完整性 | `git show --stat df2e28c 7dbaf4c` | 两 commit 均只改 `scripts/tool-table-videos-syncer.py` + `tests/test_sync_videos.py`，未混入 `data/_countries-data.json` |
| 遮蔽修复 diff | `git show 7dbaf4c` | 循环局部 `target` → `existing_entry` 共 6 处，`resolve_rebuild_args(target)` 参数未被遮蔽 |

### 评审折叠项闭合核对

| 折叠项 | 严重度 | 闭合位置 | 证据 |
|:---|:---:|:---|:---|
| HG-SEC-081 duration 判空 pin raw 值 | 🟡 | `build_increments` L169（保留 `raw_duration`）+ `run_apply` L301（raw 判空） | t18（缺 duration/platform → 保留现值，json 无 'None'） |
| HG-SEC-082 数据印证漂移 | 🟡 | dev prompt §验证预期「28 新增 + 1 更新」 | 实测 dry-run 精确 28+1+30 |
| HG-SEC-083 4A 措辞统一 | 🟢 | `build_increments` L145 `key=(cz,url)` + 注释 | 源码原本即「同 country+url」 |
| HG-SEC-084 test_05 语义漂移 | 🟢 | `test_05` L239-245（第三条 title 改为「中东为何永不团结」= 与 json 相同） | 保持 skip 语义，注释说明勿用「（重复）」后缀 |
| HG-SEC-085 title 空用例缺口 + N 口径 | 🟢 | `test_20`（title 空 → 保留既有）+ `test_17`（畸形条目不计 N） | 实测 255 passed 含 t17/t20 |

---

## 五、结论理由

1. 三态增量模型（new_items/updates/skipped）实现与设计 §4.2 step 4 逐条一致：触发判据唯一（url 已存在 + yaml title 非空 + title ≠ json 既有 title），title 相同/空落 skip，维持幂等。
2. 更新步三字段语义全落地：title 直接覆盖、duration 以 raw yaml 值判空（HG-SEC-081，杜绝 `'None'` 覆盖）、platform yaml→detect→保留既有（U1，不删既有数据）。
3. ops 核查发现的 `target` 变量遮蔽缺陷（df2e28c 引入）已在 7dbaf4c 正确修复，且 `test_21` 用 rebuild 配置透传断言锁死回归——若未来再遮蔽 target，`[执行]` 行会回退固定默认，断言即失败。
4. G 判定修订（new 与 updates 双空才中断）正确修复「仅更新无新增误判中断」；全包含统计 N/M 与 build_increments 同口径（去重 + 畸形条目排除）。
5. 三项实测证据全数通过且与设计预期精确吻合（专项 21 passed / 全量 255 passed / dry-run 28+1+30 零写盘），安全面沿用已审计路径（safe_load / shell=False / json.dump），零新增攻击面。

---

## 六、处理

- ✅ PASS → 审计三件套 + commit（仅 commit 不 push，AGENTS.md 约定 + 本任务约束）
- 报告: `documents/review/table-videos-syncer-v1.2-impl-audit-v1.0-20260830.md`
- 追踪文件: `.review-level.yaml`（append implementation-audit 条目）+ `review-log.md`（append 审计条目）
- commit: `docs@review: syncer v1.2 实现审计 (HTML-GEN-CL006)`
