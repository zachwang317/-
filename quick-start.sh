#!/bin/bash

echo "======================================"
echo "多语言翻译Agent - 快速部署脚本"
echo "======================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未安装Docker，请先安装Docker"
    echo "   访问：https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：未安装Docker Compose，请先安装Docker Compose"
    echo "   访问：https://docs.docker.com/compose/install/"
    exit 1
fi

# 创建必要的目录
mkdir -p assets logs

# 复制环境变量模板
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据实际情况修改配置"
    echo "   重要：修改 PGDATABASE_URL 数据库连接信息"
    echo ""
fi

# 询问是否立即启动
echo "是否立即启动服务？(y/n)"
read -r answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo "🚀 启动服务中..."
    docker-compose up -d
    
    echo ""
    echo "✅ 服务启动成功！"
    echo ""
    echo "📊 访问地址："
    echo "   前端页面：http://localhost:5000"
    echo ""
    echo "📝 常用命令："
    echo "   查看日志：docker-compose logs -f"
    echo "   停止服务：docker-compose down"
    echo "   重启服务：docker-compose restart"
    echo ""
    echo "📚 更多信息请查看 DEPLOY.md"
else
    echo ""
    echo "✅ 准备完成！"
    echo "   运行以下命令启动服务："
    echo "   docker-compose up -d"
fi
