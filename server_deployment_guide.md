# LAYRA 服务器部署配置指南

本指南将帮助您配置GitHub Actions以将LAYRA项目部署到您自己的服务器。

## 在GitHub设置密钥

要成功部署到服务器，您需要在GitHub仓库中设置以下密钥。在仓库页面，进入 `Settings` > `Secrets and variables` > `Actions`，然后添加以下密钥：

### 服务器连接密钥

1. `SSH_HOST` - 服务器IP地址或域名
2. `SSH_USER` - SSH用户名
3. `SSH_PRIVATE_KEY` - SSH私钥（整个私钥内容）
4. `SSH_KNOWN_HOSTS` - SSH已知主机（可通过运行 `ssh-keyscan -H 您的服务器IP` 获取）

### Docker Hub密钥

5. `DOCKERHUB_USERNAME` - Docker Hub用户名
6. `DOCKERHUB_TOKEN` - Docker Hub访问令牌（不是密码）

## 服务器准备

在使用GitHub Actions进行部署之前，请确保您的服务器满足以下条件：

1. 已安装Docker和Docker Compose
2. SSH用户有足够的权限运行Docker命令
3. 服务器防火墙已开放以下端口：
   - 3000 (前端)
   - 8000 (后端API)
   - 9110 (MinIO)
   - 27017 (MongoDB)
   - 3306 (MySQL)
   - 6379 (Redis)
   - 19530 (Milvus)

## 设置SSH密钥

1. 在本地计算机上生成SSH密钥对（如果还没有）：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. 将公钥添加到服务器的authorized_keys文件：
   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server-ip
   ```

3. 检索私钥内容以添加到GitHub密钥：
   ```bash
   cat ~/.ssh/id_ed25519
   ```
   将整个输出（包括BEGIN和END行）复制并保存为GitHub中的`SSH_PRIVATE_KEY`密钥。

4. 获取并添加known_hosts内容：
   ```bash
   ssh-keyscan -H your-server-ip
   ```
   将输出复制并保存为GitHub中的`SSH_KNOWN_HOSTS`密钥。

## 工作流程说明

CI/CD工作流程包含以下阶段：

1. **构建和推送Docker镜像**：构建应用程序并将镜像推送到Docker Hub
2. **部署到服务器**：将应用程序部署到远程服务器

部署步骤包括：
1. 配置SSH连接
2. 传输必要的部署文件到服务器
3. 执行远程部署脚本

## 故障排除

如果部署失败，请检查以下内容：

1. GitHub Actions日志中的错误信息
2. 确保所有密钥都已正确设置
3. 验证服务器是否可以从互联网访问
4. 确保SSH用户具有运行Docker命令的权限
5. 检查服务器上的Docker日志以获取更多信息：
   ```bash
   docker-compose logs
   ```

## 检查部署状态

部署后，您可以通过以下方式检查应用程序状态：

1. 在浏览器中访问您的前端应用：`http://your-server-ip:3000`
2. 检查容器状态：
   ```bash
   ssh user@your-server-ip "cd /opt/layra && docker-compose ps"
   ``` 