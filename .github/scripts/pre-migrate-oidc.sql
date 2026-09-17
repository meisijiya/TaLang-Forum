-- #18 v3: OIDCIdentity 表预迁移
--
-- 绕开 #01 OIDCIdentity schema bug：
--   上游 mlogclub/bbs-go:latest 的 internal/models/models.go OIDCIdentity struct 用
--   `gorm:"size:512;not null;uniqueIndex:uk_oidc_issuer_subject"` 给 issuer / subject。
--   GORM AutoMigrate 在 MySQL 8.x + utf8mb4 下生成：
--     UNIQUE INDEX uk_oidc_issuer_subject (provider_key, issuer, subject)
--   索引长度 = (64 + 512 + 512) × 4 字节 = 4352 字节 > MySQL 3072 字节上限
--   → POST /api/install/install 在 InitDB → models.Models iteration 阶段
--     CREATE TABLE t_o_id_c_identity 报 Error 1071 (42000)，install 失败，10 张表后中止
--
-- 修法：在 install wizard 跑之前，先 DROP + CREATE 同名表（用更短的 VARCHAR(255)）
--   索引长度 = (64 + 255 + 255) × 4 = 2296 字节 < MySQL 3072 字节上限 ✓
--   GORM AutoMigrate 看到表已存在 → 跳过 t_o_id_c_identity → wizard 跑通
--
-- 表名注意：GORM NamingStrategy 把 OIDCIdentity 转 snake_case 成 o_id_c_identity
--   加 TablePrefix "t_" → t_o_id_c_identity（不是 t_oidc_identity）
--   本 SQL 必须用 GORM 生成的全名，否则 GORM 会试图 CREATE 新表又撞 1071
--
-- 列定义来源：本机 mlogclub/bbs-go:oidc255-fix 镜像 install 后实证
--   docker exec bbs-go-mysql-1 mysql -ubbsgo -pbbsgo_password bbsgo -e "SHOW CREATE TABLE t_o_id_c_identity\G"
--
-- 触发时机（workflow）：docker compose up -d mysql + 等 healthy → 跑本 SQL →
--                       docker compose up -d bbs-go → bbs-go 启动 install wizard → 通过

-- 防御：install wizard 未跑前 t_o_id_c_identity 必不存在；DROP IF EXISTS 是 no-op
-- 如表已存在（重复跑 SQL），DROP 会清掉但 GORM 还没碰过表，安全
DROP TABLE IF EXISTS `t_o_id_c_identity`;

CREATE TABLE `t_o_id_c_identity` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `provider_key` varchar(64) NOT NULL,
    `issuer` varchar(255) NOT NULL,
    `subject` varchar(255) NOT NULL,
    `user_id` bigint NOT NULL,
    `email` varchar(128) DEFAULT NULL,
    `nickname` varchar(64) DEFAULT NULL,
    `avatar` varchar(1024) DEFAULT NULL,
    `create_time` bigint DEFAULT NULL,
    `update_time` bigint DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_oidc_issuer_subject` (`provider_key`,`issuer`,`subject`),
    UNIQUE KEY `uk_oidc_user_provider` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
