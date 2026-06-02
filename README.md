# FirstPro - Python + 软件测试实战项目

[![GitHub](https://img.shields.io/badge/GitHub-YourPanghu%2FFirstPro-blue?logo=github)](https://github.com/YourPanghu/FirstPro)

> 🎯 目标：从零到能找到广深莞地区软件测试工作  
> 📍 当前进度：Python 基础 ✅ → API 自动化 ✅ → Postman ✅ → Selenium ✅ → **Git ✅**

---

## 📁 项目结构

```
FirstPro/
├── 01-python-basics/          # Python 测试入门
│   ├── 01_first_test.py       # 第一个接口测试脚本
│   ├── 02_assertions.py       # 断言：测试的核心
│   ├── 03_test_functions.py   # 用函数组织测试用例
│   └── 04_data_driven.py      # 数据驱动测试（面试高频）
│
├── 02-api-testing/            # API 接口自动化测试
│   ├── test_crud_api.py       # CRUD 完整流程
│   ├── test_with_pytest.py    # Pytest 框架实战
│   ├── run_all.py             # 一键运行所有测试
│   └── test_report.json       # 测试报告（自动生成）
│
├── 03-postman-automation/     # Postman/Newman 自动化
│   ├── firstpro_api_collection.json  # Postman 集合（可导入！）
│   ├── run_newman.js          # Newman CLI 运行器
│   └── reports/               # Newman 测试报告
│
├── 04-selenium-automation/    # Selenium Web 自动化 🆕
│   ├── 01_first_selenium.py   # 第一个 Selenium 脚本
│   ├── 02_element_locators.py # 8种定位 + 3种等待
│   ├── 03_page_object.py      # Page Object 设计模式
│   ├── 04_pytest_selenium.py  # Pytest + Selenium 整合
│   ├── pages/                 # 页面对象类
│   ├── reports/               # HTML 测试报告
│   └── screenshots/           # 截图（含失败截图）
│
├── requirements.txt           # Python 依赖
├── pytest.ini                 # Pytest 配置
└── README.md                  # 本文件
```

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# API 接口测试（快速）
python 02-api-testing/run_all.py

# Selenium Web 自动化（需要 Chrome 浏览器）
pytest 04-selenium-automation/04_pytest_selenium.py -v

# Selenium + HTML 报告
pytest 04-selenium-automation/ -v --html=04-selenium-automation/reports/selenium_report.html

# 全部 Pytest 测试
pytest -v
```

### 3. Postman 集合
```bash
npm install -g newman
node 03-postman-automation/run_newman.js
```
或在 Postman 桌面版: **Import → File → 选择 `firstpro_api_collection.json`**

---

## 📚 学习路线

| 阶段 | 内容 | 测试结果 |
|------|------|----------|
| 🔰 入门 | Python 发请求、看状态码、读响应头 | ✅ |
| 🔰 入门 | 断言：检查字段存在、类型、值、包含 | ✅ |
| 🟡 进阶 | 封装测试函数、数据驱动测试 | ✅ |
| 🟢 实战 | API CRUD 完整流程、Pytest 框架 | ✅ 13/13 |
| 🔵 工程 | Postman Collection + Newman CLI | ✅ |
| 🟢 实战 | **Selenium: 元素定位、显式等待、Page Object** | ✅ 9/9 |

---

## 🎓 广深莞测试岗位技能对照

| JD 要求 | 本项目覆盖 | 掌握程度 |
|---------|-----------|----------|
| Python 编程 | ✅ | 测试脚本编写 |
| Postman 接口测试 | ✅ | Collection + Newman |
| 测试用例设计 | ✅ | CRUD + 异常场景 |
| 断言/数据驱动 | ✅ | @parametrize + JSON 数据文件 |
| HTTP 协议 | ✅ | 状态码、请求头、响应体 |
| **Selenium Web 自动化** | ✅ 🆕 | **8 种定位 + 显式等待 + Page Object** |
| Git | ⏳ | 下一步 |
| JMeter/性能测试 | ⏳ | 后续模块 |
| MySQL/SQL | ⏳ | 后续模块 |

---

## 💡 面试话术准备

**"你做过自动化测试吗？"**
> 我用 Python + requests 实现了接口自动化测试，支持数据驱动。用 Pytest 框架组织用例，生成 HTML 报告。Selenium 这边用 Page Object 模式封装页面，配合显式等待和 Pytest fixture 管理浏览器生命周期。失败自动截图，可以直接接入 Jenkins/GitHub Actions。

**"怎么做数据驱动测试？"**
> 测试数据从代码分离，存到 JSON 文件里，一个通用函数循环执行。Python 里用 pytest 的 @parametrize，Postman 里用 Collection Runner 的 Data File。

**"Selenium 怎么定位元素？8 种定位方式优先级？"**
> ID > Name > CSS Selector > XPath > 其他。优先用 data-testid（如果前端有）、ID 和 Name，因为它们最稳定。XPath 最灵活但最脆弱，放在最后兜底。

**"Page Object 模式是什么？为什么用？"**
> 每个页面写一个类，元素定位和操作封装在类里。测试用例只调用 page.search()，不写 find_element。好处是元素定位只写一次，页面改版只改 Page 类，不用动测试用例。

---

## 📈 下一步

- [ ] Git 仓库搭建 + GitHub 上传（简历上的项目链接）
- [ ] JMeter 性能测试模块
- [ ] MySQL/SQL 数据库测试模块
- [ ] 真实国内 API 实战（聚合数据、和风天气等）
- [ ] 简历优化 + 广深莞岗位投递
