# JMeter 安装指南 (Windows)

> Apache JMeter 是纯 Java 应用，不需要安装，解压即用。

---

## ✅ 你的环境

| 项目 | 状态 |
|------|------|
| Java 17 | ✅ 已安装 |
| JMeter 5.6.3 | ✅ 已安装 (`D:\computor_software\Program_softwares\apache-jmeter-5.6.3`) |

---

## 📥 1. 下载 JMeter（已完成，仅供参考）

> 你的电脑已安装 JMeter 5.6.3，以下为参考信息。

1. 打开 [Apache JMeter 下载页](https://jmeter.apache.org/download_jmeter.cgi)
2. 下载 **Binaries → apache-jmeter-X.X.X.zip**（推荐最新稳定版 5.6.3+）
3. 解压到你想放的位置，例如：`D:\Tools\apache-jmeter-5.6.3`

⚠️ **下载很慢？** 用清华镜像：
```
https://mirrors.tuna.tsinghua.edu.cn/apache//jmeter/binaries/apache-jmeter-5.6.3.zip
```

---

## 🚀 2. 验证安装

打开终端（Git Bash / CMD），进入 JMeter 目录：

```bash
# 进入 bin 目录
cd D:\Tools\apache-jmeter-5.6.3\bin

# 启动 GUI（学习阶段用）
jmeter.bat

# 查看 CLI 帮助（自动化阶段用）
jmeter.bat -?
```

---

## ⚡ 3. 可选：加入 PATH（推荐）

方便在任意目录直接敲 `jmeter` 命令：

1. 搜索 → **编辑系统环境变量** → 环境变量
2. 用户变量 → Path → 新建 → 添加 `D:\Tools\apache-jmeter-5.6.3\bin`
3. 重启终端，验证：`jmeter -v`

---

## 🎯 4. 两种使用方式

| 方式 | 场景 | 命令 |
|------|------|------|
| **GUI** | 编写/调试测试计划 | `jmeter.bat` 双击或命令行 |
| **CLI** | 自动化压测/CI 集成 | `jmeter -n -t test.jmx -l result.jtl -e -o report/` |

**学习时用 GUI 可视化编写，面试时重点说 CLI 模式。**

---

## 📂 5. 本模块文件说明

```
06-jmeter/
├── install_jmeter.md              # 本文件
├── 01_first_test_plan.jmx         # 🟢 入门：第一个 HTTP 测试计划
├── 02_assertions.jmx              # 🟡 进阶：响应断言 + 持续时间断言
├── 03_parameterization.jmx        # 🟠 进阶：CSV 数据驱动
├── 04_full_scenario.jmx           # 🔴 实战：完整性能测试场景
├── test-data/
│   └── users.csv                  # 参数化测试数据
├── run_jmeter.py                  # Python CLI 运行脚本
└── reports/                       # CLI 生成的 HTML 报告
```

---

## 📖 下一步

搞定安装后，用 JMeter GUI 打开 `01_first_test_plan.jmx`，点击绿色 ▶ 运行，看第一个测试结果！
