"""base_page.py — 通用 page object（其他 page 继承）"""
from playwright.sync_api import Page

from common.utils import full_url


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, path: str):
        self.page.goto(full_url(path))

    def get_title(self) -> str:
        return self.page.title()

    def text(self, selector: str) -> str:
        return self.page.text_content(selector) or ""

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_url(self, path: str, timeout: int = 10000):
        self.page.wait_for_url(full_url(path), timeout=timeout)

    def screenshot(self, name: str):
        self.page.screenshot(path=f"reports/screenshots/{name}.png", full_page=True)
