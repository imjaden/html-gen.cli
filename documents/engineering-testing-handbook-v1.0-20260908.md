---
title: html-gen 工程测试手册
topic: html-gen
type: summary
version: 1.0
date: 2026-09-08
author: hermes-v0.20.6(2026.8.27)
profile: dev
provider: deepseek
model: deepseek-v4-flash
tags: [html-gen, testing, pytest, xdist, selenium, webdriverwait, speedup, handbook, summary]
---

# html-gen 工程测试 v1.0

> 本文是 html-gen 测试执行效率优化的主题手册（2026-08-19 测试提速：pytest-xdist 并行 + sleep 调低 + WebDriverWait 显式等待三方案组合），覆盖耗时构成、决策、命令形态、提速脚本、flaky 回退方法与验证顺序。内容以 2026-09-08 当前实现为准（pytest.ini / requirements-dev.txt / scripts/speedup_sleeps.py / skills/test-speed-optimization 实测互证）。

## 1. 功能定位

全量测试（当时 136 tests）实测 **165.58s**（约 2 分 45 秒）——开发迭代全量回归等待过长。优化目标：组合三类提速方案把全量压到 **~25-30s（-82%）**，同时不引入 flaky。

耗时构成（design 实测 + review 复核）：

- 固定 `time.sleep` ≈53s（**170 处**：0.3×46 / 0.15×34 / 0.1×23 / 0.6×12 / 0.8×12 等；review grep -c=170、awk 求和 52.91s 吻合）。
- setUp 页面加载 sleep ≈75s（125 个 Selenium × sleep(0.6)）。
- 浏览器/驱动开销 + 真实执行 ≈35-40s。

## 2. 演进与审计结论

| 环节 | 结论 |
|:--|:--|
| 设计 v1.0 (2026-08-19) | review PASS 100/A（design commit 9565b8b；review 35fa11a） |
| 实施 | 顺序：① 全项目 D'（15 个 Selenium 文件 setUp sleep→WebDriverWait）→ ② 全项目 D（交互 sleep 按映射调低）→ ③ 单文件→全量单线程验证（无 flaky）→ ④ -n 4 并行全量 → ⑤ 记录基准 |
| 实施审计 (2026-08-21) | L2 Implementation Audit PASS 100/A（T1-T7；对象 008ef6d flaky fix + 8b85a65 skill pitfall） |

### 最小验证实测（design，test_table_features.py 11 tests 单文件基准）

| 方案 | 耗时 | 对比基线 | 稳定性 |
|:--|:--|:--|:--|
| 原始基线 | 17.78s | — | 稳定 |
| D: 调低 sleep | 13.10-13.20s | -26% | 多次通过 |
| D': WebDriverWait 替换 setUp 0.6s | 10.92-11.02s | -38% | 多次通过 |
| D+D' 组合 | 9.50-9.59s | -47% | 多次通过 |
| C: pytest-xdist -n 4 全量 | 136 tests, 48.19s | -70% | 全过 |

### 实施审计实测（独立复跑）

- 并行 `-n 4` = **146 passed, 25.17s**（达成目标 25-30s）；单线程 `-n 0` = **146 passed, 80.30s 无 flaky**（相对原 165s 仍 -52%）。
- 🟢 观察：ops 证据「单线程 24.50s」与实际不符（推测并行运行误标注），不影响结论。

## 3. 命令与工程形态

```ini
# pytest.ini（当前全文）
[pytest]
addopts = -n 4
testpaths = tests
```

```text
# requirements-dev.txt（当前全文）
pytest-xdist>=3.8.0
PyYAML>=6.0        # dev 依赖（syncer），不违反运行时零依赖
```

```shell
python3 -m pytest tests/ -q -n 4     # 日常全量（自动并行）
python3 -m pytest tests/ -q -n 0     # 关并行单线程调试
python3 -m pytest tests/ -q -p no:xdist
python3 -m pytest tests/ -q --tb=short   # 失败定位
```

- pytest.ini 默认 `addopts = -n 4`：日常全量自动并行；单文件运行同样生效（xdist 对单文件无害）；定向调试用 `-n 0` 或 `-p no:xdist`。
- WebDriverWait 模式：`WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '<主元素>')))`；主元素按页面：table `.data-table` / knowledge `.kw-tabs` / doc `.doc-body`。**注入必须 `By`+`WebDriverWait`+`EC` 三 import 同补**（原文件常缺 By → NameError）。
- D sleep 保守映射：0.3→0.15、0.4→0.2、0.5→0.25、0.6→0.3、0.8→0.4、0.9→0.45；**0.08/0.1/0.15/0.2/0.25 不动**（预计固定 sleep 52.9s→32.2s）。审计实测落地分布：0.15×80 / 0.2×23 / 0.4×12 / 0.3×6 / 0.45×2。

## 4. 提速脚本 speedup_sleeps.py

- 位置：skills/test-speed-optimization/scripts/（随 skill 沉淀；仓库 scripts/ 无副本）。
- 形态：`--dry-run` 预览 / `--apply` 应用（先 .bak）/ restore 回滚；**幂等**（`# [speedup]` 标记，已调低不重复改）；白名单小值不动。
- 从 .bak 回退的文件会在下次 --dry-run 再次列出属预期（勿二次 apply）。

## 5. 关键决策（原文编号）

| 编号 | 决策 |
|:--|:--|
| 1 | C = pytest-xdist `-n 4`（10 核 CPU，xdist 3.8.0；-n 4 实测最优，再高受 Chrome 进程/内存限制） |
| 2 | D = sleep 调低，保守映射逐文件验证（不可一刀切） |
| 3 | D' = WebDriverWait 显式等待替换固定 0.6s |
| 4 | 优化策略 + 提速脚本沉淀为 skill（skills/test-speed-optimization） |
| （确认） | pytest.ini 默认 `addopts = -n 4`；skill 命名 test-speed-optimization |

## 6. 已知坑 / flaky 回退

| # | 坑 | 处理 |
|:--|:--|:--|
| P1 | sleep 不可一刀切 | 保守映射 + 逐文件验证 + 连跑 2 次；任何文件失败即回退该文件该处 |
| P2 | split stale flaky | 回退实证：test_countries_table 3×0.5、test_drama 2×0.8（split 多标签/陈旧内容场景）保留大 sleep；改事件驱动等待而非盲目加时长 |
| P3 | 异步 UI 断言等固定 sleep 不可靠 | toast 用 `WebDriverWait.until(EC.text_to_be_present_in_element((By.ID,'docToast'),'已复制: …'))`（T4；连跑 3 次稳定 0.84-1.02s；SKILL.md 坑位 #6） |
| P4 | 副本测试文件路径 | 复制测试文件后必须改 `Path(__file__)` 相对定位，否则指向他人目录 |
| P5 | xdist 并行资源 | 10 核 -n 4 最优；内存不足降 `-n 2` |
| P6 | 脚本误改 | dry-run + .bak 备份 + 幂等标记三保险 |
| P7 | 耗时/计数口径 | ops 提交的标签可能与独立实测不符——引用数据以独立实测为准 |

## 7. 验证顺序（提速后复跑模板）

1. 单文件跑（改动的测试文件）；
2. 全量单线程 `-n 0` 连跑 2 次（无 flaky）；
3. `-n 4` 并行全量；
4. 抽样 flaky 文件（test_table_features / test_drama_knowledge）连跑 3 次。

## 8. 参考文档

- 保留原位：pytest.ini、requirements-dev.txt、tests/、skills/test-speed-optimization（SKILL.md + scripts/speedup_sleeps.py）、features.md、review-log.md / .review-level.yaml（历史不追改）。
- 本族过程文档（4 份）已归档（2026-09-08 执行） → `documents/archive/{root,review}-20260908/`：

| 素材 | 归档路径 | 归档桶 |
|:--|:--|:--|
| 测试提速设计 v1.0 | documents/archive/root-20260908/test-speed-optimization-design-v1.0-20260819.md | root |
| 设计评审 / process prompt | documents/archive/review-20260908/test-speed-optimization-{review-v1.0,review-prompt}-20260819.md | review |
| 实现审计 | documents/archive/review-20260908/test-speed-optimization-implementation-review-v1.0-20260821.md | review |
