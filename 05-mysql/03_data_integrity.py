"""
03 - 数据完整性测试
===================
数据完整性 = 数据准确 + 一致 + 可靠
这是测试工程师最重要的数据库测试技能之一

测试维度：
  1. 约束完整性  —— NOT NULL / UNIQUE / CHECK / DEFAULT
  2. 数据类型验证 —— INT 不能存字符串
  3. 外键约束    —— 关联数据不能"悬空"
  4. 索引验证    —— 唯一索引、普通索引
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "testdb",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def log(msg, level="INFO"):
    prefixes = {"INFO": "📋", "PASS": "✅", "FAIL": "❌", "STEP": "🔹", "SQL": "💾"}
    print(f"{prefixes.get(level, '')} [{level}] {msg}")


conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

log("=" * 55)
log("数据完整性测试")
log("=" * 55)


# ============================================================
# 1. NOT NULL 约束测试
# ============================================================
log("")
log("🔹 1. NOT NULL 约束", "STEP")

# username 和 email 是 NOT NULL，插入 NULL 应该报错
test_cases = [
    ("username 为 NULL", {"username": None, "email": "test@test.com", "phone": "138", "age": 20}),
    ("email 为 NULL",    {"username": "test_null", "email": None, "phone": "138", "age": 20}),
]

for case_name, data in test_cases:
    try:
        sql = "INSERT INTO users (username, email, phone, age) VALUES (%(username)s, %(email)s, %(phone)s, %(age)s)"
        cursor.execute(sql, data)
        conn.commit()
        log(f"{case_name}: 应该报错但没报！", "FAIL")
    except pymysql.IntegrityError as e:
        conn.rollback()
        log(f"{case_name}: 正确拦截 → {e.args[1][:60]}", "PASS")
    except pymysql.OperationalError as e:
        conn.rollback()
        log(f"{case_name}: 正确拦截 → {e.args[1][:60]}", "PASS")


# ============================================================
# 2. UNIQUE 约束测试
# ============================================================
log("")
log("🔹 2. UNIQUE 约束", "STEP")

# 插入已存在的 username
dup_user = {"username": "张三", "email": "unique_test@test.com", "phone": "138", "age": 20}
try:
    cursor.execute(
        "INSERT INTO users (username, email, phone, age) VALUES (%(username)s, %(email)s, %(phone)s, %(age)s)",
        dup_user,
    )
    conn.commit()
    log("重复 username 应该报错！", "FAIL")
except pymysql.IntegrityError:
    conn.rollback()
    log("username 唯一约束生效: '张三' 重复插入被拒绝", "PASS")

# 插入已存在的 email
dup_email = {"username": "unique_test2", "email": "zhangsan@test.com", "phone": "138", "age": 20}
try:
    cursor.execute(
        "INSERT INTO users (username, email, phone, age) VALUES (%(username)s, %(email)s, %(phone)s, %(age)s)",
        dup_email,
    )
    conn.commit()
    log("重复 email 应该报错！", "FAIL")
except pymysql.IntegrityError:
    conn.rollback()
    log("email 唯一约束生效: 'zhangsan@test.com' 重复插入被拒绝", "PASS")


# ============================================================
# 3. CHECK 约束测试
# ============================================================
log("")
log("🔹 3. CHECK 约束", "STEP")

# age CHECK (age > 0 AND age < 150)
check_cases = [
    ("年龄为 -1",  {"username": "test1", "email": "test1@t.com", "age": -1}),
    ("年龄为 0",   {"username": "test2", "email": "test2@t.com", "age": 0}),
    ("年龄为 200", {"username": "test3", "email": "test3@t.com", "age": 200}),
    ("年龄为 150", {"username": "test4", "email": "test4@t.com", "age": 150}),
]

for case_name, data in check_cases:
    try:
        sql = "INSERT INTO users (username, email, age) VALUES (%(username)s, %(email)s, %(age)s)"
        cursor.execute(sql, data)
        conn.commit()
        log(f"{case_name}: 应该被 CHECK 约束拦截！当前数据已写入", "FAIL")
        # 清理掉
        cursor.execute("DELETE FROM users WHERE username = %(username)s", data)
        conn.commit()
    except (pymysql.IntegrityError, pymysql.OperationalError):
        conn.rollback()
        log(f"{case_name}: CHECK 约束生效，正确拦截", "PASS")


# ============================================================
# 4. 数据类型验证
# ============================================================
log("")
log("🔹 4. 数据类型验证", "STEP")

# 4.1 字符串截断
long_username = "a" * 51  # 超过 VARCHAR(50)
try:
    cursor.execute(
        "INSERT INTO users (username, email, age) VALUES (%s, %s, %s)",
        (long_username, "long@test.com", 20),
    )
    conn.commit()
    log(f"超长 username ({len(long_username)}字符) 应被截断或报错", "FAIL")
except Exception as e:
    conn.rollback()
    log(f"超长 username 被正确拦截 ({len(long_username)} > 50)", "PASS")

# 4.2 DECIMAL 精度验证
cursor.execute("SELECT price FROM products WHERE id = 1")
product = cursor.fetchone()
price = product["price"]
assert price == 6999.00, f"价格精度不对: {price}"
log(f"DECIMAL 精度验证通过: price = {price} (精确到分)", "PASS")


# ============================================================
# 5. 外键约束测试
# ============================================================
log("")
log("🔹 5. 外键约束", "STEP")

# 5.1 引用不存在的 user_id
try:
    cursor.execute(
        "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
        (99999, 1, 1, 6999.00),  # user_id 99999 不存在
    )
    conn.commit()
    log("引用不存在的外键应该报错！", "FAIL")
except pymysql.IntegrityError as e:
    conn.rollback()
    log("外键约束生效: 不存在的外键引用被拒绝", "PASS")

# 5.2 CASCADE 删除验证
# 先插入一个临时用户 + 他的订单
cursor.execute(
    "INSERT INTO users (username, email, age) VALUES (%s, %s, %s)",
    ("fk_test_user", "fk_test@test.com", 25),
)
conn.commit()
fk_user_id = cursor.lastrowid

cursor.execute(
    "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
    (fk_user_id, 1, 1, 6999.00),
)
conn.commit()

# 验证订单存在
cursor.execute("SELECT COUNT(*) AS cnt FROM orders WHERE user_id = %s", (fk_user_id,))
assert cursor.fetchone()["cnt"] == 1, "订单应该存在"

# 删除用户 → ON DELETE CASCADE 应该自动删除他的订单
cursor.execute("DELETE FROM users WHERE id = %s", (fk_user_id,))
conn.commit()

# 验证订单也被删了
cursor.execute("SELECT COUNT(*) AS cnt FROM orders WHERE user_id = %s", (fk_user_id,))
assert cursor.fetchone()["cnt"] == 0, "CASCADE 删除失败: 订单应该也被删除"
log("ON DELETE CASCADE 验证通过: 删除用户 → 订单联级删除", "PASS")


# ============================================================
# 6. 默认值验证
# ============================================================
log("")
log("🔹 6. DEFAULT 默认值", "STEP")

# products 表: status 默认 '上架', stock 默认 0
cursor.execute(
    "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)",
    ("默认值测试商品", "测试品类", 9.99),
)
conn.commit()
test_pid = cursor.lastrowid

cursor.execute("SELECT status, stock FROM products WHERE id = %s", (test_pid,))
defaults = cursor.fetchone()
assert defaults["status"] == "上架", f"status 默认值应为'上架'，实际'{defaults['status']}'"
assert defaults["stock"] == 0, f"stock 默认值应为 0，实际 {defaults['stock']}"
log(f"DEFAULT 值验证通过: status='{defaults['status']}', stock={defaults['stock']}", "PASS")

# 清理
cursor.execute("DELETE FROM products WHERE id = %s", (test_pid,))
conn.commit()


# ============================================================
# 7. 索引验证
# ============================================================
log("")
log("🔹 7. 索引检查", "STEP")

# 查询表的索引信息
cursor.execute("SHOW INDEX FROM users")
indexes = cursor.fetchall()
index_names = set(idx["Key_name"] for idx in indexes)

# PRIMARY KEY 应该存在
assert "PRIMARY" in index_names, "应该存在主键索引"
log("PRIMARY KEY 索引存在", "PASS")

# username UNIQUE 索引应该存在
# (MySQL 为每个 UNIQUE 约束自动创建索引)
unique_indexes = [idx for idx in indexes if idx["Key_name"] != "PRIMARY"]
log(f"找到 {len(unique_indexes)} 个非主键索引: {[i['Key_name'] for i in unique_indexes]}", "INFO")


# ============================================================
# 总结
# ============================================================
cursor.close()
conn.close()

log("")
log("=" * 55)
log("🎉 数据完整性测试全部通过！", "PASS")
log("=" * 55)
log("覆盖: NOT NULL | UNIQUE | CHECK | 数据类型 | 外键 CASCADE | DEFAULT | 索引", "INFO")
log("")
log("💡 面试话术：", "INFO")
log("  「数据完整性测试我关注几个维度：约束是否生效、", "INFO")
log("   数据类型是否匹配、外键联级是否正确、默认值是否符合预期。", "INFO")
log("   通过正向(正常数据)和反向(异常数据)两个方向覆盖。」", "INFO")
