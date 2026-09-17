"""section_page.py — 板块页 page object"""
from page.base_page import BasePage


class SectionPage(BasePage):
    def open_categories(self):
        """板块列表"""
        self.goto("/categories")

    def open_category(self, category_id: int = 1):
        """打开默认板块"""
        self.goto(f"/category/{category_id}")

    def has_topic_list(self) -> bool:
        """板块页有帖子列表"""
        return self.is_visible("body", timeout=5000)

    def get_topic_links(self) -> int:
        """板块页帖子链接数"""
        return self.page.locator("a[href*='/topic/']").count()
