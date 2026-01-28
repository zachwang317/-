## 项目概述
- **名称**: 多语言翻译 Agent
- **功能**: 读取包含中文列的CSV文件，自动识别中文列，将内容翻译成指定目标语言，生成包含原始列和翻译列的新CSV文件

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| read_csv | `graphs/nodes/read_csv_node.py` | task | 读取CSV文件并识别中文列 | - | - |
| translate | `graphs/nodes/translate_node.py` | agent | 批量翻译中文内容到目标语言 | - | `config/translate_llm_cfg.json` |
| generate_csv | `graphs/nodes/generate_csv_node.py` | task | 生成CSV文件并上传到对象存储 | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
无子图

## 集成使用
- 节点 `translate` 使用集成 `大语言模型` (integration-doubao-seed)
- 节点 `generate_csv` 使用集成 `对象存储` (integration-s3-storage)
