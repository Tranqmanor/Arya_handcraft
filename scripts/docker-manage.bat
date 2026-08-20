@echo off
REM Docker 生产环境管理脚本(Windows版)

cd /d "%~dp0..\server"

if "%1"=="" (
    echo 使用: %0 {start^|stop^|restart^|logs^|status^|build^|backup}
    echo   start    - 启动服务
    echo   stop     - 停止服务
    echo   restart  - 重启服务
    echo   logs     - 查看日志(可选服务名)
    echo   status   - 查看状态
    echo   build    - 重新构建
    echo   backup   - 备份数据库
    exit /b 0
)

if "%1"=="start" (
    echo 启动生产环境...
    docker compose -f docker-compose.prod.yml up -d
    echo 服务已启动
) else if "%1"=="stop" (
    echo 停止生产环境...
    docker compose -f docker-compose.prod.yml down
    echo 服务已停止
) else if "%1"=="restart" (
    echo 重启生产环境...
    docker compose -f docker-compose.prod.yml restart
    echo 服务已重启
) else if "%1"=="logs" (
    echo 查看日志...
    if "%2"=="" (
        docker compose -f docker-compose.prod.yml logs -f api
    ) else (
        docker compose -f docker-compose.prod.yml logs -f %2
    )
) else if "%1"=="status" (
    echo 服务状态:
    docker compose -f docker-compose.prod.yml ps
) else if "%1"=="build" (
    echo 重新构建镜像...
    docker compose -f docker-compose.prod.yml build
    echo 镜像构建完成
) else if "%1"=="backup" (
    echo 备份数据库...
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set date=%%c%%a%%b
    for /f "tokens=1-3 delims=: " %%a in ('time /t') do set time=%%a%%b%%c
    docker compose -f docker-compose.prod.yml exec db pg_dump -U arya arya_handcraft > backup_%date%_%time%.sql
    echo 数据库已备份到: backup_%date%_%time%.sql
) else (
    echo 无效命令: %1
    exit /b 1
)