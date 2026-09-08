# 测试执行效率优化 — 设计文档

## 版本

v1.0 (2026-08-19)

## 背景与问题来源

全量测试 `python3 -m pytest tests/ -q` 实测 136 tests 耗时 165.58s（约 2 分 45 秒），开发迭代时全量回归等待过长。

**耗时构成分析**（实测 + 统计）：
1. 固定 time.sleep 硬性等待 ≈ 53s（170 处，0.3s×46 / 0.15s×34 / 0.1s×23 / 0.6s×12 / 0.8s×12 等）
2. setUp 页面加载 sleep ≈ 75s（125 个 Selenium 测试 × sleep(0.6) 等页面渲染）
3. 浏览器/驱动开销 + 真实执行 ≈ 35-40s

**最小验证结果**（test_table_features.py 11 tests 单文件基准，已实测）：

| 方案 | 耗时 | 对比基线 | 稳定性 |
|:--|:--|:--|:--|
| 原始基线 | 17.78s | — | 稳定 |
| D: 调低 sleep（0.3→0.15, 0.6→0.3 等） | 13.10-13.20s | -26% | ✅ 多次通过 |
| D': WebDriverWait 替换 setUp 0.6s | 10.92-11.02s | -38% | ✅ 多次通过 |
| D+D' 组合 | 9.50-9.59s | -47% | ✅ 多次通过 |
| C: pytest-xdist -n 4 全量并行 | 136 tests, 48.19s | -70% | ✅ 全过 |

**目标**: 三者组合（C + D + D'）全量从 165s 降至 ~25-30s（-82%）。

## 决策

| 项 | 决策 |
|:--|:--|
| 1 并行 | C=采用 pytest-xdist -n 4（10 核 CPU，已装 xdist 3.8.0） |
| 2 sleep 调低 | D=采用（保守映射，逐文件验证） |
| 3 setUp 等待 | D'=WebDriverWait 显式等待替换固定 0.6s |
| 4 skills 沉淀 | 将优化策略 + 提速脚本沉淀为 skill（写 skills/） |

## 实现方案

### C1. pytest-xdist 并行（基础设施）

- 依赖: pytest-xdist（dev 依赖，已装，不违反"运行时零依赖"——仅测试用）
- 命令: `python3 -m pytest tests/ -q -n 4`
- 10 核 CPU 实测 -n 4 最优（再高受 Chrome 进程/内存限制）
- 已验证: 136 tests 全过，test_templates 生成 demos 与并行 worker 无冲突（17 passed in 2.09s）
- 可选: pytest.ini / pyproject.toml 加 `addopts = -n 4`（默认并行）或留命令行显式传

**已确认**: pytest.ini 默认加 `addopts = -n 4`。日常 `python3 -m pytest tests/ -q` 即自动并行；单文件运行 `python3 -m pytest tests/test_xxx.py` 同样生效（xdist 对单文件无害）。定向调试可 `-n 0` 或 `-p no:xdist` 关闭并行。

### D. sleep 值调低（全项目）

**保守映射**（最小验证已证实安全）：
```
0.3s → 0.15s   0.4s → 0.2s    0.5s → 0.25s
0.6s → 0.3s    0.8s → 0.4s    0.9s → 0.45s
0.08/0.1/0.15/0.2/0.25 保持不变
```
- 预计固定 sleep 52.9s → 32.2s（省 ~20.7s）
- **注意**: 不可一刀切，需逐文件验证（不同页面渲染速度不同）。实施顺序: 先改 setUp sleep → 跑全量 → 再改交互 sleep → 再跑。任何文件失败即回退该文件该处

### D'. WebDriverWait 替换 setUp 固定等待

- 每个 Selenium 测试类 setUp 中 `sleep(0.6)` 替换为:
  ```python
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
  WebDriverWait(self.driver, 5).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, '<页面主元素>'))
  )
  ```
- 主元素选择器按页面而定（table: .data-table / knowledge: .kw-tabs / doc: .doc-body）
- 事件驱动: 页面渲染完成立即继续，不等固定时间
- 预计 setUp 75s → ~15-20s（省 ~55s）

### 实施顺序（dev 执行）

1. 全项目 D': setUp sleep(0.6) → WebDriverWait（15 个 Selenium 文件）
2. 全项目 D: 交互 sleep 按映射调低
3. 跑单文件验证 → 全量单线程验证（确认无 flaky）
4. 加 -n 4 并行跑全量（确认无资源竞争）
5. 记录基准: 目标 136 tests ~25-30s

## 测试（本方案自身的验收）

- 全量 `pytest tests/ -q` 单线程: 136 passed，无 flaky（连跑 2 次）
- 全量 `pytest tests/ -q -n 4`: 136 passed，~25-30s
- 抽样 flaky 检查: test_table_features / test_drama_knowledge 各连跑 3 次稳定

## Skills 沉淀

将优化策略与脚本沉淀为 skill，写入项目 skills/ 目录：

### skill 1: `skills/test-speed-optimization/SKILL.md`

内容:
- 触发条件: 测试执行慢 / 需要提速
- 耗时分析方法论（sleep 分布统计、--durations 定位）
- 三类方案: xdist 并行 / sleep 调低映射 / WebDriverWait 替换
- 验证流程与稳定性检查
- 已知坑: 副本测试文件必须修正 PROJECT 绝对路径（Path(__file__) 依赖）

### skill 2: 提速脚本 `scripts/speedup_sleeps.py`

功能: 自动扫描 tests/*.py，按映射调低 time.sleep 值（dry-run + 应用模式）
```
python3 scripts/speedup_sleeps.py --dry-run   # 预览改动
python3 scripts/speedup_sleeps.py --apply     # 应用
```
- 幂等: 已调低的 sleep 不重复修改（只匹配原始大值）
- 白名单: 0.08/0.1/0.15/0.2/0.25 不动
- 生成 .bak 备份，--apply 前可回滚

### skill 3: 全量提速执行命令（写入 html-gen skill 或独立 skill）

```
python3 -m pytest tests/ -q -n 4    # 日常全量（~48s）
python3 -m pytest tests/ -q -n 4 --tb=short   # 失败定位
```

## 影响范围

| 文件 | 改动 |
|:--|:--|
| tests/ 15 个 Selenium 文件 | setUp sleep→WebDriverWait + 交互 sleep 调低 |
| pytest.ini / pyproject.toml（可选） | addopts -n 4 |
| skills/test-speed-optimization/ | 新 skill（SKILL.md + scripts/speedup_sleeps.py） |
| AGENTS.md | 测试治理节更新（全量命令 + 优化约定） |

## 风险

- 中: sleep 调低可能引入 flaky（不同机器/负载下渲染速度不同）→ 用保守映射 + 逐文件验证 + 连跑 2 次
- 低: xdist 并行 Chrome 实例多 → 10 核够用；若内存不足降 -n 2
- 低: 脚本误改 → dry-run + .bak 备份
- 不改变测试语义: 只改等待机制，不改断言/流程

## 待确认（已确认）

| 项 | 确认 |
|:--|:--|
| pytest.ini addopts | A=默认加 `-n 4`（pytest.ini 配置，日常全量自动并行；单文件/定向跑不受影响） |
| skill 命名 | `test-speed-optimization` |
