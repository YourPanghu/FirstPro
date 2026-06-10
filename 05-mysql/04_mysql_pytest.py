"""
04 - Pytest + MySQL 整合
=========================
把数据库测试用 Pytest 框架组织起来

面试高频考点：
  - fixture 管理数据库连接
  - 事务回滚保证测试独立性
  - parametrize 数据驱动 SQL 测试

运行: pytest 05-mysql/04_mysql_pytest.py -v
"""

import pytest
import pymysql


# ============================================================
# 测试配置
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "testdb",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


# ============================================================
# Fixture: 每个测试用例独立的数据库连接
# ============================================================
@pytest.fixture
def db():
    """
    每个测试用例拿到的 db 都是独立的事务
    测试结束后自动 rollback → 不污染真实数据
    """
    conn = pymysql.connect(**DB_CONFIG)
    conn.begin()
    yield conn
    conn.rollback()
    conn.close()


@pytest.fixture
def cursor(db):
    """快捷 fixture: 直接拿游标"""
    cur = db.cursor()
    yield cur
    cur.close()


# ============================================================
# 测试类: 用户表 CRUD
# ============================================================
class TestUsersCRUD:
    """用户表增删改查测试"""

    def test_user_count(self, cursor):
        """测试：用户表不为空"""
        cursor.execute("SELECT COUNT(*) AS cnt FROM users")
        result = cursor.fetchone()
        assert result["cnt"] >= 5, f"用户数应 >= 5，实际 {result['cnt']}"

    def test_user_fields(self, cursor):
        """测试：用户记录包含必要字段"""
        cursor.execute("SELECT * FROM users WHERE id = 1")
        user = cursor.fetchone()
        required_fields = ["id", "username", "email", "phone", "age", "created_at"]
        for field in required_fields:
            assert field in user, f"缺少字段: {field}"
        assert isinstance(user["id"], int)
        assert isinstance(user["age"], int)

    @pytest.mark.parametrize("user_id,expected_name", [
        (1, "张三"),
        (2, "李四"),
        (3, "王五"),
        (4, "赵六"),
        (5, "孙七"),
    ])
    def test_user_by_id(self, cursor, user_id, expected_name):
        """数据驱动测试: 用 parametrize 跑多组数据"""
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        assert user is not None, f"用户 {user_id} 不存在"
        assert user["username"] == expected_name, (
            f"ID {user_id} 期望 {expected_name}，实际 {user['username']}"
        )

    def test_insert_user(self, db, cursor):
        """测试：插入用户"""
        cursor.execute(
            "INSERT INTO users (username, email, phone, age) VALUES (%s, %s, %s, %s)",
            ("pytest_user", "pytest@test.com", "13900139000", 25),
        )
        # 不 commit：MySQL 同一事务内可以读到自己的未提交修改
        # fixture 的 rollback 会自动清理，不污染数据库

        # 验证插入成功（同一事务内可见）
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM users WHERE id = %s", (new_id,))
        inserted = cursor.fetchone()
        assert inserted["username"] == "pytest_user"
        assert inserted["email"] == "pytest@test.com"

    def test_update_user_age(self, db, cursor):
        """测试：更新用户年龄"""
        # 先记住原值
        cursor.execute("SELECT age FROM users WHERE id = 1")
        original_age = cursor.fetchone()["age"]

        # 更新（事务内，不提交，fixture 自动回滚恢复）
        new_age = original_age + 1
        cursor.execute("UPDATE users SET age = %s WHERE id = %s", (new_age, 1))
        assert cursor.rowcount == 1

        # 验证
        cursor.execute("SELECT age FROM users WHERE id = 1")
        assert cursor.fetchone()["age"] == new_age

    def test_delete_rollback(self, db, cursor):
        """测试：事务回滚 —— 删除后回滚，数据应该还在"""
        # 插入一条临时数据
        cursor.execute(
            "INSERT INTO users (username, email, age) VALUES (%s, %s, %s)",
            ("rollback_test", "rollback@test.com", 30),
        )
        db.commit()
        temp_id = cursor.lastrowid

        # 删除
        cursor.execute("DELETE FROM users WHERE id = %s", (temp_id,))
        # 不 commit，直接 rollback
        db.rollback()

        # fixture 的 db 会 rollback，但这里我们用了内层的 db.rollback()
        # 所以需要重新开始事务才能查询
        db.begin()
        cursor.execute("SELECT * FROM users WHERE id = %s", (temp_id,))
        # 注意：上面 rollback 后数据可能不存在了（因为我们commit后又rollback了删除）
        # 这里验证的是: rollback 使 delete 失效
        user = cursor.fetchone()
        # 正式清理
        cursor.execute("DELETE FROM users WHERE id = %s", (temp_id,))
        db.commit()
        assert user is not None, "rollback 后数据应该还在"


# ============================================================
# 测试类: 商品表查询
# ============================================================
class TestProducts:
    """商品表测试"""

    def test_product_count(self, cursor):
        cursor.execute("SELECT COUNT(*) AS cnt FROM products")
        assert cursor.fetchone()["cnt"] >= 8

    def test_products_in_stock(self, cursor):
        """测试：上架商品库存 > 0"""
        cursor.execute(
            "SELECT name, stock FROM products WHERE status = '上架'"
        )
        products = cursor.fetchall()
        for p in products:
            assert p["stock"] > 0, f"{p['name']} 上架但库存为 {p['stock']}"

    @pytest.mark.parametrize("category,min_count", [
        ("手机", 2),
        ("电脑", 1),
        ("耳机", 2),
        ("平板", 2),
        ("手表", 1),
    ])
    def test_category_count(self, cursor, category, min_count):
        """数据驱动：每个品类至少有 min_count 个商品"""
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM products WHERE category = %s",
            (category,),
        )
        cnt = cursor.fetchone()["cnt"]
        assert cnt >= min_count, f"{category} 品类商品数 {cnt} < {min_count}"

    def test_price_range(self, cursor):
        """测试：价格在合理范围"""
        cursor.execute("SELECT MIN(price) AS min_p, MAX(price) AS max_p FROM products")
        price_range = cursor.fetchone()
        assert price_range["min_p"] >= 0, "价格不应为负"
        assert price_range["max_p"] <= 100000, "价格不应超过 10 万"


# ============================================================
# 测试类: 订单表 JOIN 查询
# ============================================================
class TestOrders:
    """订单表关联查询测试"""

    def test_order_user_exists(self, cursor):
        """测试：每个订单的用户都存在"""
        cursor.execute("""
            SELECT o.id FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            WHERE u.id IS NULL
        """)
        orphans = cursor.fetchall()
        assert len(orphans) == 0, f"存在 {len(orphans)} 个孤儿订单"

    def test_order_product_exists(self, cursor):
        """测试：每个订单的商品都存在"""
        cursor.execute("""
            SELECT o.id FROM orders o
            LEFT JOIN products p ON o.product_id = p.id
            WHERE p.id IS NULL
        """)
        orphans = cursor.fetchall()
        assert len(orphans) == 0, f"存在 {len(orphans)} 个孤儿订单"

    def test_total_price_correct(self, cursor):
        """测试：total_price = quantity * unit_price"""
        cursor.execute("""
            SELECT o.id, o.quantity, o.total_price, p.price
            FROM orders o
            JOIN products p ON o.product_id = p.id
        """)
        orders = cursor.fetchall()
        for o in orders:
            expected = o["quantity"] * o["price"]
            assert o["total_price"] == expected, (
                f"订单 {o['id']}: total_price={o['total_price']} ≠ "
                f"{o['quantity']} × {o['price']} = {expected}"
            )
