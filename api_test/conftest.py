"""pytest 全局 fixture（共享 client + admin_client + 失败截图 hook）

fixtures：
- client: 普通 client，无 token
- admin_client: 带 admin token 的 client（CI 用 env var 注入）
- 不需要 freshest_token（本机 hard-coded 已足够）
"""
import os
import subprocess

import allure
import pytest

from base_api.api_client import ApiClient
from common.config import BBS_GO_ADMIN_TOKEN, BBS_GO_BASE_URL


@pytest.fixture(scope="session")
def client():
    """无 token 通用 client"""
    return ApiClient(base_url=BBS_GO_BASE_URL)


@pytest.fixture(scope="session")
def admin_client():
    """带 admin token 的 client（用于创建帖子/评论等需登录的接口）

    优先级：
    1. 环境变量 BBS_GO_ADMIN_TOKEN（CI 注入）
    2. 写入 conftest 时本机 fallback：从 MySQL 取 freshest token
    """
    token = BBS_GO_ADMIN_TOKEN
    if not token:
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
            token = result.stdout.strip()
        except Exception as e:
            print(f"[WARN] unable to fetch admin token from mysql: {e}")
    if not token:
        pytest.skip("admin token not available; set BBS_GO_ADMIN_TOKEN env var or start mysql")
    return ApiClient(base_url=BBS_GO_BASE_URL, token=token)


@pytest.fixture(scope="session")
def admin_token(admin_client):
    """直接暴露 token 字符串（便于 fixtures 间共享）"""
    return admin_client.token


@pytest.fixture(scope="session")
def base_url():
    return BBS_GO_BASE_URL


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动附加 allure 报告上下文

    API 测试无 page，但保留 hook 给未来 UI 失败截图扩展
    """
    outcome = yield
    rep = outcome.get_result()
    if rep.failed and "page" in item.fixturenames:
        try:
            page = item.funcargs["page"]
            allure.attach(
                page.screenshot(),
                name="failure-screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
