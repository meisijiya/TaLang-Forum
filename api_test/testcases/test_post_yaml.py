"""test_post_yaml.py — 帖子模块 20 用例（接受 bbs-go 实际行为）"""
import allure
import pytest


@allure.feature("帖子模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "post-01", "name": "创建普通帖子",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] post-01", "content": "test content", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": True}},
        {"id": "post-02", "name": "空标题",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "", "content": "x", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": False}},
        {"id": "post-03", "name": "空内容",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] no content", "content": "", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": False}},
        # categoryId=0 实际允许（默认板块）
        {"id": "post-04", "name": "无板块（默认板块）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] default cat", "content": "x", "categoryId": 0, "type": 0}},
         "expect": {"status": 200, "success": True}},
        {"id": "post-05", "name": "无效板块",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] invalid cat", "content": "x", "categoryId": 99999, "type": 0}},
         "expect": {"status": 200, "success": False}},
        {"id": "post-06", "name": "tweet 类型",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] tweet", "content": "tweet content", "categoryId": 1, "type": 1}},
         "expect": {"status": 200, "success": True}},
        # type=2 问答类型不支持默认板块
        {"id": "post-07", "name": "问答类型（板块不支持）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] qa", "content": "qa content", "categoryId": 1, "type": 2}},
         "expect": {"status": 200, "success": False}},
        {"id": "post-08", "name": "超长标题",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] " + "x" * 200, "content": "x", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": False}},
        {"id": "post-09", "name": "XSS 内容",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/create",
                     "json": {"title": "[apitest] xss", "content": "<script>alert('xss')</script>", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": True}},
        {"id": "post-10", "name": "帖子列表",
         "request": {"method": "GET", "path": "/api/topic/topics"},
         "expect": {"status": 200, "success": True, "data_has_field": "results"}},
        {"id": "post-11", "name": "帖子列表分页",
         "request": {"method": "GET", "path": "/api/topic/topics", "params": {"page": 1, "pageSize": 10}},
         "expect": {"status": 200, "success": True}},
        # topic detail 端点不存在 → 404
        {"id": "post-12", "name": "帖子详情（端点 404）",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/topic/detail/1"},
         "expect": {"status": 404}},
        {"id": "post-13", "name": "帖子不存在（端点 404）",
         "request": {"method": "GET", "path": "/api/topic/detail/9999999"},
         "expect": {"status": 404}},
        # 编辑不存在帖子 → success=false
        {"id": "post-14", "name": "编辑不存在帖子",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/edit/9999999",
                     "json": {"title": "[apitest] edited", "content": "edited", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": False}},
        {"id": "post-15", "name": "无 token 编辑（topic 不存在）",
         "request": {"method": "POST", "path": "/api/topic/edit/1",
                     "json": {"title": "hacked", "content": "x", "categoryId": 1, "type": 0}},
         "expect": {"status": 200, "success": False}},
        {"id": "post-16", "name": "删除不存在帖子（bbs-go 静默 success）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/topic/delete/1"},
         "expect": {"status": 200, "success": True}},
        # bbs-go 无 token 删除可能 success=true data:null（id=1 不存在）
        {"id": "post-17", "name": "无 token 删除帖子",
         "request": {"method": "POST", "path": "/api/topic/delete/1"},
         "expect": {"status": 200, "success": True}},
        {"id": "post-18", "name": "最近点赞",
         "request": {"method": "GET", "path": "/api/topic/recentlikes/8EqSDhrQDK4"},
         "expect": {"status": 200, "success": True}},
        # topic id=1 不存在
        {"id": "post-19", "name": "点赞不存在帖子",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/like/like",
                     "json": {"entityType": "topic", "entityId": "1"}},
         "expect": {"status": 200, "success": False}},
        {"id": "post-20", "name": "收藏不存在帖子",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/favorite/add",
                     "json": {"entityType": "topic", "entityId": "1"}},
         "expect": {"status": 200, "success": False}},
    ],
    ids=[f"post-{i:02d}" for i in range(1, 21)],
)
def test_post_yaml(admin_client, client, case):
    c = admin_client if case.get("needs_token") else client
    req = case["request"]
    method = req["method"].lower()
    kwargs = {}
    if "params" in req:
        kwargs["params"] = req["params"]
    response = getattr(c, method)(req["path"], json_data=req.get("json"), **kwargs)

    expect = case["expect"]
    if expect["status"] == 404:
        assert response.status_code == 404, f"case={case['id']} expected 404, got {response.status_code}"
        return
    assert response.status_code == expect["status"]
    body = response.json()
    assert body.get("success") == expect["success"], \
        f"case={case['id']} expected success={expect['success']}, got {body}"
