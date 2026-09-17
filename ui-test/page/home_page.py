"""home_page.py — 首页 page object"""
from page.base_page import BasePage


class HomePage(BasePage):
    def open(self):
        self.goto("/")

    def is_loaded(self) -> bool:
        """首页已加载（body 可见）"""
        return self.is_visible("body", timeout=5000)

    def has_topic_link(self) -> bool:
        """首页有帖子链接"""
        return self.is_visible("a[href*='/topic/']", timeout=3000)

    def get_topic_count(self) -> int:
        """获取首页帖子链接数"""
        return self.page.locator("a[href*='/topic/']").count()
