from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def find(self, by, value):
        """查找单个元素"""
        return self.driver.find_element(by, value)

    def find_all(self, by, value):
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

class WebOptionsPage(BasePage):
    
    URL = "https://the-internet.herokuapp.com/add_remove_elements/"

    # --- 元素定位（只在这里写一次！） ---
    CLICK_ADD_BTN = (By.CSS_SELECTOR, "button[onclick='addElement()']")
    CLICK_DELETE_BTN = (By.CLASS_NAME, "added-manually")
    FORM_TITLE = (By.CSS_SELECTOR, "h3")

    def open(self):
        self.driver.get(self.URL)
        return self

    def add_elem(self):
        self.click(*self.CLICK_ADD_BTN)
        return self
    
    def delete_elem(self):
        self.click(*self.CLICK_DELETE_BTN)
        return self

    def has_delete_button(self):
        return len(self.find_all(*self.CLICK_DELETE_BTN)) > 0

    def get_page_title(self):
        return self.get_text(*self.FORM_TITLE)
    


def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def test_weboptions_with_po():
    print("=" * 60)
    print("Page Object 模拟实战：Web 页面操作测试")
    print("=" * 60)

    driver = setup_driver()

    try:
        # 1. 打开页面
        print("\n 📕 步骤 1：打开操作页面")
        page = WebOptionsPage(driver)
        page.open()
        page.wait_until_visible(*page.FORM_TITLE)
        print(f"    当前标题：{page.get_page_title()}")
        print(f"    当前 URL：{page.get_url()}")

        # 2. 点击添加模块
        print("\n 🖱 步骤 2：点击添加按钮")
        page.add_elem()
        page.wait_until_visible(*page.CLICK_DELETE_BTN)
        assert page.has_delete_button(), "页面应出现 Delete 按钮"
        assert page.get_text(*page.CLICK_DELETE_BTN) == "Delete"
        print("     ✔ 点击添加按钮成功")

        # 3. 点击删除按钮
        print("\n 🖱 步骤 3：点击删除按钮")
        page.delete_elem()
        page.wait.until(EC.invisibility_of_element_located(page.CLICK_DELETE_BTN))
        time.sleep(2)
        assert not page.has_delete_button(), "Delete 按钮应已消失"
        print("     ✔ 点击删除按钮成功，Delete 按钮已消失")

        print()
        print("=" * 60)
        print("✔ Page Object 模式测试通过！")
        print("=" * 60)

    finally:
        driver.quit()

if __name__ == "__main__":
    test_weboptions_with_po()



        