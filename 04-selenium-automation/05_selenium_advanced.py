"""
05 - Selenium 深入实战
=========================
6 个面试高频考点，每个都是工作中每天都会用到的

考点:
  1. Alert 弹窗处理 → accept/dismiss/text/input
  2. iframe 内元素定位 → switch_to.frame()
  3. 文件上传 → send_keys(绝对路径)
  4. 多窗口/标签切换 → window_handles
  5. 下拉框操作 → Select 类
  6. 鼠标悬停 + 截图对比 → ActionChains + save_screenshot

测试站点: https://the-internet.herokuapp.com/ （经典测试练习站）

运行:
  python 04-selenium-automation/05_selenium_advanced.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

BASE = "https://the-internet.herokuapp.com"


def setup_driver():
    """统一的浏览器启动配置"""
    options = Options()
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


# ============================================================
# 练习 1: Alert 弹窗处理
# ============================================================
def demo_alerts():
    """
    面试问题："Selenium 怎么处理弹窗？"

    三种弹窗:
      alert     → 只有确定按钮
      confirm   → 确定 + 取消
      prompt    → 输入框 + 确定 + 取消

    核心 API:
      driver.switch_to.alert.accept()    # 点确定
      driver.switch_to.alert.dismiss()   # 点取消
      driver.switch_to.alert.text        # 获取弹窗文字
      driver.switch_to.alert.send_keys() # 输入文字 (prompt)
    """
    print("=" * 60)
    print("练习 1: Alert 弹窗处理")
    print("=" * 60)

    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        # --- 1.1 普通 Alert (只有一个确定按钮) ---
        print("\n📋 1.1 普通 Alert")
        driver.get(f"{BASE}/javascript_alerts")

        # 点击 "Click for JS Alert" 按钮
        driver.find_element(By.CSS_SELECTOR, "button[onclick='jsAlert()']").click()

        # 切换到弹窗
        alert = driver.switch_to.alert
        print(f"   弹窗文字: {alert.text}")
        alert.accept()  # 点确定
        print("   ✅ 已点击确定，弹窗关闭")

        # 验证结果
        result = driver.find_element(By.ID, "result").text
        print(f"   页面反馈: {result}")

        # --- 1.2 Confirm 弹窗 (确定+取消) ---
        print("\n📋 1.2 Confirm 弹窗 — 点取消")
        driver.find_element(By.CSS_SELECTOR, "button[onclick='jsConfirm()']").click()

        alert = driver.switch_to.alert
        print(f"   弹窗文字: {alert.text}")
        alert.dismiss()  # 点取消！
        print("   ✅ 已点击取消")

        result = driver.find_element(By.ID, "result").text
        print(f"   页面反馈: {result}")

        # --- 1.3 Prompt 弹窗 (输入框) ---
        print("\n📋 1.3 Prompt 弹窗 — 输入文字")
        driver.find_element(By.CSS_SELECTOR, "button[onclick='jsPrompt()']").click()

        alert = driver.switch_to.alert
        print(f"   弹窗文字: {alert.text}")
        alert.send_keys("Hello Selenium!")  # 在弹窗里输入
        alert.accept()
        print("   ✅ 已输入并点确定")

        result = driver.find_element(By.ID, "result").text
        print(f"   页面反馈: {result}")

        print("\n✅ Alert 弹窗处理完成")

    finally:
        driver.quit()


# ============================================================
# 练习 2: iframe 内元素定位
# ============================================================
def demo_iframe():
    """
    面试问题："如果元素在 iframe 里，怎么定位？"

    核心 API:
      driver.switch_to.frame(name_or_id)       # 通过 name/id 切换
      driver.switch_to.frame(webelement)        # 通过元素切换
      driver.switch_to.frame(0)                 # 通过索引切换（第1个iframe）
      driver.switch_to.default_content()        # 切回主页面！
      driver.switch_to.parent_frame()           # 切回上一层 iframe

    关键点: iframe 里的元素，不切换进去是找不到的！
    面试话术: "先 switch_to.frame() 切进去，操作完后 switch_to.default_content() 切回来"
    """
    print()
    print("=" * 60)
    print("练习 2: iframe 内元素定位")
    print("=" * 60)

    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(f"{BASE}/iframe")

        # --- 演示: 不切换直接找 iframe 里的元素 → 找不到 ---
        print("\n📋 尝试1: 不切换 iframe，直接找里面的元素")
        try:
            # iframe 里有一个 id='tinymce' 的编辑器
            driver.find_element(By.ID, "tinymce")
            print("   找到了？(不应该!)")
        except:
            print("   ❌ 找不到！因为元素在 iframe 里面")

        # --- 正确方式1: 通过 WebElement 切换 ---
        print("\n📋 尝试2: 先找到 iframe 元素，再切进去")
        iframe_elem = driver.find_element(By.CSS_SELECTOR, "iframe")
        driver.switch_to.frame(iframe_elem)
        print("   ✅ 已切换到 iframe")

        # 现在可以操作 iframe 里的元素了
        editor = driver.find_element(By.ID, "tinymce")
        print(f"   编辑器初始内容: {editor.text[:50]}...")

        # TinyMCE 是富文本编辑器，不是 input/textarea
        # 方案: 用 JS 直接设置内容（工作中处理 CKEditor/TinyMCE 的标准方式）
        driver.execute_script(
            "arguments[0].innerHTML = '<p>iframe 里的文字被我改了！</p>';",
            editor
        )
        print("   ✅ 已通过 JS 修改富文本编辑器内容")

        # 验证修改
        new_text = editor.text
        print(f"   修改后内容: {new_text}")

        # --- 切回主页面 ---
        print("\n📋 切回主页面")
        driver.switch_to.default_content()
        print("   ✅ 已切回主页面")

        # 验证回到了主页面（可以找到主页面的元素）
        header = driver.find_element(By.CSS_SELECTOR, "h3").text
        print(f"   主页面标题: {header}")

        print("\n✅ iframe 操作完成")
        print()
        print("💡 面试话术:")
        print('   "iframe 里的元素要先 switch_to.frame() 切进去才能操作，')
        print('    操作完要 switch_to.default_content() 切回主页面，')
        print('    否则后续操作会找不到元素。"')

    finally:
        driver.quit()


# ============================================================
# 练习 3: 文件上传
# ============================================================
def demo_file_upload():
    """
    面试问题："Selenium 怎么做文件上传？"

    核心: 找到 <input type='file'> 元素，直接 send_keys(文件的绝对路径)
    注意: 不要点"选择文件"按钮打开系统弹窗，Selenium 控制不了系统弹窗！

    面试话术: "文件上传就是找到 input[type=file] 元素，
     send_keys 传入文件的绝对路径。不要点击按钮打开系统弹窗，
     那个 Selenium 控制不了。"
    """
    print()
    print("=" * 60)
    print("练习 3: 文件上传")
    print("=" * 60)

    driver = setup_driver()

    try:
        # --- 首先创建一个测试文件 ---
        test_file_dir = os.path.join(os.path.dirname(__file__), "test_files")
        os.makedirs(test_file_dir, exist_ok=True)
        test_file = os.path.join(test_file_dir, "test_upload.txt")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是要上传的测试文件内容\nSelenium 文件上传测试")

        print(f"\n📋 测试文件: {test_file}")

        # --- 上传 ---
        driver.get(f"{BASE}/upload")

        # 核心就这一行！
        file_input = driver.find_element(By.ID, "file-upload")
        file_input.send_keys(test_file)
        print(f"   ✅ 文件路径已填入")

        # 点击上传按钮
        driver.find_element(By.ID, "file-submit").click()
        print("   ✅ 已点击上传")

        # 验证上传成功
        wait = WebDriverWait(driver, 5)
        result = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3"))
        ).text
        print(f"   上传结果: {result}")

        # 确认文件名出现在结果页
        uploaded_file = driver.find_element(By.ID, "uploaded-files").text
        print(f"   上传的文件名: {uploaded_file}")
        assert "test_upload.txt" in uploaded_file, "上传失败！"
        print("   ✅ 上传验证通过")

        print()
        print("✅ 文件上传完成")

    finally:
        driver.quit()
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            os.rmdir(test_file_dir)


# ============================================================
# 练习 4: 多窗口/标签切换
# ============================================================
def demo_window_switching():
    """
    面试问题："点击链接打开新窗口，怎么切换过去操作？"

    核心 API:
      driver.window_handles    → 所有窗口的句柄列表
      driver.current_window_handle → 当前窗口句柄
      driver.switch_to.window(handle) → 切换到指定窗口
      driver.close()           → 关闭当前窗口
    """
    print()
    print("=" * 60)
    print("练习 4: 多窗口/标签切换")
    print("=" * 60)

    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(f"{BASE}/windows")
        print(f"\n   当前窗口数: {len(driver.window_handles)}")

        # --- 点击链接，打开新窗口 ---
        print("\n📋 点击 'Click Here' 打开新窗口")
        driver.find_element(By.LINK_TEXT, "Click Here").click()
        time.sleep(1)  # 等新窗口打开

        windows = driver.window_handles
        print(f"   现在窗口数: {len(windows)}")
        print(f"   当前窗口句柄: {driver.current_window_handle[-8:]}...")

        # --- 切换到新窗口 ---
        print("\n📋 切换到新窗口")
        driver.switch_to.window(windows[1])
        print(f"   新窗口标题: {driver.title}")
        print(f"   当前窗口句柄: {driver.current_window_handle[-8:]}...")
        new_window_text = driver.find_element(By.CSS_SELECTOR, "h3").text
        print(f"   新窗口内容: {new_window_text}")

        # --- 切回原窗口 ---
        print("\n📋 切回原窗口")
        driver.close()  # 先关掉新窗口
        print("   ✅ 已关闭新窗口")

        driver.switch_to.window(windows[0])
        print(f"   原窗口标题: {driver.title}")
        print(f"   窗口数: {len(driver.window_handles)}")

        print("\n✅ 多窗口切换完成")
        print()
        print("💡 面试话术:")
        print('   "用 window_handles 获取所有窗口句柄，')
        print('    switch_to.window(handle) 切换到目标窗口，')
        print('    操作完 close() 关掉，再切回原窗口。"')

    finally:
        driver.quit()


# ============================================================
# 练习 5: 下拉框操作 (Select 类)
# ============================================================
def demo_select_dropdown():
    """
    面试问题："Selenium 怎么操作下拉框？"

    核心: Select 类专门处理 <select> 标签
    三种选择方式:
      select_by_visible_text("显示的文字")  ← 最常用
      select_by_value("value值")
      select_by_index(索引)                ← 从 0 开始
    """
    print()
    print("=" * 60)
    print("练习 5: 下拉框操作 (Select)")
    print("=" * 60)

    driver = setup_driver()

    try:
        driver.get(f"{BASE}/dropdown")
        print(f"\n   页面标题: {driver.title}")

        # 定位 select 元素
        select_elem = driver.find_element(By.ID, "dropdown")
        select = Select(select_elem)

        # --- 方式 1: 通过可见文字选择 ---
        print("\n📋 方式1: select_by_visible_text('Option 1')")
        select.select_by_visible_text("Option 1")
        selected = select.first_selected_option
        print(f"   当前选中: {selected.text}")
        assert selected.text == "Option 1"
        print("   ✅ 选择成功")

        # --- 方式 2: 通过 value 属性选择 ---
        print("\n📋 方式2: select_by_value('2')")
        select.select_by_value("2")
        selected = select.first_selected_option
        print(f"   当前选中: {selected.text}")
        assert selected.text == "Option 2"
        print("   ✅ 选择成功")

        # --- 方式 3: 通过索引选择 (从0开始，但0是禁用项所以从1开始) ---
        print("\n📋 方式3: select_by_index(1) —— 注意索引从0开始，第0个是占位符被跳过了")
        select.select_by_index(1)
        selected = select.first_selected_option
        print(f"   当前选中: {selected.text}")
        assert selected.text == "Option 1"
        print("   ✅ 索引选择成功")

        # --- 遍历所有选项 ---
        print("\n📋 查看所有选项:")
        for i, option in enumerate(select.options):
            print(f"   选项 {i}: value='{option.get_attribute('value')}' text='{option.text}'")

        print()
        print("✅ 下拉框操作完成")
        print()
        print("💡 Select 类常用方法:")
        print("   select_by_visible_text()   → 按显示文字选（最常用）")
        print("   select_by_value()          → 按 value 属性选")
        print("   select_by_index()          → 按位置索引选")
        print("   first_selected_option      → 获取当前选中的项")
        print("   options                    → 获取所有选项")
        print("   deselect_all()             → 多选下拉框取消全选")

    finally:
        driver.quit()


# ============================================================
# 练习 6: 鼠标悬停 + 截图对比
# ============================================================
def demo_hover_and_screenshot():
    """
    面试问题："怎么模拟鼠标悬停？截图怎么做？"

    鼠标悬停: ActionChains(driver).move_to_element(elem).perform()
    截图对比: 操作前截图 + 操作后截图 = 对比差异

    面试话术: "用 ActionChains 模拟真实用户鼠标操作，
     截图对比用于可视化回归测试，操作前后各截一张，
     发现 UI 变化自动告警。"
    """
    print()
    print("=" * 60)
    print("练习 6: 鼠标悬停 + 截图对比")
    print("=" * 60)

    driver = setup_driver()

    try:
        driver.get(f"{BASE}/hovers")
        print(f"\n   打开悬停测试页面")

        screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        # --- 6.1 悬停前截图 ---
        before_img = os.path.join(screenshot_dir, "hover_before.png")
        driver.save_screenshot(before_img)
        print(f"\n📸 悬停前截图: {before_img}")

        # --- 6.2 鼠标悬停 ---
        print("\n📋 鼠标悬停到第一个头像上")
        avatar = driver.find_element(By.CSS_SELECTOR, ".figure")
        actions = ActionChains(driver)
        actions.move_to_element(avatar).perform()
        print("   悬停中...")
        time.sleep(1)  # 等悬停效果出现

        # 验证悬停效果：名字应该出现了
        figcaption = avatar.find_element(By.CSS_SELECTOR, ".figcaption")
        hover_name = figcaption.find_element(By.CSS_SELECTOR, "h5").text.strip()
        profile_link = figcaption.find_element(By.CSS_SELECTOR, "a").text.strip()
        print(f"   悬停显示的用户名: {hover_name}")
        print(f"   悬停显示的链接: {profile_link}")
        assert hover_name == "name: user1", f"悬停效果不对: {hover_name}"
        print("   ✅ 悬停效果验证通过")

        # --- 6.3 悬停后截图 ---
        after_img = os.path.join(screenshot_dir, "hover_after.png")
        driver.save_screenshot(after_img)
        print(f"\n📸 悬停后截图: {after_img}")

        # --- 6.4 对比 ---
        # 简单方式：比较文件大小（严格对比可用 Pillow）
        before_size = os.path.getsize(before_img)
        after_size = os.path.getsize(after_img)
        print(f"\n📋 截图对比:")
        print(f"   悬停前: {before_size:,} bytes")
        print(f"   悬停后: {after_size:,} bytes")
        print(f"   差异: {abs(after_size - before_size):,} bytes")

        # 悬停后的截图应该更大（多了显示的文字）
        if after_size != before_size:
            print("   ✅ 截图有差异（悬停效果已生效）")
        else:
            print("   ⚠️ 截图无差异（悬停可能没生效）")

        print()
        print("✅ 鼠标悬停 + 截图对比完成")
        print()
        print("💡 ActionChains 其他常用操作:")
        print("   move_to_element(elem)        → 悬停")
        print("   click(elem).perform()        → 点击")
        print("   double_click(elem).perform() → 双击")
        print("   context_click(elem).perform()→ 右键")
        print("   drag_and_drop(src, tgt).perform() → 拖拽")
        print("   key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()")
        print("       → Ctrl+A 全选")

    finally:
        driver.quit()


# ============================================================
# 面试总结
# ============================================================
def print_interview_cheatsheet():
    print()
    print("=" * 60)
    print("🎓 面试速查表: Selenium 深入篇")
    print("=" * 60)
    print("""
  Q: Alert 弹窗怎么处理？
  A: driver.switch_to.alert 切换到弹窗，
     accept() 确定、dismiss() 取消、
     text 获取文字、send_keys() 输入。

  Q: iframe 里的元素怎么定位？
  A: switch_to.frame() 切进去再找，
     操作完 switch_to.default_content() 切回来。

  Q: 文件上传怎么做？
  A: 找到 input[type=file]，send_keys(绝对路径)。
     不要点系统弹窗，Selenium 控制不了。

  Q: 新窗口怎么切换？
  A: window_handles 获取所有窗口句柄，
     switch_to.window(handle) 切换。

  Q: 下拉框怎么操作？
  A: Select 类，select_by_visible_text() 最常用。

  Q: 怎么模拟鼠标悬停/拖拽？
  A: ActionChains，move_to_element/perform()。
     可以链式组合多个动作。

  Q: 截图有什么用？
  A: 失败自动截图排查问题；
     截图对比做可视化回归测试，发现 UI 变化。
""")
    print("=" * 60)


if __name__ == "__main__":
    # 按顺序执行，想单独跑某个可以把其他的注释掉
    demo_alerts()
    demo_iframe()
    demo_file_upload()
    demo_window_switching()
    demo_select_dropdown()
    demo_hover_and_screenshot()
    print_interview_cheatsheet()

    print()
    print("🎉 所有 6 个练习完成！")
    print()
    print("下一步建议:")
    print("  1. 把这 6 个函数手抄一遍，理解每行代码的作用")
    print("  2. 去 https://the-internet.herokuapp.com/ 找其他页面练手")
    print("  3. 打开浏览器 F12，看看 iframe 标签和 select 标签长什么样")
