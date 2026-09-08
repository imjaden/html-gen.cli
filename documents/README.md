---
title: documents 目录说明
topic: html-gen
type: index
version: 1.0
date: 2026-09-08
author: hermes-v0.20.6(2026.8.27)
profile: dev
provider: deepseek
model: deepseek-v4-flash
tags: [html-gen, documents, handbook, archive, index]
---

# documents/ — 治理文档入口

> html-gen.cli 的治理文档入口：**主题手册**（现行知识，v1.0 2026-09-08 落盘）位于本目录根；**历史 process 文档**（设计/评审/审计/流程 prompt）按主题与批次归档于 `archive/`；功能与运行事实源见仓库根 `features.md` 与 `skills/`。

## 主题手册索引（现行知识）

| 手册 | 主题/功能域 | 覆盖 | 对应素材归档桶 | 编制日期 |
|:--|:--|:--|:--|:--|
| html-gen-cli-handbook-v1.0-20260908.md | CLI 命令面 / 数据格式 / prompt 供给与在线阅读站点（CL003/004/007/008） | 18 份 | solutions / root / review | 2026-09-08 |
| table-template-handbook-v1.0-20260908.md | A 型表格交互 + videos/favicon 工具链（cmd-f-search/table-actions/quickfilter/videos/syncer/favicon） | 23 份 | solutions / root / review | 2026-09-08 |
| doc-slide-template-handbook-v1.0-20260908.md | B/D 模板 UI 与 Markdown 渲染（bare 模式、宽度三级、meta show-md、h4-h6、排版、sidebar+table、slide 工具栏） | 17 份 | solutions / root / review | 2026-09-08 |
| pages-content-handbook-v1.0-20260908.md | 落地页双源与索引 + 内容案例（drama 知识库/表格、provinces/countries 双表数据工程） | 18 份 | solutions / root / review | 2026-09-08 |
| engineering-testing-handbook-v1.0-20260908.md | 测试执行效率（pytest-xdist、sleep 调低、WebDriverWait、防 flaky） | 4 份 | root / review | 2026-09-08 |

## 备注

- 文档命名：`{topic}-handbook-v1.0-{date}.md`；主题手册只写「现行知识」，不复制命令细节之外的历史叙事。
- `handoff/` 为跨 profile 交接快照，保留原位不归档；`.hermes-project.yaml` 活跃指向其中的 handoff-html-gen.cli-ops.md。
- 归档桶命名 `{solutions,root,review}-{date}/`（review 单数，与源目录一致），分别对应设计最终版 / 根级散件 / 评审报告与流程 prompt；桶内为 point-in-time 快照，正文不追改。
- `features.md`（仓库根）与 `skills/`、`prompts/` 是功能/运行事实源；`review-log.md` / `.review-level.yaml` 为审计历史记录，均保留原位不追改。

## 归档批次记录

| 执行日期 | 桶 | 数量 | 批次说明 |
|:--|:--|:--|:--|
| 2026-09-08 | archive/solutions-20260908/ | 11 | documents-consolidation phase-3：设计最终版（M1×4 M2×5 M3×1 M4×1） |
| 2026-09-08 | archive/root-20260908/ | 19 | 根级散件 + verify-prompt 系列（M1×1 M2×3 M3×6 M4×3 M5×1 HIST×5） |
| 2026-09-08 | archive/review-20260908/ | 57 | review/ 全部现存（M1×13 M2×15 M3×10 M4×14 M5×3 HIST×2） |

合计 87 份 process 文档（= M1-M5 素材 80 + HIST 7）；5 份手册（本索引上表）与 handoff/ 5 份不在归档之列。
