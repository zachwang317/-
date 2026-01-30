# 多语言翻译Agent - 部署指南

## 📦 部署方式

### 方式一：Docker Compose 部署（推荐）

#### 前提条件
- 已安装 Docker 和 Docker Compose
- 服务器端口 5000 和 5432 可用

#### 部署步骤

1. **克隆或下载项目代码**

2. **修改配置**（可选）
   
   编辑 `docker-compose.yml`，修改数据库密码等配置：
   ```yaml
   environment:
     - POSTGRES_PASSWORD=你的密码
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **查看日志**
   ```bash
   docker-compose logs -f translation-app
   ```

5. **访问前端**
   ```
   http://你的服务器IP:5000
   ```

6. **停止服务**
   ```bash
   docker-compose down
   ```

---

### 方式二：直接部署到服务器

#### 前提条件
- Python 3.8+
- PostgreSQL 数据库
- 对象存储（可选）

#### 部署步骤

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   
   创建 `.env` 文件：
   ```env
   PGDATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名
   ```

3. **初始化数据库**
   ```bash
   # 连接到PostgreSQL
   psql -U 用户名 -d 数据库名
   
   # 执行初始化脚本
   \i init-db.sql
   ```

4. **启动服务**
   ```bash
   bash scripts/http_run.sh -m http -p 5000
   ```

5. **访问前端**
   ```
   http://服务器IP:5000
   ```

---

## 🗄️ 数据库管理

### 添加术语

连接到数据库并执行：

```sql
-- 添加单个术语
INSERT INTO "翻译知识库" ("中文", "英语", "日语", "韩语")
VALUES ('你的术语', 'English', '日本語', '한국어');

-- 批量添加术语
INSERT INTO "翻译知识库" ("中文", "英语", "日语") VALUES
('术语1', 'Term 1', '用語1'),
('术语2', 'Term 2', '用語2'),
('术语3', 'Term 3', '用語3');
```

### 查看所有术语

```sql
SELECT * FROM "翻译知识库";
```

### 删除术语

```sql
DELETE FROM "翻译知识库" WHERE "中文" = '要删除的术语';
```

### 添加新语言支持

```sql
-- 添加法语列
ALTER TABLE "翻译知识库" ADD COLUMN "法语" VARCHAR;

-- 更新现有术语的法语翻译
UPDATE "翻译知识库" SET "法语" = 'Français' WHERE "中文" = '中文术语';
```

---

## 🔧 配置说明

### LLM配置文件

编辑 `config/translate_llm_cfg.json`：

```json
{
    "config": {
        "model": "doubao-seed-1-8-251228",
        "temperature": 0.3,
        "thinking": "enabled"
    },
    "sp": "系统提示词...",
    "up": "用户提示词..."
}
```

### 环境变量说明

| 变量名 | 说明 | 必填 |
|-------|------|------|
| `PGDATABASE_URL` | PostgreSQL数据库连接字符串 | ✅ |
| `S3_ACCESS_KEY_ID` | 对象存储Access Key | ❌ |
| `S3_SECRET_ACCESS_KEY` | 对象存储Secret Key | ❌ |
| `S3_BUCKET_NAME` | 对象存储桶名 | ❌ |
| `S3_ENDPOINT` | 对象存储终端地址 | ❌ |

---

## 📊 使用说明

### 上传CSV文件

支持以下格式：
- 文件格式：`.csv`
- 编码：UTF-8
- 列数：任意（系统自动识别中文列）

### 输入目标语言

支持多种格式：
- 中文：`英文`、`日文`、`韩文`
- 英文：`English`、`Japanese`、`Korean`
- ISO代码：`en`、`ja`、`ko`

多语言翻译示例：
```
英文,日文,韩文,法文
```

### 下载结果

翻译完成后，系统会生成包含翻译列的新CSV文件：
- 原始列 + 翻译列
- 命名格式：`原始列名_目标语言_翻译`

---

## 🐛 故障排查

### 无法连接数据库

**检查数据库连接：**
```bash
docker exec -it translation-db psql -U postgres -d translation_db -c "SELECT 1;"
```

**检查环境变量：**
```bash
docker exec translation-app env | grep PGDATABASE_URL
```

### 翻译失败

**检查日志：**
```bash
docker-compose logs -f translation-app
```

**检查网络连接：**
```bash
# 测试能否访问豆包大模型
ping api.coze.com
```

### 前端无法访问

**检查端口：**
```bash
netstat -tlnp | grep 5000
```

**检查防火墙：**
```bash
# 开放端口
firewall-cmd --add-port=5000/tcp --permanent
firewall-cmd --reload
```

---

## 📈 性能优化

### 大文件处理

- 使用并行翻译：系统已支持多语言并行翻译
- 调整批次大小：修改配置文件中的 `max_completion_tokens`
- 使用SSD：数据库和日志放在SSD上

### 数据库优化

```sql
-- 创建索引（如果查询频繁）
CREATE INDEX IF NOT EXISTS idx_chinese ON "翻译知识库"("中文");
```

---

## 🔐 安全建议

1. **修改默认密码**
   - 修改 `docker-compose.yml` 中的数据库密码
   - 不要在代码中硬编码敏感信息

2. **使用HTTPS**
   - 在反向代理（如Nginx）中配置SSL证书

3. **限制访问**
   - 配置防火墙规则
   - 使用IP白名单

4. **定期备份**
   ```bash
   # 备份数据库
   docker exec translation-db pg_dump -U postgres translation_db > backup.sql
   ```

---

## 📞 技术支持

如遇到问题，请查看：
- 日志文件：`/app/work/logs/bypass/app.log`
- 项目文档：`docs/` 目录
- GitHub Issues（如果有）

---

## 📝 更新日志

- v2.6: 移除向量检索，使用精确匹配
- v2.5: 添加数据库术语增强功能
- v2.0: 支持多语言并行翻译
- v1.0: 初始版本
