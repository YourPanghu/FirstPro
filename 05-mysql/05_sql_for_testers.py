"""
05 - SQL 查询 —— 测试工程师必备 SQL 技能
=========================================
面试中经常让你"写一条 SQL 查出 XX"
本文件整理了测试工作中最常用的 20+ 条 SQL 查询

建议：每条都自己敲一遍，不要复制粘贴
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


def run_sql(title, sql, params=None):
    """执行 SQL 并打印结果"""
    print()
    log(f"💾 {title}", "STEP")
    log(f"   SQL: {sql.strip()}", "SQL")
    cursor.execute(sql, params)
    results = cursor.fetchall()
    if results:
        # 打印列名
        cols = list(results[0].keys())
        log(f"   结果 ({len(results)} 行):", "INFO")
        for row in results:
            values = " | ".join(str(row[c]) for c in cols)
            log(f"   {values}", "INFO")
    else:
        log("   (无结果)", "INFO")
    return results


log("=" * 55)
log("测试工程师必备 SQL 查询手册")
log("=" * 55)

# ============================================================
# 一、基础查询
# ============================================================
log("")
log("🔹 一、基础查询", "STEP")

run_sql("1. 查询所有用户",
    "SELECT * FROM users")

run_sql("2. 查询指定列（避免 SELECT *）",
    "SELECT id, username, email, age FROM users")

run_sql("3. WHERE 等值条件",
    "SELECT * FROM users WHERE age = 25")

run_sql("4. WHERE 范围条件",
    "SELECT * FROM users WHERE age BETWEEN 25 AND 30")

run_sql("5. WHERE IN 条件",
    "SELECT * FROM users WHERE id IN (1, 3, 5)")

run_sql("6. LIKE 模糊查询",
    "SELECT * FROM products WHERE name LIKE '%iPhone%'")

run_sql("7. ORDER BY 排序（降序）",
    "SELECT name, price FROM products ORDER BY price DESC LIMIT 5")

run_sql("8. LIMIT 分页（第1页，每页3条）",
    "SELECT * FROM users LIMIT 3 OFFSET 0")

# ============================================================
# 二、聚合函数
# ============================================================
log("")
log("🔹 二、聚合函数", "STEP")

run_sql("9. COUNT —— 统计行数",
    "SELECT status, COUNT(*) AS cnt FROM orders GROUP BY status")

run_sql("10. SUM —— 求和",
    "SELECT SUM(total_price) AS total_revenue FROM orders WHERE status != '已取消'")

run_sql("11. AVG —— 平均值",
    "SELECT category, ROUND(AVG(price), 2) AS avg_price FROM products GROUP BY category")

run_sql("12. MAX/MIN —— 最大最小值",
    "SELECT MAX(price) AS max_price, MIN(price) AS min_price FROM products WHERE status = '上架'")

run_sql("13. GROUP BY + HAVING（分组后过滤）",
    "SELECT user_id, COUNT(*) AS cnt FROM orders GROUP BY user_id HAVING cnt >= 2")

# ============================================================
# 三、JOIN 联表查询
# ============================================================
log("")
log("🔹 三、JOIN 联表查询", "STEP")

run_sql("14. INNER JOIN —— 两表交集",
    """SELECT o.id, u.username, p.name, o.quantity, o.total_price
       FROM orders o
       INNER JOIN users u ON o.user_id = u.id
       INNER JOIN products p ON o.product_id = p.id
       ORDER BY o.id""")

run_sql("15. LEFT JOIN —— 左表全保留",
    """SELECT u.username, COUNT(o.id) AS order_count
       FROM users u
       LEFT JOIN orders o ON u.id = o.user_id
       GROUP BY u.id, u.username
       ORDER BY order_count DESC""")

# ============================================================
# 四、子查询
# ============================================================
log("")
log("🔹 四、子查询", "STEP")

run_sql("16. 子查询（查出消费超过平均值的订单）",
    """SELECT id, user_id, total_price
       FROM orders
       WHERE total_price > (SELECT AVG(total_price) FROM orders)""")

run_sql("17. EXISTS 子查询（有订单的用户）",
    """SELECT username, email FROM users u
       WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id)""")

# ============================================================
# 五、常用函数
# ============================================================
log("")
log("🔹 五、常用函数", "STEP")

run_sql("18. CONCAT —— 拼接字符串",
    "SELECT CONCAT(username, ' <', email, '>') AS contact FROM users")

run_sql("19. COALESCE —— 处理 NULL",
    "SELECT username, COALESCE(phone, '未填写') AS phone_display FROM users")

run_sql("20. CASE WHEN —— 条件判断（年龄段分组）",
    """SELECT username, age,
       CASE
         WHEN age < 25 THEN '25岁以下'
         WHEN age BETWEEN 25 AND 30 THEN '25-30岁'
         ELSE '30岁以上'
       END AS age_group
       FROM users""")

# ============================================================
# 六、数据验证常用查询
# ============================================================
log("")
log("🔹 六、测试工程师常用的数据验证查询", "STEP")

run_sql("21. 检查重复数据",
    """SELECT email, COUNT(*) AS cnt
       FROM users GROUP BY email HAVING cnt > 1""")

run_sql("22. 检查空值",
    "SELECT * FROM users WHERE phone IS NULL OR phone = ''")

# Python 字符串字面量中，单引号或双引号定义的字符串不能直接跨多行，因此这里用了""" """" 方便换行，如果强行用双引号写成多行，Python 会报语法错误
run_sql("23. 检查状态分布（测试数据完整性）",
    """SELECT status, COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 1) AS pct
       FROM orders GROUP BY status ORDER BY cnt DESC""")

run_sql("24. 检查商品库存预警",
    "SELECT name, stock FROM products WHERE stock < 50 AND status = '上架'")

# ============================================================
# 总结
# ============================================================
cursor.close()
conn.close()

log("")
log("=" * 55)
log("📝 面试高频 SQL 速记", "STEP")
log("=" * 55)
log("1. 查重复:  SELECT col, COUNT(*) ... GROUP BY ... HAVING COUNT(*) > 1", "INFO")
log("2. 查第N高:  SELECT ... ORDER BY ... DESC LIMIT 1 OFFSET N-1", "INFO")
log("3. 分页:     SELECT ... LIMIT page_size OFFSET (page-1)*page_size", "INFO")
log("4. JOIN:    INNER JOIN(交集) vs LEFT JOIN(左表全保留)", "INFO")
log("5. 子查询:  用在 WHERE / FROM / SELECT 里都可以", "INFO")
log("6. 聚合:    GROUP BY ... HAVING (分组后过滤)", "INFO")
log("7. NULL处理: COALESCE(col, '默认值') 或 IS NULL / IS NOT NULL", "INFO")
log("8. 条件:    CASE WHEN ... THEN ... ELSE ... END", "INFO")
