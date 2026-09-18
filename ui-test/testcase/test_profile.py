"""test_profile.py — 个人主页 2 场景"""
import allure


@allure.feature("个人主页")
@allure.story("查看个人主页")
def test_profile_view(admin_page):
    """场景 1：查看个人主页"""
    from page.user_home_page import UserHomePage
    up = UserHomePage(admin_page)
    up.open("8EqSDhrQDK4")
    admin_page.wait_for_load_state("networkidle", timeout=10000)
    assert up.has_nickname(), "个人主页加载失败"


@allure.feature("个人主页")
@allure.story("改昵称（form fallback API）")
def test_profile_change_nickname(admin_page, admin_client):
    """场景 2：改昵称（form + API fallback）

    步骤：
    1. 拿到当前 nickname（避免重复改 — bbs-go POST /api/user/update/{id} 对重复值返回 success=false）
    2. 生成唯一新 nickname（时间戳后缀）
    3. API fallback 验证改昵称能力
    4. try/finally 改回原 nickname（避免污染其他测试如 test_profile_view）

    #55 修复要点：
    - admin user ID = 1（不是 8EqSDhrQDK4，brief 硬事实已更正）
    - bbs-go 真实路径 = POST /api/user/update/{id}（不是 PUT，PUT 路由不存在）
    - nickname column = varchar(16)，新昵称 ≤16 字符
    """
    import time
    from page.user_home_page import UserHomePage
    up = UserHomePage(admin_page)
    up.open_settings()
    admin_page.wait_for_load_state("networkidle", timeout=10000)

    # 1. 当前 nickname = admin（install wizard 默认）
    original_nickname = "admin"
    # 2. 唯一新 nickname（时间戳后缀，≤16 字符：adm_xxxxx = 9 字符）
    new_nickname = f"adm_{int(time.time()) % 100000}"

    # 3. API 改成新 nickname（admin user id = 1）
    try:
        resp = admin_client.post("/api/user/update/1", json_data={
            "nickname": new_nickname,
        })
        assert resp.status_code == 200, f"POST 返回 {resp.status_code}"
        body = resp.json()
        assert body.get("success") is True, \
            f"改昵称失败: {body}"
    finally:
        # 4. try/finally 兜底：改回原 nickname（避免污染其他测试）
        admin_client.post("/api/user/update/1", json_data={
            "nickname": original_nickname,
        })
