"""
模拟01测试脚本
=================
用Python发HTTP请求、检查响应状态码和响应头
这是做接口测试最基本的技能 —— 把 Postman 的操作变成代码
"""

import json
import requests

print("=" * 60)
print("1. GET 请求 - 获取数据")
print("=" * 60)

url = "http://www.baidu.com"
response = requests.get(url)

"""
百度服务器返回的 HTTP 响应头 Content-Type: text/html 没有带 charset=utf-8。
requests 库在自动检测编码时，可能没有正确识别出 UTF-8，而是用了其他编码（比如 ISO-8859-1）去解码页面内容。
结果 response.text 里的中文字符全部变成了乱码，所以断言 "百度" in data 自然失败。
"""
response.encoding = 'utf-8' # 这里手动设置响应编码为 utf-8

print(f'URL: {url}')
print(f'请求方法: GET')
print()

print("=" * 60)
print("2. 检查状态码")
print("=" * 60)

print(f'状态码: {response.status_code}')
print(f'状态描述: {response.reason}')

# 断言：这就是"自动化验证"的核心
assert response.status_code == 200, f"× 期望 200，实际 {response.status_code}"
print("√ 状态码断言通过：200 OK")
print()

print("=" * 60)
print("3. 查看响应头 —— Fiddler 里看到的东西")
print("=" * 60)

for key, value in response.headers.items():
    if key.lower() in ["content-type", "content-length", "server", "date"]:
        print(f"  {key}: {value}")
print()

print("=" * 60)
print("4. 查看响应体 —— 返回的 HTML 源码（前500字符）")
print("=" * 60)

# data = response.json() 百度首页传过来的是 HTML 文本，不是 JSON 数据，所以这里会报错
data = response.text
print(data[:500])
print()

print("=" * 60)
print("5. 提取字段做断言 —— 检查返回值对不对")
print("=" * 60)

assert "百度" in data, f"× 期望包含 '百度'，实际不包含"
print("√ 包含 '百度' 断言通过")
print()

print("🎉 恭喜！你已经完成了第一个网页自动化测试脚本！")
