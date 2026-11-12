#!/usr/bin/env bash
# 测试卫生探针（HTML-GEN-CL034）：验证 Selenium 用例是否仍依赖固定 /tmp 共享路径。
#
# 做一件坏事：起一个第三者进程不停覆盖 /tmp/test-show-md.html（模拟并发会话/并行 worker 撞名），
# 同时跑 TestDocShowMd。夹具若走 tempfile.mkdtemp()（当前实现）⇒ 用例不受影响、应全绿；
# 若夹具写的是固定共享路径 ⇒ 页面被顶掉、用例应红（这就是本探针的判别力）。
#
# 防假绿（HG-SEC-219）：
# - 前置 `CHROMEDRIVER_REQUIRED=1`：缺驱动时是 RuntimeError 报错，不会退化成 skip；
# - 再断言日志含 `2 passed`：skip 掉时会得 `2 skipped` 却 rc=0，这一条把它抓出来。
#
# 本脚本故意写 /tmp/test-show-md.html（制造坏环境即是其职责，末尾自删），属 testing.md 新规的例外。
# 用法: bash scripts/probe-tmp-pollution.sh [轮数(默认3)]
set -u
cd "$(dirname "$0")/.." || exit 1
rounds=${1:-3}
fails=0
for i in $(seq 1 "$rounds"); do
  ( for _ in $(seq 1 400); do
      printf '<html><body><p>polluted</p></body></html>' > /tmp/test-show-md.html
      sleep 0.01
    done ) &
  poll=$!
  CHROMEDRIVER_REQUIRED=1 python3 -m pytest tests/test_templates.py -k TestDocShowMd -q -n 0 \
    > "/tmp/probe-tmp-pollution-$i.log" 2>&1
  rc=$?
  kill "$poll" 2>/dev/null; wait "$poll" 2>/dev/null
  # 假绿防线：没真跑满 2 例（skip/收错）一律记失败
  if ! grep -q "2 passed" "/tmp/probe-tmp-pollution-$i.log"; then
    echo "round $i: 未真跑满 2 例（skip 或报错）⇒ 记失败"
    rc=1
  fi
  echo "round $i: rc=$rc  ($(tail -1 "/tmp/probe-tmp-pollution-$i.log"))"
  [ "$rc" -ne 0 ] && fails=$((fails + 1))
done
rm -f /tmp/test-show-md.html /tmp/probe-tmp-pollution-*.log
echo "TOTAL_FAILS=${fails}（0 = 夹具已与共享路径解耦，且两例真跑）"
[ "$fails" -eq 0 ]
