"""
API 自动化测试实战：CRUD 完整流程
===================================
模拟一个完整的接口测试场景：
Create(新建) → Read(查询) → Update(修改) → Delete(删除)

这 4 个操作覆盖了 80% 的接口测试工作
就像在 Postman 里按顺序发请求，然后用 Tests 标签写断言
"""
import requests
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://jsonplaceholder.typicode.com"
PRINT_PREFIX = ""


def log(msg, level="INFO"):
    """统一日志输出"""
    prefixes = {"INFO": "📋", "PASS": "✅", "FAIL": "❌", "STEP": "🔹"}
    print(f"{prefixes.get(level, '')} [{level}] {msg}")


# ============================================================
# 步骤 1: 查询列表 —— GET /posts
# ============================================================
log("=" * 55)
log("步骤 1: 查询文章列表 GET /posts")
log("=" * 55)

resp = requests.get(f"{BASE_URL}/posts")
assert resp.status_code == 200, f"状态码错误: {resp.status_code}"

posts = resp.json()
assert len(posts) > 0, "文章列表不应为空"
assert len(posts) <= 100, f"默认分页应该是 100 条，实际 {len(posts)}"

log(f"返回了 {len(posts)} 篇文章", "PASS")
log(f"第一条标题: {posts[0]['title']}", "INFO")
log(f"响应头 Content-Type: {resp.headers.get('Content-Type')}", "INFO")


# ============================================================
# 步骤 2: 查询单条 —— GET /posts/1
# ============================================================
log("")
log("=" * 55)
log("步骤 2: 查询单篇文章 GET /posts/1")
log("=" * 55)

post_id = 1
resp = requests.get(f"{BASE_URL}/posts/{post_id}")
assert resp.status_code == 200

post = resp.json()
# 验证核心字段
required_fields = ["userId", "id", "title", "body"]
for field in required_fields:
    assert field in post, f"缺少字段: {field}"
    log(f"  {field}: {str(post[field])[:50]}", "INFO")

log(f"单篇文章查询成功，包含 {len(post)} 个字段", "PASS")


# ============================================================
# 步骤 3: 创建文章 —— POST /posts
# ============================================================
log("")
log("=" * 55)
log("步骤 3: 创建新文章 POST /posts")
log("=" * 55)

new_article = {
    "title": "Python 接口自动化测试实战",
    "body": "本文介绍如何使用 Python + requests 实现接口自动化测试",
    "userId": 1
}

resp = requests.post(f"{BASE_URL}/posts", json=new_article)
assert resp.status_code == 201, f"创建应返回 201，实际 {resp.status_code}"

created = resp.json()
assert created["title"] == new_article["title"]
assert created["body"] == new_article["body"]
assert "id" in created, "新建文章应该有 id"

log(f"文章创建成功，新 ID: {created['id']}", "PASS")
log(f"返回数据: {created['title']}", "INFO")


# ============================================================
# 步骤 4: 修改文章 —— PUT /posts/1
# ============================================================
log("")
log("=" * 55)
log("步骤 4: 更新文章 PUT /posts/1")
log("=" * 55)

update_data = {
    "id": 1,
    "title": "【已更新】Python 接口自动化测试实战",
    "body": "更新后的内容：增加了 Pytest 框架的使用方法",
    "userId": 1
}

resp = requests.put(f"{BASE_URL}/posts/1", json=update_data)
assert resp.status_code == 200, f"更新应返回 200，实际 {resp.status_code}"

updated = resp.json()
assert updated["title"] == update_data["title"], (
    f"标题未更新: {updated['title']}"
)

log(f"文章更新成功", "PASS")
log(f"新标题: {updated['title']}", "INFO")


# ============================================================
# 步骤 5: 删除文章 —— DELETE /posts/1
# ============================================================
log("")
log("=" * 55)
log("步骤 5: 删除文章 DELETE /posts/1")
log("=" * 55)

resp = requests.delete(f"{BASE_URL}/posts/1")
assert resp.status_code == 200, f"删除应返回 200，实际 {resp.status_code}"

log(f"文章删除成功", "PASS")


# ============================================================
# 步骤 6: 查不存在的资源 —— 异常场景
# ============================================================
log("")
log("=" * 55)
log("步骤 6: 异常场景 —— 查询不存在的文章")
log("=" * 55)

resp = requests.get(f"{BASE_URL}/posts/99999")
assert resp.status_code == 404, f"不存在的文章应返回 404，实际 {resp.status_code}"

log("返回 404 Not Found，符合预期", "PASS")


# ============================================================
# 步骤 7: 请求参数验证 —— Query String
# ============================================================
log("")
log("=" * 55)
log("步骤 7: 带查询参数 GET /posts?userId=1")
log("=" * 55)

# 传参方式 1: 拼在 URL 里（跟 Postman 的 Params 一样）
resp = requests.get(f"{BASE_URL}/posts", params={"userId": 1})
assert resp.status_code == 200

filtered = resp.json()
# 全都要属于 userId=1
all_match = all(p["userId"] == 1 for p in filtered)
assert all_match, "过滤结果中包含其他用户的数据"

log(f"过滤出 userId=1 的文章，共 {len(filtered)} 篇", "PASS")


# ============================================================
# 总结
# ============================================================
log("")
log("=" * 55)
log("🎉 全部 7 个测试步骤通过！")
log("=" * 55)
log(f"覆盖了: GET列表 | GET单条 | POST创建 | PUT更新 | DELETE删除 | 异常场景 | 参数过滤", "INFO")
