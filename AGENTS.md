## 项目概述
- **名称**: 多语言翻译 Agent（增强版）
- **功能**: 读取包含中文列的CSV文件，自动识别中文列，将内容翻译成指定目标语言，生成包含原始列和翻译列的新CSV文件。支持知识库RAG增强、并行处理和优化的列排列。

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| read_csv | `graphs/nodes/read_csv_node.py` | task | 读取CSV文件并识别中文列 | - | - |
| query_terminology | `graphs/nodes/query_terminology_node.py` | task | 从知识库检索专词（可选） | - | - |
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
- 节点 `query_terminology` 使用集成 `知识库` (integration-knowledge-base)

## 新增功能（v2.0）
1. **列排列优化**：输出CSV按指定顺序排列，先展示原始列，再按目标语言顺序展示翻译列，列名格式为 `列序号_列名_目标语言_翻译`
2. **并行处理**：支持按目标语言并行翻译，提升大数据量场景下的处理效率
3. **知识库RAG**：支持从知识库检索专词，提升翻译准确率（可选）
