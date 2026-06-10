-- ============================================================
-- 测试数据库初始化脚本
-- ============================================================
-- 用法：
--   Windows 命令行（推荐，避免中文乱码）：
--     mysql -u root -p --default-character-set=utf8mb4 < test_data.sql
--   PowerShell / CMD 直接：
--     mysql -u root -p < test_data.sql
--   或者直接用 Python 初始化（最可靠）：
--     python -c "exec(open('05-mysql/init_db.py').read())"
--   或在 MySQL Workbench / DBeaver 中执行
-- ============================================================

-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS testdb
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE testdb;

-- ============================================================
-- 1. 用户表 —— 最常用的测试表
-- ============================================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    email       VARCHAR(100) NOT NULL UNIQUE,
    phone       VARCHAR(20),
    age         INT CHECK (age > 0 AND age < 150),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 2. 商品表 —— 用于测试关联查询
-- ============================================================
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200)   NOT NULL,
    category    VARCHAR(50)    NOT NULL,
    price       DECIMAL(10,2)  NOT NULL CHECK (price >= 0),
    stock       INT            DEFAULT 0,
    status      ENUM('上架', '下架', '缺货') DEFAULT '上架',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 3. 订单表 —— 用于测试事务/关联
-- ============================================================
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL CHECK (quantity > 0),
    total_price DECIMAL(10,2) NOT NULL,
    status      ENUM('待付款', '已付款', '已发货', '已完成', '已取消') DEFAULT '待付款',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 插入测试数据
-- ============================================================

-- 用户数据
INSERT INTO users (username, email, phone, age) VALUES
('张三',   'zhangsan@test.com',   '13800138001', 25),
('李四',   'lisi@test.com',       '13800138002', 30),
('王五',   'wangwu@test.com',     '13800138003', 28),
('赵六',   'zhaoliu@test.com',    '13800138004', 35),
('孙七',   'sunqi@test.com',      '13800138005', 22);

-- 商品数据
INSERT INTO products (name, category, price, stock, status) VALUES
('iPhone 15',        '手机',  6999.00,  100, '上架'),
('MacBook Pro',      '电脑',  14999.00,  50, '上架'),
('AirPods Pro',      '耳机',  1999.00,  200, '上架'),
('iPad Air',         '平板',  4999.00,   80, '上架'),
('Apple Watch',      '手表',  2999.00,    0, '缺货'),
('小米14',           '手机',  3999.00,  150, '上架'),
('华为 MatePad',     '平板',  3499.00,   60, '上架'),
('索尼 WH-1000XM5',  '耳机',  2299.00,   30, '下架');

-- 订单数据
INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
(1, 1, 1, 6999.00,  '已完成'),
(1, 3, 2, 3998.00,  '已完成'),
(2, 2, 1, 14999.00, '已发货'),
(3, 1, 1, 6999.00,  '待付款'),
(3, 6, 1, 3999.00,  '已付款'),
(4, 4, 1, 4999.00,  '已完成'),
(5, 7, 2, 6998.00,  '已取消');
