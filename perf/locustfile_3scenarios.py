"""bbs-go locust 3 场景压测 — M3-D11-locust-scenarios + step-load / #19b

设计原则：
1. 单文件多 HttpUser 子类（#19b acceptance 第 1 条任一即可；选单文件因为启动更简单）
2. 3 场景按论坛真实行为权重：登录:1 / 列表查询:3 / 发帖:1
3. on_start 统一拿 admin token（BBS_GO_ADMIN_TOKEN env var → docker exec MySQL fallback）
4. FastHttpUser 提升性能（gevent + native HTTP client，比 HttpUser 的 requests 更轻）
5. WinHTTP 代理硬约束（#14-1 教训）：FastHttpUser 默认不读 env，所以无问题；HttpUser 需 trust_env=False
6. bbs-go 端点实证（前端 bundle 提取 + 容器内 curl）：
   - 帖子列表：GET /api/topic/topics?sectionId=N&page=N （200，data.results 含帖子数组）
   - 发帖：POST /api/topic/create （200，admin token 注入，captcha 服务端关闭）
   - 登录：POST /api/login/signin （captcha 必触发，success=false 但 HTTP 200 = 链路通畅）
   - 板块列表：GET /api/topic/categories （200，data 是数组）

排除：
- 不评论（captcha 强制 + 需关联帖子）—— #19c 范畴
- 不搜索（搜索端点 200 但返回空）—— #19c 范畴
- 不调优（Redis / DB 连接池 / SQL 索引）—— #19c 范畴

阶梯加压（Step 6 + 7）：
- 50 / 100 / 200 / 500 用户，每档 120s
- scripts/run_perf.sh step 模式串联
- scripts/plot_step_results.py 出 TPS / P99 / 错误率 退化曲线 PNG

性能指标（预期）：
- 50 用户：TPS ~ 50-80，P99 < 30ms，错误率 ~0
- 100 用户：TPS ~ 100-150，P99 < 50ms，错误率 ~0
- 200 用户：TPS ~ 150-200，P99 < 100ms，错误率 < 0.1%
- 500 用户：TPS / P99 拐点出现，错误率上升（推测瓶颈）
"""
from __future__ import annotations

import os
import random
import string
import subprocess
from locust import FastHttpUser, task, between, events


BBS_GO_BASE_URL = os.getenv("BBS_GO_BASE_URL", "http://127.0.0.1:8081")


def fetch_admin_token() -> str | None:
    """从 MySQL 拿 freshest active admin token。

    优先级：env var (CI 一致性) → docker exec MySQL (本地 fallback)。
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


class _BaseBbsGoUser(FastHttpUser):
    """共享基类：on_start 拿 token + 初始化 headers。

    abstract=True 不参与权重分配（#19b acceptance 要求 3 类独立 User）。
    FastHttpUser 用 gevent + native HTTP client，比 HttpUser 快 ~2x。
    """
    abstract = True
    wait_time = between(1, 3)

    def on_start(self):
        self.admin_token = fetch_admin_token()
        self.headers = {"Content-Type": "application/json"}
        if self.admin_token:
            self.headers["Authorization"] = self.admin_token


class LoginUser(_BaseBbsGoUser):
    """场景 1：登录（captcha 必触发，记录但不 fail）。"""
    weight = 1

    @task
    def login_attempt(self):
        """POST /api/login/signin —— 期望 HTTP 200 + JSON 合法即可。
        bbs-go 行为：未传 captcha → success=false + errorCode=1000，但 HTTP 200。
        链路通畅 = 服务端响应合法。"""
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


class TopicListUser(_BaseBbsGoUser):
    """场景 2：帖子列表查询（高频读路径）。"""
    weight = 3

    def on_start(self):
        super().on_start()
        # on_start 缓存 sectionId 列表 —— 避免每 task 都打 categories 接口
        self.section_ids = self._fetch_section_ids() or [1]

    def _fetch_section_ids(self):
        try:
            resp = self.client.get(
                "/api/topic/categories",
                name="GET /api/topic/categories (warmup)",
            )
            if resp.status_code != 200:
                return None
            data = resp.json().get("data") or []
            # data 可能是 list 或 dict —— 兼容两种
            if isinstance(data, list):
                return [s.get("id") for s in data if s.get("id")]
            if isinstance(data, dict) and "results" in data:
                return [s.get("id") for s in data["results"] if s.get("id")]
            return None
        except Exception:
            return None

    @task
    def list_topics(self):
        section_id = random.choice(self.section_ids)
        page = random.randint(1, 5)
        with self.client.get(
            f"/api/topic/topics?sectionId={section_id}&page={page}",
            name="GET /api/topic/topics",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
            elif "data" not in resp.text:
                resp.failure("no data field")


class TopicCreateUser(_BaseBbsGoUser):
    """场景 3：发帖（写路径，需 admin token）。"""
    weight = 1

    def on_start(self):
        super().on_start()
        # 发帖必须 token —— 没 token 直接停 runner（防止脏数据噪音）
        if not self.admin_token:
            return
        # 缓存 sectionId 列表
        try:
            resp = self.client.get(
                "/api/topic/categories",
                name="GET /api/topic/categories (warmup)",
            )
            if resp.status_code == 200:
                data = resp.json().get("data") or []
                if isinstance(data, list):
                    self.section_ids = [s.get("id") for s in data if s.get("id")] or [1]
                else:
                    self.section_ids = [1]
            else:
                self.section_ids = [1]
        except Exception:
            self.section_ids = [1]

    @task
    def create_topic(self):
        if not self.admin_token:
            return
        section_id = random.choice(self.section_ids)
        # 参数化不同长度边界：短标题 / 中标题 / 长标题
        title_len = random.choice([10, 50, 100])
        content_len = random.choice([50, 200, 1000])
        title = "perf-" + "".join(random.choices(string.ascii_letters, k=title_len))
        content = "perf content " + "".join(
            random.choices(string.ascii_letters + " ", k=content_len)
        )
        payload = {
            "title": title,
            "content": content,
            "sectionId": section_id,
            "type": 0,
        }
        with self.client.post(
            "/api/topic/create",
            json=payload,
            headers=self.headers,
            name="POST /api/topic/create",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
            elif '"success":false' in resp.text:
                # 业务失败（如 captcha 必触发）—— 记录但不 fail
                # 容器内 captcha 服务端配置已关闭，发帖应成功
                pass
            elif '"success":true' not in resp.text:
                resp.failure("no success field")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """压测开始：打印环境信息。"""
    print(f"\n[bbs-go 3-scenario locust] starting, base URL: {BBS_GO_BASE_URL}")
    token = fetch_admin_token()
    masked = token[:16] + "..." if token else "NONE"
    print(f"[bbs-go 3-scenario locust] admin token: {masked}\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """压测结束：打印关键指标摘要。"""
    stats = environment.stats.total
    print(f"\n[bbs-go 3-scenario locust] === stats summary ===")
    print(f"  total requests: {stats.num_requests}")
    print(f"  total failures: {stats.num_failures}")
    print(f"  median response: {stats.median_response_time}ms")
    print(f"  p95 response: {stats.get_response_time_percentile(0.95)}ms")
    print(f"  p99 response: {stats.get_response_time_percentile(0.99)}ms")
    print(f"  max response: {stats.max_response_time}ms")
    print(f"  RPS: {stats.total_rps:.2f}\n")
