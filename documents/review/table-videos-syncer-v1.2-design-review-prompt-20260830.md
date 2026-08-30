# HTML-GEN-CL006 设计评审 Prompt（2026-08-30）

你是 review profile 的设计评审会话，在 /Users/jadenli/CodeSpace/html-gen.cli 项目目录内工作。
请以中文回复，评审意见全部使用中文。

## 背景

HTML-GEN-CL006：scripts/tool-table-videos-syncer.py 增量模型两态→三态（新增/更新/跳过），
url 已存在且 yaml title 非空且不同 → 全字段覆盖更新；全包含提示补充「yaml 检查 N 条 / 涉及 M 个国家」统计。

探讨决策（本对话已锁定）：
- 1B：全字段覆盖（title/duration/platform 以 yaml 为准，空值保留既有）
- 2A：yaml title 为空 → 不触发更新
- 3A：统计仅 yaml 输入侧（N 条 / M 国）
- 4A：统计用去重口径（yaml 内部同 url 取首条）
- 1A（platform 子项）：yaml platform 缺省 → detect_platform(url) 兜底；detect 空 → 保留 json 既有值
- 2A（duration 子项）：yaml duration 空 → 保留 json 现值（防写 'None'）
- 3A（触发判据）：仅 title 不同触发；url 相同 title 相同 → 跳过

## 待评审文档

documents/solutions/table-videos-syncer-design-v1.2-20260830.md（v1.2 设计）

## 参考材料（只读）

- documents/solutions/table-videos-syncer-design-v1.1-20260829.md（v1.1 设计）
- scripts/tool-table-videos-syncer.py（当前源码）
- tests/test_sync_videos.py（当前 13 用例）
- data/_countries-data.json + cache/data/_countries-data.videos.yaml（实时数据口径参考）

## 评审任务

1. 对照 v1.2 设计与当前源码逐项核对可实现性：
   - build_increments 三态返回改造（new_items / updates / skipped）
   - run_apply 更新步：title 覆盖 / duration 空保留 / platform detect 兜底空保留
   - G 判定：new_items 与 updates 双空才中断（仅更新无新增不早退）
   - 全包含统计消息（去重口径）
   - dry-run / --apply 输出新增更新段
2. 校验决策一致性：1B/2A/3A/4A + 三个子决策是否完整落入设计；有无遗漏或矛盾
3. 校验幂等性：更新写盘 → W 镜像回写 → 下次运行跳过的闭环是否成立
4. 校验测试计划：6 个新增用例是否覆盖全部行为变更；有无缺口（如 test_05 第三条由跳过变更新的影响是否说明）
5. 风险与边界：'None' 防护、空 title 清空防护、platform 不清除、触发判据收敛是否到位

## 输出

产出评审文档 documents/review/table-videos-syncer-v1.2-design-review-v1.0-20260830.md，
结构参照该目录既有评审文档风格，包含：

1. 评审结论：PASS / CONDITIONAL / FAIL（附一句理由）
2. 逐项核对表（设计项 → 源码现状 → 可实现性 → 意见）
3. 问题清单：严重 / 一般 / 建议 三档（每项含位置、问题、建议）
4. 测试计划评审意见
5. 结论理由（3-5 条）

## 收尾

评审文档写好后：

1. git add documents/review/table-videos-syncer-v1.2-design-review-v1.0-20260830.md
2. git commit -m "docs@review: syncer v1.2 设计评审 (HTML-GEN-CL006)"
3. 打印评审结论与问题清单摘要（简短，供 ops 会话转达）

注意：不要修改任何源码/测试/设计文档，只做评审与写评审文档。不要 git push。
