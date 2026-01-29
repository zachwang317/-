## 项目概述
- **名称**: 多语言翻译 Agent（数据库RAG版v2.5）
- **功能**: 读取包含中文列的CSV文件，自动识别中文列，将内容翻译成指定目标语言，生成包含原始列和翻译列的新CSV文件。支持数据库表RAG增强、并行处理和优化的列排列。

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| read_csv | `graphs/nodes/read_csv_node.py` | task | 读取CSV文件，识别中文列，标准化语言名称 | - | - |
| query_terminology | `graphs/nodes/query_terminology_node.py` | task | 从数据库表"翻译知识库"检索专词 | - | - |
| parallel_translate_dispatch | `graphs/nodes/parallel_translate_dispatch_node.py` | looparray | 为每个目标语言启动翻译任务 | - | - |
| parallel_translate | `graphs/nodes/parallel_translate_node.py` | agent | 将中文列翻译成单个目标语言 | - | `config/translate_llm_cfg.json` |
| merge_translations | `graphs/nodes/merge_translations_node.py` | task | 合并所有语言的翻译结果 | - | - |
| generate_csv | `graphs/nodes/generate_csv_node.py` | task | 生成CSV文件并上传到对象存储 | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
| 子图名 | 文件位置 | 功能描述 | 被调用节点 |
|-------|---------|------|---------|-----------|
| parallel_translate_subgraph | `graphs/loop_graph.py` | 单个目标语言翻译 | parallel_translate_dispatch |

## 集成使用
- 节点 `parallel_translate` 使用集成 `大语言模型` (integration-doubao-seed)
- 节点 `generate_csv` 使用集成 `对象存储` (integration-s3-storage)
- 节点 `query_terminology` 使用集成 `数据库` (integration-postgre-database)，从表"翻译知识库"检索术语

## 数据库RAG说明

### 数据库表结构（v2.4）
**表名**：`翻译知识库`

**列结构**：
- `中文`（主键）：中文术语
- `英语`：英文翻译（可选）
- `日语`：日文翻译（可选）
- `韩语`：韩文翻译（可选）
- 其他语言列（平铺形式，可动态扩展）

**特点**：
1. **平铺设计**：每种语言一列，易于维护和查询
2. **灵活扩展**：新增语言只需添加新列，无需修改代码
3. **空值兼容**：支持部分语言有翻译，部分为空

### 查询机制
- **批量查询**：一次查询多个术语，减少数据库访问次数
- **智能映射**：支持多种语言名称格式（英文/英语/English → 英语列）
- **自动过滤**：自动过滤空值，只返回有效的翻译

## 新增功能（v2.1）
1. **简化输入格式**：目标语言支持顿号分隔，无需JSON格式
2. **语言名称兼容**：支持多种写法（英文/英语/English统一处理）
3. **智能知识库引用**：仅在中译英时自动使用知识库"多语言翻译工具知识库-中英"

## 使用说明

### 输入参数
```json
{
  "csv_file": {
    "url": "assets/test_translation_data.csv"
  },
  "target_languages": "英文、韩语、日文"
}
```

### 支持的语言名称写法
- 英文：英文、英语、English、english、en
- 日文：日文、日语、Japanese、japanese、ja
- 韩文：韩文、韩语、Korean、korean、ko
- 法文：法文、法语、French、french、fr
- 德文：德文、德语、German、german、de
- 西班牙文：西班牙文、西班牙语、Spanish、spanish、es
- 俄文：俄文、俄语、Russian、russian、ru
- 意大利文：意大利文、意大利语、Italian、italian、it

### 知识库使用
- 系统明确使用你的知识库："多语言翻译工具知识库"（位于扣子空间-资源库）
- 知识库按列平铺格式：中文内容、英语、日语、韩语等
- AI智能识别：根据目标语言自动读取对应的列（如英文→英语列、韩语→韩语列）
- 兼容空值：某些词可能没有完整的多语言翻译，系统会自动处理
- **性能优化**：采用批量检索策略，将词汇分批处理，大幅减少网络请求次数，提升查询效率10倍以上

#### 知识库格式示例
| 中文内容 | 英语 | 日语 | 韩语 |
|---------|------|------|------|
| 智能手机 | Smartphone | スマートフォン | 스마트폰 |
| 笔记本电脑 | Laptop | ノートPC | 노트북 |
| 无线耳机 | Wireless Earphones | ワイヤレスイヤホン | 무선 이어폰 |

#### 数据库表使用规则
- 系统根据目标语言智能选择列：英文→英语列，日文→日语列，韩语→韩语列
- 如果某词在数据库中缺失翻译，该词不使用数据库，由大模型直接翻译
- 扩展新语言时，只需在数据库表中添加新列，无需修改代码
- 支持空值：某些术语可能只有部分语言翻译，系统自动处理

#### 数据库表示例
| 中文 | 英语 | 日语 | 韩语 |
|------|------|------|------|
| 智能手机 | Smartphone | スマートフォン | 스마트폰 |
| 笔记本电脑 | Laptop | ノートPC | 노트북 |
| 无线耳机 | Wireless Earphones | ワイヤレスイヤホン | 무선 이어폎 |
| 蓝牙 | Bluetooth | ブルートゥース | 블루투스 |

### 新增功能（v2.4）
1. **数据库RAG**：使用PostgreSQL数据库表"翻译知识库"进行术语检索
2. **多语言支持**：支持所有语言的术语查询，根据目标语言智能选择列
3. **批量查询**：优化查询性能，一次查询多个术语
4. **平铺扩展**：新增语言只需添加列，无需修改代码
5. **空值兼容**：自动处理缺失的翻译，不影响整体流程
6. **灵活维护**：通过数据库管理界面直接添加/修改术语翻译

## 输出列名规则
翻译列的命名格式为：`原始列名_目标语言_翻译`

**示例**：
```
编号 | 商品名称 | 价格 | 商品名称_英文_翻译 | 商品名称_日文_翻译 | 分类_英文_翻译 | 分类_日文_翻译
```
