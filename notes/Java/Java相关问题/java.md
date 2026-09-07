---
id: "kb-programming-java"
title: "Java"
category: "编程语言"
status: "published"
order: 1
---

# ☕ Java

---

## Spring Boot 框架

### 是什么
- 基于 Spring 框架的快速开发脚手架，核心思想：**约定优于配置**
- Spring = 发动机，Spring Boot = 整车（开箱即用）

### 核心特点
1. **内嵌服务器**：内置 Tomcat，`java -jar` 直接运行，不用外部部署
2. **自动配置**：根据引入的依赖自动配置 Bean
3. **起步依赖（Starter）**：一个 starter 搞定一组功能，如 `spring-boot-starter-web` = Spring MVC + Tomcat
4. **Actuator 监控**：内置健康检查、指标暴露

### IDEA 创建 Spring Boot 项目
1. File → New → Project → Spring Initializr
2. 配置 Group、Artifact、JDK（推荐 Java 17，Spring Boot 3.x 最低要求）
3. 选依赖：Spring Web、DevTools、Lombok 等
4. 生成项目，等待依赖下载

### 项目结构
- 启动类：`@SpringBootApplication` 注解 + `main` 方法
- 配置文件：`application.yml`
- Controller 示例：`@RestController` + `@GetMapping`

### 对比传统 Spring
| 传统 Spring | Spring Boot |
|---|---|
| 手动配置 DispatcherServlet | 自动配好，引入 starter 就行 |
| 配置 Tomcat | 内嵌 Tomcat，直接运行 jar |
| XML 配置 Bean | `@Component` 扫描自动注册 |
| 打 war 包部署到外部 Tomcat | 打 jar 包直接运行 |

### 一句话总结
- **Maven** = 管依赖 + 管构建
- **Spring Boot** = 管开发（少写配置，快速搭建）
- Maven 拉依赖 → Spring Boot 自动配置 → 开发者专注业务代码

### 注意事项
- Spring Boot 3.x 要求 Java 17+
- 第一次创建项目下载依赖较慢（需从 Maven 中央仓库拉取）

---

## Maven 构建工具

### 是什么
- Java 项目的**构建和依赖管理工具**
- **pom.xml**：项目配置文件，声明依赖和构建信息
- **GAV 坐标**：`groupId:artifactId:version`，依赖的唯一标识
- **本地仓库**：`~/.m2/repository`，jar 包缓存

### 核心功能
1. **依赖管理**：在 `pom.xml` 中声明依赖，Maven 自动从中央仓库下载 jar 及其所有传递依赖
2. **项目构建**：编译、测试、打包（jar/war）一条命令搞定（`mvn clean package`）
3. **项目结构规范**：约定大于配置，源码 `src/main/java`，配置 `src/main/resources`，测试 `src/test/java`

---

## application.yml 配置文件

### 是什么
- Spring Boot 的核心配置文件，相当于项目的"启动说明书"
- 告诉项目怎么连数据库、跑在哪个端口、MyBatis 怎么配置等

### 关键配置项
1. **spring.datasource** — 数据库连接
   - driver-class-name: MySQL 8.0 驱动
   - url: jdbc:mysql://IP:3306/库名?参数（时区、编码、SSL等）
   - username / password: 数据库账号密码
2. **mybatis** — MyBatis 配置
   - mapper-locations: XML 映射文件路径
   - type-aliases-package: 实体类包路径
   - map-underscore-to-camel-case: 下划线自动转驼峰
   - log-impl: StdOutImpl（控制台打印 SQL）
3. **server.port** — 应用端口，默认 8080

### 远程数据库连接
- 需要对方的 IP + 端口 + 密码
- 对方 MySQL 需允许远程连接（CREATE USER 'root'@'%' IDENTIFIED BY '密码'）
- Windows 防火墙可能拦截 ping，需放行 ICMP 或关闭防火墙测试
