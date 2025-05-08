-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS imagedb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 确保用户存在并具有正确权限
CREATE USER IF NOT EXISTS 'mysqluser'@'%' IDENTIFIED BY 'mysql577715';
GRANT ALL PRIVILEGES ON imagedb.* TO 'mysqluser'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 切换到目标数据库
USE imagedb;

-- 创建用户表（如果不存在）
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 