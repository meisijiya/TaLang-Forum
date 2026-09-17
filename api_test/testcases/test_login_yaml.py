"""test_login_yaml.py — YAML 数据驱动登录测试（8 用例）"""
import allure
import pytest


@allure.feature("登录模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "login-01", "name": "登录无 captcha",
         "request": {"method": "POST", "path": "/api/login/signin",
                     "json": {"username": "admin", "password": "Test@12345"}},
         "expect": {"status": 200, "success": False, "error_message_contains": "验证码"}},
        {"id": "login-02", "name": "空用户名",
         "request": {"method": "POST", "path": "/api/login/signin",
                     "json": {"username": "", "password": "Test@12345", "captchaId": "x", "captchaCode": "y"}},
         "expect": {"status": 200, "success": False}},
        {"id": "login-03", "name": "密码错误",
         "request": {"method": "POST", "path": "/api/login/signin",
                     "json": {"username": "admin", "password": "WrongPassword", "captchaId": "x", "captchaCode": "y"}},
         "expect": {"status": 200, "success": False}},
        {"id": "login-04", "name": "用户不存在",
         "request": {"method": "POST", "path": "/api/login/signin",
                     "json": {"username": "ghost_user", "password": "Test@12345", "captchaId": "x", "captchaCode": "y"}},
         "expect": {"status": 200, "success": False}},
        {"id": "login-05", "name": "空密码",
         "request": {"method": "POST", "path": "/api/login/signin",
                     "json": {"username": "admin", "password": "", "captchaId": "x", "captchaCode": "y"}},
         "expect": {"status": 200, "success": False}},
        {"id": "login-06", "name": "SQL 注入尝试",
         "request": {"method": "POST", "path": "/api/login/signin",
                     "json": {"username": "admin' OR '1'='1", "password": "x", "captchaId": "x", "captchaCode": "y"}},
         "expect": {"status": 200, "success": False}},
        {"id": "login-07", "name": "无效 captcha code",
         "request": {"method": "POST", "path": "/api/login/signin",
                     "json": {"username": "admin", "password": "Test@12345", "captchaId": "x", "captchaCode": "9999"}},
         "expect": {"status": 200, "success": False}},
        {"id": "login-08", "name": "登出端点（实际 404）",
         "request": {"method": "POST", "path": "/api/login/signout"},
         "expect": {"status": 404}},
    ],
    ids=[f"login-{i:02d}" for i in range(1, 9)],
)
def test_login_yaml(client, case):
    req = case["request"]
    method = req["method"].lower()
    response = getattr(client, method)(req["path"], json_data=req.get("json"))

    expect = case["expect"]
    if expect["status"] == 404:
        assert response.status_code == 404, f"case={case['id']} expected 404, got {response.status_code}"
        return
    assert response.status_code == expect["status"]
    body = response.json()
    assert body.get("success") == expect["success"], \
        f"case={case['id']} expected success={expect['success']}, got {body}"
    if "error_message_contains" in expect:
        assert expect["error_message_contains"] in body.get("message", ""), \
            f"case={case['id']} expected message contains '{expect['error_message_contains']}'"
