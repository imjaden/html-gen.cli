---
title: Handoff - ops/20260824_164803_6
date: 2026-09-28
source_session: 20260824_164803_688ced
generated_by: hermes-0.21.3
topic: html-gen
type: handoff
version: 1.0
author: ops
summary: 云智慧新闻组管线上线：知识库新增「📰新闻动态」组，已 14 篇（含 09-09 新文，上游元数据修复已生效）；周报 cron、skill、AGENTS.md 文
next: 更新索引路径（改 INDEX_FILE 默认值或 wrapper 注入 WEB2MD_INDEX），手动补跑一周增量，确
risk: web2md 索引迁至 script-miner/cache/web2md/web2md_index.json，sync
---

# Handoff: html-gen-demo

📌 语义摘要

**已完成**
云智慧新闻组管线上线：知识库新增「📰新闻动态」组，已 14 篇（含 09-09 新文，上游元数据修复已生效）；周报 cron、skill、AGENTS.md 文档均落地。
**未完成**
web2md 索引迁至 script-miner/cache/web2md/web2md_index.json，sync 脚本仍指旧路径 → 09-26 cron rc=1，10-03 将再失败，期间新文章漏采。
**下一步建议**
更新索引路径（改 INDEX_FILE 默认值或 wrapper 注入 WEB2MD_INDEX），手动补跑一周增量，确认飞书投递成功。

## 目标
hi

## 输入
- profile: ops
- session: 20260824_164803_688ced
- 消息数: 240

## 输出 / 关键路径
- /Users/jadenli/CodeSpace/html-gen.cli/data/_cloudwise-news.json
- /Users/jadenli/CodeSpace/html-gen.cli/demos/cloudwise-business-analysis.html
- /Users/jadenli/CodeSpace/html-gen.cli/scripts/cloudwise-fetch.py
- /Users/jadenli/CodeSpace/html-gen.cli/scripts/cloudwise-news-sync.py

## 边界
- started: 1787561283.231105, messages: 240

## 确认点
- [ ] 基于以上决策，复述整体需求及解决方案，罗列待决策清单（若有，附推荐项）、下一步行动计划（不要直接执行）

## 权限
- [无]

## 来源
- 63eb4e9 sync@html-gen: cloudwise news group - 13 a
- 2dc29eb docs@html-gen: cloudwise news pipeline in

## 下一步清单
1. 继续: hi
2. 基于以上决策，复述整体需求及解决方案，罗列待决策清单（若有，附推荐项）、下一步行动计划（不要直接执行）

## 建议技能
article-smart-reader, references, research, scripts
