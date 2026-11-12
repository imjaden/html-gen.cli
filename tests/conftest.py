"""pytest 全局测试基建（HTML-GEN-CL024：chromedriver 路径 env 化）。

为什么要有这个文件：驱动二进制路径原先硬编码在 31 个测试文件里（third-party 仓
`~/CodeSpace/script-miner/` 下的绝对路径）—— 换机器 / CI 必然全红，且把别仓目录结构渗进本仓。

约定：
- `CHROMEDRIVER` env 覆盖二进制路径；缺省值 = `~` 下 script-miner 仓的 cache（向后兼容，本机行为不变）。
  缺省值用 `os.path.expanduser('~')` 分段拼，**不写死用户名**（他人机器上是可跑的，不是 skip）。
- `CHROMEDRIVER_REQUIRED=1`（CI 用）：缺二进制 ⇒ `RuntimeError` 而不是 skip —— 门禁不许静默放水。
- `chromedriver_service()`：缺二进制时抛 `unittest.SkipTest`（带实际路径与 env 提示）。
"""
import os
import unittest
from pathlib import Path

from selenium.webdriver.chrome.service import Service

# 缺省路径 = 用户 home 下的 script-miner cache（分段拼接：不留可复制的「硬编码绝对路径」范式）
DEFAULT_CHROMEDRIVER = os.path.join(
    os.path.expanduser('~'), 'CodeSpace', 'script-miner', 'cache', 'chromedriver', 'chromedriver')
CHROMEDRIVER = os.environ.get('CHROMEDRIVER') or DEFAULT_CHROMEDRIVER
REQUIRED = os.environ.get('CHROMEDRIVER_REQUIRED', '') not in ('', '0', 'false', 'False')


def chromedriver_path():
    return Path(CHROMEDRIVER)


def chromedriver_available():
    return chromedriver_path().is_file()


def chromedriver_service():
    """返回 Service；二进制不存在 ⇒ SkipTest（`CHROMEDRIVER_REQUIRED=1` 时改抛 RuntimeError）。"""
    if not chromedriver_available():
        msg = (f'chromedriver 不存在: {CHROMEDRIVER}（用 CHROMEDRIVER=<path> 覆盖；'
               f'缺省值 {DEFAULT_CHROMEDRIVER}）')
        if REQUIRED:
            raise RuntimeError(f'{msg} —— CHROMEDRIVER_REQUIRED=1 要求缺驱动即失败（CI 口径）')
        raise unittest.SkipTest(msg)
    return Service(CHROMEDRIVER)
