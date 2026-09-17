"""UI 测试全局 conftest

fixtures:
- browser: Chromium session-scope
- context / admin_context: 每个 test 一个 context
- page / admin_page: page with/without admin cookie
- admin_client: 带 admin token 的 API client（用于 API fallback 创建测试数据）
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

# 让 base/ common/ base_api/ page/ 可被测试代码 import
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "base"))
sys.path.insert(0, str(Path(__file__).parent / "common"))
sys.path.insert(0, str(Path(__file__).parent / "base_api"))


BBS_GO_BASE_URL = os.getenv("BBS_GO_BASE_URL", "http://127.0.0.1:8081")
ADMIN_TOKEN = os.getenv("BBS_GO_ADMIN_TOKEN", "")
ADMIN_OBFUSCATED_ID = "8EqSDhrQDK4"


@pytest.fixture(scope="session")
def base_url():
    return BBS_GO_BASE_URL


@pytest.fixture(scope="session")
def admin_obfuscated_id():
    return ADMIN_OBFUSCATED_ID


def _fetch_admin_token() -> str:
    """fallback: 从 MySQL 拿 freshest token"""
    if ADMIN_TOKEN:
        return ADMIN_TOKEN
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
        return result.stdout.strip()
    except Exception:
        return ""


@pytest.fixture(scope="session")
def _pw():
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture(scope="session")
def _browser(_pw):
    b = _pw.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    yield b
    b.close()


@pytest.fixture()
def browser(_browser):
    """alias for compatibility"""
    yield _browser


@pytest.fixture()
def context(_browser):
    ctx = _browser.new_context()
    yield ctx
    ctx.close()


@pytest.fixture()
def admin_context(_browser):
    token = _fetch_admin_token()
    if not token:
        pytest.skip("admin token not available")
    storage_state = {
        "cookies": [
            {
                "name": "bbsgo_token",
                "value": token,
                "domain": "127.0.0.1",
                "path": "/",
                "httpOnly": False,
                "secure": False,
                "sameSite": "Lax",
            },
        ],
        "origins": [],
    }
    ctx = _browser.new_context(storage_state=storage_state)
    yield ctx
    ctx.close()


@pytest.fixture()
def page(context):
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture()
def admin_page(admin_context):
    page = admin_context.new_page()
    yield page
    page.close()


@pytest.fixture()
def admin_client():
    """带 admin token 的 API client（UI 测试用 API fallback 创建测试数据）"""
    from api_client import ApiClient  # base_api/api_client.py
    token = _fetch_admin_token()
    if not token:
        pytest.skip("admin token not available")
    return ApiClient(base_url=BBS_GO_BASE_URL, token=token)


def full_url(path: str) -> str:
    """拼接完整 URL（page.goto 不支持 base_url）"""
    if path.startswith("http"):
        return path
    return BBS_GO_BASE_URL.rstrip("/") + path
