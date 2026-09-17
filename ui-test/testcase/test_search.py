"""test_search.py — 搜索模块 2 场景"""
import allure


@allure.feature("搜索模块")
@allure.story("关键词搜索")
def test_search_keyword(page):
    """场景 1：搜索关键词"""
    from page.search_page import SearchPage
    sp = SearchPage(page)
    sp.search("apitest")
    page.wait_for_load_state("networkidle", timeout=10000)
    assert sp.has_results(), "搜索结果页加载失败"


@allure.feature("搜索模块")
@allure.story("空状态搜索")
def test_search_empty(page):
    """场景 2：搜索无结果状态"""
    from page.search_page import SearchPage
    sp = SearchPage(page)
    sp.search("zzz_nonexistent_keyword_xyz_99999")
    page.wait_for_load_state("networkidle", timeout=10000)
    assert sp.has_results(), "空状态搜索页加载失败"
