"""
02 - 元素定位与等待机制
==========================
面试必问：Selenium 有哪些定位方式？怎么处理页面加载等待？

8 种定位方式：
  ID, Name, Class, Tag, Link Text, Partial Link Text, CSS Selector, XPath

3 种等待方式：
  1. time.sleep()     → 固定等待（不推荐）
  2. implicitly_wait()→ 隐式等待（全局设置）
  3. WebDriverWait   → 显式等待（推荐！等特定条件）
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')


def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


# ============================================================
# 1. 八种元素定位方式演示
# ============================================================
def demo_element_locators():
    """
    打开百度首页，演示每种定位方式
    """
    print("=" * 60)
    print("八种元素定位方式（以百度首页为例）")
    print("=" * 60)

    driver = setup_driver()
    driver.get("https://www.baidu.com")

    locators = [
        # (定位方式, 描述, By.XXX, 值)
        ("ID",              "搜索框（最常用）",           By.ID,              "kw"),
        ("NAME",            "搜索框 by name 属性",        By.NAME,            "wd"),
        ("CLASS_NAME",      "顶部容器",                   By.CLASS_NAME,      "s_tab"),
        ("TAG_NAME",        "第一个 input 标签",          By.TAG_NAME,        "input"),
        ("CSS_SELECTOR",    "搜索框 CSS 选择器",          By.CSS_SELECTOR,    "#kw"),
        ("XPATH",           "搜索框 XPath",              By.XPATH,           "//input[@id='kw']"),
        ("LINK_TEXT",       "新闻链接（精确文本）",        By.LINK_TEXT,       "新闻"),
        ("PARTIAL_LINK_TEXT","贴吧链接（部分文本）",        By.PARTIAL_LINK_TEXT, "贴"),
    ]

    for name, desc, by_method, value in locators:
        try:
            elem = driver.find_element(by_method, value)
            tag = elem.tag_name
            print(f"  ✅ {name:20s} | {desc:25s} | 找到: <{tag}>")
        except Exception as e:
            print(f"  ❌ {name:20s} | {desc:25s} | 未找到")

    driver.quit()
    print()


# ============================================================
# 2. 三种等待方式对比
# ============================================================
def demo_wait_strategies():
    """
    对比三种等待方式的区别
    """
    print("=" * 60)
    print("三种等待方式")
    print("=" * 60)

    # --- 方式 1: time.sleep() ---
    print("\n1️⃣ time.sleep() — 固定等待")
    print("   优点: 简单粗暴")
    print("   缺点: 浪费时间，元素提前加载还要等，元素慢了会报错")
    print("   使用场景: 调试时临时用，正式代码别用")

    # --- 方式 2: implicitly_wait() ---
    print("\n2️⃣ driver.implicitly_wait() — 隐式等待")
    print("   优点: 全局设置一次，后面自动等")
    print("   缺点: 不够灵活，不能等特定条件")
    print("   用法: driver.implicitly_wait(10)  # 最多等 10 秒")

    # --- 方式 3: WebDriverWait — 显式等待（推荐！）---
    print("\n3️⃣ WebDriverWait — 显式等待（✅ 推荐）")
    print("   优点: 等特定条件出现，条件满足立即继续")
    print("   用法: WebDriverWait(driver, 10).until(EC.条件)")

    print("\n   常用等待条件:")
    conditions = [
        "presence_of_element_located     → 元素出现在 DOM 中",
        "visibility_of_element_located   → 元素可见",
        "element_to_be_clickable         → 元素可点击",
        "text_to_be_present_in_element   → 元素中包含指定文本",
        "title_contains                  → 页面标题包含指定文字",
        "alert_is_present                → 弹窗出现",
    ]
    for c in conditions:
        print(f"     {c}")


# ============================================================
# 3. 显式等待实战
# ============================================================
def demo_explicit_wait():
    """
    用显式等待操作测试表单页面
    说明：百度等真实网站有反自动化措施（元素在 DOM 中但 JS 阻止交互）
    实际工作中遇到这种情况常用：
      1. driver.execute_script("arguments[0].value='xxx';", elem)  JS 直接设值
      2. ActionChains 模拟真实鼠标/键盘操作
      3. 换用其他定位方式/策略

    这里用 Selenium 官方测试页面来展示正确的显式等待用法
    """
    print()
    print("=" * 60)
    print("显式等待实战: 测试表单（不用 time.sleep！）")
    print("=" * 60)

    driver = setup_driver()
    # 使用 webdriver 自带的测试页面，比百度稳定
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")

    try:
        wait = WebDriverWait(driver, 10)

        # 等文本框出现后输入
        print("\n📋 等待文本框可见...")
        text_input = wait.until(
            EC.visibility_of_element_located((By.ID, "my-text-id"))
        )
        text_input.send_keys("显式等待输入的内容")
        print("   ✅ 文本框已可见，输入内容")

        # 等下拉框可点击后操作
        print("📋 等待下拉框可交互...")
        dropdown = wait.until(
            EC.element_to_be_clickable((By.NAME, "my-select"))
        )
        dropdown.click()
        print("   ✅ 下拉框已可点击")

        # 等提交按钮出现
        print("📋 等待提交按钮...")
        submit_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]"))
        )
        print(f"   按钮文本: {submit_btn.text}")
        print("   ✅ 提交按钮已就绪")

        print()
        print("✅ 全程没有用 time.sleep()！这就是显式等待的威力")
        print()
        print("💡 实际工作中百度搜索框的应对策略：")
        print("   # 策略1: JS 直接设值（绕过前端验证）")
        print("   driver.execute_script(")
        print('       "arguments[0].value=\'搜索词\'", search_box)')
        print("   # 策略2: ActionChains 模拟真实用户")
        print("   from selenium.webdriver.common.action_chains import ActionChains")
        print("   ActionChains(driver).move_to_element(elem).click().send_keys('text').perform()")

    finally:
        driver.quit()
        print("\n浏览器已关闭")


if __name__ == "__main__":
    demo_element_locators()
    demo_wait_strategies()
    demo_explicit_wait()
