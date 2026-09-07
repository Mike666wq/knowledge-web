# Gitlab+Jenkins+hexo实现CICD持续集成

## 目录

- [1. 介绍](#1-介绍)
- [2. CICD 环境搭建](#2-cicd环境搭建)
  - [2.1 docker 环境](#21-docker环境)
  - [2.2 GitLab 配置](#22-gitlab配置)
  - [2.3 Harbor 配置](#23-harbor配置)
  - [2.4 Jenkins 配置](#24-jenkins配置)
- [3. hexo 系统 CICD 实战](#3-hexo系统cicd实战)
  - [3.1 配置 hexo 高可用](#31-配置hexo高可用)
  - [3.2 集群配置私仓地址](#32-集群配置私仓地址)
  - [3.3 jenkins 配置 CICD](#33-jenkins配置cicd)
  - [3.4 Hexo 仓库配置](#34-hexo仓库配置)
  - [3.5 编写 Dockerfile](#35-编写dockerfile)
  - [3.6 测试](#36-测试)
- [4. 关键点总结](#4-关键点总结)
  - [4.1 整体流程](#41-整体流程)
  - [4.2 关键点全景](#42-关键点全景)
  - [4.3 Jenkins 节点配置（核心枢纽）](#43-jenkins-节点配置核心枢纽)
  - [4.4 易踩坑清单（本次实践踩过的 4 个）](#44-易踩坑清单本次实践踩过的-4-个)

## 1. 介绍

- `Gitlab`+`Jenkins`+`Docker`+`Harbor`+`K8S集群` 的`CICD`搭建教程
- 在搭建好的`CICD`平台上`持续集成部署hexo博客系统`
- 其中`Gitlab`+`Jenkins` +`Harbor`都是通过`容器化`部署
- 篇幅有限，关于CD环境`k8s集群`这里用之前部署好的，并且已经做了`kubeconfig`证书

下面为涉及到的机器：

| 用到的机器 | ip |
| --- | --- |
| 客户机 | 本地物理机 |
| Gitlab+Jenkins+Docker | 192.168.116.132 |
| docker镜像仓库:harbor | 192.168.116.133 |
| k8s集群-master节点 | 192.168.116.129 |
| k8s集群-node节点 | 192.168.116.130 |
| k8s集群-node节点 | 192.168.116.131 |

1. 这里客户机用本地的IDE持续编码，然后push代码到gitlab。
2. gitlab中的web钩子触发jenkins中配置好的构建触发器，通过shell命令拉取gitlab仓库中的代码。
3. 通过拉取的应用源码和Dockerfile文件来构建应用镜像。
4. 构建完成后将应用镜像push到harbor私有镜像仓库。
5. 通过shell命令的方式在jenkins中用kubelet客户端将镜像从私有仓库拉取到k8s集群并更新其deploy中的镜像。
6. 默认deploy更新副本的方式为滚动更新，整个流程中，只有客户机push代码是手手动的方式，其他全是自动。

![架构图](./assets/gitlab-jenkins-hexo-cicd/architecture-diagram.png)

## 2. CICD环境搭建

CI即为持续集成(Continue Integration,简称CI)，用通俗的话讲，就是持续的整合版本库代码编译后制作应用镜像。建立有效的持续集成环境可以减少开发过程中一些不必要的问题、提高代码质量、快速迭代等,

常用的工具和平台有:

- Jenkins:基于Java开发的一种持续集成工具,用于监控持续重复的工作,旨在提供一个开放易用的软件平台,使软件的持续集成变成可能。
- Bamboo: 是一个企业级商用软件,可以部署在大规模生产环境中。

CD即持续交付Continuous Delivery和持续部署Continuous Deployment，用通俗的话说，即可以持续的部署到生产环境给客户使用，这里分为两个阶段，持续交付我理解为满足上线条件的过程，但是没有上线，持续部署，即为上线应用的过程

关于CD环境，我们使用以前搭建好的K8s集群，K8s集群可以实现应用的健康检测，动态扩容，滚动更新等优点，关于K8s集群的搭建，小伙伴可以看看我的其他文章

### 2.1 docker环境

- 点击进入华为开源镜像Docker安装，按照步骤装好
- 自行配置好镜像加速服务，否则境内无法push镜像，可以参考[这篇文章](https://iproute.cn/2025/12/17/docker-tian-jia-http-dai-li/)

### 2.2 GitLab配置

GitLab是一个基于Git的版本控制平台，,提供了Git仓库管理、代码审查、问题跟踪、活动反馈和wiki

```bash
[root@jenkins ~]# docker pull beginor/gitlab-ce
```

创建共享卷目录

```bash
[root@jenkins ~]# mkdir -p /data/gitlab/etc/ /data/gitlab/log/ /data/gitlab/data
[root@jenkins ~]# chmod 777 /data/gitlab/etc/ /data/gitlab/log/ /data/gitlab/data/
```

创建gitlab容器

```bash
[root@jenkins ~]# docker run -itd \
--name=gitlab --restart=always \
--privileged=true   \
-p 8443:443  -p 80:80 -p 222:22 \
-v  /data/gitlab/etc:/etc/gitlab \
-v  /data/gitlab/log:/var/log/gitlab \
-v  /data/gitlab/data:/var/opt/gitlab  beginor/gitlab-ce

[root@jenkins ~]# docker ps -a
CONTAINER ID   IMAGE               COMMAND             CREATED         STATUS                   PORTS                                                                                                                   NAMES
845af40a46fa   beginor/gitlab-ce   "/assets/wrapper"   4 minutes ago   Up 4 minutes (healthy)   0.0.0.0:80->80/tcp, [::]:80->80/tcp, 0.0.0.0:222->22/tcp, [::]:222->22/tcp, 0.0.0.0:8443->443/tcp, [::]:8443->443/tcp   gitlab
```

切记:这里的端口要设置成80，要不push项目会提示没有报错，如果宿主机端口被占用，需要把这个端口腾出来

关闭容器修改配置文件

```bash
[root@jenkins ~]# docker stop gitlab
```

`external_url 'http://192.168.116.132'`

```bash
[root@jenkins ~]# cat /data/gitlab/etc/gitlab.rb |grep external_url |grep -Ev ^#
external_url 'http://192.168.116.132'
```

`gitlab_rails['gitlab_ssh_host'] = '192.168.116.132'`

```bash
[root@jenkins ~]# cat /data/gitlab/etc/gitlab.rb |grep gitlab_ssh_host
gitlab_rails['gitlab_ssh_host'] = '192.168.116.132'
```

`gitlab_rails[gitlab_shell_ssh_port] = 222`

```bash
[root@jenkins ~]# cat /data/gitlab/etc/gitlab.rb | grep gitlab_shell_ssh
gitlab_rails['gitlab_shell_ssh_port'] = 222
```

修改`/data/gitlab/data/gitlab-rails/etc/gitlab.yml` 中的host信息

```bash
[root@jenkins ~]# vim /data/gitlab/data/gitlab-rails/etc/gitlab.yml
gitlab:
    ## Web server settings (note: host is the FQDN, do not include http://)
    host: 192.168.116.132
    port: 80
    https: false
```

修改完配置文件之后。直接启动容器

```bash
[root@jenkins ~]# docker start gitlab
```

等待一段时间启动，在宿主机所在的物理机访问，`http://192.168.116.132/` ，会自动跳转到修改密码(root用户),如果密码设置的没有满足一定的复杂性，则会报500，需要重新设置

![image-20260723155023930](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723155023930.png)

使用root用户登录进系统

![image-20260723155343263](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723155343263.png)

登录后的页面

![image-20260723155408622](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723155408622.png)

下面是创建一个项目用于熟悉和测试gitlab

![image-20260723155457048](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723155457048.png)

将自己的公钥传上去

![](./assets/gitlab-jenkins-hexo-cicd/image-20251217144053019.png)

复制公钥

![](./assets/gitlab-jenkins-hexo-cicd/image-20251217144326705.png)

随便上传点东西测试，参考代码在网页上

![](./assets/gitlab-jenkins-hexo-cicd/image-20251217144618686.png)

上传的代码

```cmd
C:\Users\bbben\Desktop\demo>git init
Initialized empty Git repository in C:/Users/bbben/Desktop/demo/.git/

C:\Users\bbben\Desktop\demo>git remote add origin ssh://git@192.168.116.132:222/root/test-repo.git

C:\Users\bbben\Desktop\demo>git add .

C:\Users\bbben\Desktop\demo>git commit -m "Initial commit"
[master (root-commit) 9abe30c] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 index.html

C:\Users\bbben\Desktop\demo>git push -u origin master
The authenticity of host '[192.168.116.132]:222 ([192.168.116.132]:222)' can't be established.
ED25519 key fingerprint is SHA256:NRKS3b6IhBlR2Y++OnQo55C8l+MTbF4+7VFT7qU5Ovo.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[192.168.116.132]:222' (ED25519) to the list of known hosts.
Enumerating objects: 3, done.
Counting objects: 100% (3/3), done.
Writing objects: 100% (3/3), 219 bytes | 219.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To ssh://192.168.116.132:222/root/test-repo.git
 * [new branch]      master -> master
branch 'master' set up to track 'origin/master'.
```

确认代码上传成功

![image-20260723160248439](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723160248439.png)

### 2.3 Harbor配置

- 这里仓库我们选择harbor，因为有web页面，当然也可以使用 registry
- 首先需要设置selinux、防火墙

```bash
[root@harbor ~]# cat /etc/selinux/config | grep -Ev "^#|^$"
SELINUX=disabled
SELINUXTYPE=targeted
[root@harbor ~]# getenforce 
Disabled
[root@harbor ~]# systemctl disable --now firewalld
```

- 安装并启动docker并安装docker-compose
  - docker-compose下载地址：https://github.com/docker/compose/releases/download/v5.0.0/docker-compose-linux-x86_64
  - 现在官方已经收编了`docker compose`

```bash
[root@harbor ~]# mv docker-compose-linux-x86_64 /bin/docker-compose
[root@harbor ~]# chmod +x /bin/docker-compose
[root@harbor ~]# docker-compose -v
Docker Compose version v5.0.0

[root@harbor ~]# docker compose version
Docker Compose version v5.3.1
```

- 解压harbor 安装包：harbor-offline-installer-v2.14.1.tgz，导入相关镜像

```bash
[root@harbor ~]# tar xzvf harbor-offline-installer-v2.14.1.tgz
[root@harbor ~]# cd harbor
[root@harbor harbor]# docker load -i harbor.v2.15.2.tar.gz 
Loaded image: goharbor/harbor-exporter:v2.15.2
Loaded image: goharbor/harbor-portal:v2.15.2
Loaded image: goharbor/harbor-db:v2.15.2
Loaded image: goharbor/harbor-registryctl:v2.15.2
Loaded image: goharbor/nginx-photon:v2.15.2
Loaded image: goharbor/registry-photon:v2.15.2
Loaded image: goharbor/harbor-core:v2.15.2
Loaded image: goharbor/harbor-jobservice:v2.15.2
Loaded image: goharbor/valkey-photon:v2.15.2
Loaded image: goharbor/prepare:v2.15.2
Loaded image: goharbor/harbor-log:v2.15.2
Loaded image: goharbor/trivy-adapter-photon:v2.15.2
```

修改配置文件

```bash
[root@harbor ~]# cd harbor
[root@harbor harbor]# cp harbor.yml.tmpl harbor.yml
[root@harbor harbor]# vim harbor.yml
```

设置主机地址和密码， 把https部分的内容注释掉

```bash
[root@harbor harbor]# cat harbor.yml |grep -Ev "^ *#|^ *$"
hostname: 192.168.116.133
...........
harbor_admin_password: Harbor12345
...........

[root@harbor harbor]# ./prepare 
prepare base dir is set to /root/harbor
WARNING:root:WARNING: HTTP protocol is insecure. Harbor will deprecate http protocol in the future. Please make sure to upgrade to https
Generated configuration file: /config/portal/nginx.conf
Generated configuration file: /config/log/logrotate.conf
Generated configuration file: /config/log/rsyslog_docker.conf
Generated configuration file: /config/nginx/nginx.conf
Generated configuration file: /config/core/env
Generated configuration file: /config/core/app.conf
Generated configuration file: /config/registry/config.yml
Generated configuration file: /config/registryctl/env
Generated configuration file: /config/registryctl/config.yml
Generated configuration file: /config/db/env
Generated configuration file: /config/jobservice/env
Generated configuration file: /config/jobservice/config.yml
copy /data/secret/tls/harbor_internal_ca.crt to shared trust ca dir as name harbor_internal_ca.crt ...
ca file /hostfs/data/secret/tls/harbor_internal_ca.crt is not exist
copy  to shared trust ca dir as name storage_ca_bundle.crt ...
copy None to shared trust ca dir as name redis_tls_ca.crt ...
Generated and saved secret to file: /data/secret/keys/secretkey
Successfully called func: create_root_cert
Generated configuration file: /compose_location/docker-compose.yml
Clean up the input dir
```

开始安装

```bash
[root@harbor harbor]# ./install.sh 

[Step 0]: checking if docker is installed ...

Note: docker version: 29.6.2

[Step 1]: checking docker-compose is installed ...

Note: Docker Compose version v5.3.1

[Step 2]: loading Harbor images ...
Loaded image: goharbor/harbor-exporter:v2.15.2
Loaded image: goharbor/harbor-portal:v2.15.2
Loaded image: goharbor/harbor-db:v2.15.2
Loaded image: goharbor/harbor-registryctl:v2.15.2
Loaded image: goharbor/nginx-photon:v2.15.2
Loaded image: goharbor/registry-photon:v2.15.2
Loaded image: goharbor/harbor-core:v2.15.2
Loaded image: goharbor/harbor-jobservice:v2.15.2
Loaded image: goharbor/valkey-photon:v2.15.2
Loaded image: goharbor/prepare:v2.15.2
Loaded image: goharbor/harbor-log:v2.15.2
Loaded image: goharbor/trivy-adapter-photon:v2.15.2


[Step 3]: preparing environment ...

[Step 4]: preparing harbor configs ...
prepare base dir is set to /root/harbor
WARNING:root:WARNING: HTTP protocol is insecure. Harbor will deprecate http protocol in the future. Please make sure to upgrade to https
Clearing the configuration file: /config/portal/nginx.conf
Clearing the configuration file: /config/log/logrotate.conf
Clearing the configuration file: /config/log/rsyslog_docker.conf
Clearing the configuration file: /config/nginx/nginx.conf
Clearing the configuration file: /config/core/env
Clearing the configuration file: /config/core/app.conf
Clearing the configuration file: /config/registry/passwd
Clearing the configuration file: /config/registry/config.yml
Clearing the configuration file: /config/registryctl/env
Clearing the configuration file: /config/registryctl/config.yml
Clearing the configuration file: /config/db/env
Clearing the configuration file: /config/jobservice/env
Clearing the configuration file: /config/jobservice/config.yml
Generated configuration file: /config/portal/nginx.conf
Generated configuration file: /config/log/logrotate.conf
Generated configuration file: /config/log/rsyslog_docker.conf
Generated configuration file: /config/nginx/nginx.conf
Generated configuration file: /config/core/env
Generated configuration file: /config/core/app.conf
Generated configuration file: /config/registry/config.yml
Generated configuration file: /config/registryctl/env
Generated configuration file: /config/registryctl/config.yml
Generated configuration file: /config/db/env
Generated configuration file: /config/jobservice/env
Generated configuration file: /config/jobservice/config.yml
copy /data/secret/tls/harbor_internal_ca.crt to shared trust ca dir as name harbor_internal_ca.crt ...
ca file /hostfs/data/secret/tls/harbor_internal_ca.crt is not exist
copy  to shared trust ca dir as name storage_ca_bundle.crt ...
copy None to shared trust ca dir as name redis_tls_ca.crt ...
loaded secret from file: /data/secret/keys/secretkey
Generated configuration file: /compose_location/docker-compose.yml
Clean up the input dir


Note: stopping existing Harbor instance ...


[Step 5]: starting Harbor ...
[+] up 10/10
 ✔ Network harbor_harbor       Created                                                                                                                                                                                           0.1s
 ✔ Container harbor-log        Started                                                                                                                                                                                           1.0s
 ✔ Container registryctl       Started                                                                                                                                                                                           1.8s
 ✔ Container redis             Started                                                                                                                                                                                           2.1s
 ✔ Container harbor-db         Started                                                                                                                                                                                           2.0s
 ✔ Container harbor-portal     Started                                                                                                                                                                                           1.8s
 ✔ Container registry          Started                                                                                                                                                                                           2.1s
 ✔ Container harbor-core       Started                                                                                                                                                                                           2.5s
 ✔ Container harbor-jobservice Started                                                                                                                                                                                           2.9s
 ✔ Container nginx             Started                                                                                                                                                                                           3.0s
✔ ----Harbor has been installed and started successfully.----
```

查看相关的容器

```bash
[root@harbor harbor]# docker ps -a
CONTAINER ID   IMAGE                                 COMMAND                  CREATED          STATUS                    PORTS                                     NAMES
fcdb297df352   goharbor/harbor-jobservice:v2.15.2    "/harbor/entrypoint.…"   55 seconds ago   Up 46 seconds (healthy)                                             harbor-jobservice
7602bf1becf6   goharbor/nginx-photon:v2.15.2         "nginx -g 'daemon of…"   55 seconds ago   Up 53 seconds (healthy)   0.0.0.0:80->8080/tcp, [::]:80->8080/tcp   nginx
b6db0bcda8c9   goharbor/harbor-core:v2.15.2          "/harbor/entrypoint.…"   56 seconds ago   Up 53 seconds (healthy)                                             harbor-core
558f11ed7606   goharbor/registry-photon:v2.15.2      "/home/harbor/entryp…"   56 seconds ago   Up 55 seconds (healthy)                                             registry
99a721500ba8   goharbor/harbor-db:v2.15.2            "/docker-entrypoint.…"   56 seconds ago   Up 55 seconds (healthy)                                             harbor-db
9fcf97ec790a   goharbor/valkey-photon:v2.15.2        "valkey-server /etc/…"   56 seconds ago   Up 55 seconds (healthy)                                             redis
f5d64f86d5f3   goharbor/harbor-registryctl:v2.15.2   "/home/harbor/start.…"   56 seconds ago   Up 55 seconds (healthy)                                             registryctl
a4f41522ff72   goharbor/harbor-portal:v2.15.2        "nginx -g 'daemon of…"   56 seconds ago   Up 55 seconds (healthy)                                             harbor-portal
934be5a9cf42   goharbor/harbor-log:v2.15.2           "/bin/sh -c /usr/loc…"   56 seconds ago   Up 55 seconds (healthy)   127.0.0.1:1514->10514/tcp                 harbor-log
```

使用浏览器访问，并且完成登录

![](./assets/gitlab-jenkins-hexo-cicd/image-20251217155949219.png)
![image-20260723164312456](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723164312456.png)

CI服务器的docker配置
  - 这里因为我们要在192.168.173.10(CI服务器)上push镜像到192.168.173.20(私仓)，所以需要修改CI服务器上的Docker配置。添加仓库地址

```bash
[root@jenkins ~]# cat /etc/docker/daemon.json 
{
  "registry-mirrors": ["https://service-crproxy.onrender.com", "http://192.168.116.133"],
  "insecure-registries": ["service-crproxy.onrender.com", "192.168.116.133"],
  "exec-opts": ["native.cgroupdriver=systemd"]
}
[root@jenkins ~]# systemctl daemon-reload
[root@jenkins ~]# systemctl restart docker
```

测试一下

```bash
[root@jenkins ~]# docker login 192.168.116.133
Username: admin
Password: 

WARNING! Your credentials are stored unencrypted in '/root/.docker/config.json'.
Configure a credential helper to remove this warning. See
https://docs.docker.com/go/credential-store/

Login Succeeded
```

push一个镜像

```bash
[root@jenkins ~]# docker pull nginx
Using default tag: latest
latest: Pulling from library/nginx
d26f27cc8c41: Pull complete 
062e450697fa: Pull complete 
82454cdbf456: Pull complete 
3c7ab7949321: Pull complete 
cacfcdd01f30: Pull complete 
b6698f04e005: Pull complete 
2bedaf25031a: Pull complete 
ea1d76ccc2c6: Download complete 
6c496f5b5050: Download complete 
Digest: sha256:5a88c9c45479443d7be2eadc894b4ed0a9801bae03d97a5760ae13b5c2005942
Status: Downloaded newer image for nginx:latest
docker.io/library/nginx:latest
[root@jenkins ~]# docker images -a
                                                                                                                                                                                              i Info →   U  In Use
IMAGE                      ID             DISK USAGE   CONTENT SIZE   EXTRA
beginor/gitlab-ce:latest   e5d73a0ebc3d       2.25GB          528MB    U   
nginx:latest               5a88c9c45479        238MB           66MB        
[root@jenkins ~]# docker tag nginx:latest 192.168.116.133/library/nginx:v1
[root@jenkins ~]# docker images -a
                                                                                                                                                                                              i Info →   U  In Use
IMAGE                              ID             DISK USAGE   CONTENT SIZE   EXTRA
192.168.116.133/library/nginx:v1   5a88c9c45479        238MB           66MB        
beginor/gitlab-ce:latest           e5d73a0ebc3d       2.25GB          528MB    U   
nginx:latest                       5a88c9c45479        238MB           66MB        
[root@jenkins ~]# docker push 192.168.116.133/library/nginx:v1
The push refers to repository [192.168.116.133/library/nginx]
d26f27cc8c41: Pushed 
3c7ab7949321: Pushed 
062e450697fa: Pushed 
b6698f04e005: Pushed 
cacfcdd01f30: Pushed 
82454cdbf456: Pushed 
2bedaf25031a: Pushed 
v1: digest: sha256:db4f612f385437d11eb26620a4f1d7efb3ff44e1296a3c21540b30454e6e2bf3 size: 2290

i Info → Not all multiplatform-content is present and only the available single-platform image was pushed
         sha256:5a88c9c45479443d7be2eadc894b4ed0a9801bae03d97a5760ae13b5c2005942 -> sha256:db4f612f385437d11eb26620a4f1d7efb3ff44e1296a3c21540b30454e6e2bf3
```

![image-20260723165143973](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723165143973.png)

### 2.4 Jenkins配置

镜像jenkins拉取

```bash
[root@jenkins ~]# docker pull jenkins/jenkins:latest
```

创建共享卷，修改所属组和用户,和容器里相同
  - 这里要改成 1000，是因为容器里是以 jenkins 用户的身份去读写数据，而在容器里jenkins 的 uid 是 1000

```bash
[root@jenkins ~]# mkdir /jenkins
[root@jenkins ~]# chown 1000:1000 /jenkins
```

创建 jenkins 容器

```bash
[root@jenkins ~]# docker run -itd -p 8080:8080 \
-p 50000:50000 \
--name jenkins  --privileged=true \
--restart=always \
-v /jenkins:/var/jenkins_home jenkins/jenkins:latest
831341851fc92433c05c3a143e39540009d95cc4a43da937a404852f05490096
[root@jenkins ~]# docker ps -a | grep jenkins
831341851fc9   jenkins/jenkins:latest   "/usr/bin/tini -- /u…"   18 seconds ago   Up 17 seconds            0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp, 0.0.0.0:50000->50000/tcp, [::]:50000->50000/tcp                            jenkins
```

浏览器访问

![image-20260723165759474](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723165759474.png)

为了修改配置，关闭 jenkins 容器

```bash
[root@jenkins ~]# docker stop jenkins
jenkins
```

修改Jenkins插件下载服务器为国内地址

```bash
[root@jenkins ~]# cat /jenkins/hudson.model.UpdateCenter.xml
<?xml version='1.1' encoding='UTF-8'?>
<sites>
  <site>
    <id>default</id>
    <url>https://mirrors.huaweicloud.com/jenkins/update-center.json</url>
  </site>
</sites>
```

修改谷歌为百度，因为此处json文件为换行，格式比较混乱，使用jq工具查看比较方便

```bash
[root@jenkins ~]# yum -y install jq
[root@jenkins ~]# sed -i s#https://www.google.com/#https://www.baidu.com/#g /jenkins/updates/default.json
[root@jenkins ~]# cat /jenkins/updates/default.json | jq '.connectionCheckUrl'
"https://www.baidu.com/"
[root@jenkins ~]# cat /jenkins/updates/default.json | jq 'keys'  # 查看所有的可配置项，也就是json的key
[
  "connectionCheckUrl",
  "core",
  "deprecations",
  "generationTimestamp",
  "id",
  "plugins",
  "signature",
  "updateCenterVersion",
  "warnings"
]
```

重启docker，获取登录密匙，下面初始化的时候用到

```bash
[root@jenkins ~]# docker restart jenkins
jenkins
[root@jenkins jenkins]# cat /jenkins/secrets/initialAdminPassword 
01e48dec1540450dadbef3eab8b50447
```

需要修改jenkins绑定的docker的启动参数， 让Jenkins可以通过tcp远程操作容器(模拟需要CI的机器在远端，不然本地的话，sock一样可以使用)

```bash
[root@jenkins ~]# cat /lib/systemd/system/docker.service |grep -Ev "^#|^$"
.......
ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2376 -H fd:// --containerd=/run/containerd/containerd.sock
.......
[root@jenkins ~]# systemctl daemon-reload
[root@jenkins ~]# systemctl restart docker
```

打开Jenkins，完成初始化

![](./assets/gitlab-jenkins-hexo-cicd/image-20251217163455464.png)

安装推荐的插件， 如果此处显示离线了，说明上面的Jenkins插件下载服务器失效了，可以重新找一个

![image-20260723171022141](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723171022141.png)

插件安装完成后，创建管理员用户

![](./assets/gitlab-jenkins-hexo-cicd/image-20251218095110819.png)
!![image-20260723172011140](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723172011140.png)
![image-20260723172033030](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723172033030.png)

依次点击`Manage Jenkins` ->`Manage Plugins` ->`AVAILABLE` ->`Search` 搜索`docker`、`docker-build-step`

![](./assets/gitlab-jenkins-hexo-cicd/image-20251218095301307.png)
![](./assets/gitlab-jenkins-hexo-cicd/image-20251218095443225.png)

安装完成之后，返回主页

![image-20260723173637537](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723173637537.png)

将docker运行的服务器添加上去

![image-20260723174122780](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723174122780.png)
![](./assets/gitlab-jenkins-hexo-cicd/image-20251218100453668.png)
![](./assets/gitlab-jenkins-hexo-cicd/image-20251218100508335.png)

修改镜像库启动参数

```bash
[root@harbor ~]# cat /lib/systemd/system/docker.service |grep -Ev "^#|^$"
.......
ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2376 -H fd:// --containerd=/run/containerd/containerd.sock
.......
[root@harbor ~]# systemctl daemon-reload
[root@harbor ~]# systemctl restart docker
```

填写docker的参数

![](./assets/gitlab-jenkins-hexo-cicd/image-20251218101713286.png)

将构建docker的服务器也关联上去

![](./assets/gitlab-jenkins-hexo-cicd/image-20251218101339787.png)
![](./assets/gitlab-jenkins-hexo-cicd/image-20251218101829991.png)

jenkins 安全设置
后面 gitlab 要和 jenkins 进行联动，所以必须要需要对 jenkins 的安全做一些设置，依次点击 系统管理-全局安全配置-授权策略，勾选”匿名用户具有可读权限”

![](./assets/gitlab-jenkins-hexo-cicd/image-20251218101927133.png)
![](./assets/gitlab-jenkins-hexo-cicd/image-20251218101943764.png)

添加 JVM 运行参数 -Dhudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION=true 运行跨站请求访问

```bash
[root@jenkins ~]# docker exec -u root -it jenkins bash
root@cf6baf3b3ba5:/# sed -i 's/exec java/exec java -Dhudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION=true/' /usr/local/bin/jenkins.sh
root@cf6baf3b3ba5:/# cat /usr/local/bin/jenkins.sh |grep 'exec java'
root@cf6baf3b3ba5:/# exit
```

下载kubectl客户端工具
  - 这里的话我们要通过jenkins上的kubectl客户端连接k8s,所以我们需要安装一个k8s的客户端kubectl，下载k8s客户端

```bash
# 此处使用安装kubernetes的kubectl方式安装即可，此处只用到客户端功能
[root@jenkins ~]# systemctl enable kubelet && systemctl start kubelet
[root@jenkins ~]# kubectl version --client=true
Client Version: v1.29.2
Kustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3
```

然后拷贝kubeconfig 证书,k8s集群(一主两从)中查看证书位置/etc/kubernetes/admin.conf

```bash
[root@jenkins ~]# scp root@master:/etc/kubernetes/admin.conf .
The authenticity of host 'master (192.168.116.129)' can't be established.
ED25519 key fingerprint is SHA256:0Kzw0G1D6vq1qELP394G3Vrp/DTl9AIKcUzAIPpOfXQ.
This host key is known by the following other names/addresses:
    ~/.ssh/known_hosts:1: 192.168.116.130
    ~/.ssh/known_hosts:4: node01
    ~/.ssh/known_hosts:5: node02
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'master' (ED25519) to the list of known hosts.
root@master's password: 
admin.conf                                                                                                                                                                      100% 5659     2.5MB/s   00:00    
```

拷贝证书和k8s集群客户端工具到jenkins容器内

```bash
[root@jenkins ~]# docker cp admin.conf jenkins:/
Successfully copied 7.68kB to jenkins:/
[root@jenkins ~]# docker cp /usr/bin/kubectl jenkins:/usr/bin/
Successfully copied 49.7MB to jenkins:/usr/bin/
```

kubectl命令测试，赋予jenkins用户对/admin.conf的权限

```bash
[root@jenkins ~]# docker exec -u root -it jenkins bash
root@cbc0b2dae78b:/# chown jenkins:jenkins /admin.conf
root@cbc0b2dae78b:/# exit
exit

[root@jenkins ~]# docker exec -it jenkins bash
jenkins@cbc0b2dae78b:/$ kubectl --kubeconfig=/admin.conf get nodes
NAME     STATUS   ROLES           AGE    VERSION
master   Ready    control-plane   5d4h   v1.29.2
node01   Ready    <none>          5d4h   v1.29.2
node02   Ready    <none>          5d4h   v1.29.2
```

## 3. hexo系统CICD实战

### 3.1 配置hexo高可用

要部署Nginx来运行hexo博客系统，hexo编译完后为一堆静态文件，所以我们需要创建一个svc和一个deploy，使用SVC提供服务，使用deploy提供服务能力,使用Nginx+hexo的静态文件构成的镜像

```bash
[root@jenkins ~]# mkdir /jenkins/kubernetes
[root@jenkins ~]# cd /jenkins/kubernetes
[root@jenkins kubernetes]# vim nginx.yaml
```

nginx.yaml文件

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: nginx
  name: nginxdep
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: web
        resources:
          requests:
            cpu: 100m
      restartPolicy: Always
```

将nginx部署

```bash
[root@jenkins ~]# docker exec -it -u root jenkins bash
root@cbc0b2dae78b:/# cd /var/jenkins_home/kubernetes/
root@cbc0b2dae78b:/var/jenkins_home/kubernetes# kubectl apply -f nginx.yaml --kubeconfig=/admin.conf 
deployment.apps/nginxdep created
root@cbc0b2dae78b:/var/jenkins_home/kubernetes# kubectl --kubeconfig=/admin.conf get pods
NAME                        READY   STATUS    RESTARTS   AGE
nginxdep-7dc8c7dc56-7nvjc   1/1     Running   0          102s
nginxdep-7dc8c7dc56-mpnd4   1/1     Running   0          102s
root@cbc0b2dae78b:/var/jenkins_home/kubernetes# kubectl --kubeconfig=/admin.conf get deploy
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
nginxdep   2/2     2            2           112s
```

service创建

```bash
root@cbc0b2dae78b:/var/jenkins_home/kubernetes# kubectl --kubeconfig=/admin.conf expose deploy nginxdep --port=8888 --target-port=80 --type=NodePort
service/nginxdep exposed
root@cbc0b2dae78b:/var/jenkins_home/kubernetes# kubectl --kubeconfig=/admin.conf get svc
NAME                   TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)          AGE
kubernetes             ClusterIP      10.0.0.1        <none>          443/TCP          5d4h
nginxdep               NodePort       10.13.218.147   <none>          8888:30356/TCP   22s
service-clusterip      ClusterIP      10.11.13.137    <none>          80/TCP           2d2h
service-externalname   ExternalName   <none>          www.baidu.com   <none>           2d1h
service-headliness     ClusterIP      None            <none>          80/TCP           2d2h
service-nodeport       NodePort       10.3.55.154     <none>          80:30002/TCP     2d1h
```

访问测试

![image-20260723203351121](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723203351121.png)

### 3.2 集群配置私仓地址

通过kubectl set命令更新deploy的镜像时，获取的镜像是通过私仓获取的，所以需要在启动参数添加私仓地址
需要**修改三个节点**，因为三个node才是需要去获取镜像的

```bash
[root@master,node01,node02 ~]# vim /etc/docker/daemon.json 
{
  "registry-mirrors": ["https://service-crproxy.onrender.com", "http://192.168.116.133"],
  "insecure-registries": ["service-crproxy.onrender.com", "192.168.116.133"],
  "exec-opts": ["native.cgroupdriver=systemd"]
}
[root@master,node01,node02 ~]# systemctl daemon-reload
[root@master,node01,node02 ~]# systemctl restart docker
```

### 3.3 jenkins配置CICD

jenkins上配置整个CICD流程，从而实现自动化

![](./assets/gitlab-jenkins-hexo-cicd/image-20251222114653237.png)
![image-20260723205746735](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723205746735.png)

这里的Token为了安全，可以设置复杂一些，同时需要记住访问方式：JENKINS_URL/job/hexo-cicd/build?token=TOKEN_NAME
并且记录下来，不要忘记，此处我填入的是`38381f8eee9f40e9a4fece7f64924d5f`

![](./assets/gitlab-jenkins-hexo-cicd/image-20251222134309273.png)

添加构建步骤——执行shell
  - 这一步是将新的网站源码获取到

![](./assets/gitlab-jenkins-hexo-cicd/image-20251222134358493.png)

```bash
cd ~
rm -rf blog
git clone http://192.168.173.10/root/blog.git
```

![](./assets/gitlab-jenkins-hexo-cicd/image-20251222134620426.png)

再次增加构建步骤
  - 这一步是将下载的源码在容器从进行处理，可以得到能够运行的容器环境
  - 本案例就是将前端代码放入nginx的网站根目录，然后构造一个新的镜像

![](./assets/gitlab-jenkins-hexo-cicd/image-20251222134740309.png)
![](./assets/gitlab-jenkins-hexo-cicd/image-20251222135421593.png)

再次添加构建步骤
  - 这一步是修改kubernetes集群中运行的镜像，使其更新为最新的版本

```bash
export KUBECONFIG=/kcl;
/kubectl --kubeconfig=/admin.conf set image deployment/nginxdep *="192.168.173.20/library/blog:${BUILD_NUMBER}"
```

![](./assets/gitlab-jenkins-hexo-cicd/image-20251224094415617.png)

这里可能有问题，实际是在容器中使用k8s命令可以这么写
```bash
kubectl --kubeconfig=/admin.conf set image deployment/nginxdep *=192.168.116.133/library/blog:${BUILD_NUMBER}
```

![image-20260723234542506](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723234542506.png)

### 3.4 Hexo仓库配置

新建blog仓库

![](./assets/gitlab-jenkins-hexo-cicd/image-20251222140531915.png)

配置 gitlab 和 jenkins 的联动

![](./assets/gitlab-jenkins-hexo-cicd/image-20251222140627904.png)
![](./assets/gitlab-jenkins-hexo-cicd/image-20251222140724353.png)

配置触发的钩子

![](./assets/gitlab-jenkins-hexo-cicd/image-20251222140814804.png)
![](./assets/gitlab-jenkins-hexo-cicd/image-20251222141029966.png)

### 3.5 编写Dockerfile

编写Dockerfile，用于将新的前端代码加入nginx的镜像中

```bash
# 将Dockerfile文件加入到hexo的源码目录中
FROM 192.168.173.20/library/nginx:latest
MAINTAINER Aaronxu
ADD ./public  /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g","daemon off;"]
```

### 3.6 测试

本地部署hexo博客，然后将代码推送到仓库中
本地找一个空文件夹，然后cmd进入文件夹中

```bash
C:\Users\bbben\Desktop\blog>hexo init		# 安装hexo请参考官网教程
C:\Users\bbben\Desktop\blog>hexo g
C:\Users\bbben\Desktop\blog>git init
C:\Users\bbben\Desktop\blog>git remote add origin ssh://git@192.168.173.10:222/root/blog.git
C:\Users\bbben\Desktop\blog>git add .
C:\Users\bbben\Desktop\blog>git commit -m "Initial commit"
C:\Users\bbben\Desktop\blog>git push -u origin master
Enumerating objects: 6916, done.
Counting objects: 100% (6916/6916), done.
Delta compression using up to 32 threads
Compressing objects: 100% (6688/6688), done.
Writing objects: 100% (6916/6916), 8.12 MiB | 1.38 MiB/s, done.
Total 6916 (delta 1875), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (1875/1875), done.
To ssh://192.168.116.132:222/root/blog.git
 * [new branch]      master -> master
branch 'master' set up to track 'origin/master'.
```

确保仓库中代码已成功上传

![](./assets/gitlab-jenkins-hexo-cicd/image-20251224094015978.png)

确认成功执行

![](./assets/gitlab-jenkins-hexo-cicd/image-20251224095254175.png)

查看到pods自动更新的状态

```bash
[root@node01 ~]# kubectl get pods
NAME                        READY   STATUS        RESTARTS      AGE
nginxdep-7dc8c7dc56-kxvxl   1/1     Terminating   1 (46h ago)   46h
nginxdep-bbffc4f57-8cnzd    1/1     Running       0             30s
nginxdep-bbffc4f57-kjh7b    1/1     Running       0             58s
```

访问页面，确认成功

![](./assets/gitlab-jenkins-hexo-cicd/image-20251224095419090.png)

![image-20260723234418908](Gitlab+Jenkins+hexo实现CICD持续集成/image-20260723234418908.png)


## 4. 关键点总结

### 4.1 整体流程

整个 CI/CD 流水线围绕一条主线展开：**本地代码变更 → 自动触发 → 自动构建 → 自动部署**。除了客户机 `git push` 是手动操作外，其余全部自动化。

**流程走向**：

```
[客户机]                              [CI 集群]                                        [镜像仓库]              [CD 集群]
  C:\blog  --git push-->   GitLab(192.168.116.132)  --webhook-->   Jenkins(192.168.116.132)              k8s master/node (192.168.116.129/130/131)
                          :80                          (token)         |
                                                                          v
                                                                    [Execute shell 1] git clone http://192.168.116.132/root/blog.git
                                                                          v
                                                                    [Execute shell 2] docker build (FROM 192.168.116.133/library/nginx:v1 + ADD ./public)
                                                                          v
                                                                    [Execute shell 3] docker push 192.168.116.133/library/blog:${BUILD_NUMBER}
                                                                          v
                                                                    kubectl set image deployment/nginxdep *=192.168.116.133/library/blog:${BUILD_NUMBER} --> Harbor(192.168.116.133)
                                                                                                                                                          ^
                                                                                                                                                          |
                                                                                                                                                  k8s 各 node 的 docker
                                                                                                                                                  从 Harbor 拉新镜像
                                                                                                                                                          |
                                                                                                                                                          v
                                                                                                                                                  Pod 滚动更新完成
```

**6 个关键动作**：

1. **本地 push**（手动）：开发者 `git push` 到 GitLab 的 `blog` 仓库
2. **webhook 触发**（自动）：GitLab 调用 Jenkins 的 `JENKINS_URL/job/hexo-cicd/build?token=TOKEN_NAME`
3. **拉取源码**（自动）：Jenkins 第一条 shell 步骤执行 `git clone`
4. **构建并推送镜像**（自动）：Jenkins 第二条 shell 步骤执行 `docker build` + `docker push`，镜像 tag = `${BUILD_NUMBER}`
5. **更新 K8s Deployment**（自动）：Jenkins 第三条 shell 步骤执行 `kubectl set image`，触发滚动更新
6. **验证访问**（手动）：浏览器访问 NodePort 看到新页面

### 4.2 关键点全景

按重要性分三档：

**⭐⭐⭐ 枢纽级（Jenkins 节点配置是核心）**

1. **Jenkins 节点同时是 4 种客户端** —— docker client、kubectl client、git client、HTTP client（调 webhook），任何一种不通整个流水线就断
2. **`/etc/docker/daemon.json` 必须包含 Harbor 的 insecure-registry** —— 涉及 Jenkins 宿主机、k8s 所有 node、Harbor 自身，多台机器要保持一致
3. **kubectl + kubeconfig 三件套必须完整** —— kubectl 二进制、`/admin.conf` 凭证、`chown jenkins:jenkins` 权限，缺一不可

**⭐⭐ 关键路径**

4. **Dockerfile 的 `FROM` tag 必须与 Harbor 中实际存在的镜像一致** —— 本次踩坑：Harbor 里是 `nginx:v1` 而非 `nginx:latest`
5. **hexo 生成的 `public/` 目录必须提交到 git** —— `ADD ./public` 找不到目录会直接构建失败
6. **docker.service 需开启 TCP 监听** —— Jenkins 容器通过 `tcp://192.168.116.132:2376` 控制宿主机的 docker daemon

**⭐ 容易忽略**

7. **Jenkins 全局安全配置** —— 勾选"匿名用户具有可读权限" + 关闭 CSRF，GitLab webhook 才能调用通
8. **k8s 三台 node 的 docker daemon.json 要和 Jenkins 宿主机保持一致** —— Pod 调度到任何一台 node 上都要能拉镜像

### 4.3 Jenkins 节点配置（核心枢纽）

Jenkins 节点是整个 CI/CD 流水线的"枢纽"，所有自动化动作都在这里发起。它必须在容器内同时具备以下 4 类能力：

#### 4.3.1 节点职责矩阵

| 能力 | 需要的组件 | 配置位置 |
| --- | --- | --- |
| 拉 git 源码 | git / Jenkins 内置 + HTTP 凭证 | job 的第一个 shell 步骤 |
| 构建/推送镜像 | docker CLI + Harbor 账号 | Jenkins → Manage Jenkins → Clouds → Docker Host |
| 控制 K8s 集群 | kubectl 二进制 + kubeconfig | 容器内 `/usr/bin/kubectl`、`/admin.conf` |
| 接收 GitLab 触发 | Webhook + Token | job 配置 + GitLab Webhook 设置 |

#### 4.3.2 与 K8s 集群通信

Jenkins 本身不部署 K8s，它是通过 **kubectl 客户端 + kubeconfig 凭证** 以"外部控制"的方式操作 K8s 集群。需要 3 步：

**Step 1：在宿主机准备 kubectl**

```bash
# Jenkins 宿主机（192.168.116.132）
systemctl enable kubelet && systemctl start kubelet
kubectl version --client=true
```

**Step 2：从 K8s master 拷贝凭证**

```bash
scp root@master:/etc/kubernetes/admin.conf .
```

**Step 3：注入到 Jenkins 容器并修正权限**

```bash
# 拷贝凭证和工具到容器
docker cp admin.conf jenkins:/
docker cp /usr/bin/kubectl jenkins:/usr/bin/

# 必须做权限修正，否则 jenkins 用户读不到
docker exec -u root -it jenkins bash
chown jenkins:jenkins /admin.conf
exit

# 验证
docker exec -it jenkins bash
kubectl --kubeconfig=/admin.conf get nodes
```

#### 4.3.3 与 Harbor 私有仓库通信

私有仓库通信分两个层面：

**Docker daemon 层（拉/推镜像用，必做）**

所有要访问 Harbor 的 docker 主机都需要修改 `/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": ["..."],
  "insecure-registries": ["192.168.116.133"]
}
```

⚠️ `insecure-registries` 不是镜像加速，是"信任这个地址用 HTTP"。两者不要混淆。

涉及机器清单：

| 机器 | 是否需要配 | 原因 |
| --- | --- | --- |
| Jenkins 宿主机 `192.168.116.132` | ✅ 必须 | 构建/推送镜像都要用 |
| k8s master `192.168.116.129` | ✅ 必须 | node 上的 kubelet 要调 docker 拉镜像 |
| k8s node01 `192.168.116.130` | ✅ 必须 | Pod 实际拉镜像在这里发生 |
| k8s node02 `192.168.116.131` | ✅ 必须 | Pod 实际拉镜像在这里发生 |
| Harbor `192.168.116.133` | ✅ 必须 | 自身要能 push/pull |

**HTTP API 层（curl 调用 Harbor 管理 API，可选）**

本次未涉及。如果要做镜像清理、扫描、策略配置等高级功能，需要 Harbor REST API + 凭据（admin/Harbor12345）。

#### 4.3.4 Docker 远程访问

Jenkins 跑在容器里，但容器本身没有 docker daemon，所以要让 Jenkins 能 build/push 镜像，必须让宿主机的 docker daemon **监听 TCP**：

```bash
# 修改 docker.service
vim /usr/lib/systemd/system/docker.service

# ExecStart 一行改成
ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2376 -H fd:// --containerd=/run/containerd/containerd.sock

# 重启
systemctl daemon-reload
systemctl restart docker
```

然后在 Jenkins Web 里：

> Manage Jenkins → Clouds → New Cloud → Docker → Docker Host URI = `tcp://192.168.116.132:2376`

#### 4.3.5 容器内凭证注入的"三件套"

这是本次实践中最容易遗漏的环节。**Jenkins 容器在重启时，`/admin.conf` 和 `/usr/bin/kubectl` 都会丢失**（因为容器是 ephemeral 的），需要每次重启后重新注入，或写进 entrypoint 脚本。

| 注入物 | 来源 | 命令 |
| --- | --- | --- |
| kubeconfig 凭证 | K8s master 的 `/etc/kubernetes/admin.conf` | `docker cp admin.conf jenkins:/` |
| kubectl 二进制 | 宿主机 `/usr/bin/kubectl` | `docker cp /usr/bin/kubectl jenkins:/usr/bin/` |
| 文件权限 | 让 jenkins 用户可读 | `chown jenkins:jenkins /admin.conf` |

### 4.4 易踩坑清单（本次实践踩过的 4 个）

| # | 坑 | 现象 | 根因 | 修复 |
| --- | --- | --- | --- | --- |
| 1 | Docker 走 HTTPS/443 失败 | `dial tcp ... :443: connection refused` | `daemon.json` 的 `insecure-registries` 未生效 | 加 Harbor IP 后必须 `systemctl daemon-reload && systemctl restart docker` |
| 2 | Harbor 中找不到镜像 | `... not found` | `Dockerfile` 的 `FROM` tag 与 Harbor 实际不一致（如写成 `latest`，实际是 `v1`） | 修改 `FROM 192.168.116.133/library/nginx:v1` 后重新 build |
| 3 | kubectl 路径错误 | `/kubectl: not found` | 教程笔误：`/kubectl` 应为 `kubectl`（实际路径在 PATH 里） | 改成 `kubectl --kubeconfig=/admin.conf set image ...` |
| 4 | k8s Pod 拉不到新镜像 | Pod 卡在 `ImagePullBackOff` | k8s node 节点的 `daemon.json` 没加 Harbor IP | 三个 node 都要 `insecure-registries: ["192.168.116.133"]` 并重启 docker |
