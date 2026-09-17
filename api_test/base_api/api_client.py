"""ApiClient — 通用 HTTP 客户端封装（用于 bbs-go 接口测试）

设计原则：
1. 单例 Session 复用连接池
2. WinHTTP 代理硬约束（#14-1 教训）：trust_env=False 屏蔽 Windows 系统代理
3. 自动重试 500/502/503/504（#14 教程模式）
4. Allure @step 自动记录每个 HTTP 调用
5. Token 注入统一在 _headers()
"""
from __future__ import annotations

import os
from typing import Any, Optional

import allure
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ApiClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url or os.getenv("BBS_GO_BASE_URL", "http://127.0.0.1:8081")
        self.token = token or os.getenv("BBS_GO_ADMIN_TOKEN")
        self.session = requests.Session()
        # #14-1 教训：WinHTTP 代理硬约束；trust_env=False 防止 Windows 系统代理干扰
        self.session.trust_env = False
        retry = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = self.token
        return h

    @allure.step("POST {path}")
    def post(self, path: str, json_data: Any = None, **kwargs):
        if "json" not in kwargs:
            kwargs["json"] = json_data
        headers = kwargs.pop("headers", None) or self._headers()
        kwargs["headers"] = headers
        return self.session.post(f"{self.base_url}{path}", **kwargs)

    @allure.step("GET {path}")
    def get(self, path: str, **kwargs):
        kwargs.pop("json_data", None)  # tolerate legacy param, drop if passed
        kwargs.pop("json", None)  # GET doesn't accept json body
        headers = kwargs.pop("headers", None) or self._headers()
        kwargs["headers"] = headers
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    @allure.step("PUT {path}")
    def put(self, path: str, json_data: Any = None, **kwargs):
        if "json" not in kwargs:
            kwargs["json"] = json_data
        headers = kwargs.pop("headers", None) or self._headers()
        kwargs["headers"] = headers
        return self.session.put(f"{self.base_url}{path}", **kwargs)

    @allure.step("DELETE {path}")
    def delete(self, path: str, **kwargs):
        kwargs.pop("json_data", None)
        kwargs.pop("json", None)
        headers = kwargs.pop("headers", None) or self._headers()
        kwargs["headers"] = headers
        return self.session.delete(f"{self.base_url}{path}", **kwargs)

    def healthcheck(self) -> bool:
        try:
            r = self.get("/api/install/status")
            return r.status_code == 200 and r.json().get("data", {}).get("installed", False)
        except Exception:
            return False
