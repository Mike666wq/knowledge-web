---
id: "kb-linux-nginx-operations"
title: "Nginx 运维速查"
summary: "HTTPS 反向代理、Gzip 与 500 错误排查。"
category: "操作系统"
status: "published"
order: 17
parent: "kb-linux-operations"
tags: ["nginx", "https", "gzip"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Nginx 运维速查

## 18. HTTPS 反向代理配置（Nginx + Let's Encrypt）

**核心概念：**
- HTTPS = HTTP + TLS 加密，防止窃听、篡改、伪装
- Nginx 作为反向代理终止 TLS，解密后转发 HTTP 到后端应用
- Let's Encrypt 提供免费 TLS 证书，90 天有效期，自动续期

**操作步骤：**
1. 安装 Nginx + Certbot：`apt install nginx certbot python3-certbot-nginx`
2. 确保域名 DNS 解析到服务器 IP
3. 配置 Nginx 反向代理（先只配 HTTP 80 端口）
4. `certbot --nginx -d 域名1 -d 域名2` 一键申请+配置
5. 确认自动续期：`systemctl status certbot.timer` + `certbot renew --dry-run`
6. 防火墙放行 80 和 443 端口

**常见坑：**
- 没配 HTTPS 时浏览器自动尝试 443 端口超时导致页面加载慢
- Nginx 以 www-data 用户运行，无法读 /root/ 目录下的文件（Permission denied → 500）

---

## 19. Nginx gzip 压缩配置

- 在 `/etc/nginx/nginx.conf` 的 `http {}` 块中添加 gzip 配置
- 关键参数：`gzip on; gzip_vary on; gzip_comp_level 5; gzip_min_length 1024;`
- gzip_types 覆盖 text/css/js/json/xml/svg 等
- 验证：`curl -sI -H "Accept-Encoding: gzip" https://域名 | grep content-encoding`
- 效果：HTML/CSS/JS 压缩 60-80%，页面加载明显变快

---

## 20. Nginx 500 错误排查命令

**命令**：`awk '$9 == 500 {print $4, $7, $1}' /var/log/nginx/access.log | head -20`

**拆解**：
- awk 默认分隔符：空格（包括连续多个空格、Tab），行首行尾空格自动忽略
- `$9 == 500`：Nginx combined 日志格式中 `$9` 是 HTTP 状态码，匹配 500 错误
- `{print $4, $7, $1}`：打印请求时间 `$4`、URI 路径 `$7`、客户端 IP `$1`
- `head -20`：只看前 20 条
- 自定义分隔符：用 `-F` 参数，如 `awk -F',' '{print $1}' file.csv`
- 注意：`==` 是精确匹配，不是正则匹配（正则用 `~`）

**用途**：排查服务器 500 错误时，快速找出出错的请求时间、路径和来源 IP

---

<!-- KB:INSERT:nginx-operations-additions -->
