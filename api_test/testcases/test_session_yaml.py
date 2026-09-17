"""test_session_yaml.py — session 模块 5 用例（接受 bbs-go 实际行为）

关键发现：bbs-go /api/user/current 对任何 Authorization 头都返回 success=true data=null
（实际意义：token 解析失败时静默降级为匿名）。
"""
import allure
import pytest

from base_api.api_client import ApiClient
from common.config import BBS_GO_BASE_URL


@allure.feature("Session 模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "session-01", "name": "有效 token 获取 session",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/current"},
         "expect": {"status": 200, "success": True, "data_has_fields": ["id", "username", "nickname"]}},
        # bbs-go 行为：无效 token 也 success=true data=null
        {"id": "session-02", "name": "无效 token（bbs-go 静默降级）",
         "request": {"method": "GET", "path": "/api/user/current",
                     "headers": {"Authorization": "invalid_token_xyz_12345"}},
         "expect": {"status": 200, "success": True, "data_is_null": True}},
        {"id": "session-03", "name": "过期 token（bbs-go 静默降级）",
         "request": {"method": "GET", "path": "/api/user/current",
                     "headers": {"Authorization": "EXPIRED_TOKEN_1234567890"}},
         "expect": {"status": 200, "success": True, "data_is_null": True}},
        {"id": "session-04", "name": "无 Authorization header（bbs-go bypass）",
         "request": {"method": "GET", "path": "/api/user/current"},
         "expect": {"status": 200, "success": True}},
        {"id": "session-05", "name": "格式错误 Bearer token（bbs-go 静默降级）",
         "request": {"method": "GET", "path": "/api/user/current",
                     "headers": {"Authorization": "Bearer not_a_real_token"}},
         "expect": {"status": 200, "success": True, "data_is_null": True}},
    ],
    ids=[f"session-{i:02d}" for i in range(1, 6)],
)
def test_session_yaml(admin_client, client, case):
    c = admin_client if case.get("needs_token") else client
    req = case["request"]
    method = req["method"].lower()
    headers_override = req.get("headers")
    if headers_override and "Authorization" in headers_override:
        tmp = ApiClient(base_url=BBS_GO_BASE_URL)
        custom_headers = tmp._headers()
        custom_headers.update(headers_override)
        response = tmp.session.get(f"{BBS_GO_BASE_URL}{req['path']}", headers=custom_headers)
    else:
        response = getattr(c, method)(req["path"])

    expect = case["expect"]
    assert response.status_code == expect["status"]
    body = response.json()
    assert body.get("success") == expect["success"], \
        f"case={case['id']} expected success={expect['success']}, got {body}"
    if "data_has_fields" in expect:
        data = body.get("data") or {}
        for field in expect["data_has_fields"]:
            assert field in data, f"case={case['id']} expected field '{field}'"
    if expect.get("data_is_null"):
        assert body.get("data") is None, f"case={case['id']} expected data=null, got {body.get('data')}"
