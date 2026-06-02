"""
03 - Page Object 设计模式
============================
企业级自动化测试的标准模式，面试必问！

核心思想:
  每个页面写成一个类，页面上的元素和操作封装在类里
  测试用例只关心"做什么"，不关心"怎么找到元素"

好处:
  1. 元素定位只写一次，所有测试用例复用
  2. 页面改版，只需要改 Page 类，不用改测试用例
  3. 测试代码可读性高，像读自然语言
"""

from typing import Self


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sys
sys.stdout.reconfigure(encoding='utf-8')


# ============================================================
# 1. 基础 Page 类（所有页面的父类）
# ============================================================
class BasePage:
    """所有 Page Object 的基类，封装通用操作"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find(self, by, value):
        """查找单个元素"""
        return self.driver.find_element(by, value)

    def find_all(self, by, value):
        """查找多个元素"""
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        """点击元素"""
        self.wait.until(EC.element_to_be_clickable((by, value))).click()

    def type(self, by, value, text):
        """输入文本"""
        elem = self.wait.until(EC.visibility_of_element_located((by, value)))
        elem.clear()
        elem.send_keys(text)

    def get_text(self, by, value):
        """获取元素文本"""
        return self.wait.until(
            EC.presence_of_element_located((by, value))
        ).text

    def get_title(self):
        """获取页面标题"""
        return self.driver.title

    def get_url(self):
        """获取当前 URL"""
        return self.driver.current_url

    def wait_until_visible(self, by, value):
        """等待元素可见"""
        return self.wait.until(EC.visibility_of_element_located((by, value)))


# ============================================================
# 2. 表单页面 Page Object（Selenium 官方测试站）
# ============================================================
# WebFormPage 继承自 BasePage
class WebFormPage(BasePage):
    """Selenium 官方测试表单页"""

    URL = "https://www.selenium.dev/selenium/web/web-form.html"

    # --- 元素定位（只在这里写一次！） ---
    TEXT_INPUT = (By.ID, "my-text-id")
    PASSWORD_INPUT = (By.NAME, "my-password")
    TEXTAREA = (By.NAME, "my-textarea")
    DROPDOWN = (By.NAME, "my-select")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button[type=submit]")
    FORM_TITLE = (By.CSS_SELECTOR, "h1")

    def open(self):
        self.driver.get(self.URL)
        return self

    def fill_text(self, text):
        """
            TEXT_INPUT 是一个 元组 (tuple)，存了两个定位参数：by(By.ID) 和 value("my-text-id")
            “ * ” 叫解包运算符（unpacking operator）：将元组中的元素解包成单独的参数
            self.type(*self.TEXT_INPUT, text) 等价于：self.type(By.ID, "my-text-id", text)
        """
        self.type(*self.TEXT_INPUT, text)
        return self

    def fill_password(self, password):
        self.type(*self.PASSWORD_INPUT, password)
        return self

    def fill_textarea(self, text):
        self.type(*self.TEXTAREA, text)
        return self

    def get_page_title(self):
        return self.get_text(*self.FORM_TITLE)

    def submit(self):
        self.click(*self.SUBMIT_BTN)
        # 提交后页面变化，返回新的 Page
        return SubmissionPage(self.driver)

    def get_text_input_value(self):
        """获取已输入的值（验证用的）"""
        elem = self.find(*self.TEXT_INPUT)
        return elem.get_attribute("value")


# ============================================================
# 3. 提交结果页 Page Object
# ============================================================
class SubmissionPage(BasePage):
    """表单提交后的结果页"""

    def wait_loaded(self):
        """等待结果页加载完成"""
        self.wait_until_visible(By.CSS_SELECTOR, "body")
        return self

    def get_result_text(self):
        """获取结果页内容"""
        return self.driver.find_element(By.TAG_NAME, "body").text[:200]


# ============================================================
# 4. 百度首页 Page Object（带反自动化应对策略）
# ============================================================
class BaiduHomePage(BasePage):
    """
    百度首页 — 真实网站示例

    ⚠️ 百度对 Selenium 有检测机制，元素虽能找到但 send_keys/click 可能失败
    应对策略（写进面试里是加分项！）：
      1. execute_script JS 直接操作 DOM（绕过事件监听）
      2. ActionChains 模拟真实鼠标键盘操作
      3. CDP (Chrome DevTools Protocol) 注入防检测脚本
    """

    URL = "https://www.baidu.com"
    SEARCH_BOX = (By.ID, "kw")
    SEARCH_BTN = (By.ID, "su")

    def open(self):
        self.driver.get(self.URL)
        return self

    def search_by_js(self, keyword):
        """
        策略: 用 JS 绕过前端事件限制

        这是面试加分回答：
        "遇到 Selenium 无法交互的页面，我会用 execute_script
         直接操作 DOM，这是模拟真实用户操作失败时的降级方案"
        """
        search_box = self.find(*self.SEARCH_BOX)
        # JS 直接设置输入框值
        self.driver.execute_script(
            "arguments[0].value = arguments[1];", search_box, keyword
        )
        # JS 触发表单提交
        self.driver.execute_script(
            "document.getElementById('su').click();"
        )
        return self


# ============================================================
# 5. 测试用例：用 Page Object 写测试
# ============================================================
def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def test_webform_with_po():
    """
    用 Page Object 模式测试表单页面
    看看有什么不同：
    - 测试代码没有 By.ID, By.CSS 这些定位代码
    - 测试代码像自然语言一样可读
    """
    print("=" * 60)
    print("Page Object 模式实战: Web 表单测试")
    print("=" * 60)

    driver = setup_driver()

    try:
        # 步骤 1: 打开表单页
        print("\n📋 步骤 1: 打开表单页")
        form = WebFormPage(driver)
        form.open()
        print(f"   页面标题: {form.get_page_title()}")
        print(f"   当前 URL: {form.get_url()}")

        # 步骤 2: 填写表单
        print("\n📋 步骤 2: 填写表单")
        form.fill_text("测试用户")
        assert form.get_text_input_value() == "测试用户", "输入值不一致"
        print("   ✅ 文本输入框填写成功")

        form.fill_password("test123456")
        print("   ✅ 密码框填写成功")

        # 步骤 3: 提交
        print("\n📋 步骤 3: 提交表单")
        result = form.submit()
        result.wait_loaded()
        print(f"   提交后 URL: {result.get_url()}")
        print(f"   提交结果: {result.get_result_text()[:100]}")

        # 步骤 4: 断言
        print("\n📋 步骤 4: 验证提交结果")
        assert "Received" in result.get_result_text() or "form" in result.get_url().lower(), (
            "提交后应该收到确认"
        )
        print("   ✅ 表单提交成功")

        print()
        print("=" * 60)
        print("✅ Page Object 模式测试通过！")
        print("=" * 60)

    finally:
        driver.quit()


def test_baidu_with_js_workaround():
    """
    百度搜索测试 —— 使用 JS 绕过反自动化机制
    这展示了真实工作中遇到问题怎么解决
    """
    print()
    print("=" * 60)
    print("Page Object 实战: 百度搜索 (JS 绕过策略)")
    print("=" * 60)

    driver = setup_driver()

    try:
        home = BaiduHomePage(driver)
        home.open()
        print(f"   打开百度: {home.get_title()}")

        home.search_by_js("Page Object 设计模式")
        print("   已通过 JS 执行搜索")

        import time
        time.sleep(2)
        print(f"   搜索结果标题: {home.get_title()}")

        # 百度有反爬验证，可能弹出"百度安全验证"
        if "安全验证" in home.get_title():
            print("   ⚠️ 百度触发了安全验证（反自动化机制）")
            print("   这是真实工作中的常见问题，应对方式:")
            print("     1. 添加 Cookie/Token 绕过验证")
            print("     2. 使用 undetected-chromedriver 库")
            print("     3. 通过 CDP 注入 stealth.js")
        else:
            assert "Page Object" in home.get_title(), "搜索结果标题应包含关键词"
            print("   ✅ 搜索成功！")

    finally:
        driver.quit()


def compare_code():
    """对比有无 Page Object 的代码区别"""
    print()
    print("=" * 60)
    print("代码对比: 有无 Page Object 的区别")
    print("=" * 60)
    print("""
  ❌ 不用 Page Object:
    driver.find_element(By.ID, "my-text-id").send_keys("test")
    driver.find_element(By.NAME, "my-password").send_keys("pass")
    # 80 个测试用例里都有这些定位代码！
    # 页面改版 ID 变了？→ 改 80 个文件！

  ✅ 用 Page Object:
    form = WebFormPage(driver)
    form.fill_text("test").fill_password("pass").submit()
    # 80 个测试用例都调用 form.fill_text()
    # 页面改版？→ 只改 WebFormPage 一个类！
  """)
    print("=" * 60)


if __name__ == "__main__":
    #test_webform_with_po()
    test_baidu_with_js_workaround()
    #compare_code()
