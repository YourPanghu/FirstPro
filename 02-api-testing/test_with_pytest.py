"""
Pytest 测试框架实战
====================
pytest 是 Python 最流行的测试框架，面试必问！

安装: pip install pytest

运行: pytest test_with_pytest.py -v
      pytest test_with_pytest.py -v --html=report.html  (生成 HTML 报告)
"""
import pytest
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://jsonplaceholder.typicode.com"


# ============================================================
# 1. fixture: 测试前置准备
# ============================================================
@pytest.fixture
def sample_post_data():
    """准备测试用的文章数据（像 Postman 的 Pre-request Script）"""
    return {
        "title": "Pytest 测试文章",
        "body": "这是 fixture 生成的测试数据",
        "userId": 1
    }


@pytest.fixture
def created_post(sample_post_data):
    """创建一篇文章，测试完自动不删除（这个 API 是假的所以不会真创建）"""
    resp = requests.post(f"{BASE_URL}/posts", json=sample_post_data)
    assert resp.status_code == 201
    return resp.json()


# ============================================================
# 2. 测试用例: GET 请求
# ============================================================
class TestGetPosts:
    """测试 GET 请求相关接口"""

    def test_get_all_posts(self):
        """获取所有文章"""
        resp = requests.get(f"{BASE_URL}/posts")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_get_post_by_id(self):
        """获取单篇文章"""
        resp = requests.get(f"{BASE_URL}/posts/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert "title" in data

    def test_get_post_not_found(self):
        """获取不存在的文章应返回 404"""
        resp = requests.get(f"{BASE_URL}/posts/99999")
        assert resp.status_code == 404

    @pytest.mark.parametrize("post_id,expected_user_id", [
        (1, 1),
        (2, 1),
        (10, 1),
        (20, 2),
    ])
    def test_post_user_id(self, post_id, expected_user_id):
        """数据驱动测试：验证不同文章的 userId"""
        resp = requests.get(f"{BASE_URL}/posts/{post_id}")
        assert resp.status_code == 200
        assert resp.json()["userId"] == expected_user_id


# ============================================================
# 3. 测试用例: POST 请求
# ============================================================
class TestCreatePost:
    """测试创建文章"""

    def test_create_post_success(self, sample_post_data):
        """创建文章成功"""
        resp = requests.post(f"{BASE_URL}/posts", json=sample_post_data)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == sample_post_data["title"]
        assert "id" in data

    def test_create_post_missing_title(self):
        """缺少必填字段 title"""
        resp = requests.post(f"{BASE_URL}/posts", json={"body": "test"})
        # jsonplaceholder 不验证，但真实项目应该返回 400
        # 这里演示的是测试思路
        assert resp.status_code in [201, 400], f"状态码: {resp.status_code}"

    @pytest.mark.parametrize("field", ["title", "body", "userId"])
    def test_create_post_required_fields_in_response(self, field, sample_post_data):
        """创建的响应中应包含所有提交的字段"""
        resp = requests.post(f"{BASE_URL}/posts", json=sample_post_data)
        assert resp.status_code == 201
        assert field in resp.json(), f"响应中缺少字段: {field}"


# ============================================================
# 4. 测试用例: DELETE 和异常场景
# ============================================================
class TestDeletePost:
    """测试删除文章"""

    def test_delete_post(self):
        """删除文章"""
        resp = requests.delete(f"{BASE_URL}/posts/1")
        assert resp.status_code == 200


# ============================================================
# 5. 运行说明
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("运行 Pytest 测试:")
    print("  pytest test_with_pytest.py -v")
    print("")
    print("生成 HTML 报告:")
    print("  pip install pytest-html")
    print("  pytest test_with_pytest.py -v --html=report.html")
    print("=" * 55)
    pytest.main([__file__, "-v"])
