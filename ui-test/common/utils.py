"""utils.py — UI 测试工具函数"""
import os

BBS_GO_BASE_URL = os.getenv("BBS_GO_BASE_URL", "http://127.0.0.1:8081")


def full_url(path: str) -> str:
    """拼接完整 URL（page.goto 不支持 base_url）"""
    if path.startswith("http"):
        return path
    return BBS_GO_BASE_URL.rstrip("/") + path
