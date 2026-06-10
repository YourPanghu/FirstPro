# FirstPro - Python + 软件测试实战项目

[![GitHub](https://img.shields.io/badge/GitHub-YourPanghu%2FFirstPro-blue?logo=github)](https://github.com/YourPanghu/FirstPro)

> 🎯 目标：从零到能找到广深莞地区软件测试工作  
> 📍 当前进度：Python 基础 ✅ → API 自动化 ✅ → Postman ✅ → Selenium ✅ → Git ✅ → Selenium 深入 ✅ → MySQL ✅ → JMeter 性能测试 ✅ → 国内 API 实战 ✅

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
├── 04-selenium-automation/    # Selenium Web 自动化
│   ├── 01_first_selenium.py   # 第一个 Selenium 脚本
│   ├── 02_element_locators.py # 8种定位 + 3种等待
│   ├── 03_page_object.py      # Page Object 设计模式
│   ├── 03-1_imitate_page_object.py  # 🖊 Page Object 练手
│   ├── 04_pytest_selenium.py  # Pytest + Selenium 整合
│   ├── 05_selenium_advanced.py # 🆕 深入：弹窗/iframe/上传/窗口/下拉/悬停
│   ├── pages/                 # 页面对象类
│   ├── reports/               # HTML 测试报告
│   └── screenshots/           # 截图（含失败截图）
│
├── 05-mysql/                  # MySQL 数据库测试
│   ├── test_data.sql          # 测试数据库初始化脚本
│   ├── conftest.py            # Pytest fixtures（连接管理+事务回滚）
│   ├── 01_connect_db.py       # 连接数据库 + 第一个查询
│   ├── 02_crud_testing.py     # CRUD 增删改查 + 断言
│   ├── 03_data_integrity.py   # 数据完整性测试（约束/外键/索引）
│   ├── 04_mysql_pytest.py     # Pytest + MySQL 整合（parametrize）
│   └── 05_sql_for_testers.py  # 测试工程师必备 SQL 手册（24条）
│
├── 06-jmeter/                  # JMeter 性能测试 🆕
│   ├── install_jmeter.md       # JMeter 安装指南（Windows）
│   ├── 01_first_test_plan.jmx  # 🟢 入门：第一个 HTTP 测试计划
│   ├── 02_assertions.jmx       # 🟡 进阶：5种断言（响应/JSON/时间/状态码/大小）
│   ├── 03_parameterization.jmx # 🟠 进阶：CSV 数据驱动 + 变量引用
│   ├── 04_full_scenario.jmx    # 🔴 实战：完整性能测试场景（双线程组+定时器）
│   ├── test-data/
│   │   └── users.csv           # CSV 参数化测试数据
│   ├── run_jmeter.py           # Python CLI 运行器（含结果解析）
│   ├── results/                # .jtl 原始结果文件
│   └── reports/                # JMeter HTML 报告
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

# MySQL 数据库测试（需要先执行建库脚本）
mysql -u root -p < 05-mysql/test_data.sql
python 05-mysql/02_crud_testing.py

# Pytest 运行 MySQL 测试
pytest 05-mysql/04_mysql_pytest.py -v

# JMeter 性能测试（需要先安装 JMeter，参见 06-jmeter/install_jmeter.md）
python 06-jmeter/run_jmeter.py --check              # 检查 JMeter 是否可用
python 06-jmeter/run_jmeter.py --test 01_first_test_plan.jmx   # 运行单个测试
python 06-jmeter/run_jmeter.py --all --users 10 --duration 30 # 批量压测

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
| 🔵 进阶 | **Selenium 深入: Alert/iframe/上传/窗口/下拉/悬停** | ✅ 6/6 |
| 🚀 工程 | Git + GitHub 项目上线 | ✅ |
| 🔵 工程 | **MySQL: CRUD/约束/事务/联表查询/Pytest整合** | ✅ |
| 🚀 工程 | **JMeter: HTTP压测/断言/CSV数据驱动/阶梯加压/HTML报告** | ✅ |

---

## 🎓 广深莞测试岗位技能对照

| JD 要求 | 本项目覆盖 | 掌握程度 |
|---------|-----------|----------|
| Python 编程 | ✅ | 测试脚本编写 |
| Postman 接口测试 | ✅ | Collection + Newman |
| 测试用例设计 | ✅ | CRUD + 异常场景 |
| 断言/数据驱动 | ✅ | @parametrize + JSON 数据文件 |
| HTTP 协议 | ✅ | 状态码、请求头、响应体 |
| **Selenium Web 自动化** | ✅ 🆕 | **8 种定位 + 显式等待 + Page Object + Alert/iframe/上传/窗口切换** |
| Git | ✅ | GitHub 项目 + 持续提交 |
| **JMeter/性能测试** | ✅ 🆕 | **HTTP压测/断言/CSV数据驱动/阶梯加压/TPS分析** |
| MySQL/SQL | ✅ | CRUD/约束/事务/JOIN/子查询/Pytest整合 |

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

**"性能测试你怎么做？"**
> 我用 JMeter 做性能测试。流程是：先做单用户冒烟测试确认功能正常，再阶梯加压找到性能拐点。关注指标有 TPS、平均响应时间、P90/P95/P99 线、错误率。用 CSV Data Set Config 做数据驱动。CLI 模式 + Python 脚本驱动，可以集成到 Jenkins 里跑。

**"数据库测试你怎么做？"**
> 我会验证 CRUD 操作的正确性，每条 SQL 都有关联的断言点。数据完整性方面测试 NOT NULL / UNIQUE / CHECK 约束是否生效，外键联级删除/更新是否正确，默认值是否符合预期。用事务回滚保证测试数据不污染真实库。Pytest 这边用 fixture 管理连接，parametrize 做数据驱动，和接口测试的套路一致。

**"你对接过真实第三方 API 吗？"**
> 我做过真实国内 API 的自动化测试。对接了和风天气、聚合数据、一言三个平台。我把 API 请求封装成客户端类，测试用例只调用方法不写 requests。对需要 Key 的 API 用 .env 管理凭证，没配置 Key 的测试自动 skip。总共 30 个测试用例，覆盖了正常场景、异常场景、数据驱动和响应时间检查。

**"API 测试你怎么保证质量？"**
> 我按套路来：先检查状态码，再验证响应结构（必需字段都在），然后检查字段类型（int/str/list 对不对），最后验证业务逻辑（比如最高温不能低于最低温、翻页数据不能重复）。异常场景也覆盖，比如无效参数、超大页码。数据驱动用 CSV 管理测试数据，parametrize 批量跑。
---

## 📈 下一步

- [x] Git 仓库搭建 + GitHub 上传（简历上的项目链接）
- [x] MySQL/SQL 数据库测试模块
- [x] JMeter 性能测试模块
- [x] 真实国内 API 实战（聚合数据、和风天气等）→ [RealAPITesting](https://github.com/YourPanghu/RealAPITesting)
- [ ] 简历优化 + 广深莞岗位投递
