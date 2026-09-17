#!/usr/bin/env bash
# 一键启动 locust 压测 — M3-D10-locust-basic / #19a
# 模式：
#   ./run_perf.sh                          # 启动 Web UI (http://localhost:8089)
#   ./run_perf.sh headless 100 10 60s      # headless: 100 用户 / 10 ramp / 60s
#
# 说明：本脚本假定 `python` 已在 PATH 中（git-bash 子 shell 中 WindowsApps stub 解析失败，
#       在主 omp session shell 中通过 `python` 解析正常）。如需强制指定 python.exe：
#       PYTHON_BIN=/path/to/python.exe ./run_perf.sh headless 100 10 60s
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

PYTHON_BIN="${PYTHON_BIN:-python}"

mkdir -p reports/19a-evidence

if [ "$#" -eq 0 ]; then
  echo "Starting locust Web UI at http://localhost:8089"
  "${PYTHON_BIN}" -m locust -f locustfile.py --host="${BBS_GO_BASE_URL:-http://127.0.0.1:8081}"
elif [ "${1:-}" = "headless" ]; then
  USERS="${2:-100}"
  RAMP="${3:-10}"
  DURATION="${4:-60s}"
  REPORT_BASE="reports/19a-evidence/locust-login"
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  echo "Running locust headless: ${USERS} users, ${RAMP} ramp, ${DURATION} duration"
  "${PYTHON_BIN}" -m locust -f locustfile.py \
    --host="${BBS_GO_BASE_URL:-http://127.0.0.1:8081}" \
    --users="${USERS}" \
    --spawn-rate="${RAMP}" \
    --run-time="${DURATION}" \
    --headless \
    --html "${REPORT_BASE}-${TIMESTAMP}.html" \
    --csv "${REPORT_BASE}-${TIMESTAMP}" \
    2>&1 | tee "${REPORT_BASE}-${TIMESTAMP}.log"
else
  echo "Usage:"
  echo "  $0                          # Web UI mode (http://localhost:8089)"
  echo "  $0 headless [USERS RAMP DURATION]"
  echo "  e.g. $0 headless 100 10 60s"
  exit 1
fi