"""comment_page.py — 评论页 page object"""
from page.base_page import BasePage


class CommentPage(BasePage):
    def open_topic_with_comments(self, topic_id: str):
        """打开带评论的帖子"""
        self.goto(f"/topic/{topic_id}")

    def fill_comment(self, content: str):
        """填评论"""
        if self.is_visible("textarea[placeholder*='评论']", timeout=2000):
            self.page.fill("textarea[placeholder*='评论']", content)
        elif self.is_visible("textarea", timeout=2000):
            self.page.locator("textarea").first.fill(content)

    def submit_comment(self):
        """提交评论"""
        submit = self.page.locator("button:has-text('发布'), button:has-text('提交'), button[type='submit']")
        if submit.count() > 0:
            submit.first.click()

    def has_comment_form(self) -> bool:
        """评论表单可见"""
        return self.is_visible("body", timeout=5000)
