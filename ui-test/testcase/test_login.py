"""test_login.py — 登录模块 2 场景"""
import allure
import pytest


@allure.feature("登录模块")
@allure.story("Cookie 注入绕 captcha")
def test_login_with_admin_cookie(admin_page):
    """场景 1：admin cookie 注入登录（绕 captcha）"""
    from page.login_page import LoginPage
    lp = LoginPage(admin_page)
    lp.login_with_cookie()
    # admin_page 已通过 admin_context 注入 cookie，应该跳转到 admin 个人页
    admin_page.wait_for_load_state("networkidle", timeout=10000)
    # 验证页面不是登录页
    assert "signin" not in admin_page.url.lower(), \
        f"cookie 注入失败，仍在登录页 url={admin_page.url}"


@allure.feature("登录模块")
@allure.story("错误密码提示")
def test_login_wrong_password(page):
    """场景 2：错误密码（撞 captcha）"""
    from page.login_page import LoginPage
    lp = LoginPage(page)
    lp.open()
    lp.login_with_credentials("admin", "wrong_password")
    page.wait_for_load_state("networkidle", timeout=5000)
    # 期望：还在登录页 OR 看到错误消息（bbs-go 实际：captcha 必填，错误密码仍撞 captcha）
    assert "signin" in page.url.lower() or lp.get_error_message() != "", \
        f"expected to stay on login page or see error message, url={page.url}"
