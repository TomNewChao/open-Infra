/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80029
 Source Schema         : open_infra

 Target Server Type    : MySQL
 Target Server Version : 80029
 File Encoding         : 65001

 Date: 29/09/2022 19:04:04
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alarm
-- ----------------------------
CREATE TABLE IF NOT EXISTS `alarm`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT,
  `alarm_id` int(0) NOT NULL,
  `alarm_level` int(0) NOT NULL,
  `alarm_module` int(0) NOT NULL,
  `alarm_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `alarm_details` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `alarm_md5` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `is_recover` tinyint(1) NOT NULL,
  `alarm_happen_time` datetime(6) NOT NULL,
  `alarm_recover_time` datetime(6) NULL DEFAULT NULL,
  `alarm_refresh_time` datetime(6) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `alarm_alarm_md5_2c312216`(`alarm_md5`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 583 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alarm_notify
-- ----------------------------
CREATE TABLE IF NOT EXISTS `alarm_notify`  (
  `create_time` datetime(6) NOT NULL,
  `id` bigint(0) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `phone_number` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `desc` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `email`(`email`) USING BTREE,
  UNIQUE INDEX `phone_number`(`phone_number`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alarm_notify_strategy
-- ----------------------------
CREATE TABLE IF NOT EXISTS `alarm_notify_strategy`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT,
  `alarm_name` int(0) NOT NULL,
  `alarm_keywords` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `alarm_notify_id` bigint(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `alarm_notify_strateg_alarm_notify_id_b657903c_fk_alarm_not`(`alarm_notify_id`) USING BTREE,
  CONSTRAINT `alarm_notify_strateg_alarm_notify_id_b657903c_fk_alarm_not` FOREIGN KEY (`alarm_notify_id`) REFERENCES `alarm_notify` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 97 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
CREATE TABLE IF NOT EXISTS `auth_group`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
CREATE TABLE IF NOT EXISTS `auth_group_permissions`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `group_id` int(0) NOT NULL,
  `permission_id` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_group_permissions_group_id_permission_id_0cd325b0_uniq`(`group_id`, `permission_id`) USING BTREE,
  INDEX `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm`(`permission_id`) USING BTREE,
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
CREATE TABLE IF NOT EXISTS `auth_permission`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `content_type_id` int(0) NOT NULL,
  `codename` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_permission_content_type_id_codename_01ab375a_uniq`(`content_type_id`, `codename`) USING BTREE,
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 77 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
CREATE TABLE IF NOT EXISTS `django_admin_log`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `object_repr` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `action_flag` smallint(0) UNSIGNED NOT NULL,
  `change_message` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `content_type_id` int(0) NULL DEFAULT NULL,
  `user_id` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `django_admin_log_content_type_id_c4bce8eb_fk_django_co`(`content_type_id`) USING BTREE,
  INDEX `django_admin_log_user_id_c564eba6_fk_users_id`(`user_id`) USING BTREE,
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
CREATE TABLE IF NOT EXISTS `django_content_type`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `model` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `django_content_type_app_label_model_76bd3d3b_uniq`(`app_label`, `model`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 20 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
CREATE TABLE IF NOT EXISTS `django_migrations`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 87 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
CREATE TABLE IF NOT EXISTS `django_session`  (
  `session_key` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `session_data` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`) USING BTREE,
  INDEX `django_session_expire_date_a5c62663`(`expire_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_account
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_account`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `account` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `ak` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `sk` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 55 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_eip_info
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_eip_info`  (
  `id` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `eip` char(39) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `eip_status` int(0) NULL DEFAULT NULL,
  `eip_type` int(0) NULL DEFAULT NULL,
  `eip_zone` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `bandwidth_id` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `bandwidth_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `bandwidth_size` int(0) NULL DEFAULT NULL,
  `example_id` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `example_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `example_type` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  `account` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `refresh_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_high_risk_port
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_high_risk_port`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `port` int(0) NOT NULL,
  `desc` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 514 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_project_info
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_project_info`  (
  `id` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `zone` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `account_id` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `hw_cloud_project_info_account_id_89dd7cf8_fk_hw_cloud_account_id`(`account_id`) USING BTREE,
  CONSTRAINT `hw_cloud_project_info_account_id_89dd7cf8_fk_hw_cloud_account_id` FOREIGN KEY (`account_id`) REFERENCES `hw_cloud_account` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_scan_eip_port_info
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_eip_port_info`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `eip` char(39) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `port` int(0) NOT NULL,
  `status` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `link_protocol` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `transport_protocol` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `account` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `region` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `service_info` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `protocol` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_scan_eip_port_status
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_eip_port_status`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `account` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `status` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 17 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_scan_obs_anonymous_bucket
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_obs_anonymous_bucket`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `account` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `bucket` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `url` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_scan_obs_anonymous_bucket_status
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_obs_anonymous_bucket_status`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `account` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `status` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hw_cloud_scan_obs_anonymous_file
-- ----------------------------
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_obs_anonymous_file`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `account` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `bucket` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `url` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `path` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `data` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 823 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
CREATE TABLE IF NOT EXISTS `users`  (
  `password` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `last_login` datetime(6) NULL DEFAULT NULL,
  `username` varchar(150) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `first_name` varchar(150) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `last_name` varchar(150) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `email` varchar(254) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `id` int(0) NOT NULL,
  `mobile` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `is_superuser` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users_groups
-- ----------------------------
CREATE TABLE IF NOT EXISTS `users_groups`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `group_id` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `users_groups_user_id_group_id_fc7788e8_uniq`(`user_id`, `group_id`) USING BTREE,
  INDEX `users_groups_group_id_2f3517aa_fk_auth_group_id`(`group_id`) USING BTREE,
  CONSTRAINT `users_groups_group_id_2f3517aa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `users_groups_user_id_f500bee5_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users_user_permissions
-- ----------------------------
CREATE TABLE IF NOT EXISTS `users_user_permissions`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `permission_id` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `users_user_permissions_user_id_permission_id_3b86cbdf_uniq`(`user_id`, `permission_id`) USING BTREE,
  INDEX `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm`(`permission_id`) USING BTREE,
  CONSTRAINT `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `users_user_permissions_user_id_92473840_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

--
-- Table structure for table `kubeconfig_info`
--
CREATE TABLE IF NOT EXISTS `kubeconfig_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `email` varchar(254) NOT NULL,
  `role` varchar(16) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `review_time` datetime(6) DEFAULT NULL,
  `expired_time` int DEFAULT NULL,
  `send_ok` tinyint(1) DEFAULT NULL,
  `service_name` varchar(128) DEFAULT NULL,
  `modify_time` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

--
-- Table structure for table `service_info`
--
CREATE TABLE IF NOT EXISTS  `service_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_name` varchar(64) DEFAULT NULL,
  `service_alias` varchar(64) DEFAULT NULL,
  `url` varchar(200) DEFAULT NULL,
  `url_alias` varchar(200) DEFAULT NULL,
  `namespace` varchar(64) DEFAULT NULL,
  `cluster` varchar(64) DEFAULT NULL,
  `service_introduce` varchar(64) DEFAULT NULL,
  `community` varchar(16) DEFAULT NULL,
  `month_abnormal_time` double DEFAULT NULL,
  `year_abnormal_time` double DEFAULT NULL,
  `month_sla` double DEFAULT NULL,
  `year_sla` double DEFAULT NULL,
  `remain_time` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;


--
-- Table structure for table `hw_cloud_obs_interact`
--
CREATE TABLE IF NOT EXISTS `hw_cloud_obs_interact` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `community` varchar(16) NOT NULL,
  `user_id` varchar(32) NOT NULL,
  `password` varchar(64) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;


--
-- Table structure for table `hw_cloud_obs_interact`
--
CREATE TABLE IF NOT EXISTS `hw_cloud_bill_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bill_cycle` varchar(16) NOT NULL,
  `account` varchar(32) NOT NULL,
  `resource_type_name` varchar(64) NOT NULL,
  `consume_amount` double NOT NULL,
  `discount_rate` double DEFAULT NULL,
  `actual_cost` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
