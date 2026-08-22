# 仓库根 Dockerfile:为 Railway 同仓库多服务场景提供固定构建入口。
# 背景:新服务未应用 railway.toml 的 buildContext=server 时,Railway 默认从仓库根
# 寻找 ./Dockerfile,故此文件以【仓库根】为构建上下文编写,路径均带 server/ 前缀。
# 旧服务(buildContext=server)仍使用 server/Dockerfile,两者互不影响。
FROM public.ecr.aws/docker/library/python:3.12-slim

# 时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖(健康检查用 curl)
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝应用代码(server/ → /app/,含 app/ alembic/ alembic.ini)
COPY server/ .

RUN mkdir -p /app/logs

EXPOSE 8000

# 启动命令:先执行数据库迁移(幂等),再启动 API
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]