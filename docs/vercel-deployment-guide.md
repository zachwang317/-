# Vercel部署问题解决方案

## ❌ 问题原因

你的 `requirements.txt` 中包含很多**不适合Vercel环境**的包：

| 包名 | 问题 | 解决方案 |
|------|------|---------|
| `opencv-python` | 需要系统库，~90MB，无法在Vercel安装 | 移除（项目中不需要） |
| `PyGObject` | 需要GTK库，Vercel不支持 | 移除 |
| `dbus-python` | 需要D-Bus系统库，Vercel不支持 | 移除 |
| `psycopg2-binary` | 本地PostgreSQL驱动 | 移除（使用云数据库） |
| `coze-coding-dev-sdk` | 内部SDK，不适合公开部署 | 移除 |
| `coze-coding-utils` | 内部SDK，不适合公开部署 | 移除 |

## ✅ 解决方案

我已创建 `requirements.vercel.txt`，只包含Vercel需要的最小依赖。

---

## 🚀 两种部署方式

### 方式一：使用requirements.vercel.txt（推荐）

#### 1. 修改Vercel配置

在Vercel项目设置中：

1. 进入 **Settings** → **General** → **Build & Development Settings**
2. 修改 **Build Command** 为：
   ```
   pip install -r requirements.vercel.txt
   ```
3. 修改 **Install Command** 为：
   ```
   pip install -r requirements.vercel.txt
   ```

#### 2. 创建vercel.json（已完成）

我已创建 `vercel.json` 配置文件。

#### 3. 推送到GitHub

```bash
git add vercel.json requirements.vercel.txt
git commit -m "feat: 添加Vercel部署配置"
git push origin main
```

#### 4. 重新部署

在Vercel控制台点击 **Redeploy**

---

### 方式二：创建简化版API（更适合Vercel）

#### 1. 创建API目录结构

```bash
mkdir -p api
```

#### 2. 创建Vercel Serverless Function

创建 `api/translate.py`：

```python
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 解析JSON
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # 这里调用你的翻译服务
            # result = translate_csv(data)
            
            # 返回响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "success",
                "message": "Translation API endpoint"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "service": "Multi-Language Translation Agent",
            "version": "3.0",
            "endpoints": {
                "POST /api/translate": "Translate CSV file"
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
```

#### 3. 创建前端页面

创建 `index.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>多语言翻译Agent</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .container {
            background: #f5f5f5;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        input[type="file"],
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            background: #0070f3;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #0056b3;
        }
        .info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 多语言翻译Agent</h1>
        
        <div class="form-group">
            <label for="csvFile">上传CSV文件</label>
            <input type="file" id="csvFile" accept=".csv" />
        </div>
        
        <div class="form-group">
            <label for="targetLanguages">目标语言</label>
            <input type="text" id="targetLanguages" placeholder="例如：英文,日文,韩文" />
        </div>
        
        <button onclick="translate()">开始翻译</button>
        
        <div class="info">
            <strong>支持的语言：</strong><br>
            英文、日文、韩文、法文、德文、西班牙文、俄文、意大利文、葡萄牙文
        </div>
    </div>

    <script>
        function translate() {
            alert('翻译功能正在开发中，请使用Docker部署版本：\n\ndocker-compose up -d');
        }
    </script>
</body>
</html>
```

---

## 🎯 推荐部署方案

由于这个项目是一个**完整的LangGraph工作流**，包含：
- ✅ 长时间运行的翻译任务
- ✅ PostgreSQL数据库
- ✅ 对象存储（S3）
- ✅ 复杂的后端服务

**Vercel不是最佳选择**，因为：
- ❌ Serverless Functions有执行时间限制（最多60秒）
- ❌ 不适合长时间运行的工作流
- ❌ 需要额外的数据库和存储服务

### ✅ 推荐方案

#### 方案A：Docker + 云服务器（推荐）
```bash
docker-compose up -d
```
- 适合：生产环境
- 优点：完整功能，无限制
- 成本：$5-10/月（Vultr/DigitalOcean）

#### 方案B：Railway.app
- 适合：快速部署
- 优点：自动部署，有数据库和存储
- 成本：免费额度 + $5/月起

#### 方案C：Render.com
- 适合：中小型项目
- 优点：免费Web服务
- 成本：免费额度 + $7/月起

---

## 📝 快速解决Vercel部署错误

如果你坚持使用Vercel，按以下步骤操作：

1. **使用requirements.vercel.txt**
   - 在Vercel设置中修改构建命令为：
     ```
     pip install -r requirements.vercel.txt
     ```

2. **创建简单的API入口**
   - 创建 `api/` 目录
   - 添加Python函数作为入口点

3. **推送代码**
   ```bash
   git add .
   git commit -m "feat: 添加Vercel配置"
   git push origin main
   ```

4. **在Vercel重新部署**

---

**建议：使用Docker Compose部署到云服务器，这是最稳定、最完整的方案。** 🚀
