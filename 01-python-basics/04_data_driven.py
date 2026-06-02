"""
04 - 数据驱动测试
==================
面试高频考点！面试官问"怎么做数据驱动"就看这个

核心思想: 把测试数据从代码里分离出来，同一套逻辑跑多组数据
Postman 里叫 CSV/JSON Data File → 用 Collection Runner 跑
Python 里叫 参数化测试 → 用循环或 pytest 的 @parametrize
"""

import requests

# ============================================================
# 1. 传统方式：一个用例写一个函数（重复代码很多）
# ============================================================

# ❌ 不好的写法：
# def test_user_1():
#     resp = requests.get("https://api.example.com/users/1")
#     assert resp.status_code == 200
# def test_user_2():
#     resp = requests.get("https://api.example.com/users/2")
#     assert resp.status_code == 200
# def test_user_3():
#     ...  # 重复！重复！重复！


# ============================================================
# 2. 数据驱动方式：数据是数据，逻辑是逻辑
# ============================================================
print("=" * 60)
print("数据驱动测试 - 用一组数据跑同一套逻辑")
print("=" * 60)


def test_get_post(post_id, expected_user_id, expected_title_contains):
    """
    一个通用的测试函数，用不同数据调用它

    参数:
        post_id: 文章ID
        expected_user_id: 期望的作者ID
        expected_title_contains: 标题中应包含的关键词
    """
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    resp = requests.get(url)

    assert resp.status_code == 200, f"状态码错误: {resp.status_code}"

    data = resp.json()
    assert data["id"] == post_id, f"id 不匹配"
    assert data["userId"] == expected_user_id, f"userId 不匹配"
    assert expected_title_contains in data["title"], (
        f"标题中未找到 '{expected_title_contains}': {data['title']}"
    )

    print(f"  ✅ post_id={post_id} 测试通过 | userId={data['userId']}")


# 测试数据 —— 这就是数据驱动的"数据"
test_data = [
    # (post_id, expected_user_id, expected_title_contains)
    (1,  1,  "sunt"),
    (2,  1,  "qui"),
    # (3,  1,  "dolorem"),
    (10, 1,  "optio"),
    (20, 2,  "dolor"),
    # (30, 3,  "nihil"),
    (40, 4,  "enim"),
]

print(f"\n用 {len(test_data)} 组数据依次测试:\n")

for post_id, user_id, keyword in test_data:
    test_get_post(post_id, user_id, keyword)

print()
print("🎉 数据驱动测试全部通过！只用了一个函数 + 一组数据")
print()


# ============================================================
# 3. 进阶：从 JSON 文件读取数据（模拟 Postman 的 Data File）
# ============================================================
print("=" * 60)
print("从 JSON 文件读取测试数据")
print("=" * 60)

# 写入测试数据文件（通常这个文件是你提前准备好的）
import json
import os

"""
    os.path.dirname(__file__) 获取当前文件的目录的绝对路径，然后拼接上 test_data.json 文件名，得到文件的绝对路径
"""
data_file = os.path.join(os.path.dirname(__file__), "test_data.json")
test_data_json = [
    {"method": "GET",    "url": "/posts/1",  "expected_status": 200},
    {"method": "GET",    "url": "/posts/99", "expected_status": 200},
    {"method": "GET",    "url": "/posts/999","expected_status": 404},  # 不存在的文章
    {"method": "POST",   "url": "/posts",    "expected_status": 201},
]

with open(data_file, "w", encoding="utf-8") as f:
    json.dump(test_data_json, f, indent=2, ensure_ascii=False)

print(f"✅ 测试数据文件已生成: {data_file}")
print(f"   这就是 Postman Data File 的 Python 版本！")
print()


# 读取并执行
with open(data_file, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

BASE_URL = "https://jsonplaceholder.typicode.com"

print(f"从文件加载了 {len(test_cases)} 条测试用例:\n")

for i, case in enumerate(test_cases, 1):
    full_url = BASE_URL + case["url"]

    if case["method"] == "GET":
        resp = requests.get(full_url)
    elif case["method"] == "POST":
        resp = requests.post(full_url, json={"title": "test", "body": "test", "userId": 1})

    try:
        assert resp.status_code == case["expected_status"], (
            f"期望 {case['expected_status']}，实际 {resp.status_code}"
        )
        print(f"  ✅ 用例 {i}: {case['method']} {case['url']} → {resp.status_code}")
    except AssertionError as e:
        print(f"  ❌ 用例 {i}: {case['method']} {case['url']} → {e}")

print()
print("🎉 JSON 数据驱动测试完成！")
print("   这套思路在面试中可以重点讲")