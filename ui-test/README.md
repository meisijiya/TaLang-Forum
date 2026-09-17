# bbs-go UI 自动化测试

**版本**：#46a 重写（2026-09-17）
**场景数**：12 场景 / 6 模块
**技术栈**：pytest 8.3.3 + Playwright 1.60 + allure-pytest

## 模块分布

| 模块 | 场景数 | 测试文件 |
|---|---|---|
| 登录 (login) | 2 | testcase/test_login.py |
| 板块 (section) | 2 | testcase/test_section.py |
| 帖子 (topic) | 2 | testcase/test_topic.py |
| 评论 (comment) | 2 | testcase/test_comment.py |
| 搜索 (search) | 2 | testcase/test_search.py |
| 个人主页 (profile) | 2 | testcase/test_profile.py |
| **合计** | **12** | 6 files |

## 快速开始

### 1. 安装依赖
```bash
cd ui-test
pip install -r requirements.txt
playwright install chromium
```

### 2. 设置环境变量
```bash
# 必填：admin token（注入 cookie 绕 captcha）
export BBS_GO_ADMIN_TOKEN="<admin_token>"

# 可选：自定义 base URL
export BBS_GO_BASE_URL="http://127.0.0.1:8081"
```

### 3. 跑测试
```bash
# 单跑 pytest
python -m pytest testcase/ -v

# pytest + allure 结果
python -m pytest testcase/ -v --alluredir=reports/allure-results --clean-alluredir

# 有头模式（debug 用）
./scripts/run_ui.sh test-headed

# 一键 test + report
./scripts/run_ui.sh all
```

## captcha 处理策略

bbs-go 登录强制 captcha。**本 UI 测试用 cookie 注入绕 captcha**（#16 决策）：

1. **base/browser.py** 的 `admin_context` fixture 自动注入 `bbsgo_token` cookie 到 storage_state
2. **admin_page fixture** 用 admin_context 创建 page，所有需要登录的 UI 测试用 admin_page
3. **conftest.py** 的 `admin_client` fixture 提供带 token 的 API client（用于 form fallback API 创建测试数据）

## 设计模式

- **base/browser.py**：sync_playwright + admin_context（cookie 注入）+ admin_page（带 cookie page）
- **page/objects**：8 个 page object 封装 locator 操作
- **testcase/**：6 个 test_*.py，每个 2 场景
- **API fallback**：部分场景用 admin_client 调 API 创建测试数据（如创建帖子再访问详情），避免 form submit 撞 captcha

## 已知坑

- **Playwright Chromium 二进制**：`playwright install chromium` 必跑；网络阻塞时手动下载
- **cookie 注入仅绕登录 captcha**：发帖/评论 captcha 是服务端决策，form submit 必撞；用 API fallback
- **页面加载超时**：默认 10s，`wait_for_load_state("networkidle")` 等异步渲染

## CI 接入

GitHub Actions workflow：`.github/workflows/ui-test.yml`（v3 已落地，不动）
- `working-directory: ui-test`
- `pip install -r requirements.txt`
- `playwright install --with-deps chromium`
- `export BBS_GO_ADMIN_TOKEN=$(...)`
- `python -m pytest testcase/ -v --alluredir=reports/allure-results`
- allure generate + upload artifact
