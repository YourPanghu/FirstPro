"""
02 - CRUD 操作 + 断言测试
==========================
CRUD = Create(增) + Read(查) + Update(改) + Delete(删)
这也是数据库测试最核心的内容，和 API 测试的 CRUD 思路一致

测试思路：
  执行 SQL → 断言结果 → 验证数据状态
  每条 SQL 操作都要有对应的"验证点"
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


# ============================================================
# 连接数据库
# ============================================================
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

log("=" * 55)
log("数据库 CRUD 断言测试")
log("=" * 55)


# ============================================================
# R - Read（查询） —— 最基础的操作
# ============================================================
log("")
log("🔹 Read: 查询测试", "STEP")

# 测试点 1: 查单条 —— 验证字段完整性
cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
user = cursor.fetchone()
assert user is not None, "用户 1 应该存在"
assert user["username"] == "张三", f"用户名应为张三，实际 {user['username']}"
assert "@" in user["email"], f"邮箱格式不对: {user['email']}"
assert isinstance(user["age"], int), f"年龄应为整数，实际 {type(user['age'])}"
log("单条查询 + 字段断言 通过", "PASS")

# 测试点 2: 查多条 —— 验证数量 + 排序
cursor.execute("SELECT * FROM users ORDER BY age DESC")
users = cursor.fetchall()
assert len(users) >= 5, f"用户数应 >= 5，实际 {len(users)}"
# 按年龄降序，第一条应该最大
assert users[0]["age"] >= users[-1]["age"], "降序排列错误"
log(f"多条查询通过: 共 {len(users)} 条，最大年龄 {users[0]['age']}岁", "PASS")

# 测试点 3: 条件查询 —— 验证过滤正确
cursor.execute("SELECT * FROM users WHERE age >= %s", (30,))
older_users = cursor.fetchall()
for u in older_users:
    assert u["age"] >= 30, f"{u['username']} 年龄 {u['age']} < 30，不符合条件"
log(f"条件查询通过: {len(older_users)} 人年龄 >= 30", "PASS")


# ============================================================
# C - Create（新增） —— 插入数据
# ============================================================
log("")
log("🔹 Create: 新增测试", "STEP")

# 先记下插入前的数量
cursor.execute("SELECT COUNT(*) AS cnt FROM users")
before_count = cursor.fetchone()["cnt"]

# 插入新用户
new_user = {
    "username": "测试用户_CRUD",
    "email": "test_crud@example.com",
    "phone": "13900139001",
    "age": 26,
}
sql = """
    INSERT INTO users (username, email, phone, age)
    VALUES (%(username)s, %(email)s, %(phone)s, %(age)s)
"""
cursor.execute(sql, new_user)
new_id = cursor.lastrowid  # ← 立刻保存！后续 execute() 会重置 lastrowid
conn.commit()  # ← 重要！不 commit 数据不会真正写入

# 验证点 1: 数量 +1
cursor.execute("SELECT COUNT(*) AS cnt FROM users")
after_count = cursor.fetchone()["cnt"]
assert after_count == before_count + 1, (
    f"新增后数量应为 {before_count + 1}，实际 {after_count}"
)
log(f"新增成功: {before_count} → {after_count} (+1)", "PASS")

# 验证点 2: 查回来，字段要对
cursor.execute("SELECT * FROM users WHERE id = %s", (new_id,))
inserted = cursor.fetchone()
assert inserted["username"] == new_user["username"]
assert inserted["email"] == new_user["email"]
assert inserted["age"] == new_user["age"]
log(f"新用户验证通过: ID={new_id}, username={inserted['username']}", "PASS")

# 验证点 3: UNIQUE 约束 —— 重复 username 应该报错
try:
    cursor.execute(sql, new_user)
    conn.commit()
    log("重复插入应该报错但没报！", "FAIL")
    assert False, "UNIQUE 约束失效"
except pymysql.IntegrityError:
    conn.rollback()  # 回滚错误的事务
    log("UNIQUE 约束生效: 重复 username 正确报错", "PASS")


# ============================================================
# U - Update（修改） —— 更新数据
# ============================================================
log("")
log("🔹 Update: 修改测试", "STEP")

# 修改刚插入的用户
update_sql = "UPDATE users SET age = %s, phone = %s WHERE id = %s"
new_age = 30
new_phone = "13900139002"
cursor.execute(update_sql, (new_age, new_phone, new_id))
conn.commit()

# 验证点 1: affected rows = 1
assert cursor.rowcount == 1, f"应影响 1 行，实际 {cursor.rowcount}"

# 验证点 2: 改后的值要正确
cursor.execute("SELECT age, phone FROM users WHERE id = %s", (new_id,))
updated = cursor.fetchone()
assert updated["age"] == new_age, f"年龄未更新: {updated['age']}"
assert updated["phone"] == new_phone, f"手机号未更新: {updated['phone']}"
log(f"更新成功: age={new_age}, phone={new_phone}", "PASS")

# 验证点 3: 其他字段不应被影响
cursor.execute("SELECT username, email FROM users WHERE id = %s", (new_id,))
unchanged = cursor.fetchone()
assert unchanged["username"] == new_user["username"], "username 被意外修改"
assert unchanged["email"] == new_user["email"], "email 被意外修改"
log("其他字段未被影响，符合预期", "PASS")


# ============================================================
# D - Delete（删除） —— 删除数据
# ============================================================
log("")
log("🔹 Delete: 删除测试", "STEP")

# 删除刚插入的用户
cursor.execute("DELETE FROM users WHERE id = %s", (new_id,))
conn.commit()

# 验证点 1: affected rows = 1
assert cursor.rowcount == 1, f"应删除 1 行，实际 {cursor.rowcount}"

# 验证点 2: 查不到了
cursor.execute("SELECT * FROM users WHERE id = %s", (new_id,))
deleted = cursor.fetchone()
assert deleted is None, f"删除后仍能查到 id={new_id}"
log(f"删除成功: id={new_id} 已查不到", "PASS")

# 验证点 3: 数量恢复
cursor.execute("SELECT COUNT(*) AS cnt FROM users")
final_count = cursor.fetchone()["cnt"]
assert final_count == before_count, (
    f"删除后数量应恢复 {before_count}，实际 {final_count}"
)
log(f"数量恢复: {final_count} == {before_count}", "PASS")


# ============================================================
# 联表查询（JOIN）—— 面试必问
# ============================================================
log("")
log("🔹 JOIN: 联表查询测试", "STEP")

# 查询每个用户的订单数
join_sql = """
    SELECT u.username, COUNT(o.id) AS order_count,
           COALESCE(SUM(o.total_price), 0) AS total_spent
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.username
    ORDER BY total_spent DESC
"""
cursor.execute(join_sql)
user_orders = cursor.fetchall()

# 验证点：至少有一个用户有订单
has_order = [u for u in user_orders if u["order_count"] > 0]
assert len(has_order) > 0, "应该有用户下了订单"

log("用户订单统计:", "INFO")
for u in user_orders:
    log(f"  {u['username']:<6} | 订单数: {u['order_count']} | 总消费: ¥{u['total_spent']:,.2f}", "INFO")
log(f"联表查询通过: {len(has_order)} 位用户有订单", "PASS")


# ============================================================
# 子查询
# ============================================================
log("")
log("🔹 子查询测试", "STEP")

# 查询消费最高的用户
sub_sql = """
    SELECT username, email
    FROM users
    WHERE id = (
        SELECT user_id FROM orders
        GROUP BY user_id
        ORDER BY SUM(total_price) DESC
        LIMIT 1
    )
"""
cursor.execute(sub_sql)
top_user = cursor.fetchone()
log(f"消费最高: {top_user['username']} ({top_user['email']})", "PASS")


# ============================================================
# 清理 + 总结
# ============================================================
cursor.close()
conn.close()

log("")
log("=" * 55)
log("🎉 CRUD 断言测试全部通过！", "PASS")
log("=" * 55)
log("覆盖: SELECT | INSERT | UPDATE | DELETE | JOIN | 子查询 | UNIQUE约束 | 字段断言", "INFO")
log("")
log("💡 面试话术：「数据库测试我会验证 CRUD 操作的", "INFO")
log("   正确性，包括字段值断言、约束检查、联表查询结果、", "INFO")
log("   事务回滚后的数据状态。每条 SQL 都有对应的验证点。」", "INFO")
