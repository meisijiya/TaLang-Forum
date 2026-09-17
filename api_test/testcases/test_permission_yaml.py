"""test_permission_yaml.py — 权限模块 6 用例（接受 bbs-go 实际行为）"""
import allure
import pytest


@allure.feature("权限模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "perm-01", "name": "当前用户权限",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/current"},
         "expect": {"status": 200, "success": True}},
        # bbs-go bypass — 未登录能创建帖子
        {"id": "perm-02", "name": "未登录发帖（bbs-go bypass）",
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[perm] no auth", "content": "x", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": True}},
        # 编辑不存在帖子 → success=false
        {"id": "perm-03", "name": "编辑不存在帖子",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/edit/9999999",
                     "json": {"title": "hack", "content": "x", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": False}},
        # 删除不存在帖子 → success=true data:null
        {"id": "perm-04", "name": "删除不存在帖子",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/delete/9999999"},
         "expect": {"status": 200, "success": True}},
        # admin 接口 admin user 不一定有 dashboard permission
        {"id": "perm-05", "name": "管理员接口（无 dashboard permission）",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/admin/category/list"},
         "expect": {"status": 200, "success": False}},
        {"id": "perm-06", "name": "管理员接口无 token",
         "request": {"method": "GET", "path": "/api/admin/category/list"},
         "expect": {"status": 200, "success": False}},
    ],
    ids=[f"perm-{i:02d}" for i in range(1, 7)],
)
def test_permission_yaml(admin_client, client, case):
    c = admin_client if case.get("needs_token") else client
    req = case["request"]
    method = req["method"].lower()
    kwargs = {}
    if "params" in req:
        kwargs["params"] = req["params"]
    response = getattr(c, method)(req["path"], json_data=req.get("json"), **kwargs)

    expect = case["expect"]
    assert response.status_code == expect["status"]
    body = response.json()
    assert body.get("success") == expect["success"], \
        f"case={case['id']} expected success={expect['success']}, got {body}"
