"""
01 - 第一个 Selenium 自动化脚本
==================================
打开百度 → 搜索关键词 → 检查结果 → 截图保存

这个脚本做的事情：
  Postman → 发请求、看响应
  Selenium → 打开浏览器、操作页面、看页面内容
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


def setup_driver():
    """初始化浏览器驱动"""
    options = Options()
    # options.add_argument("--headless")      # 无头模式（后台运行，不显示窗口）
    options.add_argument("--no-sandbox")
    # 避免共享内存 /dev/shm 太小导致崩溃，常见于 Docker
    options.add_argument("--disable-dev-shm-usage")
    # 固定窗口为 1920×1080，保证元素布局和截图一致
    options.add_argument("--window-size=1920,1080")

    # webdriver-manager 自动下载匹配的 ChromeDriver，不用手动管理版本！
    # Service(...)：封装 ChromeDriver 可执行文件的路径和启动方式
    service = Service(ChromeDriverManager().install())
    # 用配置好的驱动和选项启动 Chrome，得到 driver 对象
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def test_baidu_search():
    """
    测试用例：百度搜索
    步骤：
      1. 打开百度首页
      2. 在搜索框输入关键词
      3. 点击搜索按钮
      4. 检查搜索结果页面标题
      5. 截图保存
    """
    print("=" * 60)
    print("测试用例: 百度搜索 'Selenium 自动化测试'")
    print("=" * 60)

    driver = setup_driver()

    try:
        # --- 步骤 1: 打开网页 ---
        print("\n📋 步骤 1: 打开百度首页")
        driver.get("https://www.baidu.com")
        print(f"   当前 URL: {driver.current_url}")
        print(f"   页面标题: {driver.title}")

        # --- 步骤 2: 定位搜索框，输入文字 ---
        print("\n📋 步骤 2: 定位搜索框，输入关键词")
        # 定位方式: By.ID ("kw" 是百度搜索框的 id)
#        search_box = driver.find_element(By.ID, "kw")
        search_box = driver.find_element(By.ID, "chat-textarea")
        search_box.clear()
        search_box.send_keys("Selenium 自动化测试")
        print("   已输入: Selenium 自动化测试")

        # --- 步骤 3: 点击搜索按钮 ---
        print("\n📋 步骤 3: 点击搜索按钮")
#        search_btn = driver.find_element(By.ID, "su")
        search_btn = driver.find_element(By.ID, "chat-submit-button")
        search_btn.click()
        print("   已点击搜索")

        # 等待页面加载
        time.sleep(2)

        # --- 步骤 4: 检查结果 ---
        print("\n📋 步骤 4: 检查搜索结果")
        new_title = driver.title
        print(f"   搜索结果页标题: {new_title}")

        # 断言: 标题应该包含搜索关键词
        assert "Selenium" in new_title or "百度" in new_title, (
            f"标题不符合预期: {new_title}"
        )
        print("   ✅ 标题断言通过")

        # 查找搜索结果元素
        results = driver.find_elements(By.CSS_SELECTOR, ".result, .c-container")
        print(f"   找到 {len(results)} 条搜索结果")

        if len(results) > 0:
            # 打印第一条结果
            first_result = results[0].text[:100].replace("\n", " ")
            print(f"   第一条结果: {first_result}...")

        assert len(results) > 0, "没有找到搜索结果"
        print("   ✅ 搜索结果断言通过")

        # --- 步骤 5: 截图 ---
        print("\n📋 步骤 5: 截图保存")
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        screenshot_path = os.path.join(SCREENSHOT_DIR, "baidu_search.png")
        driver.save_screenshot(screenshot_path)
        print(f"   截图已保存: {screenshot_path}")

        print()
        print("=" * 60)
        print("✅ 测试用例全部通过！")
        print("=" * 60)

    except Exception as e:
        # 失败时也截图，方便排查
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        error_path = os.path.join(SCREENSHOT_DIR, "error_screenshot.png")
        driver.save_screenshot(error_path)
        print(f"\n❌ 测试失败！错误截图: {error_path}")
        raise e

    finally:
        # 无论成功失败都要关闭浏览器
        driver.quit()
        print("\n浏览器已关闭")


if __name__ == "__main__":
    test_baidu_search()
