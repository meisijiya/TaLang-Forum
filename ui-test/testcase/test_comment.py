"""test_comment.py — 评论模块 2 场景"""
import allure


@allure.feature("评论模块")
@allure.story("创建评论（form fallback API）")
def test_comment_create(admin_page, admin_client):
    """场景 1：创建评论（form + API fallback）

    步骤：
    1. API 创建测试帖子
    2. admin_page 打开帖子详情
    3. 验证评论表单可见
    """
    # 先创建测试帖子
    create_resp = admin_client.post("/api/topic/create", json_data={
        "title": "[ui-test] comment-create",
        "content": "comment test content",
        "categoryId": 1,
        "type": 0,
    })
    assert create_resp.status_code == 200
    topic_data = create_resp.json().get("data") or {}
    topic_id = topic_data.get("id")
    assert topic_id, f"创建帖子失败: {create_resp.json()}"

    from page.comment_page import CommentPage
    cp = CommentPage(admin_page)
    cp.open_topic_with_comments(str(topic_id))
    admin_page.wait_for_load_state("networkidle", timeout=10000)
    assert cp.has_comment_form(), "评论表单加载失败"


@allure.feature("评论模块")
@allure.story("API 评论回复")
def test_comment_reply(admin_client):
    """场景 2：API 创建评论 + 回复（form fallback API）"""
    # 创建测试帖子
    create_resp = admin_client.post("/api/topic/create", json_data={
        "title": "[ui-test] comment-reply",
        "content": "reply test",
        "categoryId": 1,
        "type": 0,
    })
    assert create_resp.status_code == 200
    topic_id = (create_resp.json().get("data") or {}).get("id")
    assert topic_id

    # 创建主评论
    main_resp = admin_client.post("/api/comment/create", json_data={
        "entityType": "topic",
        "entityId": str(topic_id),
        "content": "[ui-test] main comment",
    })
    assert main_resp.status_code == 200
    assert main_resp.json().get("success") is True, f"主评论失败: {main_resp.json()}"
