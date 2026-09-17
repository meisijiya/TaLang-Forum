"""screenshot.py — UI 测试失败时自动截图"""
import os
from datetime import datetime
from pathlib import Path

import allure
import pytest


SCREENSHOTS_DIR = Path(__file__).parent.parent / "reports" / "screenshots"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.failed and "page" in item.fixturenames:
        try:
            page = item.funcargs["page"]
            SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = SCREENSHOTS_DIR / f"{item.name}_{ts}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            allure.attach.file(
                str(screenshot_path),
                name=f"failure-{item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            print(f"[WARN] failed to capture screenshot: {e}")
