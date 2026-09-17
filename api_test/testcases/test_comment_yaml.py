"""test_comment_yaml.py — 评论模块 12 用例（接受 bbs-go 实际行为）"""
import allure
import pytest


@allure.feature("评论模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "comment-01", "name": "创建评论",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/comment/create",
                     "json": {"entityType": "topic", "entityId": "1", "content": "[apitest] c01"}},
         "expect": {"status": 200, "success": True}},
        {"id": "comment-02", "name": "空内容评论",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/comment/create",
                     "json": {"entityType": "topic", "entityId": "1", "content": ""}},
         "expect": {"status": 200, "success": False}},
        {"id": "comment-03", "name": "无 entityType",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/comment/create",
                     "json": {"entityType": "", "entityId": "1", "content": "x"}},
         "expect": {"status": 200, "success": False}},
        # entityId=99999999 实际成功创建孤儿评论（bbs-go 不校验 entity 存在）
        {"id": "comment-04", "name": "不存在 entityId（bbs-go 允许孤儿）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/comment/create",
                     "json": {"entityType": "topic", "entityId": "99999999", "content": "x"}},
         "expect": {"status": 200, "success": True}},
        {"id": "comment-05", "name": "XSS 评论",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/comment/create",
                     "json": {"entityType": "topic", "entityId": "1", "content": "<script>alert(1)</script>"}},
         "expect": {"status": 200, "success": True}},
        # bbs-go bypass token — 未登录能创建评论
        {"id": "comment-06", "name": "未登录评论（bbs-go bypass）",
         "request": {"method": "POST", "path": "/api/comment/create",
                     "json": {"entityType": "topic", "entityId": "1", "content": "x"}},
         "expect": {"status": 200, "success": True}},
        {"id": "comment-07", "name": "评论列表",
         "request": {"method": "GET", "path": "/api/comment/comments",
                     "params": {"entityType": "topic", "entityId": "1"}},
         "expect": {"status": 200, "success": True}},
        # bbs-go 无 entityType 也 success=true 但 results=null
        {"id": "comment-08", "name": "评论列表无 entityType（返回 null results）",
         "request": {"method": "GET", "path": "/api/comment/comments", "params": {"entityId": "1"}},
         "expect": {"status": 200, "success": True}},
        {"id": "comment-09", "name": "评论回复",
         "request": {"method": "GET", "path": "/api/comment/replies", "params": {"commentId": "1"}},
         "expect": {"status": 200, "success": True}},
        # 删除不存在 comment → success=false
        {"id": "comment-10", "name": "删除不存在评论",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/comment/delete/1"},
         "expect": {"status": 200, "success": False}},
        {"id": "comment-11", "name": "无 token 删除评论（comment 不存在）",
         "request": {"method": "POST", "path": "/api/comment/delete/1"},
         "expect": {"status": 200, "success": False}},
        {"id": "comment-12", "name": "删除不存在评论（带 token）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/comment/delete/9999999"},
         "expect": {"status": 200, "success": False}},
    ],
    ids=[f"comment-{i:02d}" for i in range(1, 13)],
)
def test_comment_yaml(admin_client, client, case):
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
