#!/bin/bash

# =================================================================
# 阿里云一键部署脚本 - 多语言翻译Agent
# =================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统信息
check_system() {
    print_info "检查系统信息..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_success "操作系统: $PRETTY_NAME"
    else
        print_error "无法识别操作系统"
        exit 1
    fi
}

# 更新系统
update_system() {
    print_info "更新系统软件包..."
    apt update
    apt upgrade -y
    print_success "系统更新完成"
}

# 安装Docker
install_docker() {
    print_info "检查Docker安装状态..."
    if command -v docker &> /dev/null; then
        print_success "Docker已安装: $(docker --version)"
    else
        print_info "安装Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        systemctl start docker
        systemctl enable docker
        print_success "Docker安装完成: $(docker --version)"
    fi
}

# 安装Docker Compose
install_docker_compose() {
    print_info "检查Docker Compose安装状态..."
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose已安装: $(docker-compose --version)"
    else
        print_info "安装Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose安装完成: $(docker-compose --version)"
    fi
}

# 安装Git
install_git() {
    print_info "检查Git安装状态..."
    if command -v git &> /dev/null; then
        print_success "Git已安装: $(git --version)"
    else
        print_info "安装Git..."
        apt install git -y
        print_success "Git安装完成: $(git --version)"
    fi
}

# 克隆项目
clone_project() {
    print_info "克隆项目..."
    if [ -d "/opt/translation" ]; then
        print_warning "项目目录已存在，正在更新..."
        cd /opt/translation
        git pull origin main
    else
        print_info "从GitHub克隆项目..."
        cd /opt
        git clone https://github.com/zachwang317/-.git translation
        cd translation
    fi
    print_success "项目克隆完成"
}

# 配置环境变量
setup_env() {
    print_info "配置环境变量..."
    
    # 生成随机密码
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # 创建.env文件
    cat > .env <<EOF
# 数据库连接
PGDATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/translation_db
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=translation_db

# 对象存储配置（可选）
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
S3_ENDPOINT=

# Python环境
PYTHONPATH=/app
COZE_PROJECT_ENV=PROD
EOF
    
    print_success "环境变量配置完成"
    print_warning "数据库密码已自动生成，请妥善保存: ${DB_PASSWORD}"
    print_warning "密码已保存在 $(pwd)/.env 文件中"
}

# 创建必要目录
create_directories() {
    print_info "创建必要目录..."
    mkdir -p assets logs
    chmod -R 755 assets logs
    print_success "目录创建完成"
}

# 启动服务
start_services() {
    print_info "启动Docker Compose服务..."
    docker-compose up -d
    print_success "服务启动完成"
    
    # 等待服务启动
    print_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    print_info "检查服务状态..."
    docker-compose ps
}

# 显示访问信息
show_access_info() {
    echo ""
    print_success "=========================================="
    print_success "    部署完成！"
    print_success "=========================================="
    echo ""
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com)
    
    echo -e "${BLUE}访问地址:${NC}"
    echo -e "  http://${SERVER_IP}:5000"
    echo ""
    
    echo -e "${BLUE}管理命令:${NC}"
    echo -e "  查看日志: ${GREEN}cd /opt/translation && docker-compose logs -f${NC}"
    echo -e "  停止服务: ${GREEN}cd /opt/translation && docker-compose stop${NC}"
    echo -e "  启动服务: ${GREEN}cd /opt/translation && docker-compose start${NC}"
    echo -e "  重启服务: ${GREEN}cd /opt/translation && docker-compose restart${NC}"
    echo ""
    
    echo -e "${YELLOW}重要提示:${NC}"
    echo -e "  1. 请在阿里云控制台开放5000端口"
    echo -e "  2. 数据库密码已保存在 .env 文件中"
    echo -e "  3. 建议定期备份数据库"
    echo ""
    
    echo -e "${BLUE}端口开放教程:${NC}"
    echo -e "  1. 登录阿里云控制台"
    echo -e "  2. 进入 轻量应用服务器 → 实例"
    echo -e "  3. 点击 防火墙 → 添加规则"
    echo -e "  4. 添加规则: TCP 5000 允许所有IP"
    echo ""
}

# 主函数
main() {
    echo ""
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}  多语言翻译Agent - 阿里云一键部署脚本${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo ""
    
    # 检查root
    check_root
    
    # 检查系统
    check_system
    
    # 确认部署
    echo -e "${YELLOW}即将开始部署，这将需要5-10分钟...${NC}"
    read -p "是否继续? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "部署已取消"
        exit 1
    fi
    
    # 执行部署步骤
    update_system
    install_docker
    install_docker_compose
    install_git
    clone_project
    setup_env
    create_directories
    start_services
    show_access_info
}

# 运行主函数
main
