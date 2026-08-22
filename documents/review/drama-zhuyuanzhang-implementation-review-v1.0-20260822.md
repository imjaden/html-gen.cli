# 朱元璋（2006）知识库实现审计 — review报告 v1.0

**审查日期**: 2026-08-22
**审查级别**: L2 (Implementation Audit)
**审查对象**: 未 push 9 commits（git log @{u}..HEAD，目标 github/main）
**设计依据**: 无设计文档（数据内容型功能，1B/2A/3A/4B 探讨确认后直接实施）
**结论**: PASS (95/A)

---

## 一、数据验证

| # | 检查项 | 预期 | 实测 | 结果 |
|:--:|:---|:---|:---|:--:|
| 1 | 定向测试 `tests/test_drama_knowledge.py` | 16 passed | 16 passed (17.55s) | ✅ |
| 2 | 全量回归 `tests/ -n 4` | 146 passed | 146 passed (26.48s) | ✅ |
| 3 | 浏览器 tabs 顺序 | 中国历史 / 朱元璋（2006）/ 大明王朝1566（2007）/ 雍正王朝（1999） | 完全一致 | ✅ |
| 4 | 朱元璋 sections | 概述 / 时间轴 / 36计策（3 sections, 无 kw-item 行） | 一致 | ✅ |
| 5 | 朱元璋 overview iframe | `drama/zhuyuanzhang-overview.html?width=wide` | 一致 | ✅ |
| 6 | timeline 默认筛选 | 洪武 3 行；清筛选 7 行（至正3+洪武3+建文1） | 3 行 → 7 行 | ✅ |
| 7 | strategy 行数 | 17 行 | 17 行 | ✅ |
| 8 | strategy 生成物 COLUMNS/DATA vs JSON | 逐字段一致 | 一致（含列序/宽度/数据 17 行） | ✅ |
| 9 | timeline 生成物 COLUMNS/DATA vs JSON | 逐字段一致 | 一致（7 行） | ✅ |
| 10 | yongzheng/history strategy 列序同步（05feb12） | 生成物与 JSON 一致 | 26/36 行，列序+宽度一致 | ✅ |
| 11 | 死链 | 无 | 12 iframe refs 全存在；overview 无本地链接 | ✅ |
| 12 | 全角括号 URL 参数 | encodeURIComponent 兼容 | URLSearchParams 自动编码，实测往返恢复成功 | ✅ |
| 13 | JS 错误 | 无 | 全 tab × section 遍历后 0 错误 | ✅ |

## 二、实现评估

| 维度 | 评估 | 结果 |
|:---|:---|:--:|
| 功能正确性 | 朱元璋 tab 三 section 内容加载正确，概述宽屏嵌入、时间轴默认筛选洪武、36计策 17 行全量渲染 | ✅ |
| 数据一致性 | 新表生成物与 data JSON 逐字段一致；user 手工补 17 条数据已回填 JSON（diff 零丢失） | ✅ |
| commit 规范 | 9/9 条 type@scope 小写（feat/fix/chore/docs），subject 英文为主；`docs@handoff` 为自动生成提交 | ✅ |
| 命名规范 | `zhuyuanzhang-*`（data JSON + demos html/md + registry）与 `daming-*`/`yongzheng-*` 模式一致 | ✅ |
| 回归 | 全量 146 tests 无回归 | ✅ |
| 边界 | 36计策框架→17 行后无死链；tab label 全角括号（（2006））在 group URL 参数中编码兼容 | ✅ |

### 评分表

| 维度 | 满分 | 得分 |
|:---|:---:|:---:|
| 功能正确性 | 25 | 25 |
| 数据一致性 | 30 | 25 |
| commit/命名规范 | 15 | 15 |
| 边界处理 | 15 | 15 |
| 回归安全 | 15 | 15 |
| **合计** | **100** | **95** |

## 三、安全事项

| 编号 | 严重度 | 问题 | 状态 |
|:---|:---:|:---|:---:|
| HG-SEC-005 | 🟡 | daming-strategy-table.html 列宽与 `data/_drama-table-daming-strategy.json` 不同步：bddfc4f 压缩生成物列宽（strategy 60px / event 160px 等）但未回填 JSON（仍 90px / 280px），05feb12 修复列序时漏掉 daming。重新生成该表会回退压缩宽度。 | Open |
| HG-SEC-006 | 🟢 | review-log.md 审计追踪缺口：历史 13 次 review 均只更新 .review-level.yaml + 报告，未追加 review-log.md（git 历史仅 1 次创建提交）。本次已按规范追加。 | Open |

**说明**: 无 🔴 高危项；无凭证泄露/注入/XSS 面（纯静态数据内容型变更，未动模板 JS）。

## 四、评分

```
Base: 100   扣分: 🟡 -5 (HG-SEC-005)   🟢 -0 (HG-SEC-006)
最终: 95    Rating: A
🔴 0   🟡 1   🟢 1
```

## 五、结论

**PASS** — 朱元璋（2006）知识库功能完整落地：菜单标签统一带年份（1B）、概述+时间轴+36计策框架（2A）、时间轴范围含剧前史/剧后余波（3A）、豆瓣链接覆盖三剧（4B），全部符合探讨确认清单。146 tests 全绿，浏览器实测无死链、无 JS 错误、URL 全角括号参数编码兼容。授权 push 9 commits 至 github/main。

**遗留建议**:
- HG-SEC-005（🟡）: 回填 daming-strategy JSON 列宽至压缩值，或按需重新生成对齐——非阻塞，可随下次数据更新一并处理。
- HG-SEC-006（🟢）: 可回填历史 review-log 条目，保持追踪链完整。

---

*报告人: Security Reviewer (Hermes review profile)*
