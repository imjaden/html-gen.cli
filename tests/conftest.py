"""pytest 全局测试基建（HTML-GEN-CL024：chromedriver 路径 env 化）。

为什么要有这个文件：`/Users/<user>/CodeSpace/script-miner/cache/chromedriver/chromedriver`
是本机（第三个仓）的绝对路径，之前硬编码在 64 个测试文件里 —— 换机器 / CI 必然全红，
且把别仓的目录结构渗进了本仓测试。

约定：
- `CHROMEDRIVER` env 覆盖二进制路径；缺省值保持历史现值（向后兼容，本机行为不变）。
- `chromedriver_service()` 在二进制缺失时抛 `unittest.SkipTest`（带原因与环境变量提示）：
  缺驱动是「本机没装」而不是「代码坏了」，应当 skip 而不是 64 个文件各自抛 WebDriverException。
"""
import os
import unittest
from pathlib import Path

from selenium.webdriver.chrome.service import Service

# 本机历史默认值（script-miner 的 cache 目录）；换机器请设 CHROMEDRIVER，别改这里
DEFAULT_CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
CHROMEDRIVER = os.environ.get('CHROMEDRIVER') or DEFAULT_CHROMEDRIVER


def chromedriver_path():
    return Path(CHROMEDRIVER)


def chromedriver_available():
    return chromedriver_path().is_file()


def chromedriver_service():
    """返回 Service；二进制不存在 ⇒ SkipTest（附 env 覆盖方式）。"""
    if not chromedriver_available():
        raise unittest.SkipTest(
            f'chromedriver 不存在: {CHROMEDRIVER}（用 CHROMEDRIVER=<path> 覆盖；'
            f'缺省值 {DEFAULT_CHROMEDRIVER}）')
    return Service(CHROMEDRIVER)
