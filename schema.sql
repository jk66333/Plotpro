-- MySQL dump 10.13  Distrib 9.5.0, for macos15 (x86_64)
--
-- Host: localhost    Database: receipt_app
-- ------------------------------------------------------
-- Server version	9.5.0

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--


--
-- Table structure for table `commission_agent_entries`
--

DROP TABLE IF EXISTS `commission_agent_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commission_agent_entries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `commission_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `total_amount` double DEFAULT NULL,
  `at_agreement` double DEFAULT NULL,
  `at_registration` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `commission_id` (`commission_id`),
  CONSTRAINT `commission_agent_entries_ibfk_1` FOREIGN KEY (`commission_id`) REFERENCES `commissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `commission_agm_entries`
--

DROP TABLE IF EXISTS `commission_agm_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commission_agm_entries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `commission_id` int NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `total_amount` double DEFAULT NULL,
  `at_agreement` double DEFAULT NULL,
  `at_registration` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `commission_id` (`commission_id`),
  CONSTRAINT `commission_agm_entries_ibfk_1` FOREIGN KEY (`commission_id`) REFERENCES `commissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `commission_dgm_entries`
--

DROP TABLE IF EXISTS `commission_dgm_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commission_dgm_entries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `commission_id` int NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `total_amount` double DEFAULT NULL,
  `at_agreement` double DEFAULT NULL,
  `at_registration` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `commission_id` (`commission_id`),
  CONSTRAINT `commission_dgm_entries_ibfk_1` FOREIGN KEY (`commission_id`) REFERENCES `commissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `commission_gm_entries`
--

DROP TABLE IF EXISTS `commission_gm_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commission_gm_entries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `commission_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `total_amount` decimal(15,2) NOT NULL,
  `at_agreement` decimal(15,2) DEFAULT NULL,
  `at_registration` decimal(15,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_commission_id` (`commission_id`),
  KEY `idx_name` (`name`),
  CONSTRAINT `commission_gm_entries_ibfk_1` FOREIGN KEY (`commission_id`) REFERENCES `commissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `commission_srgm_entries`
--

DROP TABLE IF EXISTS `commission_srgm_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commission_srgm_entries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `commission_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `total_amount` decimal(15,2) NOT NULL,
  `at_agreement` decimal(15,2) DEFAULT NULL,
  `at_registration` decimal(15,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_commission_id` (`commission_id`),
  KEY `idx_name` (`name`),
  CONSTRAINT `commission_srgm_entries_ibfk_1` FOREIGN KEY (`commission_id`) REFERENCES `commissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `commissions`
--

DROP TABLE IF EXISTS `commissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plot_no` varchar(255) DEFAULT NULL,
  `sq_yards` double DEFAULT NULL,
  `original_price` double DEFAULT NULL,
  `negotiated_price` double DEFAULT NULL,
  `advance_received` double DEFAULT NULL,
  `agent_commission_rate` double DEFAULT NULL,
  `agreement_percentage` double DEFAULT NULL,
  `amount_paid_at_agreement` double DEFAULT NULL,
  `amc_charges` double DEFAULT NULL,
  `cgm_rate` double DEFAULT NULL,
  `srgm_rate` double DEFAULT NULL,
  `gm_rate` double DEFAULT NULL,
  `dgm_rate` double DEFAULT NULL,
  `total_amount` double DEFAULT NULL,
  `w_value` double DEFAULT NULL,
  `b_value` double DEFAULT NULL,
  `balance_amount` double DEFAULT NULL,
  `actual_agreement_amount` double DEFAULT NULL,
  `agreement_balance` double DEFAULT NULL,
  `mediator_amount` double DEFAULT NULL,
  `mediator_deduction` double DEFAULT NULL,
  `mediator_actual_payment` double DEFAULT NULL,
  `mediator_at_agreement` double DEFAULT NULL,
  `cgm_total` double DEFAULT NULL,
  `cgm_at_agreement` double DEFAULT NULL,
  `cgm_at_registration` double DEFAULT NULL,
  `srgm_total` double DEFAULT NULL,
  `srgm_at_agreement` double DEFAULT NULL,
  `srgm_at_registration` double DEFAULT NULL,
  `gm_total` double DEFAULT NULL,
  `gm_at_agreement` double DEFAULT NULL,
  `gm_at_registration` double DEFAULT NULL,
  `dgm_total` double DEFAULT NULL,
  `dgm_at_agreement` double DEFAULT NULL,
  `dgm_at_registration` double DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(255) DEFAULT NULL,
  `cgm_name` varchar(255) DEFAULT NULL,
  `srgm_name` varchar(255) DEFAULT NULL,
  `gm_name` varchar(255) DEFAULT NULL,
  `dgm_name` varchar(255) DEFAULT NULL,
  `project_name` varchar(255) DEFAULT NULL,
  `commission_breakdown` text,
  `agm_rate` double DEFAULT '0',
  `agm_name` varchar(255) DEFAULT NULL,
  `agm_total` double DEFAULT '0',
  `agm_at_agreement` double DEFAULT '0',
  `agm_at_registration` double DEFAULT '0',
  `agent_name` text,
  `agent_rate` double DEFAULT '0',
  `agent_total` double DEFAULT '0',
  `agent_at_agreement` double DEFAULT '0',
  `agent_at_registration` double DEFAULT '0',
  `broker_commission` double DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pending_receipts`
--

DROP TABLE IF EXISTS `pending_receipts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pending_receipts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `no` varchar(255) DEFAULT NULL,
  `project_name` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `venture` varchar(255) DEFAULT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  `amount_numeric` double DEFAULT NULL,
  `amount_words` text,
  `plot_no` varchar(255) DEFAULT NULL,
  `square_yards` varchar(255) DEFAULT NULL,
  `purpose` text,
  `drawn_bank` varchar(255) DEFAULT NULL,
  `branch` varchar(255) DEFAULT NULL,
  `payment_mode` varchar(255) DEFAULT NULL,
  `instrument_no` varchar(255) DEFAULT NULL,
  `submitted_by` varchar(255) DEFAULT NULL,
  `submitted_at` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `admin_notes` text,
  `basic_price` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plot_layouts`
--

DROP TABLE IF EXISTS `plot_layouts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plot_layouts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_name` varchar(255) NOT NULL,
  `plot_no` varchar(255) NOT NULL,
  `facing` varchar(50) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `width` double DEFAULT NULL,
  `area` double DEFAULT NULL,
  `sq_yards` double DEFAULT NULL,
  `svg_element_id` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'available',
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `boundary_east` text,
  `boundary_west` text,
  `boundary_north` text,
  `boundary_south` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_plot` (`project_name`,`plot_no`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `total_plots` int DEFAULT '0',
  `plots_to_landowners` int DEFAULT '0',
  `is_archived` tinyint(1) DEFAULT '0',
  `plots_to_mortgage` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `receipts`
--

DROP TABLE IF EXISTS `receipts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receipts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `no` varchar(255) DEFAULT NULL,
  `project_name` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `venture` varchar(255) DEFAULT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  `amount_numeric` double DEFAULT NULL,
  `amount_words` text,
  `plot_no` varchar(255) DEFAULT NULL,
  `square_yards` varchar(255) DEFAULT NULL,
  `purpose` text,
  `drawn_bank` varchar(255) DEFAULT NULL,
  `branch` varchar(255) DEFAULT NULL,
  `payment_mode` varchar(255) DEFAULT NULL,
  `created_at` varchar(255) DEFAULT NULL,
  `pan_no` varchar(255) DEFAULT NULL,
  `aadhar_no` varchar(255) DEFAULT NULL,
  `instrument_no` varchar(255) DEFAULT NULL,
  `basic_price` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=184 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'user',
  `can_view_dashboard` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` varchar(255) NOT NULL,
  `can_search_receipts` tinyint(1) NOT NULL DEFAULT '0',
  `can_view_vishvam_layout` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-10 11:16:59
