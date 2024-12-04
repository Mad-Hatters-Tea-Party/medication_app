-- MySQL dump 10.13  Distrib 8.0.40, for macos14 (x86_64)
--
-- Host: app-db.clsm00w6ehfa.us-east-1.rds.amazonaws.com    Database: app_db
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
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

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '';

--
-- Table structure for table `medication`
--

DROP TABLE IF EXISTS `medication`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medication` (
  `medication_id` int NOT NULL AUTO_INCREMENT,
  `medication_name` varchar(45) DEFAULT NULL,
  `medication_use` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`medication_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medication`
--

LOCK TABLES `medication` WRITE;
/*!40000 ALTER TABLE `medication` DISABLE KEYS */;
INSERT INTO `medication` VALUES (1,'med A','med A use for help'),(2,'med b','med b use for help'),(3,'med c','med c use for help');
/*!40000 ALTER TABLE `medication` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(25) DEFAULT NULL,
  `notification_type` int NOT NULL COMMENT '1 = refill\n2 = reminder',
  `notification_message` varchar(150) DEFAULT NULL,
  `notification_date` datetime DEFAULT NULL,
  `notification_status` int DEFAULT NULL COMMENT '0 = sent\\\\\\\\n1 = read',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`),
  KEY `user_id_notification_FK_idx` (`user_id`),
  CONSTRAINT `user_id_notification_FK` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification`
--

LOCK TABLES `notification` WRITE;
/*!40000 ALTER TABLE `notification` DISABLE KEYS */;
INSERT INTO `notification` VALUES (4,'testuser3',1,'Your prescription is ready for refill','2024-12-15 14:30:00',0,'2024-12-01 21:24:27','2024-12-01 22:55:29'),(6,'testuser3',2,'take meds','2024-12-01 14:30:00',NULL,'2024-12-01 22:53:54','2024-12-01 22:53:54');
/*!40000 ALTER TABLE `notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prescription`
--

DROP TABLE IF EXISTS `prescription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prescription` (
  `prescription_id` int NOT NULL AUTO_INCREMENT,
  `prescription_date_start` date DEFAULT NULL,
  `prescription_date_end` date DEFAULT NULL,
  `prescription_status` int DEFAULT NULL COMMENT '0 = active\n1 = archive\n',
  `user_id` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`prescription_id`),
  KEY `user_id_FK_idx` (`user_id`),
  CONSTRAINT `user_id_FK` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prescription`
--

LOCK TABLES `prescription` WRITE;
/*!40000 ALTER TABLE `prescription` DISABLE KEYS */;
INSERT INTO `prescription` VALUES (6,'2024-01-01',NULL,0,'testuser3');
/*!40000 ALTER TABLE `prescription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prescription_detail`
--

DROP TABLE IF EXISTS `prescription_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prescription_detail` (
  `prescription_id` int NOT NULL,
  `medication_id` int NOT NULL,
  `presc_dose` varchar(10) DEFAULT NULL,
  `presc_qty` int DEFAULT NULL,
  `presc_type` varchar(15) DEFAULT NULL COMMENT 'Grams\nMiligrams\nDrops\n',
  `presc_frequency` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`prescription_id`,`medication_id`),
  KEY `presc_detail_med_id_FK_idx` (`medication_id`),
  CONSTRAINT `presc_detail_med_id_FK` FOREIGN KEY (`medication_id`) REFERENCES `medication` (`medication_id`),
  CONSTRAINT `presc_detail_prec_id_FK` FOREIGN KEY (`prescription_id`) REFERENCES `prescription` (`prescription_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prescription_detail`
--

LOCK TABLES `prescription_detail` WRITE;
/*!40000 ALTER TABLE `prescription_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `prescription_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `side_effect`
--

DROP TABLE IF EXISTS `side_effect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `side_effect` (
  `side_effects_id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(25) DEFAULT NULL,
  `medication_id` int DEFAULT NULL,
  `side_effect_desc` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`side_effects_id`),
  KEY `user_id_side_effect_FK_idx` (`user_id`),
  KEY `med_id_side_effect_FK_idx` (`medication_id`),
  CONSTRAINT `med_id_side_effect_FK` FOREIGN KEY (`medication_id`) REFERENCES `medication` (`medication_id`),
  CONSTRAINT `user_id_side_effect_FK` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `side_effect`
--

LOCK TABLES `side_effect` WRITE;
/*!40000 ALTER TABLE `side_effect` DISABLE KEYS */;
INSERT INTO `side_effect` VALUES (7,'testuser3',2,'vomiting','2024-12-03 14:39:27','2024-12-03 14:39:27'),(9,'testuser3',3,'vomiting','2024-12-04 02:27:09','2024-12-04 02:27:09'),(10,'testuser3',3,'vomiting','2024-12-04 02:27:31','2024-12-04 02:27:31'),(11,'testuser3',2,'vomiting','2024-12-04 02:27:37','2024-12-04 02:27:37'),(12,'testuser3',2,'sleepy','2024-12-04 02:37:49','2024-12-04 02:37:49'),(13,'testuser3',3,'sleepy','2024-12-04 02:51:42','2024-12-04 02:51:42'),(14,'testuser3',3,'sleepy','2024-12-04 02:56:05','2024-12-04 02:56:05'),(15,'testuser3',3,'sleepy','2024-12-04 02:59:54','2024-12-04 02:59:54');
/*!40000 ALTER TABLE `side_effect` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` varchar(25) NOT NULL,
  `user_email` varchar(50) DEFAULT NULL COMMENT 'This is the email address of the user.',
  `user_phone` varchar(20) DEFAULT NULL COMMENT 'User phone number:\nCountry code + number. Eg. 44 720192837',
  `user_pwd` varchar(255) NOT NULL,
  `user_gender` int DEFAULT NULL COMMENT '0 = female\n1 = male',
  `user_dob` date DEFAULT NULL COMMENT 'User date of birth. \nAge can be calculated from date of birth.',
  `user_height` int DEFAULT NULL COMMENT 'Height = 178cm\nIn the app you can ask in Feet & Inches and you can convert to CM to store the value.',
  `user_weight` int DEFAULT NULL COMMENT 'Weight in KM. ',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('1','testuser@example.com','+1234567890','$2b$12$LTH6e1i2S8/ZtMGilMdM8Oq95huWnQFY5x.oSXxgrOSYo0KXQbtde',1,'2000-01-01',180,75,'2024-11-25 00:57:29','2024-11-25 00:57:29'),('10','testuser1234@example.com','+1234567890','$2b$12$pv7F8xCYB0//KQzMyhLpGeg7vOvJpqedGM/Mw6aaJNI/pY6nqnRt2',1,'2000-01-01',180,75,'2024-11-25 20:22:06','2024-11-25 20:22:06'),('15','testuser1234@example.com','+1234567890','$2b$12$vvbutJHTJBTyC9RrkiBoEuEnUtfedKVQzIldD/MNKSi2b78kcd7e.',1,'2000-01-01',70,160,'2024-12-01 19:31:12','2024-12-01 19:31:12'),('20','testuser1234@example.com','+1234567890','$2b$12$rULtmGoPl71NuVLkVr9lBODqEh5w7HTRHeMA.jnGsgbWG9TKP/Mfa',1,'2000-01-01',70,160,'2024-12-03 14:47:37','2024-12-03 14:47:37'),('man','newuser@example.com','+1234567890','$2b$12$Yh50/KbTcmp7WeazN6Vi.uXztVneVHJJD93kIx6xBzI0jFd1L55ai',1,'2000-01-01',60,150,'2024-12-03 23:39:10','2024-12-03 23:39:10'),('many','newuser@example.com','+1234567890','$2b$12$Gk6pI7K/61r8HdUoQOR0au50R.AWoADocGKpkJ50K4f8DZRptKauu',1,'2000-01-01',60,150,'2024-12-03 23:41:14','2024-12-03 23:41:14'),('manyy','newuser@example.com','+1234567890','$2b$12$7APjfXZMY9vecLrNpMWD8u38vNq/dY8WUKBfj6Fod/PZrwpka39AC',1,'2000-01-01',60,150,'2024-12-03 23:43:30','2024-12-03 23:43:30'),('manyyy','newuser@example.com','+1234567890','$2b$12$.doTMDH.H7//M5/EvpZ/PuD/E3SvmpDGxx.h2gYB56jztAyoc4KKm',1,'2000-01-01',60,150,'2024-12-03 23:45:20','2024-12-03 23:45:20'),('monkey','newuser@example.com','+1234567890','$2b$12$3RhRjQJbwG1ioKzWjT6iIuVPCNY8re2xtleg/WK0a/.bq3aCbQh2O',1,'2000-01-01',60,150,'2024-12-03 23:35:46','2024-12-03 23:35:46'),('new','newuser@example.com','+1234567890','$2b$12$duBYlsiQclzYPcZDlINhu.J9414MuNYpKC7b5BII93m1oc1lDN5JC',1,'2000-01-01',60,150,'2024-12-03 23:17:17','2024-12-03 23:17:17'),('newuser','newuser@example.com','+1234567890','$2b$12$2MqaYp.OWUhEjhkwLFOZnevF07Jkf/0AYqBoldkbDXICH7q3h.CLq',1,'2000-01-01',60,150,'2024-12-03 23:13:10','2024-12-03 23:13:10'),('newuser123','newuser@example.com','+1234567890','$2b$12$doXPfEXnjp65Sa7IKwkz0OpRV5XIoABkH593bduSi8mmisGtK1TIi',1,'2000-01-01',60,150,'2024-12-03 23:08:16','2024-12-03 23:08:16'),('testuser123','updateduser@example.com','1112223333','NewPassword123',0,'1985-01-01',68,160,'2024-12-01 20:23:16','2024-12-01 20:46:35'),('testuser3','testuser@example.com','1234567890','$2b$12$sMsBwHHbjvqucBaQ03FUMe3dcBUgUZW28Mwsqec2eMTgma3.8t50y',1,'1990-01-01',72,180,'2024-12-01 21:24:23','2024-12-04 00:48:29'),('user','newuser@example.com','+1234567890','$2b$12$YwMVa.PbvXdLJzCqjVzFhOVEintmVAfj7DoTLRFYzbwBU129Rd0Xu',1,'2000-01-01',60,150,'2024-12-03 23:21:52','2024-12-03 23:21:52'),('why','newuser@example.com','+1234567890','$2b$12$Fy6SWtPlJgifnbtJbh6VRek.icwDwH.7Nttv4YaVkmGM.IUxMPP7m',1,'2000-01-01',60,150,'2024-12-04 01:27:02','2024-12-04 01:27:02'),('wow','newuser@example.com','+1234567890','$2b$12$KMcGLSgadTRb/DrRlPrfdu3qArZrHLpYciS8oNYf4RSncMgXtRkt.',1,'2000-01-01',60,150,'2024-12-03 23:34:24','2024-12-03 23:34:24');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-03 21:12:06
