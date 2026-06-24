# Sunny Tea House AI 评价生成系统

这是基于需求文档生成的项目代码仓库初始化分支。包含后端（FastAPI 异步）、前端（Vue 3 + Vite）示例、Docker 多阶段构建、Alembic 迁移脚本示例与使用说明。

主要内容概览：
- backend/ (FastAPI 后端代码位于 backend/app)
- frontend/ (Vue 3 移动端 H5 示例)
- requirements.txt
- Dockerfile (多阶段：前端构建 -> 后端运行)
- docker-compose.example.yml
- alembic/ (基础配置)

默认管理员账号（仅在首次启动 DB 且不存在 admin 时自动创建）：
- 用户名: admin
- 密码: 123456

请阅读下面的运行步骤与配置说明。

---

## 快速开始（本地开发）

1. 克隆仓库并切换到分支：

   git clone https://github.com/ccbgl/AIEvalunationGenerationSystem.git
   cd AIEvalunationGenerationSystem
   git checkout feature/init_project

2. 配置环境变量（复制并修改 .env.example）：

   cp .env.example .env
   编辑 .env 填入您的 MySQL 与 Redis 地址

3. 安装 Python 依赖（推荐 Python 3.10 虚拟环境）：

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

4. 初始化数据库（使用 Alembic 或脚本）：
   - 使用 alembic（推荐）：
       alembic upgrade head
   - 或直接运行初始化脚本：
       python -m backend.app.db.init_db

5. 启动后端：

   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

6. 前端开发：

   cd frontend
   npm install
   npm run dev

## Docker 部署（单镜像运行）

构建镜像：

  docker build -t ai-tea-evaluation:latest .

运行容器（示例）：

  docker run -d \
    -p 8000:8000 \
    -v /opt/tea-shop/upload:/app/upload \
    -e MYSQL_URL="mysql+aiomysql://用户名:密码@数据库IP:3306/数据库名" \
    -e REDIS_URL="redis://RedisIP:6379/0" \
    --name ai-tea-evaluation \
    ai-tea-evaluation:latest

---

更多细节请查看各自目录下的 README 与代码注释。
