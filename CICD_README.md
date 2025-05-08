# LAYRA CI/CD 配置指南

本文档介绍了如何使用GitHub Actions为LAYRA项目设置持续集成和持续部署(CI/CD)。

## 配置概述

LAYRA项目的CI/CD流程包括以下几个部分：

1. **测试阶段**：在每次推送和PR时运行测试
2. **构建阶段**：构建Docker镜像
3. **部署阶段**：将镜像推送到Docker Hub

## 前提条件

在使用此CI/CD配置前，您需要：

1. 在GitHub仓库设置以下密钥：
   - `DOCKERHUB_USERNAME`: 您的Docker Hub用户名
   - `DOCKERHUB_TOKEN`: 您的Docker Hub访问令牌（不是密码）

## GitHub Actions工作流程说明

GitHub Actions工作流程定义在`.github/workflows/ci-cd.yml`文件中，包含以下任务：

### 测试任务

- 使用Ubuntu最新版本作为运行环境
- 设置测试所需的服务：Redis, MongoDB, MySQL, MinIO
- 安装Python 3.10及相关依赖
- 下载必要的模型
- 运行测试

### 构建和部署任务

- 仅在主分支（main或master）接收推送时执行
- 设置Docker Buildx
- 登录到Docker Hub
- 构建并推送后端镜像
- 构建前端代码
- 构建并推送前端镜像

## 手动部署指南

如果您需要在本地或服务器上手动部署LAYRA，可以使用以下步骤：

1. 克隆代码库：
   ```bash
   git clone https://github.com/liweiphys/layra.git
   cd layra
   ```

2. 使用docker-compose运行所有服务：
   ```bash
   docker-compose up -d
   ```

3. 访问应用程序：
   - 前端：http://localhost:3000
   - 后端API：http://localhost:8000

## Docker镜像说明

本项目包含两个Docker镜像：

1. **后端镜像**：包含FastAPI应用和模型服务
   - 基于Python 3.10
   - 包含所有必要的依赖和模型

2. **前端镜像**：包含Next.js应用
   - 基于Node.js 18
   - 使用多阶段构建优化镜像大小

## 环境变量配置

部署时可通过环境变量配置各项参数。主要环境变量包括：

- 数据库连接参数：
  - MYSQL_ROOT_PASSWORD, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
  - MONGODB_ROOT_USERNAME, MONGODB_ROOT_PASSWORD
- MinIO配置参数：
  - MINIO_ROOT_USER, MINIO_ROOT_PASSWORD
- 应用配置参数：
  - APP_SECRET_KEY

## 故障排除

如果您在CI/CD过程中遇到问题：

1. 检查GitHub Actions日志以获取详细错误信息
2. 确保所有密钥和环境变量正确设置
3. 验证Docker Hub凭据是否有效

## 联系方式

如有任何问题，请联系：
- **liweiphys**
- 📧 liweixmu@foxmail.com 