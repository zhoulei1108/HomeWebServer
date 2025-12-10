#!/bin/bash

# 模板目录结构重构执行脚本
# 用于 Linux/macOS 环境的自动化重构执行

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 显示标题
show_header() {
    echo "============================================================"
    echo "🏠 家庭日历系统 - 模板目录结构重构工具"
    echo "============================================================"
    echo
}

# 显示菜单
show_menu() {
    echo "📋 请选择执行模式:"
    echo "1. DRY RUN - 仅分析，不修改文件 (推荐先执行)"
    echo "2. 执行重构 - 实际修改文件和目录结构"
    echo "3. 查看详细帮助"
    echo "4. 退出"
    echo
}

# 检查环境
check_environment() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 未安装或不在PATH中"
        exit 1
    fi
    
    if [ ! -f "restructure_templates.py" ]; then
        log_error "restructure_templates.py 脚本不存在"
        exit 1
    fi
}

# 执行 DRY RUN
run_dry_run() {
    echo
    log_info "🔍 开始 DRY RUN 模式..."
    log_warn "⚠️  这不会修改任何文件，仅显示将要执行的操作"
    echo
    
    python3 restructure_templates.py --dry-run
    
    echo
    log_success "✅ DRY RUN 完成"
    log_info "💡 请检查输出结果，确认无误后选择选项2执行实际重构"
}

# 执行重构
run_execute() {
    echo
    log_warn "⚠️  警告: 即将执行实际的模板重构操作"
    log_info "💡 建议先执行 DRY RUN (选项1) 确认操作"
    echo
    
    read -p "确认执行重构? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "❌ 操作已取消"
        return
    fi
    
    echo
    log_info "🚀 开始执行模板重构..."
    log_info "📦 正在创建备份..."
    echo
    
    if python3 restructure_templates.py; then
        echo
        log_success "✅ 模板重构执行完成!"
        log_info "📋 已生成详细报告: template_restructure_report.json"
        log_info "🔄 建议执行以下步骤:"
        echo "   1. 运行开发服务器测试: python3 manage.py runserver"
        echo "   2. 检查各个页面是否正常显示"
        echo "   3. 验证功能是否完整"
        echo "   4. 如有问题，可从备份恢复"
    else
        echo
        log_error "❌ 重构过程中出现错误"
        log_info "💡 请检查错误信息并手动修复"
    fi
}

# 显示帮助
show_help() {
    echo
    log_info "📖 模板重构工具帮助"
    echo
    echo "功能:"
    echo "  - 分析当前模板文件分布"
    echo "  - 解决模板文件冲突"
    echo "  - 统一目录结构"
    echo "  - 更新代码中的模板路径引用"
    echo
    echo "目标结构:"
    echo "  templates/"
    echo "  ├── base.html"
    echo "  ├── registration/"
    echo "  ├── family/"
    echo "  ├── events/"
    echo "  ├── housework/"
    echo "  └── calendar/"
    echo
    echo "选项:"
    echo "  --dry-run    : 仅显示操作，不执行修改"
    echo "  --no-backup  : 跳过备份创建 (不推荐)"
    echo
    echo "使用示例:"
    echo "  python3 restructure_templates.py --dry-run"
    echo "  python3 restructure_templates.py"
    echo
    log_warn "⚠️  重要提示:"
    echo "  1. 执行前建议提交所有代码更改到Git"
    echo "  2. 首次使用务必先执行 DRY RUN"
    echo "  3. 工具会自动创建备份目录"
    echo "  4. 如有问题可从备份恢复"
}

# 主循环
main() {
    show_header
    
    while true; do
        show_menu
        read -p "请输入选项 (1-4): " -n 1 -r
        echo
        
        case $REPLY in
            1)
                run_dry_run
                break
                ;;
            2)
                run_execute
                break
                ;;
            3)
                show_help
                ;;
            4)
                log_info "退出程序"
                exit 0
                ;;
            *)
                log_error "❌ 无效选项，请重新选择"
                echo
                ;;
        esac
    done
}

# 脚本入口
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    check_environment
    main
fi

echo
echo "============================================================"
echo "操作完成"
echo "============================================================"