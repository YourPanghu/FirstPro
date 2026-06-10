"""
01 - MySQL 连接 + 第一个查询
=============================
就像 Selenium 第一步是打开浏览器，数据库测试的第一步是"连上数据库"
本脚本演示：连接 MySQL → 执行 SQL → 读取结果 → 断开连接

前置条件：请先执行 test_data.sql 创建测试数据库
  mysql -u root -p < test_data.sql
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 0. 准备：没有 pymysql 就先安装
# ============================================================
try:
    import pymysql
except ImportError:
    print("❌ 缺少 pymysql，正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
    import pymysql
    print("✅ pymysql 安装完成")


def log(msg, level="INFO"):
    prefixes = {"INFO": "📋", "PASS": "✅", "FAIL": "❌", "STEP": "🔹", "SQL": "💾"}
    print(f"{prefixes.get(level, '')} [{level}] {msg}")


# ============================================================
# 1. 连接数据库 —— 就像 selenium 的 driver = webdriver.Chrome()
# ============================================================
log("=" * 55)
log("步骤 1: 连接 MySQL 数据库")
log("=" * 55)

# 连接参数说明（面试可能问）：
#   host     → 数据库服务器地址（localhost 就是本机）
#   port     → 端口号（MySQL 默认 3306）
#   user     → 用户名
#   password → 密码
#   database → 要操作的数据库名
#   charset  → 字符集（utf8mb4 支持 emoji，utf8 不支持）
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",       # ← 改成你的密码
    "database": "testdb",     # ← 需要先执行 test_data.sql
    "charset": "utf8mb4",
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    log("数据库连接成功！", "PASS")
    log(f"  服务器: {DB_CONFIG['host']}:{DB_CONFIG['port']}", "INFO")
    log(f"  数据库: {DB_CONFIG['database']}", "INFO")
except pymysql.MySQLError as e:
    log(f"连接失败: {e}", "FAIL")
    log("")
    log("💡 常见原因排查：", "INFO")
    log("  1. MySQL 服务没启动 → 去服务管理器启动 MySQL", "INFO")
    log("  2. 密码不对     → 修改上面 DB_CONFIG 里的 password", "INFO")
    log("  3. 没执行建库脚本 → mysql -u root -p < 05-mysql/test_data.sql", "INFO")
    log(f"  4. 数据库不存在 → CREATE DATABASE testdb", "INFO")
    sys.exit(1)


# ============================================================
# 2. 创建游标 —— 游标 = 执行 SQL 的"笔"
# ============================================================
log("")
log("=" * 55)
log("步骤 2: 创建游标（Cursor）—— 执行 SQL 的工具")
log("=" * 55)

# 游标是什么？
# 类比：连接 = 打开浏览器，游标 = 地址栏输入框
# 连接负责"通信"，游标负责"执行命令 + 读取结果"
cursor = conn.cursor()
log("游标创建成功", "PASS")


# ============================================================
# 3. 执行第一个查询 —— SELECT
# ============================================================
log("")
log("=" * 55)
log("步骤 3: 执行第一个查询 SELECT * FROM users")
log("=" * 55)

# execute() → 执行 SQL
# fetchall() → 获取所有结果（返回元组列表）
# fetchone() → 获取一条结果
# fetchmany(n) → 获取 n 条结果

sql = "SELECT * FROM users"
log(f"执行: {sql}", "SQL")
cursor.execute(sql)

# 获取所有结果
users = cursor.fetchall()
log(f"查询到 {len(users)} 条用户记录", "PASS")

# 打印结果
log("")
log("查询结果：", "INFO")
for user in users:
    # cursor 默认返回元组，按列顺序取值
    log(f"  ID={user[0]:<3} | 用户名={user[1]:<6} | 邮箱={user[2]:<22} | 年龄={user[4]}", "INFO")


# ============================================================
# 4. 获取列信息 —— 面试可能问"怎么拿到表结构"
# ============================================================
log("")
log("=" * 55)
log("步骤 4: 获取查询结果的列信息")
log("=" * 55)

# cursor.description 返回每个列的元信息
# 每个列是一个元组: (name, type_code, display_size, internal_size, precision, scale, null_ok)
log(f"共 {len(cursor.description)} 列:", "INFO")
for col in cursor.description:
    log(f"  列名: {col[0]:<15} | 类型码: {col[1]}", "INFO")


# ============================================================
# 5. 条件查询 —— WHERE + 参数化（防 SQL 注入！）
# ============================================================
log("")
log("=" * 55)
log("步骤 5: 参数化查询 —— 防 SQL 注入的关键")
log("=" * 55)

# ❌ 错误做法（SQL 注入风险！）：
#    sql = f"SELECT * FROM users WHERE age > {user_input}"
#    cursor.execute(sql)
#
# ✅ 正确做法（参数化查询）：
#    用 %s 做占位符，参数单独传，pymysql 自动转义

min_age = 25
sql = "SELECT username, email, age FROM users WHERE age > %s"
log(f"执行: {sql}  ← %s = {min_age}", "SQL")
cursor.execute(sql, (min_age,))  # 注意：参数必须是元组 (value,)

results = cursor.fetchall()
log(f"年龄 > {min_age} 的用户有 {len(results)} 人:", "PASS")
for row in results:
    log(f"  {row[0]:<6} | {row[1]:<22} | {row[2]}岁", "INFO")


# ============================================================
# 6. 查询总数 —— COUNT
# ============================================================
log("")
log("=" * 55)
log("步骤 6: 聚合查询 —— COUNT / SUM / AVG")
log("=" * 55)

# 每个表的数据量
tables = ["users", "products", "orders"]
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    log(f"  {table} 表: {count} 条记录", "INFO")


# ============================================================
# 7. 用 DictCursor 返回字典（更直观）
# ============================================================
log("")
log("=" * 55)
log("步骤 7: DictCursor —— 用字段名取值，不用数索引")
log("=" * 55)

# 面试会话：普通 Cursor vs DictCursor
#  - 普通 Cursor: row[0], row[1] ... 依赖列顺序，容易出错
#  - DictCursor:  row['username'], row['email'] ... 用列名，更可读
#  代价：DictCursor 稍慢一点（几乎忽略不计）

dict_conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
dict_cursor = dict_conn.cursor()

dict_cursor.execute("SELECT id, username, email, age FROM users WHERE id = %s", (1,))
user = dict_cursor.fetchone()

log(f"用户名: {user['username']}  ← 用字段名取值！", "PASS")
log(f"邮箱:   {user['email']}", "PASS")
log(f"年龄:   {user['age']}", "PASS")

dict_cursor.close()
dict_conn.close()


# ============================================================
# 8. 关闭连接 —— 记得关！不然连接池会耗尽
# ============================================================
log("")
log("=" * 55)
log("步骤 8: 关闭游标 + 关闭连接")
log("=" * 55)

cursor.close()
conn.close()
log("游标已关闭", "INFO")
log("连接已关闭", "INFO")

log("")
log("=" * 55)
log("🎉 第一个 MySQL 连接脚本完成！", "PASS")
log("=" * 55)
log("你已掌握: 连接数据库 → 创建游标 → 执行查询 → 读取结果 → 关闭连接", "INFO")
log("下一步: 02_crud_testing.py —— 增删改查 + 断言", "INFO")
