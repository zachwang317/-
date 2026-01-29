## 项目概述
- **名称**: 多语言翻译 Agent（增强版v2.1）
- **功能**: 读取包含中文列的CSV文件，自动识别中文列，将内容翻译成指定目标语言，生成包含原始列和翻译列的新CSV文件。支持知识库RAG增强、并行处理和优化的列排列。

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
- 节点 `query_terminology` 使用集成 `知识库` (integration-knowledge-base)

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
- 系统自动检测目标语言中是否包含"英文"
- 如果包含英文，自动使用知识库"多语言翻译工具知识库-中英"进行术语检索
- 其他语言不使用知识库
