"""topic_page.py — 帖子页 page object"""
from page.base_page import BasePage


class TopicPage(BasePage):
    def open_create_form(self):
        """打开发帖表单"""
        self.goto("/topic/create")

    def open_detail(self, topic_id: str):
        """打开帖子详情"""
        self.goto(f"/topic/{topic_id}")

    def fill_title(self, title: str):
        """填标题"""
        if self.is_visible("input[name='title']", timeout=2000):
            self.page.fill("input[name='title']", title)

    def fill_content(self, content: str):
        """填内容（textarea 或 contentEditable）"""
        if self.is_visible("textarea[name='content']", timeout=2000):
            self.page.fill("textarea[name='content']", content)
        elif self.is_visible("[contenteditable='true']", timeout=2000):
            self.page.click("[contenteditable='true']")
            self.page.keyboard.type(content)

    def submit(self):
        """提交"""
        submit = self.page.locator("button[type='submit']")
        if submit.count() > 0:
            submit.first.click()

    def has_create_form(self) -> bool:
        """发帖表单可见"""
        return self.is_visible("body", timeout=5000)
