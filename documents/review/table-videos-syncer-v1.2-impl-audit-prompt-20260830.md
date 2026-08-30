# HTML-GEN-CL006 实现审计 Prompt（2026-08-30）

你是 review profile 的实现审计会话，在 /Users/jadenli/CodeSpace/html-gen.cli 项目目录内工作。
请以中文回复，审计意见全部使用中文。

## 背景

HTML-GEN-CL006：scripts/tool-table-videos-syncer.py 增量模型三态（新增/更新/跳过），
url 已存在且 yaml title 非空且不同 → 全字段覆盖更新；全包含提示补充「yaml 检查 N 条 / 涉及 M 个国家」统计。

## 审计对象（commit 链）

- 29bdbd2 docs@design: 设计 v1.2（含 66d955b 评审折叠项订正）
- 7a2d356 docs@review: 设计评审（PASS 90/A，HG-SEC-081..085）
- df2e28c feat@html-gen: dev 实施（syncer 三态 + 7 新用例）
- 7dbaf4c fix@html-gen: ops 核查修复（更新步变量遮蔽 target → rebuild 配置丢失 + test_21 回归）

## 参考材料（只读）

- documents/solutions/table-videos-syncer-design-v1.2-20260830.md（设计定稿）
- documents/review/table-videos-syncer-v1.2-design-review-v1.0-20260830.md（设计评审 + 折叠项）
- scripts/tool-table-videos-syncer.py（当前源码）
- tests/test_sync_videos.py（当前 21 用例）
- documents/review/table-videos-syncer-v1.2-dev-impl-prompt-20260830.md（dev 实施 prompt）

## 审计任务（对照设计逐项核验实现）

1. build_increments 三态语义：
   - 新增：url 不在该行 videos url 集合
   - 更新：url 已存在 + yaml title 非空 + ≠ json 既有 title；updates 携带 old_title 与 raw_duration
   - 跳过：其余（title 相同 / title 空）
   - yaml 内部同 country+url 去重（HG-SEC-083）
2. run_apply 更新步：
   - title 覆盖 / duration raw 判空才覆盖（HG-SEC-081）/ platform yaml→detect→保留既有（U1）
   - 无 target 参数遮蔽（ops 核查修复点，重点复核 L296 附近）
   - 防御分支（url 已存在才进 updates）
3. G 判定：new_items 与 updates 双空才中断；统计 N/M 口径（去重 + 畸形条目排除，HG-SEC-085）
4. dry-run / --apply 输出形态（新增/更新/跳过三段 + 统计提示）
5. W 回写幂等：更新后 json → yaml 镜像带新值 → 下次运行跳过
6. 测试覆盖：t14-t21 是否覆盖设计 §5 + HG-SEC-081..085 全部折叠项；test_05 fixture 调整是否正确
7. 提交完整性：git log 核对 df2e28c / 7dbaf4c 只含需求文件（syncer + tests），未混入
   data/_countries-data.json 的他人 note 编辑
8. 实测验证（自行执行）：
   - python3 -m pytest tests/test_sync_videos.py -q -n 0（21 passed）
   - python3 -m pytest tests/ -q -n 4（全量 255 passed）
   - python3 scripts/tool-table-videos-syncer.py --dry-run（28 新增 + 1 更新 + 30 跳过，零写盘；
     **不要 --apply**）

## 输出

产出审计文档 documents/review/table-videos-syncer-v1.2-impl-audit-v1.0-20260830.md，包含：

1. 审计结论：PASS / CONDITIONAL / FAIL（附一句理由）
2. 逐项核验表（设计项 → 实现位置 → 符合性 → 意见）
3. 问题清单：严重 / 一般 / 建议 三档
4. 测试与实测证据（命令 + 结果）
5. 结论理由（3-5 条）

## 追踪文件（append，参照该目录既有审计惯例）

- .review-level.yaml：review_history 追加一条（date/reviewer/review_type: impl-audit/review_level/scope/verdict/score/findings_total/findings_open/tracking/report）
- review-log.md：追加审计条目

## 收尾

1. git add 审计文档 + .review-level.yaml + review-log.md
2. git commit -m "docs@review: syncer v1.2 实现审计 (HTML-GEN-CL006)"
3. 打印审计结论与问题清单摘要（简短，供 ops 会话转达）

注意：不要修改任何源码/测试/设计文档；不要 git push。
