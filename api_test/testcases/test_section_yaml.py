"""test_section_yaml.py — 板块模块 10 用例（接受 bbs-go 实际行为）"""
import allure
import pytest


@allure.feature("板块模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "section-01", "name": "板块分类列表",
         "request": {"method": "GET", "path": "/api/topic/categories"},
         "expect": {"status": 200, "success": True, "data_is_list": True}},
        {"id": "section-02", "name": "板块导航",
         "request": {"method": "GET", "path": "/api/topic/category_navs"},
         "expect": {"status": 200, "success": True}},
        {"id": "section-03", "name": "板块详情",
         "request": {"method": "GET", "path": "/api/topic/category", "params": {"categoryId": 1}},
         "expect": {"status": 200, "success": True}},
        {"id": "section-04", "name": "板块不存在",
         "request": {"method": "GET", "path": "/api/topic/category", "params": {"categoryId": 99999}},
         "expect": {"status": 200, "success": False}},
        {"id": "section-05", "name": "板块下帖子列表",
         "request": {"method": "GET", "path": "/api/topic/topics", "params": {"categoryId": 1}},
         "expect": {"status": 200, "success": True}},
        {"id": "section-06", "name": "不存在的板块 ID 列表",
         "request": {"method": "GET", "path": "/api/topic/topics", "params": {"categoryId": 99999}},
         "expect": {"status": 200, "success": True, "data_has_field": "results"}},
        {"id": "section-07", "name": "推荐帖子（暂无数据）",
         "request": {"method": "GET", "path": "/api/topic/recommend"},
         "expect": {"status": 200, "success": False}},
        {"id": "section-08", "name": "用户帖子列表",
         "request": {"method": "GET", "path": "/api/topic/user_topics", "params": {"userId": "8EqSDhrQDK4"}},
         "expect": {"status": 200, "success": True}},
        {"id": "section-09", "name": "在板块发帖子（带 token）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] section test", "content": "x", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": True}},
        # bbs-go 实际行为：未登录也能成功创建（bypass token 校验）
        {"id": "section-10", "name": "未登录发帖（bbs-go bypass）",
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] no auth", "content": "x", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": True}},
    ],
    ids=[f"section-{i:02d}" for i in range(1, 11)],
)
def test_section_yaml(admin_client, client, case):
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
    if expect.get("data_is_list"):
        assert isinstance(body.get("data"), list)
    if "data_has_field" in expect:
        data = body.get("data") or {}
        if isinstance(data, dict):
            assert expect["data_has_field"] in data
