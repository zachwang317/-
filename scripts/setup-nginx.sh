#!/bin/bash

# Nginx配置脚本 - 多语言翻译Agent
# 用于配置域名和HTTPS

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检查是否为root
if [ "$EUID" -ne 0 ]; then
    echo "请使用root用户运行此脚本"
    exit 1
fi

# 输入域名
echo ""
echo "请输入你的域名（例如：example.com 或 www.example.com）"
read -p "域名: " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "域名不能为空"
    exit 1
fi

# 安装Nginx和Certbot
print_info "安装Nginx和Certbot..."
apt install nginx certbot python3-certbot-nginx -y

# 下载Nginx配置模板
cd /etc/nginx/sites-available/
wget -O translation https://raw.githubusercontent.com/zachwang317/-/main/nginx/translation.conf

# 替换域名
sed -i "s/your-domain.com/${DOMAIN}/g" translation

# 启用配置
ln -sf /etc/nginx/sites-available/translation /etc/nginx/sites-enabled/

# 测试配置
print_info "测试Nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    print_success "Nginx配置测试通过"
    
    # 重启Nginx
    systemctl restart nginx
    print_success "Nginx已启动"
    
    # 获取SSL证书
    print_info "正在获取SSL证书..."
    certbot --nginx -d $DOMAIN
    
    print_success "SSL证书配置完成"
    
    echo ""
    print_success "=========================================="
    print_success "  Nginx配置完成！"
    print_success "=========================================="
    echo ""
    echo "访问地址: https://${DOMAIN}"
    echo ""
    echo "管理命令："
    echo "  查看Nginx状态: systemctl status nginx"
    echo "  重启Nginx: systemctl restart nginx"
    echo "  查看Nginx日志: tail -f /var/log/nginx/translation_access.log"
    echo ""
else
    echo "Nginx配置测试失败，请检查配置文件"
    exit 1
fi
