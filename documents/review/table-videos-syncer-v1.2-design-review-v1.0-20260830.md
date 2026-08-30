# table-videos-syncer 设计评审报告 v1.2

> 评审对象: `documents/solutions/table-videos-syncer-design-v1.2-20260830.md`（commit `29bdbd2`）
> 闭环: HTML-GEN-CL006 ｜ 前置: HTML-GEN-CL002 / CL004（v1.1 已实现，设计 PASS 95/A）
> 评审日期: 2026-08-30 ｜ 评审者: Security Reviewer（L2 design-document-review）

---

## 一、结论

**✅ PASS 90/100（A）— 闭环，2 个 🟡 折叠进 dev 实施 prompt**

| 维度 | 评级 | 结论 |
|:---|:---:|:---|
| 合理性 Reasonableness | 🟢 | 三态模型是 v1.1 additive 语义的最小扩展，决策闭环，幂等闭环成立 |
| 严格性 Rigor | 🟡 | 2 项（duration 判空谓词未 pin / 数据印证漂移） |
| 安全性 Security | 🟢 | 无新增攻击面（safe_load / shell=False 沿用，title/duration 走 json.dump + 既有 escapeHtml） |

- 评分: 100 − 2×5（HG-SEC-081/082 🟡）= **90**
- Findings: **0 🔴 / 2 🟡（HG-SEC-081/082）/ 3 🟢（HG-SEC-083..085）**
- 决策追踪: 7/7 全数落入设计（1B/2A/3A/4A + platform/duration/触发判据三子决策），无遗漏、无矛盾（1 处措辞漂移 🟢 HG-SEC-083）
- 幂等闭环: 更新写盘 → W 镜像回写带新 title → 下次 url+title 相同 → 跳过，成立

---

## 二、逐项核对表（设计项 → 源码现状 → 可实现性 → 意见）

| # | 设计项 | 源码现状 | 可实现性 | 意见 |
|:-:|:---|:---|:---:|:---|
| 1 | build_increments 三态返回（new_items/updates/skipped） | L123-152 现返回 `(new_items, skipped)`，仅按 url 判新增/跳过，`existing` 为 url 集合 | ✅ | 需新增 updates 分支（url 在 existing + yaml title 非空 + ≠ json 既有 title）；需建 url→entry 映射取既有 title（🟢 HG-SEC-084） |
| 2 | run_apply 更新步（title 覆盖/duration 空保留/platform detect 兜底空保留） | L242-288 现仅 append 新增，无更新逻辑 | ✅ | 新增更新段，按 url 定位既有条目；duration 判空须 pin raw 值（🟡 HG-SEC-081） |
| 3 | G 判定修订（new 与 updates 双空才中断） | L358 现 `if not new_items` 即中断 | ✅ | 改 `if not new_items and not updates`，正确修复「仅更新无新增误判中断」 |
| 4 | 全包含统计（yaml 检查 N 条 / 涉及 M 个国家） | L359 现无统计，仅「均已包含，无需同步」 | ✅ | N=去重后有效条目数、M=去重国家数；口径需明确排除畸形条目（🟢 HG-SEC-085） |
| 5 | dry-run / --apply 输出更新段 | L363-373 dry-run 仅新增+跳过；L257-259 apply 仅新增 | ✅ | 加 `[预览]/[同步] 更新 N 条（title 变更）`，含旧→新 title（旧值取自 json） |
| 6 | W 回写（全局镜像，零改动） | L155-174 build_mirror_countries 已读 json 现值 | ✅ | 零改动，更新后自动带出新 title，幂等闭环 |
| 7 | E 重建 | L274-287 subprocess 列表参数 + shell=False | ✅ | 零改动，沿用 RIG-002 |

---

## 三、问题清单（Findings）

### 🟡 一般（2 项，折叠进 dev 实施 prompt）

| # | 位置 | 问题 | 建议 |
|:-:|:---|:---|:---|
| HG-SEC-081 | §4.2 step 4（item 构造）+ step 6（duration 空保留） | `build_increments` 构造 item 时 `duration = normalize_duration(entry.get('duration'))`，而 `normalize_duration(None)` 返回字面字符串 `'None'`（源码 L108）。若更新步以「item['duration'] 非空」为判据，yaml 缺 duration 被归一化为 `'None'`（truthy）→ 错误覆盖 json 现值，恰是 U2 声称要防止的 bug | 更新步判空须针对 raw yaml 值（`entry.get('duration') is None or == ''`），勿以 normalize 后 item 值判空；或 build_increments 为 updates 保留 raw duration |
| HG-SEC-082 | §1「yaml 31 条 / 24 国 / 31 已包含」、§4.3 示例、§6「dry-run 显示土耳其更新 1 条」 | 实测 cache yaml 现为 59 条 / 31 国（去重 url 59），json 31 条视频；yaml 中 28 条 url 不在 json（新增候选）+ 土耳其 1 条 title 不一致（更新候选）。「31/31 已包含」不成立；「dry-run 显示土耳其更新 1 条」实际会显示「28 新增 + 1 更新」 | 更新 §1/§4.3/§6 数据口径（或显式标注「快照，随手工草稿漂移」）；dev 实施 prompt §验证预期改为「28 新增 + 1 更新（土耳其 title 变更）」；验收 §6 改为以三态行为为准，勿硬编码计数 |

### 🟢 建议（3 项记录）

| # | 位置 | 问题 | 建议 |
|:-:|:---|:---|:---|
| HG-SEC-083 | §2 S 决策 / §1 / §4.2 step 4 / 源码 L135 `key=(cz,url)` | 4A「yaml 内部同 url 取首条」与 §1/§4.2/源码「同 country+url 取首条」措辞不一致 | 统一为「同 country+url 取首条」（源码已如此）；4A 措辞「同 url」改为「同 country+url」 |
| HG-SEC-084 | §5 测试计划 / test_sync_videos.py test_05 | test_05 第三条「中东为何永不团结（重复）」url 与 json 既有伊朗视频相同、title 带「（重复）」后缀 → v1.2 下由 skip 语义漂移为 update（title 覆盖）；现有断言（仅查行数/url 去重）仍过但用例语义漂移 | 显式调整 fixture（相同 title 保持 skip 语义，或改名体现 update 语义） |
| HG-SEC-085 | §5 六用例 | 2A（title 空不触发更新）与 §7「清空防护」无对应测试；N 口径「有效条目」未明确是否排除畸形条目（缺 country_zh/url 被 warn+continue） | 补「yaml title 空 → 保留 json 既有 title（跳过）」用例；明确 N 排除畸形条目 |

---

## 四、测试计划评审意见

- 6 新增用例（t14-t19）覆盖 title 覆盖 / 仅更新不早退 / dry-run 更新段 / 全包含统计 / duration+platform 空保留 / platform detect 兜底，覆盖 v1.2 主要行为变更，无「验收有、测试无」硬缺口。
- 缺口 2 处：① test_05 第三条语义漂移（🟢 HG-SEC-084，dev prompt 已提「如受影响按新语义调整」）；② 缺「title 空不触发」（2A）显式用例（🟢 HG-SEC-085）。
- t18「不写 'None'」是 HG-SEC-081 的回归护栏——若 dev 朴素实现（normalize_duration(None)→'None' 覆盖），t18 会失败；建议 dev 先按 HG-SEC-081 pin 谓词，t18 作为护栏。
- 计数 247→253（+6）与 test_sync_videos 13→19 一致。

---

## 五、结论理由

1. 三态模型（新增/更新/跳过）是 v1.1 additive 语义的最小扩展，更新触发判据唯一（title 不同）+ 幂等闭环（W 镜像带新 title → 下次 url+title 相同跳过）成立。
2. 7 项决策（1B/2A/3A/4A + platform/duration/触发判据三子决策）全数落入设计 §2，无遗漏、无矛盾。
3. 安全面无新增攻击面：safe_load / shell=False / json.dump + 既有 escapeHtml 沿用，title/duration/platform 均为本地受控数据。
4. G 判定修订（new_items 与 updates 双空才中断）正确修复「仅更新无新增误判中断」。
5. 2 个 🟡（duration 判空谓词 / 数据印证漂移）为规格精度 + 数据快照级，非架构/安全缺陷，折叠进 dev 实施 prompt 一并订正，不阻断闭环。

---

## 六、实测证据

| 验证项 | 命令/来源 | 结果 |
|:---|:---|:---|
| yaml 条数 | `yaml.safe_load` 解析 cache/data/_countries-data.videos.yaml | 59 条 / 31 国（去重 url 59，无 country+url 重复） |
| json videos | data/_countries-data.json | 31 条视频 / 31 url |
| 新增候选 | yaml url − json url | 28 条（德国/法国/伊朗/土耳其「死敌关系」/中国/…） |
| 更新候选 | url 在 json 且 title 不同 | 土耳其 1 条：「土耳其-凯末尔建立新秩序」→「土耳其-凯末尔建立新秩序#国父#第一任总统」（url 1ELCBlLmZBU 一致，json L1320 vs yaml L224） |
| normalize_duration(None) | 源码 L98-108 | `str(None)` = `'None'`（非 str/int → `return str(value)`），证实 HG-SEC-081 陷阱 |
| 幂等 | build_mirror_countries L155-174 | 读 json 现值回写，更新后自动带新 title |
| 决策一致性 | 设计 §2 七决策 vs 源码 | 7/7 落点命中，无悬空 |

---

## 七、结论与后续

PASS 90/A。三态模型 + 幂等闭环成立，7 决策全数落入设计，无 🔴 安全/架构缺陷。2 个 🟡（HG-SEC-081 duration 判空谓词、HG-SEC-082 数据印证漂移）为规格精度 + 数据快照级，折叠进 dev 实施 prompt 一并订正（dev prompt 已存在，§验证 dry-run 预期需改为「28 新增 + 1 更新」）。3 个 🟢 记录。生成/确认 dev 实施 prompt 转 dev；本次 auto-commit（仅 commit 不 push）。
