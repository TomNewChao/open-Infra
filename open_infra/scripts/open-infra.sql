-- MySQL dump 10.13  Distrib 8.0.29, for Linux (x86_64)
--
-- Host: localhost    Database: open_infra
-- ------------------------------------------------------
-- Server version	8.0.29

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alarm`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `alarm` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `alarm_id` int NOT NULL,
  `alarm_level` int NOT NULL,
  `alarm_module` int NOT NULL,
  `alarm_name` varchar(64) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `alarm_details` longtext COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `alarm_md5` varchar(64) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `is_recover` tinyint(1) NOT NULL,
  `alarm_happen_time` datetime(6) NOT NULL,
  `alarm_recover_time` datetime(6) DEFAULT NULL,
  `alarm_refresh_time` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `alarm_alarm_md5_2c312216` (`alarm_md5`)
) ENGINE=InnoDB AUTO_INCREMENT=960 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alarm_notify`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `alarm_notify` (
  `create_time` datetime(6) NOT NULL,
  `id` bigint NOT NULL AUTO_INCREMENT,
  `email` varchar(254) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `phone_number` varchar(20) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `desc` varchar(255) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone_number` (`phone_number`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alarm_notify_strategy`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `alarm_notify_strategy` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `alarm_name` int NOT NULL,
  `alarm_keywords` varchar(255) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `alarm_notify_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `alarm_notify_strateg_alarm_notify_id_b657903c_fk_alarm_not` (`alarm_notify_id`),
  CONSTRAINT `alarm_notify_strateg_alarm_notify_id_b657903c_fk_alarm_not` FOREIGN KEY (`alarm_notify_id`) REFERENCES `alarm_notify` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cpu_resource_utilization`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `cpu_resource_utilization` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(256) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `create_time` int DEFAULT NULL,
  `lower_cpu_count` int DEFAULT NULL,
  `medium_lower_cpu_count` int DEFAULT NULL,
  `medium_high_cpu_count` int DEFAULT NULL,
  `high_cpu_count` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=197 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_zh_0900_as_cs,
  `object_repr` varchar(200) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `session_data` longtext COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_account`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_account` (
  `id` int NOT NULL AUTO_INCREMENT,
  `account` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `ak` varchar(255) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `sk` varchar(255) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_bill_info`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_bill_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_cycle` varchar(16) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `account` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `resource_type_name` varchar(64) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `consume_amount` double NOT NULL,
  `discount_rate` double DEFAULT NULL,
  `actual_cost` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4210 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_eip_info`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_eip_info` (
  `id` varchar(64) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `eip` char(39) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `eip_status` int DEFAULT NULL,
  `eip_type` int DEFAULT NULL,
  `eip_zone` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `bandwidth_id` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `bandwidth_name` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `bandwidth_size` int DEFAULT NULL,
  `example_id` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `example_name` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `example_type` varchar(32) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  `refresh_time` datetime(6) NOT NULL,
  `account` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_high_risk_port`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_high_risk_port` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `port` int NOT NULL,
  `desc` varchar(255) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_obs_interact`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_obs_interact` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `community` varchar(16) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `user_id` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `password` varchar(64) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_project_info`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_project_info` (
  `id` varchar(64) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `zone` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `account_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `hw_cloud_project_info_account_id_89dd7cf8_fk_hw_cloud_account_id` (`account_id`),
  CONSTRAINT `hw_cloud_project_info_account_id_89dd7cf8_fk_hw_cloud_account_id` FOREIGN KEY (`account_id`) REFERENCES `hw_cloud_account` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_scan_eip_port_info`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_eip_port_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `eip` char(39) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `port` int NOT NULL,
  `status` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `link_protocol` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `transport_protocol` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `account` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `region` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `service_info` varchar(128) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `protocol` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_scan_eip_port_status`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_eip_port_status` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `account` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `status` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_scan_obs_anonymous_bucket`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_obs_anonymous_bucket` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `account` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `bucket` varchar(128) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `url` varchar(256) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_scan_obs_anonymous_bucket_status`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_obs_anonymous_bucket_status` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `account` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `status` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hw_cloud_scan_obs_anonymous_file`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `hw_cloud_scan_obs_anonymous_file` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `account` varchar(32) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `bucket` varchar(128) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `url` varchar(256) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `path` varchar(256) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `data` varchar(256) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=422 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kubeconfig_info`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `kubeconfig_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(64) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `role` varchar(16) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `service_name` varchar(128) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  `review_time` datetime(6) DEFAULT NULL,
  `modify_time` datetime(6) DEFAULT NULL,
  `expired_time` int DEFAULT NULL,
  `send_ok` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mem_resource_utilization`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `mem_resource_utilization` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(256) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `create_time` int DEFAULT NULL,
  `lower_mem_count` int DEFAULT NULL,
  `medium_lower_mem_count` int DEFAULT NULL,
  `medium_high_mem_count` int DEFAULT NULL,
  `high_mem_count` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=197 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_image`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `service_image` (
  `id` int NOT NULL AUTO_INCREMENT,
  `image` varchar(128) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `repository` varchar(128) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `branch` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `developer` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `email` varchar(254) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `base_image` varchar(128) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `base_os` varchar(128) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `pipline_url` varchar(256) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `num_download` int DEFAULT NULL,
  `size` varchar(32) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `cpu_limit` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `mem_limit` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `service_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `service_image_service_id_96ea0f8e_fk_service_info_id` (`service_id`),
  CONSTRAINT `service_image_service_id_96ea0f8e_fk_service_info_id` FOREIGN KEY (`service_id`) REFERENCES `service_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10586 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_info`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `service_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `service_name` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `namespace` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `cluster` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `region` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14047 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_sla`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `service_sla` (
  `id` int NOT NULL AUTO_INCREMENT,
  `url` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `service_alias` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `service_introduce` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `service_zone` varchar(64) COLLATE utf8mb4_zh_0900_as_cs DEFAULT NULL,
  `month_abnormal_time` double DEFAULT NULL,
  `year_abnormal_time` double DEFAULT NULL,
  `month_sla` double DEFAULT NULL,
  `year_sla` double DEFAULT NULL,
  `remain_time` double DEFAULT NULL,
  `service_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `service_sla_service_id_6c63d65f_fk_service_info_id` (`service_id`),
  CONSTRAINT `service_sla_service_id_6c63d65f_fk_service_info_id` FOREIGN KEY (`service_id`) REFERENCES `service_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1168 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `username` varchar(150) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `mobile` varchar(11) COLLATE utf8mb4_zh_0900_as_cs NOT NULL,
  `is_superuser` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users_groups`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `users_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_groups_user_id_group_id_fc7788e8_uniq` (`user_id`,`group_id`),
  KEY `users_groups_group_id_2f3517aa_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_groups_group_id_2f3517aa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_groups_user_id_f500bee5_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users_user_permissions`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `users_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_permissions_user_id_permission_id_3b86cbdf_uniq` (`user_id`,`permission_id`),
  KEY `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_permissions_user_id_92473840_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_zh_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-21  5:46:25
