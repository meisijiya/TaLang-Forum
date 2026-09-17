"""test_section.py — 板块模块 2 场景"""
import allure


@allure.feature("板块模块")
@allure.story("板块列表")
def test_section_list(page):
    """场景 1：板块列表页加载"""
    from page.section_page import SectionPage
    sp = SectionPage(page)
    sp.open_categories()
    page.wait_for_load_state("networkidle", timeout=10000)
    assert sp.has_topic_list(), "板块列表页加载失败"


@allure.feature("板块模块")
@allure.story("板块详情")
def test_section_detail(page):
    """场景 2：板块详情页加载"""
    from page.section_page import SectionPage
    sp = SectionPage(page)
    sp.open_category(1)
    page.wait_for_load_state("networkidle", timeout=10000)
    assert sp.has_topic_list(), "板块详情页加载失败"
