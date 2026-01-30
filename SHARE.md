# 🎁 分享指南 - 多语言翻译Agent

## 快速分享方式

### 方法1：Docker Compose 一键部署（最简单）

#### 给对方的操作步骤：

1. **发送文件包**
   ```
   发送以下文件给对方：
   - Dockerfile
   - docker-compose.yml
   - init-db.sql
   - requirements.txt
   - .env.example
   - quick-start.sh
   - DEPLOY.md
   - src/ (整个目录)
   - config/ (整个目录)
   - scripts/ (整个目录)
   ```

2. **对方执行**
   ```bash
   # 1. 解压文件
   unzip multi-lang-translation.zip
   cd multi-lang-translation
   
   # 2. 运行快速启动脚本
   chmod +x quick-start.sh
   ./quick-start.sh
   ```

3. **访问使用**
   ```
   http://localhost:5000
   ```

---

### 方法2：Git仓库分享（适合开发者）

#### 你的操作：

1. **推送到Git仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/你的用户名/multi-lang-translation.git
   git push -u origin main
   ```

2. **给对方仓库地址**

#### 对方的操作：

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/multi-lang-translation.git
cd multi-lang-translation

# 2. 配置环境
cp .env.example .env
# 编辑 .env 文件，填写数据库连接信息

# 3. 启动服务
docker-compose up -d

# 4. 访问
http://localhost:5000
```

---

### 方法3：Docker镜像分享

#### 你的操作：

1. **构建Docker镜像**
   ```bash
   docker build -t multi-lang-translation:latest .
   ```

2. **导出镜像**
   ```bash
   docker save multi-lang-translation:latest | gzip > multi-lang-translation.tar.gz
   ```

3. **发送文件**
   ```
   发送 multi-lang-translation.tar.gz 给对方
   ```

#### 对方的操作：

```bash
# 1. 加载镜像
docker load < multi-lang-translation.tar.gz

# 2. 使用镜像
docker run -d \
  --name translation-app \
  -p 5000:5000 \
  -e PGDATABASE_URL=postgresql://用户:密码@host:port/db \
  multi-lang-translation:latest
```

---

### 方法4：云服务部署（推荐给企业用户）

#### 使用Docker Hub：

1. **推送镜像到Docker Hub**
   ```bash
   # 登录Docker Hub
   docker login
   
   # 打标签
   docker tag multi-lang-translation:latest 你的用户名/multi-lang-translation:latest
   
   # 推送
   docker push 你的用户名/multi-lang-translation:latest
   ```

2. **给对方镜像地址**
   ```
   docker pull 你的用户名/multi-lang-translation:latest
   ```

#### 使用阿里云/腾讯云/华为云容器镜像服务：

操作类似，推送到对应的镜像仓库即可。

---

## 📋 分享清单检查表

### ✅ 必须包含的文件

- [x] `Dockerfile` - Docker镜像构建文件
- [x] `docker-compose.yml` - Docker编排文件
- [x] `init-db.sql` - 数据库初始化脚本
- [x] `requirements.txt` - Python依赖
- [x] `.env.example` - 环境变量模板
- [x] `DEPLOY.md` - 部署文档
- [x] `quick-start.sh` - 快速启动脚本
- [x] `src/` - 源代码目录
- [x] `config/` - 配置文件目录
- [x] `scripts/` - 脚本目录

### ✅ 可选文件

- [ ] `assets/` - 资源目录（测试数据）
- [ ] `docs/` - 文档目录
- [ ] `README.md` - 项目说明
- [ ] `AGENTS.md` - 项目索引

---

## 🎯 推荐方案对比

| 方案 | 适用场景 | 优点 | 缺点 |
|-----|---------|------|------|
| **Docker Compose** | 快速分享给非技术人员 | 最简单，一键启动 | 需要对方安装Docker |
| **Git仓库** | 开发者协作 | 方便版本控制和更新 | 需要Git知识 |
| **Docker镜像** | 离线环境 | 无需网络，直接运行 | 文件较大 |
| **云服务镜像** | 企业内部使用 | 方便分发和管理 | 需要云服务账号 |

---

## 📝 给对方的说明模板

```
【多语言翻译Agent - 使用说明】

1. 解压文件后，进入目录
   cd multi-lang-translation

2. 运行快速启动脚本
   ./quick-start.sh

3. 修改 .env 文件中的数据库连接信息（重要！）

4. 启动服务
   docker-compose up -d

5. 访问前端页面
   http://localhost:5000

6. 上传CSV文件，输入目标语言，开始翻译

详细说明请查看 DEPLOY.md 文件。
```

---

## 🆘 常见问题

### Q: 对方没有Docker怎么办？
A: 参考方式二，直接在服务器上部署，但需要Python环境

### Q: 如何自定义数据库？
A: 修改 `.env` 文件中的 `PGDATABASE_URL`，或直接使用外部数据库

### Q: 如何添加更多术语？
A: 连接到数据库，执行 INSERT 语句添加术语到 `翻译知识库` 表

### Q: 如何支持更多语言？
A: 修改数据库表结构，添加新的语言列

---

## 📞 技术支持

如果对方遇到问题，提供以下信息：
1. 详细日志：`docker-compose logs -f`
2. 数据库连接信息（脱敏）
3. CSV文件格式和大小
4. 错误截图或错误信息

---

**选择适合你的分享方式，让更多人使用你的翻译工作流！** 🎉
