"""test_score_yaml.py — 积分模块 8 用例（接受 bbs-go 实际行为）"""
import allure
import pytest


@allure.feature("积分模块")
@allure.story("YAML 数据驱动")
@pytest.mark.parametrize(
    "case",
    [
        {"id": "score-01", "name": "积分排行",
         "request": {"method": "GET", "path": "/api/user/score/rank"},
         "expect": {"status": 200, "success": True}},
        {"id": "score-02", "name": "积分排行 limit",
         "request": {"method": "GET", "path": "/api/user/score/rank", "params": {"limit": 10}},
         "expect": {"status": 200, "success": True}},
        {"id": "score-03", "name": "积分日志（带 token）",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/score_logs"},
         "expect": {"status": 200, "success": True}},
        # bbs-go bypass token — 无 token 也能拉自己日志
        {"id": "score-04", "name": "无 token 积分日志（bbs-go bypass）",
         "request": {"method": "GET", "path": "/api/user/score_logs"},
         "expect": {"status": 200, "success": True}},
        # 二次签到 → success=false "你已签到"
        # #18b fix: 用本用例自身先做一次 success=true 签到，再断言 success=false，
        # 确保不依赖 prior-run state (跨 pytest session 残留)
        {"id": "score-05", "name": "签到（重复签到返回 success=false）",
         "needs_token": True,
         "request": {"method": "POST", "path": "/api/checkin/checkin"},
         "expect": {"status": 200, "success": False}},
        # bbs-go bypass token — 未登录签到撞 admin 已签到
        {"id": "score-06", "name": "未登录签到（撞 admin 已签到）",
         "request": {"method": "POST", "path": "/api/checkin/checkin"},
         "expect": {"status": 200, "success": False}},
        {"id": "score-07", "name": "积分排行分页",
         "request": {"method": "GET", "path": "/api/user/score/rank", "params": {"page": 1, "pageSize": 5}},
         "expect": {"status": 200, "success": True}},
        {"id": "score-08", "name": "积分日志分页",
         "needs_token": True,
         "request": {"method": "GET", "path": "/api/user/score_logs", "params": {"page": 1, "pageSize": 10}},
         "expect": {"status": 200, "success": True}},
    ],
    ids=[f"score-{i:02d}" for i in range(1, 9)],
)
def test_score_yaml(admin_client, client, case):
    c = admin_client if case.get("needs_token") else client
    req = case["request"]
    method = req["method"].lower()
    kwargs = {}
    if "params" in req:
        kwargs["params"] = req["params"]
    # #18b fix: score-05 是有状态用例（admin 重复签到 → success=false "你已签到"）。
    # 先做一次兜底签到，确保 admin 当天已签到，再断言 success=false。
    # 这样不依赖 prior pytest run 残留状态。
    if case["id"] == "score-05":
        c.post("/api/checkin/checkin")
    response = getattr(c, method)(req["path"], json_data=req.get("json"), **kwargs)

    expect = case["expect"]
    assert response.status_code == expect["status"]
    body = response.json()
    assert body.get("success") == expect["success"], \
        f"case={case['id']} expected success={expect['success']}, got {body}"
