/*
 Navicat Premium Data Transfer

 Source Server         : win_docker_mysql
 Source Server Type    : MySQL
 Source Server Version : 90400 (9.4.0)
 Source Host           : localhost:3306
 Source Schema         : zhiyue

 Target Server Type    : MySQL
 Target Server Version : 90400 (9.4.0)
 File Encoding         : 65001

 Date: 13/08/2025 11:22:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for mmreader
-- ----------------------------
DROP TABLE IF EXISTS `mmreader`;
CREATE TABLE `mmreader`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `biz` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `mid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `idx` int NULL DEFAULT NULL,
  `gh_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `insert_time` datetime NULL DEFAULT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `pub_time` int NULL DEFAULT NULL,
  `content_clean` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `cover_image` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `digest` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 640 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
