# bbs-go Locust 性能测试

M3 性能链起点 — 验证整条性能链路可行 + 出第一份压测报告。

## 目录结构

```
perf/
├── locustfile.py        # 主压测脚本
├── requirements.txt     # 依赖（locust + requests + pyyaml）
├── README.md            # 本文档
├── scripts/
│   └── run_perf.sh      # 一键启动脚本
└── reports/
    └── 19a-evidence/    # 本次 100 用户报告归档
```

## 快速开始

```bash
cd perf
python -m pip install -r requirements.txt
```

### Web UI 模式（推荐本地调试）

```bash
./scripts/run_perf.sh
# 浏览器打开 http://localhost:8089，配置 Users / Spawn rate / Host
```

### Headless 模式（CI 友好）

```bash
# 100 用户 / 10 ramp / 60s 一键
./scripts/run_perf.sh headless 100 10 60s

# 自定义：500 用户 / 50 ramp / 5min
./scripts/run_perf.sh headless 500 50 300s
```

## 环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `BBS_GO_BASE_URL` | `http://127.0.0.1:8081` | bbs-go 服务地址 |
| `BBS_GO_ADMIN_TOKEN` | （从 MySQL 拿） | admin 用户 token；优先用 env var，未设则 docker exec 拿 freshest |

## 任务清单（#19a 单场景）

| 任务 | 权重 | 端点 | 鉴权 |
|---|---|---|---|
| login_attempt | 1 | POST /api/login/signin | 无（期望 captcha 失败） |
| list_categories | 3 | GET /api/topic/categories | 无 |
| current_user | 1 | GET /api/user/current | 需 Authorization 头 |

## 关键指标（Locust 自动采集）

- 总请求数
- 失败数 / 失败率
- 中位数响应时间 / P95 / P99
- RPS（每请求数/秒）
- 各 endpoint 单独统计

## 报告归档

每次 headless 运行生成 3 类产物（落 `reports/19a-evidence/`）：

- `locust-login-<timestamp>.html` — Web 报告（人读）
- `locust-login-<timestamp>_stats.csv` — 端点统计（CSV）
- `locust-login-<timestamp>.log` — stdout 全量日志（机读）

## 后续工单

- **#19b** Locust 3 场景（登录 / 帖子查询 / 发帖）+ 阶梯加压
- **#19c** 瓶颈调优（Go runtime / DB 连接池 / Redis 缓存 / SQL 索引 四选一）+ 完整性能报告