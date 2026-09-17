#!/usr/bin/env bash
# 一键启动 locust 压测 — M3-D10/D11-locust / #19a + #19b
# 模式：
#   ./run_perf.sh                                 # Web UI (http://localhost:8089) - #19a login scenario
#   ./run_perf.sh headless 100 10 60s             # headless: 100 用户 / 10 ramp / 60s - #19a
#   ./run_perf.sh 3scn                            # Web UI 跑 3 场景 - #19b
#   ./run_perf.sh 3scn-headless 100 10 60s        # headless 3 场景 - #19b 验证
#   ./run_perf.sh step                            # 阶梯加压 50/100/200/500 每档 120s - #19b 核心
#   ./run_perf.sh plot                            # 出退化曲线 PNG - #19b step 后
#
# git-bash 子 shell 调用 python 常见 2 个坑：
#   1. `python` / `python3` 解析为 /usr/bin/python3（msys，无 locust 模块）
#   2. WindowsApps/python.exe stub 在 git-bash 直接 exec 失败（返回 127）
# 解决：通过 cmd heredoc 调用 `python` —— cmd 正确解析 Microsoft Store stub → 真实 Python.exe
# 也支持环境变量 PYTHON_BIN 强制指定具体可执行（用 Windows 反斜杠路径）。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

# git-bash 子 shell 的 PATH 没有 cmd.exe，必须用绝对路径
# /mnt/c/Windows/System32/cmd.exe 在 git-bash 子 shell 可执行（直接 exec，stub 友好）
CMD_EXE="/mnt/c/Windows/System32/cmd.exe"

# Python 真实路径（cmd heredoc 内可识别 stub）
# git-bash 直接 exec 会返回 127，必须经 cmd 调用
PYTHON_BIN="${PYTHON_BIN:-python}"  # cmd heredoc 里默认用 python（cmd 正确解析 stub → 真实 Python）

HOST="${BBS_GO_BASE_URL:-http://127.0.0.1:8081}"
mkdir -p reports/19b-evidence

MODE="${1:-webui}"

# 辅助函数：通过 cmd heredoc 跑 python 命令
# 用法：py_run -m locust -f locustfile.py ...
py_run() {
  "${CMD_EXE}" <<EOF
${PYTHON_BIN} $*
EOF
}

case "${MODE}" in
  webui)
    echo "Starting locust Web UI at http://localhost:8089 (#19a login scenario)"
    py_run -m locust -f locustfile.py --host="${HOST}"
    ;;
  headless)
    USERS="${2:-100}"
    RAMP="${3:-10}"
    DURATION="${4:-60s}"
    REPORT_BASE="reports/19a-evidence/locust-login"
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    echo "Running locust headless (#19a): ${USERS} users, ${RAMP} ramp, ${DURATION} duration"
    py_run -m locust -f locustfile.py \
      --host="${HOST}" \
      --users="${USERS}" \
      --spawn-rate="${RAMP}" \
      --run-time="${DURATION}" \
      --headless \
      --html "${REPORT_BASE}-${TIMESTAMP}.html" \
      --csv "${REPORT_BASE}-${TIMESTAMP}" 2>&1 | tee "${REPORT_BASE}-${TIMESTAMP}.log"
    ;;
  3scn)
    echo "Starting locust Web UI 3-scenario at http://localhost:8089 (#19b)"
    py_run -m locust -f locustfile_3scenarios.py --host="${HOST}"
    ;;
  3scn-headless)
    USERS="${2:-100}"
    RAMP="${3:-10}"
    DURATION="${4:-60s}"
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    REPORT_BASE="reports/19b-evidence/3scenarios"
    echo "Running locust 3-scenario headless: ${USERS} users, ${RAMP} ramp, ${DURATION} duration"
    py_run -m locust -f locustfile_3scenarios.py \
      --host="${HOST}" \
      --users="${USERS}" \
      --spawn-rate="${RAMP}" \
      --run-time="${DURATION}" \
      --headless \
      --html "${REPORT_BASE}-${USERS}u-${DURATION}-${TIMESTAMP}.html" \
      --csv "${REPORT_BASE}-${USERS}u-${DURATION}-${TIMESTAMP}" 2>&1 | tee "${REPORT_BASE}-${USERS}u-${DURATION}-${TIMESTAMP}.log"
    ;;
  step)
    # 阶梯加压 50/100/200/500 每档 120s —— #19b 核心
    echo "================ STEP LOAD: 50/100/200/500 × 120s ================"
    for USERS in 50 100 200 500; do
      echo ""
      echo "================ STEP: ${USERS} users × 120s ================"
      RAMP=$(( USERS / 10 ))
      DURATION="120s"
      REPORT_BASE="reports/19b-evidence/step-${USERS}u"
      py_run -m locust -f locustfile_3scenarios.py \
        --host="${HOST}" \
        --users="${USERS}" \
        --spawn-rate="${RAMP}" \
        --run-time="${DURATION}" \
        --headless \
        --html "${REPORT_BASE}.html" \
        --csv "${REPORT_BASE}" 2>&1 | tee "${REPORT_BASE}.log"
      echo "STEP ${USERS}u done. Sleeping 30s before next step (let server drain)..."
      sleep 30
    done
    echo ""
    echo "================ ALL STEPS COMPLETE ================"
    ;;
  plot)
    py_run scripts/plot_step_results.py
    ;;
  *)
    echo "Usage: $0 [webui|headless USERS RAMP DURATION|3scn|3scn-headless USERS RAMP DURATION|step|plot]"
    exit 1
    ;;
esac
