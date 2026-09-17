"""bbs-go 接口测试共享配置"""
import os

BBS_GO_BASE_URL = os.getenv("BBS_GO_BASE_URL", "http://127.0.0.1:8081")
BBS_GO_ADMIN_USERNAME = os.getenv("BBS_GO_ADMIN_USERNAME", "admin")
BBS_GO_ADMIN_PASSWORD = os.getenv("BBS_GO_ADMIN_PASSWORD", "Test@12345")
BBS_GO_ADMIN_TOKEN = os.getenv("BBS_GO_ADMIN_TOKEN", "")
BBS_GO_ADMIN_OBFUSCATED_ID = "8EqSDhrQDK4"  # admin user id (idCodec obfuscated)

# 通用测试数据
BBS_GO_TEST_USER_PREFIX = "apitest_"
BBS_GO_TEST_TOPIC_TITLE = "[apitest] auto-generated topic"
BBS_GO_TEST_COMMENT_CONTENT = "[apitest] auto-generated comment"
