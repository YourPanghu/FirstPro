"""
一键运行所有测试
=================
python run_all.py

生成的 test_report.json 可以给 Postman/Newman 做数据驱动
"""

"""
    json：处理 JSON 数据的序列化与反序列化，用于保存测试报告。
    os：用于文件路径操作，生成报告文件时获取当前脚本目录。
    sys：用于重新配置标准输出的编码，sys.stdout.reconfigure(encoding='utf-8') 确保控制台能正常显示中文，避免打印乱码。
    time：用于计算每个请求的耗时（毫秒级）。
    requests：发送 HTTP 请求的核心库。
"""
import json
import os
import sys
import time
import requests
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://jsonplaceholder.typicode.com"


# --- 辅助函数 ---
"""
    assert_field：断言字典 data 中包含指定字段 field，否则抛出 AssertionError。
    assert_all：断言可迭代对象 items 中的所有元素都满足条件 predicate。例如，验证所有返回的文章都属于某个 userId。
这两个函数作为自定义验证函数，可以在 run_test 的 validate 参数中使用。
"""
def assert_field(data, field):
    assert field in data, f"缺少字段: {field}"

def assert_all(items, predicate):
    assert all(predicate(item) for item in items), "有数据不满足条件"


# 测试结果收集
results = []
passed = 0
failed = 0

"""
    name：测试用例名称，用于报告输出。
    method：HTTP 方法，如 "GET"、"POST"。
    url：API 路径（相对于 BASE_URL），函数内部会拼接完整 URL。
    **kwargs：接收任意额外的关键字参数，这些参数会直接传递给 requests.request。常见的如 params（查询参数）、json（请求体）、headers 等。
"""

def run_test(name, method, url, **kwargs):
    """执行一次测试并记录结果"""
    global passed, failed
    """
        使用 kwargs.pop("expected_status", 200) 从 kwargs 中移除并获取期望状态码，默认为 200。
        使用 kwargs.pop("validate", None) 获取自定义验证函数（如果有）。
        剩余的 kwargs 直接传给 requests.request。
    """
    expected_status = kwargs.pop("expected_status", 200)
    validate = kwargs.pop("validate", None)

    """
        start = time.time() 记录开始时间，请求完成后计算耗时并转换为毫秒（(当前时间 - 开始时间) * 1000）。
    """
    start = time.time()
    try:
        """
            requests.request(method, f"{BASE_URL}{url}", **kwargs) 是一个通用请求方法，根据 method 参数决定使用 GET、POST 等。
        """
        resp = requests.request(method, f"{BASE_URL}{url}", **kwargs)
        elapsed = round((time.time() - start) * 1000, 2)  # ms

        # 状态码断言
        assert resp.status_code == expected_status, (
            f"期望 {expected_status}，实际 {resp.status_code}"
        )

        # 自定义验证
        """
            如果提供了 validate 函数，则调用它并传入 resp 对象。validate 内部可以包含 assert_field、assert_all 或其他断言。
        """
        if validate:
            validate(resp)

        passed += 1
        results.append({
            "name": name, "method": method, "url": url,
            "status": "PASS", "status_code": resp.status_code,
            "elapsed_ms": elapsed
        })
        print(f"  ✅ {name} ({elapsed}ms)")

    except AssertionError as e:
        failed += 1
        results.append({
            "name": name, "method": method, "url": url,
            "status": "FAIL", "error": str(e),
            "elapsed_ms": round((time.time() - start) * 1000, 2)
        })
        print(f"  ❌ {name}: {e}")

    except Exception as e:
        failed += 1
        results.append({
            "name": name, "method": method, "url": url,
            "status": "ERROR", "error": str(e),
            "elapsed_ms": 0
        })
        print(f"  💥 {name}: {e}")


print("=" * 60)
print("🚀 开始执行 API 自动化测试套件")
print(f"   时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print()

# --- GET 请求 ---
print("[GET 测试]")
run_test("获取所有文章", "GET", "/posts")
"""
    使用 validate 验证返回的 JSON 中包含 title 字段。
    lambda r: assert_field(r.json(), "title") 是一个 lambda 函数，用于验证返回的 JSON 中包含 title 字段。
"""
run_test("获取单篇文章", "GET", "/posts/1",
         validate=lambda r: assert_field(r.json(), "title"))
run_test("获取不存在的文章", "GET", "/posts/99999", expected_status=404)
run_test("按 userId 过滤", "GET", "/posts", params={"userId": 1},
         validate=lambda r: assert_all(r.json(), lambda p: p["userId"] == 1))

# --- POST 请求 ---
print("\n[POST 测试]")
run_test("创建新文章", "POST", "/posts",
         json={"title": "测试", "body": "内容", "userId": 1},
         expected_status=201)

# --- PUT 请求 ---
print("\n[PUT 测试]")
run_test("更新文章", "PUT", "/posts/1",
         json={"id": 1, "title": "更新", "body": "新内容", "userId": 1})

# --- DELETE 请求 ---
print("\n[DELETE 测试]")
run_test("删除文章", "DELETE", "/posts/1")

# --- 汇总 ---
print()
print("=" * 60)
print(f"📊 测试结果: {passed} 通过, {failed} 失败, {passed + failed} 总计")
print(f"📈 通过率: {passed / (passed + failed) * 100:.1f}%")
print("=" * 60)

# 保存结果（可以导入 Postman 做数据驱动）
report_path = os.path.join(os.path.dirname(__file__), "test_report.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n📄 报告已保存: {report_path}")
