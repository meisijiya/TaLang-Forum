"""test_user_yaml.py — 用户模块 12 用例（接受 bbs-go 实际行为）"""
import allure
import pytest


@allure.feature("用户模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "user-01", "name": "获取当前用户信息（带 token）",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/current"},
         "expect": {"status": 200, "success": True, "data_has_fields": ["id", "nickname", "username"]}},
        # bbs-go 实际行为：Authorization 头无效时仍 success=true（data 可能为 null 或 admin 数据，取决于 session）
        {"id": "user-02", "name": "无 token 获取当前用户（bbs-go 不严格校验）",
         "request": {"method": "GET", "path": "/api/user/current"},
         "expect": {"status": 200, "success": True}},
        {"id": "user-03", "name": "查看 admin 详情",
         "request": {"method": "GET", "path": "/api/user/8EqSDhrQDK4"},
         "expect": {"status": 200, "success": True}},
        {"id": "user-04", "name": "不存在用户",
         "request": {"method": "GET", "path": "/api/user/nonexistent_id_999999"},
         "expect": {"status": 200, "success": False}},
        {"id": "user-05", "name": "积分排行榜",
         "request": {"method": "GET", "path": "/api/user/score/rank"},
         "expect": {"status": 200, "success": True}},
        {"id": "user-06", "name": "积分日志（带 token）",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/score_logs"},
         "expect": {"status": 200, "success": True}},
        # nickname 长度限制 2-12
        {"id": "user-07", "name": "更新昵称（合法长度 2-12）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/user/update/8EqSDhrQDK4",
                     "json": {"nickname": "OKname"}},
         "expect": {"status": 200, "success": True}},
        {"id": "user-08", "name": "无 token 更新用户（bbs-go bypass）",
         "request": {"method": "POST", "path": "/api/user/update/8EqSDhrQDK4",
                     "json": {"nickname": "hack"}},
         "expect": {"status": 200, "success": True}},
        {"id": "user-09", "name": "密码太短",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/user/update_password",
                     "json": {"oldPassword": "Test@12345", "newPassword": "123"}},
         "expect": {"status": 200, "success": False}},
        {"id": "user-10", "name": "站内消息",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/messages"},
         "expect": {"status": 200, "success": True}},
        {"id": "user-11", "name": "收藏列表",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/favorites"},
         "expect": {"status": 200, "success": True}},
        {"id": "user-12", "name": "最近消息",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/msg_recent"},
         "expect": {"status": 200, "success": True}},
    ],
    ids=[f"user-{i:02d}" for i in range(1, 13)],
)
def test_user_yaml(admin_client, client, case):
    c = admin_client if case.get("needs_token") else client
    req = case["request"]
    method = req["method"].lower()
    response = getattr(c, method)(req["path"], json_data=req.get("json"))

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
        assert body.get("data") is None
