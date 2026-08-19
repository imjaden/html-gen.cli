---
name: test-speed-optimization
description: html-gen Selenium 测试套件提速。测试执行慢时用 xdist 并行 + sleep 调低 + WebDriverWait 三方案优化。
version: 1.0.0
author: dev
license: MIT
metadata:
  related_skills: [html-gen, html-gen-table, html-gen-doc]
---

# 测试执行效率优化

## 何时使用

- 全量 Selenium 测试执行慢（>100s），需要提速
- 需要定位耗时瓶颈（sleep 分布 / --durations）
- 需要并行化测试（xdist）或调低固定 sleep

## 耗时分析方法论

1. **sleep 分布统计**：扫描 tests/*.py 统计 `time.sleep(X)` 分布，定位大值 sleep
   ```python
   import re
   from pathlib import Path
   for f in sorted(Path('tests').glob('test_*.py')):
       sleeps = re.findall(r'time\.sleep\(([\d.]+)\)', f.read_text())
       # 按值聚合计次
   ```
2. **--durations 定位**：`pytest tests/ -q --durations=10` 看最慢的 10 个用例
3. **区分 sleep 类型**：
   - setUp 页面加载 wait（`get()` 后的大 sleep）→ 用 WebDriverWait（D'）
   - 交互 wait（点击后的小 sleep）→ 调低映射（D）
   - localStorage 上下文 wait（clear 前的 sleep）→ 保持或微调

## 三方案

### 方案 C — pytest-xdist 并行（最大收益，零逻辑风险）

```ini
# pytest.ini
[pytest]
addopts = -n 4
```

```bash
python3 -m pytest tests/ -q -n 4     # 并行, ~4x 提速
python3 -m pytest tests/ -q -n 0     # 定向调试, 关闭并行
```

依赖：`pytest-xdist>=3.8.0`（requirements-dev.txt 或 AGENTS.md 显式声明）。

### 方案 D' — setUp sleep → WebDriverWait（最稳健）

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WebDriverWait(self.driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '<主元素>'))
)
```

主元素按页面类型：table → `.data-table`；knowledge → `.kw-tab`；doc → `.doc-body`；slide → `.slide-sidebar`。超时兜底 5s。

### 方案 D — 交互 sleep 调低映射（机械）

映射表（大值减半，小值不动）：

| 原值 | 新值 |
|:---|:---|
| 0.3 | 0.15 |
| 0.4 | 0.2 |
| 0.5 | 0.25 |
| 0.6 | 0.3 |
| 0.8 | 0.4 |
| 0.9 | 0.45 |

`0.08 / 0.1 / 0.15 / 0.2 / 0.25` 保持不变。

辅助脚本：`scripts/speedup_sleeps.py`（--dry-run / --apply / --restore）。

## 验证流程（防 flaky）

1. D' + D 改完 → 单线程连跑 2 次：`pytest tests/ -q -n 0`
2. 加并行：`pytest tests/ -q -n 4`
3. 抽样 flaky（各 3 次）：`test_table_features.py` / `test_drama_knowledge.py`
4. 任何文件失败 → 从 .bak 回退该文件（`cp test_x.py.bak test_x.py`）

## 坑

1. **副本测试文件 PROJECT 绝对路径**：不同环境 chromedriver/项目路径不同，副本文件须修正 `PROJECT`、`CHROMEDRIVER` 绝对路径。
2. **stale element**：split 面板/详情加载类交互需较慢 wait，sleep 减半可能触发 `StaleElementReferenceException`，该文件回退。
3. **WebDriverWait 注入需补 import**：若原文件未 `from selenium.webdriver.common.by import By`，注入 WebDriverWait 时必须一并补 By/WebDriverWait/EC 三个 import，否则 `NameError`。
4. **并行共享路径**：所有测试写 /tmp 须文件名唯一（不跨文件冲突），不得写 demos/ 或项目目录；xdist 下各 worker 独立进程。
5. **幂等**：speedup_sleeps.py 用 `# [speedup]` 标记已改行，二次 --apply 不重复改。注意：被回退的文件（cp .bak 还原）无标记，--dry-run 会再次列出该文件——属预期，勿二次 --apply（否则重新引入 flaky）。

## 验证清单

- [ ] 单线程 `pytest tests/ -q -n 0`：全绿，连跑 2 次无 flaky
- [ ] 并行 `pytest tests/ -q -n 4`：全绿，~25-30s
- [ ] speedup_sleeps.py --dry-run / --apply 幂等验证
- [ ] 无测试写共享路径（并行安全）
