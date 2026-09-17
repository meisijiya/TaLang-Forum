# bbs-go API 自动化测试

**版本**：#46a 重写（2026-09-17）
**用例数**：85 用例 / 9 模块
**技术栈**：pytest 8.3.3 + requests + allure-pytest + PyYAML

## 模块分布

| 模块 | 用例数 | YAML 文件 |
|---|---|---|
| 登录 (login) | 8 | data/login.yaml |
| 用户 (user) | 12 | data/user.yaml |
| 板块 (section) | 10 | data/section.yaml |
| 帖子 (post) | 20 | data/post.yaml |
| 评论 (comment) | 12 | data/comment.yaml |
| 积分 (score) | 8 | data/score.yaml |
| 权限 (permission) | 6 | data/permission.yaml |
| 上传 (upload) | 4 | data/upload.yaml |
| Session | 5 | data/session.yaml |
| **合计** | **85** | 9 files |

## 快速开始

### 1. 安装依赖
```bash
cd api_test
pip install -r requirements.txt
```

### 2. 设置环境变量
```bash
# 可选：CI 时注入 admin token（绕过登录 captcha + 直接调需要登录的 API）
export BBS_GO_ADMIN_TOKEN="<your_admin_token>"

# 可选：自定义 base URL（默认 http://127.0.0.1:8081）
export BBS_GO_BASE_URL="http://127.0.0.1:8081"
```

### 3. 跑测试
```bash
# 单跑 pytest
python -m pytest testcases/ -v

# pytest + allure 结果
python -m pytest testcases/ -v --alluredir=reports/allure-results --clean-alluredir

# 一键 test + report
./scripts/run_api.sh all
```

## captcha 处理策略

bbs-go 强制 captcha，登录接口必填 `captchaId/captchaCode`。本测试用 2 种方式绕过：

1. **token 注入**：`BBS_GO_ADMIN_TOKEN` 环境变量（CI 由 workflow 注入；本地从 MySQL 查 freshest token）
2. **admin_client fixture**：自动用 token 注入 Authorization header

## 设计模式

- **base_api/api_client.py**：单例 Session + WinHTTP `trust_env=False` + 自动重试 500/502/503/504 + allure @step
- **YAML 数据驱动**：每个模块一个 YAML，parametrize 跑多场景
- **conftest.py**：client + admin_client fixture + failure-screenshot hook
- **conftest_yaml.py**：自动根据 `test_<name>_yaml.py` 加载 `data/<name>.yaml`

## 已知坑

- **WinHTTP 代理**：Windows Git Bash 跑 requests 会触发 WinHTTP 代理；`trust_env=False` 屏蔽
- **MySQL 警告**：`mysql: [Warning] Using a password on the command line interface can be insecure` 是 CLI 默认行为，不影响
- **404 vs 200**：bbs-go 大部分接口用 200 + `success: false` 表示业务失败，不是 HTTP 4xx

## CI 接入

GitHub Actions workflow：`.github/workflows/api-test.yml`（v3 已落地，不动）
- `working-directory: api_test`
- `pip install -r requirements.txt`
- `python -m pytest testcases/ -v --alluredir=reports/allure-results`
- allure generate + upload artifact
