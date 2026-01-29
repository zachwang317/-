from typing import Optional, Dict, List
import re
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import KnowledgeClient
from graphs.state import QueryTerminologyNodeInput, QueryTerminologyNodeOutput, get_knowledge_base_column


def query_terminology_node(state: QueryTerminologyNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> QueryTerminologyNodeOutput:
    """
    title: 术语查询（通用多语言版）
    desc: 从通用多语言知识库中批量检索专词，提升翻译准确率
    integrations: 知识库
    """
    ctx = runtime.context
    
    # 初始化知识库客户端
    kb_client = KnowledgeClient(ctx=ctx)
    
    # 构建术语字典：{中文词: {目标语言: 翻译}}
    terminology_dict: Dict[str, Dict[str, str]] = {}
    
    try:
        # 从CSV数据中提取需要翻译的中文词汇
        all_chinese_words = set()
        
        for row in state.csv_data['data']:
            for col in state.chinese_columns:
                if col in row:
                    text = str(row[col])
                    # 提取中文词（2个字及以上）
                    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
                    all_chinese_words.update(chinese_words)
        
        # 如果没有中文词汇，直接返回
        if not all_chinese_words:
            return QueryTerminologyNodeOutput(terminology_dict={})
        
        # 构建需要查询的列名列表（根据目标语言）
        target_columns = []
        for target_lang in state.target_languages:
            kb_column = get_knowledge_base_column(target_lang)
            if kb_column:
                target_columns.append((target_lang, kb_column))
        
        # 如果没有需要查询的列，直接返回
        if not target_columns:
            return QueryTerminologyNodeOutput(terminology_dict={})
        
        # 批量检索：将词汇列表分成批次，每批最多10个词
        batch_size = 10
        word_list = list(all_chinese_words)
        
        # 为每个目标语言分别查询
        for target_lang, kb_column in target_columns:
            for i in range(0, len(word_list), batch_size):
                batch_words = word_list[i:i + batch_size]
                
                # 构建批量查询：直接查询中文词
                query = "\n".join(batch_words)
                
                # 检索知识库
                response = kb_client.search(
                    query=query,
                    table_names=["多语言翻译工具知识库"],  # 明确指定知识库名称
                    top_k=10,
                    min_score=0.3  # 降低阈值，确保能检索到更多相关结果
                )
                
                if response.code == 0 and response.chunks:
                    # 从检索结果中提取翻译
                    for chunk in response.chunks:
                        content = chunk.content
                        
                        # 尝试多种方式提取翻译
                        for word in batch_words:
                            if word not in content:
                                continue
                            
                            # 初始化该词的字典
                            if word not in terminology_dict:
                                terminology_dict[word] = {}
                            
                            # 方式1：尝试表格格式 "中文|英语|日语"
                            table_pattern = rf'^{re.escape(word)}\|([^\|]+)'
                            table_match = re.search(table_pattern, content, re.MULTILINE)
                            if table_match:
                                translation = table_match.group(1).strip()
                                if translation and translation != word:
                                    terminology_dict[word][target_lang] = translation
                                    continue
                            
                            # 方式2：尝试CSV格式 "中文,英语,日语"
                            csv_pattern = rf'^{re.escape(word)},([^,\n]+)'
                            csv_match = re.search(csv_pattern, content, re.MULTILINE)
                            if csv_match:
                                translation = csv_match.group(1).strip()
                                if translation and translation != word:
                                    terminology_dict[word][target_lang] = translation
                                    continue
                            
                            # 方式3：尝试JSON格式
                            json_pattern = rf'"{re.escape(word)}"\s*:\s*{re.escape(kb_column)}\s*[:：]\s*"([^"]+)"'
                            json_match = re.search(json_pattern, content)
                            if json_match:
                                translation = json_match.group(1).strip()
                                if translation and translation != word:
                                    terminology_dict[word][target_lang] = translation
                                    continue
                            
                            # 方式4：尝试从文本中提取 "中文 -> 翻译" 格式
                            arrow_pattern = rf'{re.escape(word)}\s*[→→-]\s*([^\n]+)'
                            arrow_match = re.search(arrow_pattern, content)
                            if arrow_match:
                                translation = arrow_match.group(1).strip()
                                if translation and translation != word:
                                    terminology_dict[word][target_lang] = translation
                                    continue
        
        # 打印调试信息
        print(f"知识库查询完成，共找到 {len(terminology_dict)} 个术语的翻译")
        for word, translations in terminology_dict.items():
            print(f"  {word}: {translations}")
        
        return QueryTerminologyNodeOutput(terminology_dict=terminology_dict)
    
    except Exception as e:
        # 如果知识库查询失败，返回空字典，不影响后续翻译流程
        print(f"知识库查询失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return QueryTerminologyNodeOutput(terminology_dict={})
