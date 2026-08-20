#!/bin/bash
# Docker 生产环境管理脚本

set -e

cd "$(dirname "$0")/../server"

case "$1" in
    start)
        echo "启动生产环境..."
        docker compose -f docker-compose.prod.yml up -d
        echo "服务已启动"
        ;;
    stop)
        echo "停止生产环境..."
        docker compose -f docker-compose.prod.yml down
        echo "服务已停止"
        ;;
    restart)
        echo "重启生产环境..."
        docker compose -f docker-compose.prod.yml restart
        echo "服务已重启"
        ;;
    logs)
        echo "查看日志..."
        docker compose -f docker-compose.prod.yml logs -f "${2:-api}"
        ;;
    status)
        echo "服务状态:"
        docker compose -f docker-compose.prod.yml ps
        ;;
    build)
        echo "重新构建镜像..."
        docker compose -f docker-compose.prod.yml build
        echo "镜像构建完成"
        ;;
    backup)
        echo "备份数据库..."
        docker compose -f docker-compose.prod.yml exec db pg_dump -U arya arya_handcraft > "backup_$(date +%Y%m%d_%H%M%S).sql"
        echo "数据库已备份到: backup_$(date +%Y%m%d_%H%M%S).sql"
        ;;
    *)
        echo "使用: $0 {start|stop|restart|logs|status|build|backup}"
        echo "  start    - 启动服务"
        echo "  stop     - 停止服务"
        echo "  restart  - 重启服务"
        echo "  logs     - 查看日志(可选服务名)"
        echo "  status   - 查看状态"
        echo "  build    - 重新构建"
        echo "  backup   - 备份数据库"
        exit 1
        ;;
esac