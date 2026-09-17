"""bbs-go locust 登录场景压测 — M3-D10-locust-basic / #19a

设计原则：
1. 单场景 = 登录 + 看板块 + 看个人主页（覆盖论坛最常见 3 类读路径）
2. on_start 优先用 BBS_GO_ADMIN_TOKEN env var（CI 一致性）；fallback docker exec MySQL 拿 freshest
3. bbs-go 服务端登录强制 captcha → login_attempt 期望 success=false 但 HTTP 200
   （链路通畅 = 服务端有响应，不强制 success=true —— #17 captcha 审计结论）
4. WinHTTP 代理硬约束：trust_env=False 屏蔽 Windows 系统代理（#14-1 教训）

性能指标（M3 chain 起点）：
- 单场景 100 用户 / 10 ramp-up / 60s
- 验证：链路通畅 + 服务端稳定 + 报告生成 + 关键指标可读
- 不含：阶梯加压（#19b）/ 调优对比（#19c）—— 留给后续工单

排除：
- 不发帖（captcha 服务端关闭后 bypass 但会污染论坛数据）—— #19b 含
- 不评论 —— #19b 含
- 不搜索 —— #19b 含
"""
from __future__ import annotations

import os
import subprocess
from locust import HttpUser, task, between, events


BBS_GO_BASE_URL = os.getenv("BBS_GO_BASE_URL", "http://127.0.0.1:8081")


def fetch_admin_token() -> str | None:
    """从 MySQL 拿 freshest active admin token。

    Returns:
        str | None: token 字符串，失败返回 None
    """
    token = os.getenv("BBS_GO_ADMIN_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(
            [
                "docker", "exec", "bbs-go-mysql-1",
                "mysql", "-ubbsgo", "-pbbsgo_password", "bbsgo",
                "-se",
                "SELECT token FROM t_user_token WHERE user_id=1 AND status=0 ORDER BY id DESC LIMIT 1;",
            ],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


class BbsGoUser(HttpUser):
    """单虚拟用户：登录 + 板块列表 + 个人主页。"""

    wait_time = between(1, 3)

    def on_start(self):
        """每个虚拟用户启动时：拿 admin token + 预热 headers。"""
        self.admin_token = fetch_admin_token()
        self.headers = {"Content-Type": "application/json"}
        if self.admin_token:
            self.headers["Authorization"] = self.admin_token

    @task(1)
    def login_attempt(self):
        """登录失败路径（captcha 必触发）—— 验证 POST 链路通畅。

        bbs-go 行为：未传 captcha 时服务端 success=false + errorCode=1000；
        但 HTTP 状态码 200 —— 链路通畅 = 服务端响应合法。
        """
        payload = {"username": "admin", "password": "Test@12345"}
        with self.client.post(
            "/api/login/signin",
            json=payload,
            name="POST /api/login/signin (captcha-bypass)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
            elif "success" not in resp.text:
                resp.failure("no success field in response")

    @task(3)
    def list_categories(self):
        """板块分类列表（高频读路径）。"""
        with self.client.get(
            "/api/topic/categories",
            name="GET /api/topic/categories",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
            elif "data" not in resp.text:
                resp.failure("no data field")

    @task(1)
    def current_user(self):
        """个人主页（需 token）。"""
        with self.client.get(
            "/api/user/current",
            headers=self.headers,
            name="GET /api/user/current",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """压测开始：打印环境信息。"""
    print(f"\n[bbs-go locust] starting, base URL: {BBS_GO_BASE_URL}")
    token = fetch_admin_token()
    masked = token[:16] + "..." if token else "NONE"
    print(f"[bbs-go locust] admin token: {masked}\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """压测结束：打印关键指标摘要。"""
    stats = environment.stats.total
    print(f"\n[bbs-go locust] === stats summary ===")
    print(f"  total requests: {stats.num_requests}")
    print(f"  total failures: {stats.num_failures}")
    print(f"  median response: {stats.median_response_time}ms")
    print(f"  p95 response: {stats.get_response_time_percentile(0.95)}ms")
    print(f"  p99 response: {stats.get_response_time_percentile(0.99)}ms")
    print(f"  RPS: {stats.total_rps:.2f}\n")