FROM node:18-alpine AS builder

WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用（添加NO_FONT_GOOGLE环境变量跳过Google字体检查）
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_TLS_REJECT_UNAUTHORIZED 0
RUN npm run build

# 生产环境
FROM node:18-alpine

WORKDIR /app

# 复制构建后的应用和必要文件
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# 暴露前端端口
EXPOSE 3000

# 启动应用
CMD ["npm", "start"] 