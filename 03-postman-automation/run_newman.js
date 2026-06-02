/**
 * Newman 自动化测试脚本
 * =========================
 * Newman 是 Postman 的命令行工具，可以在 CI/CD 里跑 Postman 集合
 *
 * 安装: npm install -g newman
 * 运行: node run_newman.js
 *
 * 面试加分点: 能把 Postman Collection 接入 CI/CD 流水线
 */

const { execSync } = require('child_process');
const path = require('path');

const COLLECTION = path.join(__dirname, 'firstpro_api_collection.json');
const REPORT_DIR = path.join(__dirname, 'reports');

console.log('='.repeat(55));
console.log('🚀 Newman - Postman 命令行自动化测试');
console.log('='.repeat(55));
console.log();

// ============================================================
// 检查 Newman 是否安装
// ============================================================
function checkNewman() {
    try {
        execSync('newman --version', { stdio: 'pipe' });
        return true;
    } catch {
        return false;
    }
}

// ============================================================
// 运行测试
// ============================================================
function runTests() {
    const cmd = [
        'newman run',
        `"${COLLECTION}"`,
        '--reporters cli,json',
        `--reporter-json-export "${path.join(REPORT_DIR, 'report.json')}"`,
        '--color on',
        '--timeout-request 10000',
        '--delay-request 200',
        '-n 1'  // 运行 1 次（改大可以做稳定性测试）
    ].join(' ');

    console.log('📋 命令:');
    console.log(`   ${cmd}`);
    console.log();

    try {
        execSync(cmd, { stdio: 'inherit' });
        console.log();
        console.log('✅ Newman 测试全部通过！');
    } catch (e) {
        console.log();
        console.log('❌ 有测试失败，请查看上方详情');
        process.exit(1);
    }
}

// ============================================================
// 主流程
// ============================================================
if (!checkNewman()) {
    console.log('⚠️  Newman 未安装，请先执行:');
    console.log('   npm install -g newman');
    console.log();
    console.log('安装后 Newman 就能像 Postman Collection Runner 一样');
    console.log('在命令行/CI 里批量跑接口测试了！');
    console.log();
    console.log('面试话术:');
    console.log('  "我用 Newman 把 Postman 集合接入了 Jenkins/GitHub');
    console.log('   Actions，每次提交代码自动跑接口回归测试"');
    process.exit(0);
}

// 创建报告目录
try { require('fs').mkdirSync(REPORT_DIR, { recursive: true }); } catch {}

runTests();
