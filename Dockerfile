# syntax=docker/dockerfile:1

# ========== 阶段 1：构建静态产物 ==========
# Debian slim：装 git（vitepress lastUpdated 需要），换清华源避免网络抖动
FROM node:22-bookworm-slim AS build
RUN set -eux; \
    for f in /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list; do \
      [ -f "$f" ] && sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g; s|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' "$f" || true; \
    done \
 && apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# 1) 先只拷贝依赖清单 —— 源码变动时命中缓存，跳过 npm ci
COPY package.json package-lock.json ./
RUN npm ci

# 2) 拷贝源码 + 删掉被解引用的 docs/notes 副本（Docker COPY 会把宿主软链展开成真实目录，必须先删再建）
COPY . .
RUN rm -rf docs/notes
# ★ 删掉 notes/ 下嵌套的 .git 目录（如 Linux基础/.git、Java/Java/.git 等）
#   BuildKit 在 git-aware context 下会跳过整个 nested git repo，导致整个父目录消失
RUN find notes -type d -name .git -exec rm -rf {} + 2>/dev/null || true
RUN npm run sync-notes

# 3) 门禁检查 + 构建（任何一步失败则镜像构建失败，坏镜像出不去）
RUN npm run check-md \
 && npm run build

# ========== 阶段 2：Nginx 运行时 ==========
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/docs/.vitepress/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1
