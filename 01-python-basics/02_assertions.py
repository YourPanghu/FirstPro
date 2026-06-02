"""
02 - 断言：测试工程师的核心技能
=================================
断言是自动化测试的核心 —— 让程序替你判断结果对不对
面试高频考点！一定要掌握
"""

# ============================================================
# 1. 最基本的 assert
# ============================================================
print("=" * 60)
print("1. assert 基本用法")
print("=" * 60)

status_code = 200
assert status_code == 200  # 通过，什么都不发生

# 如果断言失败会怎样？
# assert status_code == 404  # ❌ 会抛出 AssertionError
print("✅ assert 200 == 200 通过")
print()


# ============================================================
# 2. assert + 错误信息（推荐写法！）
# ============================================================
print("=" * 60)
print("2. 带错误信息的断言（面试官喜欢看你这么写）")
print("=" * 60)

actual = 150
expected = 200
# assert actual == expected, f"状态码错误！期望 {expected}，实际 {actual}"
print("   提示：取消上面一行的注释看看断言失败的提示")
print()


# ============================================================
# 3. 常用的断言类型
# ============================================================
print("=" * 60)
print("3. 接口测试常用的断言")
print("=" * 60)

# 模拟一个 API 响应
response_data = {
    "code": 0,
    "message": "success",
    "data": {
        "user_id": 1001,
        "username": "test_user",
        "email": "test@example.com",
        "age": 25,
        "tags": ["vip", "active"],
        "balance": 99.50,
        "is_active": True,
        "avatar_url": "https://cdn.example.com/avatar.jpg",
        "created_at": "2026-05-30T10:00:00Z"
    }
}

# --- 断言 1: 状态码/业务码 ---
assert response_data["code"] == 0, "业务码不正确"
print("✅ code 断言通过")

# --- 断言 2: 字符串相等 ---
assert response_data["message"] == "success", "message 不正确"
print("✅ message 断言通过")

# --- 断言 3: 包含判断 ---
assert "@" in response_data["data"]["email"], "邮箱格式不正确"
print("✅ 邮箱包含 @ 断言通过")

# --- 断言 4: 数字比较 ---
assert response_data["data"]["age"] >= 18, "用户未满 18 岁"
print("✅ 年龄断言通过")

# --- 断言 5: 类型检查 ---
assert isinstance(response_data["data"]["balance"], (int, float)), "余额应该是数字"
print("✅ 余额类型断言通过")

# --- 断言 6: 布尔值 ---
assert response_data["data"]["is_active"] is True, "用户应该处于激活状态"
print("✅ is_active 断言通过")

# --- 断言 7: 列表/数组 ---
assert len(response_data["data"]["tags"]) > 0, "tags 列表不能为空"
assert "vip" in response_data["data"]["tags"], "tags 中应包含 vip"
print("✅ tags 断言通过")

# --- 断言 8: 字符串模式 ---
assert response_data["data"]["avatar_url"].startswith("https://"), "URL 应该是 HTTPS"
assert response_data["data"]["avatar_url"].endswith(".jpg"), "图片应该是 jpg 格式"
print("✅ avatar_url 断言通过")

print()
print("🎉 这些断言覆盖了接口测试 90% 的场景！")