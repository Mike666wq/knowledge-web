---
id: "kb-linux-git-workflow"
title: "Git 本地修改与远程同步"
summary: "Git 分支同步和合并冲突实战。"
category: "操作系统"
status: "published"
order: 18
parent: "kb-linux-operations"
tags: ["git", "merge", "conflict"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Git 本地修改与远程同步

## 21. Git 本地修改与远程同步（合并冲突实战）

### 本地修改后远程更新，本地修改会不会丢？

**核心答案：本地修改不会丢**，但取决于操作方式：

**1. 同一目录用 `git pull`（正确做法）**
- `git pull origin main` 会保留本地修改，尝试自动合并
- 无冲突：本地修改 + 远程更新都在
- 有冲突：Git 提示，手动解决

**2. 在新目录重新 clone**
- 旧目录不动，新目录是干净版本
- 两个目录互不影响

**3. ⚠️ 千万别这么干**
- 在已有仓库目录再 `git clone` → 报错 "destination path already exists"
- 用 `rm -rf` 清空再 clone → **修改全丢**
- 绝对不要用删除旧目录的方式"重新 clone"

**关键概念：**
- `git clone` 是**一次性**的，把远程完整复制到本地
- 本地仓库建立后，后续同步用 `git pull`（= `git fetch` + `git merge`）
- 本地修改只要**不删本地目录**，永远都在

**最佳实践：**
```bash
git add .              # 暂存
git commit -m "..."    # 先提交本地修改（无需 push）
git pull               # 再拉远程更新
```
先 commit 再 pull，保证不丢任何东西。

---

### pull 时遇到 CONFLICT（合并冲突实战）

**报错解读：**
```
Auto-merging KVM虚拟化/KVM虚拟化技术.md        ← Git 试图自动合并
CONFLICT (content): Merge conflict in ...        ← 但失败了：本地和远程改了同一段
Automatic merge failed; fix conflicts and then commit the result.
                                                ← 需要手动解决冲突再 commit
```
**原因：** 本地和远程都改了同一个文件的同一段内容，Git 无法判断保留谁，必须手动选。

**冲突文件标记：**
打开冲突文件会看到：
```
<<<<<<< HEAD
你本地的修改内容
=======
远程最新的内容
>>>>>>> origin/main
```
- `<<<<<<< HEAD` ~ `=======` = **你的版本**
- `=======` ~ `>>>>>>> origin/main` = **远程版本**

**三种解决方式：**

**1. VSCode 编辑器（推荐）**
打开冲突文件会高亮冲突区域，顶部按钮：
- `Accept Current Change` → 保留你的
- `Accept Incoming Change` → 保留远程的
- `Accept Both Changes` → 全部保留
- `Compare Changes` → 对比查看

**2. 手动编辑**
删掉 `<<<<<<<`、`=======`、`>>>>>>>` 三个标记，保留需要的内容，保存。

**3. 放弃合并回滚**
```bash
git merge --abort    # 取消合并，回到 pull 之前状态
```

**解决完提交：**
```bash
git add .                                    # 标记冲突已解决
git commit -m "解决 xxx.md 合并冲突"          # 完成合并
```

**常用查看命令：**
```bash
git status        # 看哪些文件冲突
git diff          # 看具体冲突内容
git log --oneline -5  # 看提交历史
```

---

### 21.1 git config 查看当前配置（速查表）

#### 查配置命令
```bash
# 1. 列出所有生效配置（按优先级从高到低输出）
git config --list

# 2. 推荐：每个值显示来源文件（一眼分清全局 / 仓库 / 系统）
git config --list --show-origin

# 3. 显示作用域（git 2.26+）
git config --list --show-scope

# 4. 按层级过滤
git config --list --local       # 当前仓库 .git/config
git config --list --global      # 用户级 ~/.gitconfig 或 ~/.config/git/config
git config --list --system      # 系统级 /etc/gitconfig

# 5. 单项查询
git config user.name
git config user.email

# 6. 脚本里取值（未设置时返回非零退出码，便于判断）
git config --get user.name
```

#### 核心知识点：配置层级（高 → 低覆盖）
1. **命令行参数**（本次有效，`git -c user.name=x commit`）
2. `--local` → 仓库 `.git/config`
3. `--global` → `~/.gitconfig`（新系统可能是 `~/.config/git/config`）
4. `--system` → `/etc/gitconfig`
5. **默认值**（最低）

**高层级覆盖低层级** —— 不会清空低层级，是叠加后再覆盖。同名 key 最终用最细的那条。

#### 调试场景
- "明明全局设了 user.name，仓库里还是另一个人" → `git config --list --show-origin`，看仓库层是否覆盖
- "想确认这个机器的 git 装在哪、版本" → `git --version` + `which git`
- "想批量改所有仓库的某项配置" → 用 `--global`，不要写到 `--system`（影响其他用户）

#### 写入 / 取消（顺手补）
```bash
git config --global user.name "你的名字"
git config --global user.email "your@email"
git config --local user.name "项目专用名"   # 仅仓库内
git config --unset user.name                # 取消当前仓库的设置
git config --global --unset user.name       # 取消全局的设置
git config --global --edit                  # 直接打开 ~/.gitconfig 编辑
```

---
