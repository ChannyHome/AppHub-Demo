-- AppHub init.sql (clean)
-- 목표: 한 번 실행로 DB + tables + seed 생성, 재실행에도 안전(대부분 IF NOT EXISTS)

CREATE DATABASE IF NOT EXISTS `AppHub`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE `AppHub`;

SET FOREIGN_KEY_CHECKS=0;

-- 1) roles
CREATE TABLE IF NOT EXISTS `roles` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `role_rank` int NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 2) users (FK -> roles)
CREATE TABLE IF NOT EXISTS `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `knox_id` varchar(64) NOT NULL,
  `name` varchar(80) NOT NULL,
  `dept_name` varchar(120) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `role_id` bigint NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `knox_id` (`knox_id`),
  KEY `fk_users_role` (`role_id`),
  CONSTRAINT `fk_users_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3) app_categories
CREATE TABLE IF NOT EXISTS `app_categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `key` varchar(32) NOT NULL,
  `name` varchar(80) NOT NULL,
  `description` text,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 4) apps (FK -> app_categories, users)
CREATE TABLE IF NOT EXISTS `apps` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `category_id` bigint NOT NULL,
  `app_key` varchar(80) NOT NULL,
  `name` varchar(120) NOT NULL,
  `summary` varchar(255) DEFAULT NULL,
  `description` text,
  `icon` varchar(512) DEFAULT NULL,
  `manual` varchar(512) DEFAULT NULL,
  `voc` varchar(512) DEFAULT NULL,
  `app_kind` enum('native','web') NOT NULL,
  `web_launch_url` varchar(512) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `requires_app_approval` tinyint(1) NOT NULL DEFAULT '0',
  `latest_version_id` bigint DEFAULT NULL,
  `created_by` bigint NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_key` (`app_key`),
  KEY `fk_apps_category` (`category_id`),
  KEY `fk_apps_created_by` (`created_by`),
  CONSTRAINT `fk_apps_category` FOREIGN KEY (`category_id`) REFERENCES `app_categories` (`id`),
  CONSTRAINT `fk_apps_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 5) app_versions (FK -> apps, users)
CREATE TABLE IF NOT EXISTS `app_versions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app_id` bigint NOT NULL,
  `version` varchar(40) NOT NULL,
  `release_note_short` varchar(400) DEFAULT NULL,
  `release_note_long` mediumtext,
  `released_at` datetime DEFAULT NULL,
  `released_by` bigint NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_versions_released_by` (`released_by`),
  KEY `ix_versions_app_released_at` (`app_id`,`released_at`),
  KEY `ix_versions_app_version` (`app_id`,`version`),
  CONSTRAINT `fk_versions_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_versions_released_by` FOREIGN KEY (`released_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 6) app_artifacts (FK -> app_versions)
CREATE TABLE IF NOT EXISTS `app_artifacts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app_version_id` bigint NOT NULL,
  `os` varchar(20) NOT NULL DEFAULT 'windows',
  `arch` varchar(20) NOT NULL DEFAULT 'x86',
  `package_type` enum('zip','msi','exe') NOT NULL,
  `storage_type` enum('ftp','local') NOT NULL,
  `storage_path` varchar(1000) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_size` bigint NOT NULL,
  `sha256` char(64) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_artifacts_version` (`app_version_id`),
  CONSTRAINT `fk_artifacts_version` FOREIGN KEY (`app_version_id`) REFERENCES `app_versions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 7) category_access (FK -> users, app_categories)
CREATE TABLE IF NOT EXISTS `category_access` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `category_id` bigint NOT NULL,
  `status` enum('pending','approved','rejected','revoked') NOT NULL,
  `requested_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `approved_by` bigint DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `note` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_cat_access_user_category` (`user_id`,`category_id`),
  KEY `fk_cat_access_category` (`category_id`),
  KEY `fk_cat_access_approved_by` (`approved_by`),
  CONSTRAINT `fk_cat_access_approved_by` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_cat_access_category` FOREIGN KEY (`category_id`) REFERENCES `app_categories` (`id`),
  CONSTRAINT `fk_cat_access_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 8) app_access (FK -> users, apps)
CREATE TABLE IF NOT EXISTS `app_access` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `app_id` bigint NOT NULL,
  `status` enum('pending','approved','rejected','revoked') NOT NULL,
  `requested_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `approved_by` bigint DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `note` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_app_access_user_app` (`user_id`,`app_id`),
  KEY `fk_app_access_app` (`app_id`),
  KEY `fk_app_access_approved_by` (`approved_by`),
  CONSTRAINT `fk_app_access_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_app_access_approved_by` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_app_access_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 9) favorites (PK user_id+app_id, FK -> users, apps)
CREATE TABLE IF NOT EXISTS `favorites` (
  `user_id` bigint NOT NULL,
  `app_id` bigint NOT NULL,
  `sort_order` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`app_id`),
  KEY `fk_fav_app` (`app_id`),
  CONSTRAINT `fk_fav_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_fav_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 10) home_tiles (FK -> users, apps)
CREATE TABLE IF NOT EXISTS `home_tiles` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `app_id` bigint NOT NULL,
  `zone` enum('installed_zone') NOT NULL,
  `pos_x` int NOT NULL,
  `pos_y` int NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tiles_user_zone_pos` (`user_id`,`zone`,`pos_x`,`pos_y`),
  UNIQUE KEY `uq_tiles_user_zone_app` (`user_id`,`zone`,`app_id`),
  KEY `fk_tiles_app` (`app_id`),
  CONSTRAINT `fk_tiles_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_tiles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 11) user_app_state (PK user_id+app_id, FK -> users, apps)
CREATE TABLE IF NOT EXISTS `user_app_state` (
  `user_id` bigint NOT NULL,
  `app_id` bigint NOT NULL,
  `installed` tinyint(1) NOT NULL DEFAULT '0',
  `installed_version` varchar(40) DEFAULT NULL,
  `last_download_at` datetime DEFAULT NULL,
  `last_update_at` datetime DEFAULT NULL,
  `last_launch_at` datetime DEFAULT NULL,
  `last_seen_at` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`,`app_id`),
  KEY `fk_state_app` (`app_id`),
  CONSTRAINT `fk_state_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_state_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 12) hub_events (FK -> users)
CREATE TABLE IF NOT EXISTS `hub_events` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `occurred_at` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `event_type` enum('page_open','search','filter_change','sort_change','open_notice','open_app_detail','open_permission_request','app_action') NOT NULL,
  `page` enum('home','apps','upload','library','permission','notices') NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `meta_json` json DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_hub_events_user` (`user_id`),
  CONSTRAINT `fk_hub_events_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 13) hub_daily_metrics
CREATE TABLE IF NOT EXISTS `hub_daily_metrics` (
  `metric_date` date NOT NULL,
  `dau` int NOT NULL,
  `page_open_count` int NOT NULL,
  `search_count` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`metric_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 14) jobs (FK -> users)
CREATE TABLE IF NOT EXISTS `jobs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `job_type` enum('download','update','upload') NOT NULL,
  `status` enum('queued','running','success','failed','canceled') NOT NULL,
  `progress` int NOT NULL DEFAULT '0',
  `message` varchar(1000) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `started_at` datetime DEFAULT NULL,
  `finished_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_jobs_user` (`user_id`),
  CONSTRAINT `fk_jobs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 15) job_items (FK -> jobs, apps, app_versions, app_artifacts)
CREATE TABLE IF NOT EXISTS `job_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `job_id` bigint NOT NULL,
  `app_id` bigint NOT NULL,
  `app_version_id` bigint DEFAULT NULL,
  `artifact_id` bigint DEFAULT NULL,
  `progress` int NOT NULL DEFAULT '0',
  `message` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_job_items_job` (`job_id`),
  KEY `fk_job_items_app` (`app_id`),
  KEY `fk_job_items_version` (`app_version_id`),
  KEY `fk_job_items_artifact` (`artifact_id`),
  CONSTRAINT `fk_job_items_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_job_items_artifact` FOREIGN KEY (`artifact_id`) REFERENCES `app_artifacts` (`id`),
  CONSTRAINT `fk_job_items_job` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`),
  CONSTRAINT `fk_job_items_version` FOREIGN KEY (`app_version_id`) REFERENCES `app_versions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 16) notices (FK -> app_categories, apps, users)
CREATE TABLE IF NOT EXISTS `notices` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `scope` enum('all','apphub','category','app') NOT NULL,
  `category_id` bigint DEFAULT NULL,
  `app_id` bigint DEFAULT NULL,
  `title` varchar(200) NOT NULL,
  `body` mediumtext NOT NULL,
  `kind` enum('release','upload','maintenance','manual','general') NOT NULL,
  `start_at` datetime DEFAULT NULL,
  `end_at` datetime DEFAULT NULL,
  `priority` int NOT NULL DEFAULT '0',
  `created_by` bigint NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_notices_category` (`category_id`),
  KEY `fk_notices_app` (`app_id`),
  KEY `fk_notices_created_by` (`created_by`),
  CONSTRAINT `fk_notices_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_notices_category` FOREIGN KEY (`category_id`) REFERENCES `app_categories` (`id`),
  CONSTRAINT `fk_notices_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 17) app_run_sessions (FK -> users, apps)
CREATE TABLE IF NOT EXISTS `app_run_sessions` (
  `id` char(36) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  `knox_id_raw` varchar(64) DEFAULT NULL,
  `app_id` bigint NOT NULL,
  `app_version` varchar(40) NOT NULL,
  `started_at` datetime NOT NULL,
  `ended_at` datetime DEFAULT NULL,
  `exit_code` int DEFAULT NULL,
  `end_reason` enum('user_exit','crash','killed','unknown') NOT NULL DEFAULT 'unknown',
  `client_ip` varchar(64) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_run_sessions_user` (`user_id`),
  KEY `fk_run_sessions_app` (`app_id`),
  CONSTRAINT `fk_run_sessions_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_run_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 18) app_action_events (FK -> app_run_sessions)
CREATE TABLE IF NOT EXISTS `app_action_events` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `session_id` char(36) NOT NULL,
  `occurred_at` datetime NOT NULL,
  `action_type` varchar(50) NOT NULL,
  `action_name` varchar(120) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `duration_ms` bigint DEFAULT NULL,
  `severity` enum('info','warn','error') NOT NULL DEFAULT 'info',
  `meta_json` json DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_action_session` (`session_id`),
  CONSTRAINT `fk_action_session` FOREIGN KEY (`session_id`) REFERENCES `app_run_sessions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 19) app_daily_metrics (FK -> apps)
CREATE TABLE IF NOT EXISTS `app_daily_metrics` (
  `metric_date` date NOT NULL,
  `app_id` bigint NOT NULL,
  `unique_users` int NOT NULL,
  `launch_count` int NOT NULL,
  `total_runtime_sec` bigint NOT NULL,
  `action_count` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`metric_date`,`app_id`),
  KEY `fk_app_daily_app` (`app_id`),
  CONSTRAINT `fk_app_daily_app` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------
-- Seed data (safe-ish)
-- --------------------
INSERT IGNORE INTO `roles` (`id`, `name`, `role_rank`, `description`) VALUES
  (1, 'Guest', 10, 'Guest (카테고리 권한 없으면 비활성 표시)'),
  (2, 'User', 20, 'User (승인된 카테고리/앱 사용)'),
  (3, 'Developer', 30, 'Developer (업로드 가능, 카테고리 제한 없음)'),
  (4, 'Maintainer', 40, 'Maintainer (카테고리/권한/공지 관리)'),
  (5, 'Admin', 50, 'Admin (전체 권한)');

INSERT IGNORE INTO `users` (`id`, `knox_id`, `name`, `dept_name`, `description`, `role_id`, `is_active`) VALUES
  (1, 'ck412.park', '박찬경', '공정혁신팀', 'Seeded admin account', 5, 1);

INSERT IGNORE INTO `app_categories` (`id`, `key`, `name`, `description`, `is_active`) VALUES
  (1, 'hawk', 'Hawk', 'Hawk category', 1),
  (2, 'whaat', 'Whaat', 'Whaat category', 1);

INSERT IGNORE INTO `apps` (`id`, `category_id`, `app_key`, `name`, `summary`, `description`, `icon`, `manual`, `voc`, `app_kind`, `web_launch_url`, `is_active`, `requires_app_approval`, `latest_version_id`, `created_by`) VALUES
  (1, 1, 'hawk.wmo', 'WMO', 'WMO Tool', NULL, NULL, NULL, NULL, 'native', NULL, 1, 1, NULL, 1),
  (2, 2, 'whaat.viewer', 'Viewer', 'Viewer Tool', NULL, NULL, NULL, NULL, 'web', NULL, 1, 0, NULL, 1);

SET FOREIGN_KEY_CHECKS=1;
