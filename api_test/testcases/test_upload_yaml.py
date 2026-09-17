"""test_upload_yaml.py — 上传模块 4 用例"""
import allure
import pytest


@allure.feature("上传模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "upload-01", "name": "上传无文件（带 token）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/upload", "json": {}},
         "expect": {"status": 200, "success": False}},
        {"id": "upload-02", "name": "未登录上传",
         "request": {"method": "POST", "path": "/api/upload", "json": {"image": "dummy"}},
         "expect": {"status": 200, "success": False}},
        {"id": "upload-03", "name": "GET 上传端点",
         "request": {"method": "GET", "path": "/api/upload"},
         "expect": {"status": 404}},
        {"id": "upload-04", "name": "multipart 空表单",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/upload"},
         "expect": {"status": 200, "success": False}},
    ],
    ids=[f"upload-{i:02d}" for i in range(1, 5)],
)
def test_upload_yaml(admin_client, client, case):
    c = admin_client if case.get("needs_token") else client
    req = case["request"]
    method = req["method"].lower()
    if "json" in req:
        response = getattr(c, method)(req["path"], json_data=req.get("json"))
    else:
        response = getattr(c, method)(req["path"])

    expect = case["expect"]
    if expect["status"] == 404:
        assert response.status_code == 404
        return
    assert response.status_code == expect["status"]
    body = response.json()
    assert body.get("success") == expect["success"], \
        f"case={case['id']} expected success={expect['success']}, got {body}"
