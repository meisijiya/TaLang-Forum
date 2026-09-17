#!/usr/bin/env bash
# run_api.sh — bbs-go API 测试 runner
# Usage:
#   ./scripts/run_api.sh test       # run pytest + allure results
#   ./scripts/run_api.sh report     # generate allure HTML report
#   ./scripts/run_api.sh trend3     # show last 3 runs trend
#   ./scripts/run_api.sh all        # test + report
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

case "${1:-test}" in
  test)
    echo "[run_api] pytest → reports/allure-results/"
    python -m pytest testcases/ -v --alluredir=reports/allure-results --clean-alluredir
    ;;
  report)
    echo "[run_api] allure generate reports/allure-report/"
    allure generate reports/allure-results --clean -o reports/allure-report
    ;;
  trend3)
    echo "[run_api] allure trend last 3 runs"
    ls -lt reports/ | head -10
    ;;
  all)
    "$0" test
    "$0" report
    ;;
  *)
    echo "Usage: $0 {test|report|trend3|all}"
    exit 2
    ;;
esac
