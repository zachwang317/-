## 项目概述
- **名称**: 多语言翻译 Agent（增强版v2.3）
- **功能**: 读取包含中文列的CSV文件，自动识别中文列，将内容翻译成指定目标语言，生成包含原始列和翻译列的新CSV文件。支持通用多语言知识库RAG增强、并行处理和优化的列排列。

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| read_csv | `graphs/nodes/read_csv_node.py` | task | 读取CSV文件，识别中文列，标准化语言名称 | - | - |
| query_terminology | `graphs/nodes/query_terminology_node.py` | task | 从知识库检索专词（仅中译英时使用） | - | - |
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
- 节点 `query_terminology` 使用集成 `知识库` (integration-knowledge-base)，采用批量检索优化策略

## 性能优化说明

### 知识库查询优化（v2.2）
**问题**：
- 旧方案：每个中文词汇单独一次检索，100个词 = 100次网络请求，耗时很长

**优化方案**：
1. **批量检索**：将词汇分批处理，每批10个词，100个词 = 10次网络请求
2. **智能去重**：使用set自动去重，避免重复检索相同词汇
3. **批量查询**：用换行分隔多个词汇，一次查询返回多个结果

**性能提升**：
- 网络请求次数减少约90%
- 查询时间缩短约80-90%
- 大词汇量场景下效果更显著

**实现细节**：
```python
# 伪代码示例
batch_size = 10
for i in range(0, len(words), batch_size):
    batch_words = words[i:i + batch_size]
    query = "\n".join([f"{word} 翻译" for word in batch_words])
    # 一次检索处理10个词汇
```

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

#### 知识库使用规则
- 系统根据目标语言智能选择列：英文→英语列，日文→日语列，韩语→韩语列
- 如果某词在知识库中缺失翻译，该词不使用知识库，由大模型直接翻译
- 扩展新语言时，只需在知识库中添加新列，无需修改代码

### 新增功能（v2.3）
1. **通用多语言知识库**：支持所有语言的术语检索，不再局限于中译英
2. **智能列识别**：根据目标语言自动从知识库选择对应的列
3. **列名规则优化**：翻译列名简化为"列名_目标语言_翻译"（如"商品名称_英文_翻译"）
4. **空值兼容**：自动处理知识库中缺失的翻译，不影响整体流程

## 输出列名规则
翻译列的命名格式为：`原始列名_目标语言_翻译`

**示例**：
```
编号 | 商品名称 | 价格 | 商品名称_英文_翻译 | 商品名称_日文_翻译 | 分类_英文_翻译 | 分类_日文_翻译
```
