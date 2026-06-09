-- LIMS 数据库初始化脚本
-- 如果数据库不存在则创建
CREATE DATABASE IF NOT EXISTS lims DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE lims;

-- 设置时区
SET GLOBAL time_zone = '+8:00';
