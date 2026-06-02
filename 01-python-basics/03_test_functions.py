"""
03 - 用函数组织测试用例
========================
把测试步骤封装成函数，让代码可以复用
这是写测试框架的基础
"""

import requests


# ============================================================
# 1. 基础：一个 API 请求函数
# ============================================================
def get_api(url, expected_status=200):
    """
    发送 GET 请求并做基本断言

    参数:
        url: 请求地址
        expected_status: 期望的 HTTP 状态码

    返回:
        响应的 JSON 数据
    """
    print(f"GET {url}")
    resp = requests.get(url)

    # 核心断言
    assert resp.status_code == expected_status, (
        f"状态码错误！\n"
        f"  期望: {expected_status}\n"
        f"  实际: {resp.status_code}\n"
        f"  响应: {resp.text[:200]}"
    )

    return resp.json()


def post_api(url, body, expected_status=201):
    """
    发送 POST 请求并做基本断言
    """
    print(f"POST {url}")
    print(f"Body: {body}")
    resp = requests.post(url, json=body)

    assert resp.status_code == expected_status, (
        f"状态码错误！期望 {expected_status}，实际 {resp.status_code}"
    )

    return resp.json()


# ============================================================
# 2. 业务验证函数 —— 检查返回数据的正确性
# ============================================================
def assert_field_exists(data, field_name):
    """断言返回数据中包含某个字段"""
    assert field_name in data, f"❌ 响应中缺少字段: {field_name}"
    print(f"  ✅ 字段 {field_name} 存在: {data[field_name]}")


def assert_field_type(data, field_name, expected_type):
    """断言字段类型正确"""
    assert isinstance(data[field_name], expected_type), (
        f"❌ 字段 {field_name} 类型错误"
        f"（期望 {expected_type.__name__}，实际 {type(data[field_name]).__name__}）"
    )
    print(f"  ✅ 字段 {field_name} 类型正确: {expected_type.__name__}")


# ============================================================
# 3. 测试用例 —— 把上面组合起来
# ============================================================
def test_get_post_by_id(post_id=1):
    """
    测试用例: 获取指定 ID 的文章
    一条完整的测试用例 = 请求 + 多个断言
    """
    print(f"\n{'='*60}")
    print(f"测试用例: 获取文章 post_id={post_id}")
    print(f"{'='*60}")

    # 步骤 1: 发请求
    data = get_api(f"https://jsonplaceholder.typicode.com/posts/{post_id}")

    # 步骤 2: 验证字段存在
    assert_field_exists(data, "userId")
    assert_field_exists(data, "id")
    assert_field_exists(data, "title")
    assert_field_exists(data, "body")

    # 步骤 3: 验证字段类型
    assert_field_type(data, "userId", int)
    assert_field_type(data, "id", int)
    assert_field_type(data, "title", str)
    assert_field_type(data, "body", str)

    # 步骤 4: 验证数据正确性
    assert data["id"] == post_id, f"❌ 返回的 id 不对: {data['id']} != {post_id}"
    print(f"  ✅ id 匹配: {data['id']} == {post_id}")

    print(f"\n✅ 测试用例通过！\n")


def test_create_post():
    """
    测试用例: 创建新文章（POST 请求）
    """
    print(f"\n{'='*60}")
    print(f"测试用例: 创建新文章")
    print(f"{'='*60}")

    new_post = {
        "title": "自动化测试入门",
        "body": "这是一篇关于 Python 自动化测试的文章",
        "userId": 1
    }

    data = post_api(
        "https://jsonplaceholder.typicode.com/posts",
        new_post,
        expected_status=201  # POST 创建成功通常返回 201
    )

    assert_field_exists(data, "id")      # 新创建的文章应该返回一个 ID
    assert_field_exists(data, "title")
    assert data["title"] == new_post["title"], "标题不一致"

    print(f"\n✅ 测试用例通过！\n")


# ============================================================
# 4. 运行所有测试
# ============================================================
if __name__ == "__main__":
    print("🚀 开始执行测试用例...")
    print()

    test_get_post_by_id(1)
    test_get_post_by_id(5)
    test_create_post()

    print("=" * 60)
    print("🎉 所有测试用例执行完毕！")
    print("=" * 60)