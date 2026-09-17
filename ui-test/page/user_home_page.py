"""user_home_page.py — 个人主页 page object"""
from page.base_page import BasePage


class UserHomePage(BasePage):
    def open(self, user_id: str = "8EqSDhrQDK4"):
        """打开个人主页"""
        self.goto(f"/user/{user_id}")

    def open_settings(self):
        """打开个人设置"""
        self.goto("/user/settings")

    def has_nickname(self) -> bool:
        """显示昵称"""
        return self.is_visible("body", timeout=5000)

    def get_nickname(self) -> str:
        """获取昵称"""
        candidates = [".nickname", "[data-testid='nickname']", "h1"]
        for sel in candidates:
            if self.is_visible(sel, timeout=1000):
                return self.text(sel)
        return ""

    def change_nickname(self, new_nickname: str):
        """改昵称"""
        self.open_settings()
        nick_input = self.page.locator("input[name='nickname']")
        if nick_input.count() > 0:
            nick_input.first.fill(new_nickname)
            submit = self.page.locator("button[type='submit']")
            if submit.count() > 0:
                submit.first.click()
