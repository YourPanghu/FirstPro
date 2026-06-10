"""
Pytest 配置文件 —— MySQL 模块专用
=================================
提供数据库连接 fixture，每个测试用例可以直接用 db 参数获取连接

概念对照：
- fixture 就像一个"共享的工具"，每次测试前自动准备好
- scope="function" → 每个测试用例独立（默认，数据互不干扰）
- scope="session" → 整个测试会话共用（连接池场景）
"""

import pytest
import pymysql
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================
# 数据库连接配置（按你的环境修改）
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "testdb",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,  # 返回字典格式，方便取值
}


def get_connection():
    """获取数据库连接 —— 普通脚本用"""
    return pymysql.connect(**DB_CONFIG)


# ============================================================
# Pytest Fixtures
# ============================================================


@pytest.fixture(scope="function")
def db():
    """
    每个测试用例独立的数据库连接
    测试结束后自动关闭 + 回滚未提交的事务

    用法：
        def test_xxx(db):
            db.cursor().execute("SELECT * FROM users")
    """
    conn = pymysql.connect(**DB_CONFIG)
    conn.begin()  # 开启事务
    yield conn
    conn.rollback()  # 回滚 → 测试数据不污染真实数据库！
    conn.close()


@pytest.fixture(scope="function")
def cursor(db):
    """
    直接提供游标 —— 更简洁

    用法：
        def test_xxx(cursor):
            cursor.execute("SELECT 1")
    """
    cur = db.cursor()
    yield cur
    cur.close()


@pytest.fixture(scope="session")
def session_db():
    """
    整个测试会话共用一个连接
    用于需要保持状态的场景（如测试连接池）

    scope="session" → 所有测试用例跑完才关闭
    """
    conn = pymysql.connect(**DB_CONFIG)
    yield conn
    conn.close()
