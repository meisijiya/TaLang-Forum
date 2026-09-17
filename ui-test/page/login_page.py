"""login_page.py — 登录页 page object"""
from page.base_page import BasePage


class LoginPage(BasePage):
    def open(self):
        """打开登录页"""
        self.goto("/user/signin")

    def login_with_cookie(self):
        """用 admin cookie 注入登录（绕 captcha）—— 实际由 admin_context fixture 完成"""
        self.goto(f"/user/8EqSDhrQDK4")

    def is_login_form_visible(self) -> bool:
        """登录表单可见"""
        return self.is_visible("input[name='username']", timeout=3000)

    def get_error_message(self) -> str:
        """获取错误消息"""
        candidates = [".error", ".error-message", "[role='alert']", ".text-red-500"]
        for sel in candidates:
            if self.is_visible(sel, timeout=1000):
                return self.text(sel)
        return ""

    def login_with_credentials(self, username: str, password: str):
        """用户名+密码登录（撞 captcha）

        策略：仅尝试 fill 表单（短超时），失败则视为「无法通过 UI 登录」（captcha 拦截）
        """
        if not self.is_login_form_visible():
            return
        try:
            self.page.fill("input[name='username']", username, timeout=3000)
            self.page.fill("input[name='password']", password, timeout=3000)
        except Exception:
            # 字段不可见（动画/遮罩），跳过
            return
        # captcha 字段强制；尝试短超时 fill
        captcha = self.page.locator("input[name='captchaCode']")
        if captcha.count() > 0:
            try:
                captcha.first.fill("9999", timeout=2000)
            except Exception:
                pass
        submit = self.page.locator("button[type='submit']")
        if submit.count() > 0:
            try:
                submit.first.click(timeout=2000)
            except Exception:
                pass
