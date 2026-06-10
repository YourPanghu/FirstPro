"""
JMeter CLI 运行器 —— 用 Python 脚本驱动 JMeter 命令行模式

====================================================================
为什么需要这个脚本？
====================================================================
- JMeter GUI 只适合编写和调试，不适合自动化执行
- CLI 模式（无 GUI）才是性能测试的正确运行方式
- Python 脚本可以串联 JMeter 执行 -> 解析 JTL 结果 -> 判断阈值
- 适合集成到 Jenkins/GitHub Actions 等 CI/CD 流水线

====================================================================
JMeter CLI 核心参数速查
====================================================================
-n          非 GUI 模式（命令行运行）
-t test.jmx 指定测试计划文件
-l res.jtl  结果输出文件（CSV格式）
-e          生成 HTML 报告
-o report/  HTML 报告输出目录
-Jkey=val   覆盖 .jmx 中的属性值
-f          强制覆盖已有报告目录

====================================================================
前置条件：
1. Java 已安装
2. JMeter 已下载解压（参见 install_jmeter.md）
3. JMeter bin 目录已加入 PATH，或修改下方 DEFAULT_JMETER_HOMES

用法：
    python 06-jmeter/run_jmeter.py --test 01_first_test_plan.jmx
    python 06-jmeter/run_jmeter.py --test 04_full_scenario.jmx --users 50 --duration 60
    python 06-jmeter/run_jmeter.py --all  # 运行所有测试计划

面试重点：
"JMeter 怎么集成到 CI/CD？" -> CLI 模式 + shell/Python 脚本 + Jenkins 调用
====================================================================
"""
import subprocess
import sys
import os
import argparse
import time
import json
import xml.etree.ElementTree as ET
from pathlib import Path

# ========== 配置 ==========
# 自动探测 JMeter 安装路径（优先级：环境变量 > 默认路径 > PATH）
DEFAULT_JMETER_HOMES = [
    r"D:\computor_software\Program_softwares\apache-jmeter-5.6.3",  # 你的路径
    r"D:\Tools\apache-jmeter-5.6.3",
    r"C:\Tools\apache-jmeter-5.6.3",
]

JMETER_HOME = os.environ.get("JMETER_HOME", "")
if not JMETER_HOME:
    for path in DEFAULT_JMETER_HOMES:
        if os.path.isdir(path):
            JMETER_HOME = path
            break

if JMETER_HOME:
    JMETER_BIN = os.path.join(JMETER_HOME, "bin", "jmeter.bat") if os.name == "nt" \
        else os.path.join(JMETER_HOME, "bin", "jmeter")
else:
    JMETER_BIN = "jmeter.bat" if os.name == "nt" else "jmeter"

# 模块目录
MODULE_DIR = Path(__file__).parent
TEST_PLANS_DIR = MODULE_DIR
REPORTS_DIR = MODULE_DIR / "reports"
RESULTS_DIR = MODULE_DIR / "results"

# Windows GBK 终端兼容：用 PYTHONIOENCODING 或者替换 emoji
def safe_print(*args, **kwargs):
    """安全的 print，避免 Windows GBK 编码错误"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 回退到 ASCII
        text = " ".join(str(a) for a in args)
        text = text.encode("ascii", errors="replace").decode("ascii")
        print(text, **kwargs)


def ensure_dirs():
    """确保报告和结果目录存在"""
    REPORTS_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)


def check_jmeter():
    """检查 JMeter 是否可用"""
    # 先检查文件是否存在
    if not os.path.exists(JMETER_BIN):
        safe_print(f"[FAIL] 找不到 JMeter: {JMETER_BIN}")
        safe_print(f"       请确保 JMeter 已安装，详见 install_jmeter.md")
        return False

    safe_print(f"JMeter 路径: {JMETER_BIN}")
    safe_print(f"JMeter 目录: {JMETER_HOME}")

    # JMeter -v 启动 JVM 比较慢，给 30s 超时
    try:
        result = subprocess.run(
            [JMETER_BIN, "-v"],
            capture_output=True, text=True, timeout=30
        )
        # JMeter 把版本信息打到 stderr
        output = result.stderr or result.stdout
        for line in output.split("\n"):
            if "Apache JMeter" in line or "_" in line and "____" not in line:
                continue
        if "Apache JMeter" in output or "Copyright" in output:
            safe_print("[OK] JMeter 可用")
            return True
        elif result.returncode == 0:
            safe_print("[OK] JMeter 可用")
            return True
    except subprocess.TimeoutExpired:
        safe_print("[WARN] JMeter -v 超时(30s)，但文件存在，继续...")
        return True  # 文件存在就假设可用
    except FileNotFoundError:
        safe_print(f"[FAIL] 找不到 JMeter 命令: {JMETER_BIN}")
        return False
    except Exception as e:
        safe_print(f"[FAIL] JMeter 检查异常: {e}")
        return False

    return True


def run_test_plan(test_plan: str, users: int = None, duration: int = None,
                  ramp_up: int = None) -> dict:
    """
    运行单个 JMeter 测试计划

    Args:
        test_plan: 测试计划文件名（.jmx）
        users:     并发用户数（覆盖 JMX 中的设置）
        duration:  持续时间（秒）
        ramp_up:   Ramp-Up 时间（秒）

    Returns:
        测试结果字典
    """
    test_plan_path = TEST_PLANS_DIR / test_plan
    if not test_plan_path.exists():
        safe_print(f"[FAIL] 测试计划不存在: {test_plan_path}")
        return {"success": False, "error": "File not found"}

    # 生成输出文件名（基于测试计划名+时间戳）
    base_name = test_plan_path.stem
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"{base_name}_{timestamp}.jtl"
    report_dir = REPORTS_DIR / f"{base_name}_{timestamp}"

    # 构建 JMeter CLI 命令
    cmd = [
        JMETER_BIN,
        "-n",                          # CLI 模式（无 GUI）
        "-t", str(test_plan_path),     # 测试计划文件
        "-l", str(result_file),        # 结果输出 .jtl 文件
        "-e",                          # 生成 HTML 报告
        "-o", str(report_dir),         # HTML 报告输出目录
        "-f",                          # 强制覆盖已有报告目录
    ]

    # 可选：动态覆盖线程属性
    if users is not None:
        cmd.extend(["-Jusers", str(users)])
    if duration is not None:
        cmd.extend(["-Jduration", str(duration)])
    if ramp_up is not None:
        cmd.extend(["-Jramp_up", str(ramp_up)])

    safe_print(f"\n{'='*60}")
    safe_print(f">> 运行测试: {test_plan}")
    safe_print(f"{'='*60}")
    safe_print(f"测试计划: {test_plan_path}")
    safe_print(f"结果文件: {result_file}")
    safe_print(f"HTML报告: {report_dir}")
    if users:
        safe_print(f"并发用户: {users}")
    if duration:
        safe_print(f"持续时间: {duration}s")
    if ramp_up:
        safe_print(f"Ramp-Up: {ramp_up}s")
    safe_print(f"{'='*60}\n")

    # 执行 JMeter
    start_time = time.time()
    try:
        """ 参数含义（capture_output 捕获 stdout/stderr，text 返回字符串，timeout 超时保护，cwd 工作目录） """
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=(duration or 60) + 120,  # 额外 120s 缓冲
            cwd=str(MODULE_DIR)
        )
        elapsed = time.time() - start_time
    except subprocess.TimeoutExpired:
        safe_print("[FAIL] JMeter 执行超时！")
        return {"success": False, "error": "Timeout"}

    # 输出 JMeter 的控制台摘要
    if result.stdout:
        safe_print(result.stdout[:2000])  # 限制输出长度

    # 检查是否发生了致命错误（XML解析失败等）
    has_fatal_error = False
    if result.stderr:
        for line in result.stderr.strip().split("\n"):
            if "ERROR" in line or "Err" in line:
                safe_print(f"[WARN] {line}")
            # "Error in NonGUIDriver" 表示 JMX 解析失败，测试根本没执行
            if "Error in NonGUIDriver" in line or "XmlPullParserException" in line:
                has_fatal_error = True

    # 解析结果
    # 注意: JMeter 即使 XML 解析失败也可能返回0, 需要额外检查 stderr
    success = result.returncode == 0 and not has_fatal_error
    summary = {
        "success": success,
        "test_plan": test_plan,
        "elapsed": round(elapsed, 1),
        "result_file": str(result_file),
        "report_dir": str(report_dir),
    }

    # 解析 .jtl 结果文件获取数据
    if result_file.exists():
        stats = parse_jtl(result_file)
        summary.update(stats)
        print_summary(stats)

    if success:
        safe_print(f"\n[PASS] 测试完成！耗时 {elapsed:.0f}s")
        safe_print(f"HTML 报告: file:///{report_dir.as_posix()}/index.html")
    else:
        safe_print(f"\n[FAIL] 测试失败！返回码: {result.returncode}")

    return summary


def parse_jtl(jtl_file: Path) -> dict:
    """
    解析 JMeter 的 .jtl 结果文件（CSV 格式）

    JTL 文件结构:
    - 第一行: 表头 (timeStamp,elapsed,label,responseCode,success,...)
    - 后续行: 每条请求的数据

    返回核心性能指标:
    - total_requests:  总请求数
    - error_rate:      错误率百分比
    - avg_response_ms:  平均响应时间(毫秒)
    - p50/p90/p95/p99: 分位数响应时间
    - tps:             每秒处理事务数(估算)
    - labels:          按请求类型分组的统计

    关键理解:
    - P50(中位数): 一半请求在此时间内完成, 比平均值更稳定
    - P90: 90%请求在此时间内完成, 常作为 SLA 指标
    - P99: 99%请求在此时间内完成, 长尾问题检测
    - P99 >> P50: 说明少数请求特别慢, 存在瓶颈
    - TPS: Throughput Per Second = 总请求数 / (最大时间差/1000)
    """
    try:
        with open(jtl_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) < 2:
            return {"error": "No data in JTL file"}

        # 第一行是表头
        headers = lines[0].strip().split(",")
        # 找到关键列的索引
        idx = {
            "success": headers.index("success") if "success" in headers else -1,
            "responseCode": headers.index("responseCode") if "responseCode" in headers else -1,
            "elapsed": headers.index("elapsed") if "elapsed" in headers else -1,
            "label": headers.index("label") if "label" in headers else -1,
            "bytes": headers.index("bytes") if "bytes" in headers else -1,
            "threadName": headers.index("threadName") if "threadName" in headers else -1,
        }

        total = len(lines) - 1  # 减去表头
        success_count = 0
        elapsed_times = []
        labels = {}

        for line in lines[1:]:
            parts = line.strip().split(",")
            if len(parts) < max(idx.values()) + 1:
                continue

            # 统计成功/失败
            if idx["success"] >= 0 and parts[idx["success"]].lower() == "true":
                success_count += 1

            # 统计响应时间
            if idx["elapsed"] >= 0:
                try:
                    elapsed_times.append(int(parts[idx["elapsed"]]))
                except ValueError:
                    pass

            # 按请求标签分组
            if idx["label"] >= 0:
                label = parts[idx["label"]]
                if label not in labels:
                    labels[label] = {"count": 0, "errors": 0}
                labels[label]["count"] += 1
                if idx["success"] >= 0 and parts[idx["success"]].lower() != "true":
                    labels[label]["errors"] += 1

        if elapsed_times:
            elapsed_times.sort()
            avg = sum(elapsed_times) / len(elapsed_times)
            p50 = elapsed_times[len(elapsed_times) // 2]
            p90 = elapsed_times[int(len(elapsed_times) * 0.9)]
            p95 = elapsed_times[int(len(elapsed_times) * 0.95)]
            p99 = elapsed_times[int(len(elapsed_times) * 0.99)]
            min_t = elapsed_times[0]
            max_t = elapsed_times[-1]
            error_rate = (total - success_count) / total * 100 if total > 0 else 0
            tps = total / (max_t / 1000) if max_t > 0 else 0
        else:
            avg = p50 = p90 = p95 = p99 = min_t = max_t = error_rate = tps = 0

        return {
            "total_requests": total,
            "success_count": success_count,
            "error_rate": round(error_rate, 2),
            "avg_response_ms": round(avg, 0),
            "min_response_ms": min_t,
            "max_response_ms": max_t,
            "p50_ms": p50,
            "p90_ms": p90,
            "p95_ms": p95,
            "p99_ms": p99,
            "tps": round(tps, 2),
            "labels": labels,
        }
    except Exception as e:
        return {"error": str(e)}


def print_summary(stats: dict):
    """打印友好的测试摘要"""
    if "error" in stats:
        safe_print(f"[WARN] 无法解析结果: {stats['error']}")
        return

    safe_print(f"\n{'='*60}")
    safe_print(f">> 测试结果摘要")
    safe_print(f"{'='*60}")
    safe_print(f"  总请求数:    {stats.get('total_requests', 'N/A')}")
    safe_print(f"  成功数:      {stats.get('success_count', 'N/A')}")
    safe_print(f"  错误率:      {stats.get('error_rate', 'N/A')}%")
    safe_print(f"  {'-'*40}")
    safe_print(f"  平均响应:    {stats.get('avg_response_ms', 'N/A')} ms")
    safe_print(f"  最小响应:    {stats.get('min_response_ms', 'N/A')} ms")
    safe_print(f"  最大响应:    {stats.get('max_response_ms', 'N/A')} ms")
    safe_print(f"  P50 (中位数): {stats.get('p50_ms', 'N/A')} ms")
    safe_print(f"  P90:         {stats.get('p90_ms', 'N/A')} ms")
    safe_print(f"  P95:         {stats.get('p95_ms', 'N/A')} ms")
    safe_print(f"  P99:         {stats.get('p99_ms', 'N/A')} ms")
    safe_print(f"  {'-'*40}")
    safe_print(f"  TPS (估算):  {stats.get('tps', 'N/A')} /s")
    safe_print(f"{'='*60}")

    # 按请求标签的详细统计
    labels = stats.get("labels", {})
    if labels:
        safe_print(f"\n>> 按请求类型统计:")
        for label, info in labels.items():
            status = "[OK]" if info["errors"] == 0 else "[FAIL]"
            safe_print(f"  {status} {label}: {info['count']}次, {info['errors']}失败")


def run_all(users: int = None, duration: int = None):
    """运行所有测试计划"""
    test_plans = sorted(TEST_PLANS_DIR.glob("*.jmx"))
    if not test_plans:
        safe_print("[FAIL] 没有找到 .jmx 测试计划文件")
        return []

    safe_print(f"\n>> 批量运行 {len(test_plans)} 个测试计划\n")
    results = []
    for plan in test_plans:
        result = run_test_plan(plan.name, users=users, duration=duration)
        results.append(result)
        time.sleep(2)  # 间隔2秒

    # 汇总
    safe_print(f"\n{'='*60}")
    safe_print(f">> 全部测试完成！")
    safe_print(f"{'='*60}")
    passed = sum(1 for r in results if r.get("success"))
    safe_print(f"  通过: {passed}/{len(results)}")
    for r in results:
        status = "[OK]" if r.get("success") else "[FAIL]"
        safe_print(f"  {status} {r['test_plan']} ({r.get('elapsed', '?')}s)")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="JMeter CLI 运行器 —— 用 Python 驱动性能测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_jmeter.py --test 01_first_test_plan.jmx
  python run_jmeter.py --test 04_full_scenario.jmx --users 50 --duration 60
  python run_jmeter.py --all
  python run_jmeter.py --all --users 10 --duration 30
        """
    )
    parser.add_argument("--test", "-t", help="指定 .jmx 测试计划文件名")
    parser.add_argument("--all", "-a", action="store_true", help="运行所有测试计划")
    parser.add_argument("--users", "-u", type=int, help="并发用户数（覆盖 JMX 中的设置）")
    parser.add_argument("--duration", "-d", type=int, help="持续时间（秒）")
    parser.add_argument("--ramp-up", "-r", type=int, help="Ramp-Up 启动时间（秒）")
    parser.add_argument("--check", action="store_true", help="仅检查 JMeter 是否可用")

    args = parser.parse_args()

    if args.check:
        check_jmeter()
        sys.exit(0)

    if not check_jmeter():
        sys.exit(1)

    ensure_dirs()

    if args.all:
        run_all(users=args.users, duration=args.duration)
    elif args.test:
        run_test_plan(args.test, users=args.users, duration=args.duration,
                      ramp_up=args.ramp_up)
    else:
        parser.print_help()
        safe_print("\n提示: 至少指定 --test 或 --all")
