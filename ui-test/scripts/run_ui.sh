#!/usr/bin/env bash
# run_ui.sh — bbs-go UI 测试 runner
# Usage:
#   ./scripts/run_ui.sh test          # run pytest + allure results
#   ./scripts/run_ui.sh test-headed   # headed mode for debugging
#   ./scripts/run_ui.sh report        # generate allure HTML report
#   ./scripts/run_ui.sh report-static # static HTML report for artifacts
#   ./scripts/run_ui.sh all           # test + report
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

case "${1:-test}" in
  test)
    echo "[run_ui] pytest (headless) → reports/allure-results/"
    python -m pytest testcase/ -v --alluredir=reports/allure-results --clean-alluredir
    ;;
  test-headed)
    echo "[run_ui] pytest (headed) → reports/allure-results/"
    python -m pytest testcase/ -v --headed --alluredir=reports/allure-results --clean-alluredir
    ;;
  report)
    echo "[run_ui] allure generate reports/allure-report/"
    allure generate reports/allure-results --clean -o reports/allure-report
    ;;
  report-static)
    echo "[run_ui] allure generate static"
    allure generate reports/allure-results --clean -o reports/allure-report
    ;;
  all)
    "$0" test
    "$0" report
    ;;
  *)
    echo "Usage: $0 {test|test-headed|report|report-static|all}"
    exit 2
    ;;
esac
