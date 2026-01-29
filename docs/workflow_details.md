# 多语言翻译 Agent 工作流详细说明

## 📊 工作流可视化结构

```
┌─────────────┐    ┌──────────────┐    ┌──────────────────────┐    ┌──────────────┐    ┌──────────────┐
│   输入节点   │───→│  read_csv    │───→│  query_terminology   │───→│ parallel_    │───→│ generate_csv │───→END
│  (CSV文件+   │    │  (读取CSV)   │    │  (术语查询)          │    │ translate_   │    │  (生成CSV)   │
│   目标语言)  │    │              │    │                      │    │ dispatch     │    │              │
└─────────────┘    └──────────────┘    └──────────────────────┘    └──────────────┘    └──────────────┘
                                             │
                                             ↓
                              ┌──────────────────────┐
                              │   子图（并行翻译）    │
                              │                      │
                              │  parallel_translate  │
                              │  (大模型翻译)         │
                              └──────────────────────┘
```

## 📋 节点详细说明

### 1. read_csv (CSV读取节点)
**功能**：读取CSV文件，识别中文列，标准化语言名称

**输入参数**：
- `csv_file`: CSV文件对象
- `target_languages`: 目标语言字符串（如"英文、韩语"）

**输出参数**：
- `csv_data`: CSV数据（字典格式）
- `chinese_columns`: 中文列名列表
- `target_languages`: 标准化后的目标语言列表

**处理逻辑**：
1. 标准化语言名称（英文/英语/English → 英文）
2. 读取CSV文件内容
3. 识别包含中文的列
4. 转换为字典格式

---

### 2. query_terminology (术语查询节点)
**功能**：从知识库检索专词翻译

**输入参数**：
- `csv_data`: CSV数据
- `chinese_columns`: 中文列名列表
- `target_languages`: 目标语言列表

**输出参数**：
- `terminology_dict`: 术语字典 {中文词: {目标语言: 翻译}}

**知识库配置**：
- 知识库名称：`多语言翻译工具知识库`
- 知识库位置：扣子空间 - 资源库
- 检索方式：批量检索（每批10个词）

**智能识别逻辑**：
```
目标语言 → 知识库列名
英文      → 英语
日文      → 日语
韩文      → 韩语
法文      → 法语
...
```

---

### 3. parallel_translate_dispatch (并行翻译分发节点)
**功能**：为每个目标语言启动翻译任务

**输入参数**：
- `csv_data`: CSV数据
- `chinese_columns`: 中文列名列表
- `target_languages`: 目标语言列表
- `terminology_dict`: 术语字典

**输出参数**：
- `merged_data`: 合并后的完整数据

**并行处理逻辑**：
```
for 每个目标语言:
    调用子图进行翻译
    合并翻译结果
```

---

### 4. 子图：parallel_translate (单语言翻译节点)
**功能**：将中文列翻译成单个目标语言

**类型**：Agent节点（大模型节点）

**配置文件**：`config/translate_llm_cfg.json`

**输入参数**：
- `csv_data`: CSV数据
- `chinese_columns`: 中文列名列表
- `target_language`: 单个目标语言
- `terminology_dict`: 术语字典

**输出参数**：
- `target_language`: 已翻译的目标语言
- `translated_data`: 该语言的翻译结果

**列名生成规则**：
```
格式：原始列名_目标语言_翻译
示例：商品名称_英文_翻译、分类_日文_翻译
```

**大模型配置**：
- 模型：`doubao-seed-1-8-251228`
- 温度：`0.3`
- 最大Token：`32768`

---

### 5. merge_translations (合并翻译结果节点)
**功能**：合并所有语言的翻译结果

**输入参数**：
- `csv_data`: CSV数据
- `chinese_columns`: 中文列名列表
- `target_languages`: 目标语言列表
- `translated_results`: 所有语言的翻译结果列表

**输出参数**：
- `merged_data`: 合并后的完整数据

**合并逻辑**：
```
原始数据 + 语言1翻译 + 语言2翻译 + ... = 完整数据
```

---

### 6. generate_csv (生成CSV节点)
**功能**：生成CSV文件并上传到对象存储

**输入参数**：
- `merged_data`: 合并后的完整数据

**输出参数**：
- `output_csv_url`: 生成的CSV文件URL

**处理流程**：
1. 将字典转换为DataFrame
2. 保存为CSV文件（UTF-8-BOM编码）
3. 上传到对象存储
4. 生成签名URL（有效期1小时）

---

## 🔗 节点连接关系

### 主流程
```
输入 → read_csv → query_terminology → parallel_translate_dispatch → generate_csv → 输出
```

### 并行处理
```
parallel_translate_dispatch
    ├─→ 子图(英文翻译) ─┐
    ├─→ 子图(日文翻译) ─┼─→ merge_translations
    └─→ 子图(韩语翻译) ─┘
```

---

## 📦 配置文件

### 知识库配置
- 知识库名称：`多语言翻译工具知识库`
- 知识库格式：按列平铺
- 列映射：自动识别（英文→英语，日文→日语等）

### 大模型配置
```json
{
    "model": "doubao-seed-1-8-251228",
    "temperature": 0.3,
    "top_p": 0.7,
    "max_completion_tokens": 32768,
    "thinking": "disabled"
}
```

---

## 🎯 输入输出示例

### 输入示例
```json
{
  "csv_file": {
    "url": "assets/test_translation_data.csv"
  },
  "target_languages": "英文、韩语"
}
```

### 输出示例
```json
{
  "output_csv_url": "https://coze-coding-project.tos.coze.site/..."
}
```

---

## 🔧 关键特性

1. **语言名称兼容**
   - 支持多种写法：英文/英语/English
   - 自动标准化处理

2. **并行翻译**
   - 按目标语言并行处理
   - 提升处理效率

3. **知识库增强**
   - 通用多语言知识库
   - 智能列识别
   - 批量检索优化

4. **列名规则**
   - 格式：列名_目标语言_翻译
   - 示例：商品名称_英文_翻译

---

## 📝 文件结构

```
src/
├── graphs/
│   ├── graph.py              # 主图编排
│   ├── state.py              # 状态定义
│   ├── loop_graph.py         # 子图（并行翻译）
│   └── nodes/
│       ├── read_csv_node.py
│       ├── query_terminology_node.py
│       ├── parallel_translate_node.py
│       ├── merge_translations_node.py
│       ├── parallel_translate_dispatch_node.py
│       └── generate_csv_node.py
└── config/
    └── translate_llm_cfg.json # 大模型配置
```

---

## 💡 与扣子1.0的区别

### 扣子1.0（手动搭建）
- ✅ 可视化拖拽
- ✅ 节点配置面板
- ✅ 实时预览
- ❌ 需要手动配置每个节点
- ❌ 重复工作多

### 当前版本（代码生成）
- ✅ 代码自动生成画布
- ✅ 配置文件集中管理
- ✅ 自动编排逻辑
- ❌ 查看细节需要查看代码
- ❌ 不支持拖拽式编辑

---

## 🔍 如何查看节点配置

### 方法1：查看代码文件
每个节点的配置都在对应的Python文件中：
- `src/graphs/nodes/read_csv_node.py`
- `src/graphs/nodes/query_terminology_node.py`
- 等...

### 方法2：查看配置文件
大模型配置：
- `config/translate_llm_cfg.json`

### 方法3：查看AGENTS.md
项目结构索引：
- `AGENTS.md`

---

## 📊 性能优化

1. **批量检索**：知识库查询采用批量策略
2. **并行处理**：多目标语言并行翻译
3. **智能去重**：自动去除重复词汇
4. **缓存机制**：避免重复查询

---

**版本**：v2.3
**更新时间**：2025-01-28
