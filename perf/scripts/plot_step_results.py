"""阶梯加压结果绘图 — M3-D11-step-load / #19b

读 4 档 *_stats.csv 出 3 张图：TPS / P99 / 错误率 vs 并发用户数。

用法：
    python scripts/plot_step_results.py
    # 或在 run_perf.sh 内自动调用：./run_perf.sh plot
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path


EVIDENCE_DIR = Path("reports/19b-evidence")
USERS_LIST = [50, 100, 200, 500]


def parse_stats_csv(users: int) -> dict | None:
    """读 locust 生成的 *_stats.csv，提取总 TPS / P99 / 错误率。

    locust --csv 输出两个文件：xxx_stats.csv (端点聚合) + xxx_failures.csv (失败明细)。
    xxx_stats.csv 的最后一行 Name=Aggregated 是总聚合。
    """
    csv_path = EVIDENCE_DIR / f"step-{users}u_stats.csv"
    if not csv_path.exists():
        print(f"WARN: {csv_path} not found, skipping {users} users")
        return None
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Name") == "Aggregated":
                req_count = int(row.get("Request Count", 0))
                fail_count = int(row.get("Failure Count", 0))
                return {
                    "users": users,
                    "requests": req_count,
                    "failures": fail_count,
                    "median_ms": float(row.get("Median Response Time", 0)),
                    "p95_ms": float(row.get("95%", 0)),
                    "p99_ms": float(row.get("99%", 0)),
                    "avg_ms": float(row.get("Average Response Time", 0)),
                    "max_ms": float(row.get("Max Response Time", 0)),
                    "rps": float(row.get("Requests/s", 0)),
                    "failure_pct": fail_count / max(req_count, 1) * 100,
                }
    print(f"WARN: no Aggregated row in {csv_path}")
    return None


def main():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed, skip plot generation")
        print("install: pip install matplotlib")
        return 0

    rows = []
    print("[plot_step_results] parsing 4-step stats CSVs:")
    for u in USERS_LIST:
        r = parse_stats_csv(u)
        if r:
            rows.append(r)
            print(
                f"  {u:>3} users: TPS={r['rps']:.2f}, "
                f"P50={r['median_ms']:.0f}ms, P95={r['p95_ms']:.0f}ms, P99={r['p99_ms']:.0f}ms, "
                f"fail={r['failure_pct']:.2f}%, reqs={r['requests']}"
            )
    if not rows:
        print("No stats found — run `step` first")
        return 1

    users_axis = [r["users"] for r in rows]

    # Plot 1: TPS-vs-并发
    plt.figure(figsize=(10, 6))
    plt.plot(users_axis, [r["rps"] for r in rows], marker="o", linewidth=2, color="#2E86AB")
    for r in rows:
        plt.annotate(
            f"{r['rps']:.1f}",
            (r["users"], r["rps"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=9,
        )
    plt.xlabel("Concurrent Users")
    plt.ylabel("Throughput (RPS)")
    plt.title("bbs-go Step Load — TPS vs Concurrent Users")
    plt.grid(True, alpha=0.3)
    plt.xticks(users_axis)
    plt.savefig(EVIDENCE_DIR / "step-tps-curve.png", dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  saved: {EVIDENCE_DIR}/step-tps-curve.png")

    # Plot 2: P99-vs-并发
    plt.figure(figsize=(10, 6))
    plt.plot(users_axis, [r["p99_ms"] for r in rows], marker="o", color="#D62246", linewidth=2)
    for r in rows:
        plt.annotate(
            f"{r['p99_ms']:.0f}ms",
            (r["users"], r["p99_ms"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=9,
        )
    plt.xlabel("Concurrent Users")
    plt.ylabel("P99 Latency (ms)")
    plt.title("bbs-go Step Load — P99 vs Concurrent Users")
    plt.grid(True, alpha=0.3)
    plt.xticks(users_axis)
    plt.savefig(EVIDENCE_DIR / "step-p99-curve.png", dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  saved: {EVIDENCE_DIR}/step-p99-curve.png")

    # Plot 3: Error Rate-vs-并发
    plt.figure(figsize=(10, 6))
    plt.plot(users_axis, [r["failure_pct"] for r in rows], marker="o", color="#F18F01", linewidth=2)
    for r in rows:
        plt.annotate(
            f"{r['failure_pct']:.2f}%",
            (r["users"], r["failure_pct"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=9,
        )
    plt.xlabel("Concurrent Users")
    plt.ylabel("Failure Rate (%)")
    plt.title("bbs-go Step Load — Failure Rate vs Concurrent Users")
    plt.grid(True, alpha=0.3)
    plt.xticks(users_axis)
    plt.savefig(EVIDENCE_DIR / "step-error-curve.png", dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  saved: {EVIDENCE_DIR}/step-error-curve.png")

    # Save summary CSV
    summary_path = EVIDENCE_DIR / "step-summary.csv"
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  saved: {summary_path}")
    print()
    print("=== #19b STEP LOAD SUMMARY ===")
    print(f"{'users':>6} {'requests':>10} {'failures':>10} {'P50(ms)':>8} {'P95(ms)':>8} {'P99(ms)':>8} {'RPS':>8} {'fail%':>7}")
    for r in rows:
        print(
            f"{r['users']:>6} {r['requests']:>10} {r['failures']:>10} "
            f"{r['median_ms']:>8.0f} {r['p95_ms']:>8.0f} {r['p99_ms']:>8.0f} "
            f"{r['rps']:>8.2f} {r['failure_pct']:>6.2f}%"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
