"""search_page.py — 搜索页 page object"""
from page.base_page import BasePage


class SearchPage(BasePage):
    def open(self, query: str = ""):
        """打开搜索页"""
        if query:
            self.goto(f"/search?q={query}")
        else:
            self.goto("/search")

    def search(self, keyword: str):
        """执行搜索"""
        self.open(keyword)

    def has_results(self) -> bool:
        """搜索结果存在"""
        return self.is_visible("body", timeout=5000)

    def has_empty_state(self) -> bool:
        """空状态"""
        empty = self.page.locator("text=/暂无|没有|未找到|empty/i")
        return empty.count() > 0
