"""
04 - Pytest + Selenium 整合
=============================
企业级测试框架的标准配置

特点:
  1. conftest.py 管理 driver，测试用例自动获得浏览器
  2. 失败自动截图
  3. 生成 HTML 报告
  4. 支持参数化数据驱动

运行:
  pytest 04_pytest_selenium.py -v
  pytest 04_pytest_selenium.py -v --html=reports/selenium_report.html
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://www.selenium.dev/selenium/web"


# ============================================================
# Page Object: Selenium 测试站
# ============================================================
class WebFormPage:
    URL = f"{BASE_URL}/web-form.html"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.URL)

    def get_title(self):
        return self.driver.title

    def fill_text(self, text):
        elem = self.wait.until(EC.visibility_of_element_located((By.ID, "my-text-id")))
        elem.clear()
        elem.send_keys(text)

    def fill_password(self, pw):
        elem = self.wait.until(EC.visibility_of_element_located((By.NAME, "my-password")))
        elem.clear()
        elem.send_keys(pw)

    def submit(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]"))).click()

    def get_text_value(self):
        return self.driver.find_element(By.ID, "my-text-id").get_attribute("value")


# ============================================================
# 1. Pytest Fixture: 管理浏览器
# ============================================================
@pytest.fixture(scope="function")
def driver():
    """每个测试用例自动获得一个全新的浏览器，测试完自动关闭"""
    options = Options()
    options.add_argument("--window-size=1920,1080")
    # 本地调试不想看到浏览器窗口可以取消下面这行注释
    options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    yield driver

    driver.quit()


@pytest.fixture
def form_page(driver):
    """提供已打开的表单页"""
    page = WebFormPage(driver)
    page.open()
    return page


# ============================================================
# 2. 失败自动截图
# ============================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            filename = f"FAILED_{item.name}_{time.strftime('%H%M%S')}.png"
            filepath = os.path.join(screenshot_dir, filename)
            driver.save_screenshot(filepath)
            print(f"\n📸 失败截图: {filepath}")


# ============================================================
# 3. 测试用例
# ============================================================
class TestWebForm:
    """Web 表单测试套件"""

    def test_open_form(self, form_page):
        """测试：打开表单页"""
        assert "Web form" in form_page.get_title()

    def test_fill_text(self, form_page):
        """测试：填写文本输入框"""
        form_page.fill_text("Hello Selenium")
        assert form_page.get_text_value() == "Hello Selenium"

    @pytest.mark.parametrize("text", [
        "测试数据1",
        "Pytest自动化",
        "Selenium面试题",
    ])
    def test_fill_multiple_texts(self, form_page, text):
        """数据驱动：用不同文本填写表单"""
        form_page.fill_text(text)
        assert form_page.get_text_value() == text

    def test_submit_form(self, form_page):
        """测试：填写并提交表单"""
        form_page.fill_text("测试用户")
        form_page.fill_password("password123")
        form_page.submit()

        # 等待提交完成
        WebDriverWait(form_page.driver, 10).until(
            lambda d: "submitted-form" in d.current_url
        )
        assert "submitted-form" in form_page.driver.current_url

    def test_empty_form_submit(self, form_page):
        """测试：空表单提交（也应能成功）"""
        form_page.submit()
        WebDriverWait(form_page.driver, 10).until(
            lambda d: "submitted-form" in d.current_url
        )
        assert "Received" in form_page.driver.find_element(By.TAG_NAME, "body").text



class TestWebNavigation:
    """页面导航测试"""

    def test_page_has_correct_url(self, form_page):
        """测试：URL 是否正确"""
        assert "web-form.html" in form_page.driver.current_url

    def test_form_elements_exist(self, form_page):
        """测试：关键元素存在"""
        elements = [
            (By.ID, "my-text-id"),
            (By.NAME, "my-password"),
            (By.CSS_SELECTOR, "button[type=submit]"),
        ]
        for by, value in elements:
            elem = form_page.driver.find_element(by, value)
            assert elem is not None, f"元素不存在: {by}={value}"


# ============================================================
# 运行说明
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Pytest + Selenium 运行命令:")
    print("=" * 60)
    print()
    print("  # 普通运行")
    print("  pytest 04_pytest_selenium.py -v")
    print()
    print("  # 生成 HTML 报告")
    print("  pytest 04_pytest_selenium.py -v --html=reports/selenium_report.html")
    print()
    print("  # 只跑一个类")
    print("  pytest 04_pytest_selenium.py::TestWebForm -v")
    print()
    print("  # 失败时显示详细信息")
    print("  pytest 04_pytest_selenium.py -v --tb=long")
    print()
    print("=" * 60)

    pytest.main([__file__, "-v", "--tb=short"])
