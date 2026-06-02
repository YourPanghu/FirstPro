"""
01 - 你的第一个测试脚本
========================
学会用 Python 发 HTTP 请求、检查响应状态码和响应头
这是做接口测试最基本的技能 —— 把 Postman 的操作变成代码
"""

import requests
import json

# ============================================================
# 1. 发送 GET 请求（就像在 Postman 里点 Send）
# ============================================================
print("=" * 60)
print("1. GET 请求 - 获取数据")
print("=" * 60)

url = "https://jsonplaceholder.typicode.com/posts/1"
response = requests.get(url)

print(f"URL: {url}")
print(f"请求方法: GET")
print()


# ============================================================
# 2. 检查状态码 —— 测试工程师最常做的事
# ============================================================
print("=" * 60)
print("2. 检查状态码")
print("=" * 60)

print(f"状态码: {response.status_code}")
print(f"状态描述: {response.reason}")

# 断言：这就是"自动化验证"的核心
assert response.status_code == 200, f"❌ 期望 200，实际 {response.status_code}"
print("✅ 状态码断言通过：200 OK")
print()


# ============================================================
# 3. 查看响应头 —— Fiddler 里看到的东西
# ============================================================
print("=" * 60)
print("3. 响应头（跟 Fiddler 抓包看到的一样）")
print("=" * 60)

for key, value in response.headers.items():
    if key.lower() in ["content-type", "content-length", "server", "date"]:
        print(f"  {key}: {value}")
print()


# ============================================================
# 4. 查看响应体 —— 接口返回的 JSON 数据
# ============================================================
print("=" * 60)
print("4. 响应体（JSON 数据）")
print("=" * 60)

data = response.json()
print(json.dumps(data, indent=2, ensure_ascii=False))
print()


# ============================================================
# 5. 提取字段做断言 —— 检查返回值对不对
# ============================================================
print("=" * 60)
print("5. 字段断言")
print("=" * 60)

print(f"userId: {data['userId']}")
print(f"id: {data['id']}")
print(f"title: {data['title']}")

assert data["userId"] == 1, f"❌ userId 不正确"
assert data["id"] == 1, f"❌ id 不正确"
assert isinstance(data["title"], str), f"❌ title 应该是字符串"

print("✅ 所有字段断言通过！")
print()

print("🎉 恭喜！你已经完成了第一个接口自动化测试脚本！")
print("   这个脚本做的事情 = Postman Send → 看状态码 → 看响应头 → 看返回值")