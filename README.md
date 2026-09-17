![CI - API](https://github.com/meisijiya/TaLang-Forum/actions/workflows/api-test.yml/badge.svg)
![CI - UI](https://github.com/meisijiya/TaLang-Forum/actions/workflows/ui-test.yml/badge.svg)

# bbs-go (TaLang-Forum fork)

bbs-go 是一个轻量级社区和问答平台，适合搭建论坛、知识库和讨论社区。

> 本 fork（`meisijiya/TaLang-Forum`）由 `mlogclub/bbs-go` 派生，重点在 **pytest + allure 接口自动化 + playwright UI 自动化 + GitHub Actions CI**。

## 仓库地址

- 上游：[mlogclub/bbs-go](https://github.com/mlogclub/bbs-go)
- 本 fork：[meisijiya/TaLang-Forum](https://github.com/meisijiya/TaLang-Forum)

## CI 状态

| Workflow | 状态 | 说明 |
|---|---|---|
| API tests (pytest + allure) | ![CI - API](https://github.com/meisijiya/TaLang-Forum/actions/workflows/api-test.yml/badge.svg) | pytest 跑 api_test/testcases/ + allure 报告 |
| UI tests (playwright + allure) | ![CI - UI](https://github.com/meisijiya/TaLang-Forum/actions/workflows/ui-test.yml/badge.svg) | playwright 跑 ui-test/testcase/ + allure 报告 |

CI 当前状态：**待 #18 v2 完成阶段，oidc255-fix 镜像未推 GHCR，CI runner 拉镜像失败**。详见 `.scratch/bbs-go-issues/18-evidence/18-v2-evidence.md` §三 §四。

## 本地快速开始

```bash
# 复制 .env.example 到 .env（不入库）
cp .env.example .env

# 启动 bbs-go + MySQL（oidc255-fix 镜像本地构建/导入）
docker compose up -d
```

## 文档

- 工单与执行轨迹：`.scratch/bbs-go-issues/`
- AGENTS.md：项目级 AI 协作约定
- PROJECT_TARGET_BOOK.md：M1-M3 + M6 阶段目标 + DoD

## License

沿用上游 MIT。
