from typing import Optional, Dict, List
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
                    import re
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
        
        # 构建查询说明
        column_names = [col_name for _, col_name in target_columns]
        query_instruction = f"请从知识库的以下列中提取翻译：{', '.join(column_names)}\n\n"
        
        for i in range(0, len(word_list), batch_size):
            batch_words = word_list[i:i + batch_size]
            
            # 构建批量查询
            query = query_instruction + "\n".join([f"{word}" for word in batch_words])
            
            # 检索知识库，明确指定使用"多语言翻译工具知识库"
            response = kb_client.search(
                query=query,
                table_names=["多语言翻译工具知识库"],  # 明确指定知识库名称
                top_k=10,  # 增加返回数量以匹配多个词汇
                min_score=0.5  # 降低阈值，确保能检索到更多相关结果
            )
            
            if response.code == 0 and response.chunks:
                # 从检索结果中提取翻译
                for chunk in response.chunks:
                    content = chunk.content
                    
                    # 为每个目标语言解析翻译
                    for target_lang, kb_column in target_columns:
                        # 尝试从内容中提取该列的翻译
                        # 假设知识库格式：中文内容,英语,日语,韩语
                        import re
                        
                        # 查找包含该词的行
                        for word in batch_words:
                            if word not in content:
                                continue
                            
                            # 初始化该词的字典
                            if word not in terminology_dict:
                                terminology_dict[word] = {}
                            
                            # 尝试提取该列的翻译
                            # 方式1：查找 "中文内容,英语,日语,韩语" 格式
                            pattern = rf'{re.escape(word)},([^,\n]*)'
                            matches = re.findall(pattern, content)
                            
                            if matches:
                                # 找到匹配，需要根据列的位置提取对应的翻译
                                # 这里简化处理，尝试在内容中找到列名和对应的值
                                column_pattern = rf'{re.escape(kb_column)}[:：]?\s*([^\s,，\n]+)'
                                column_matches = re.findall(column_pattern, content)
                                
                                if column_matches:
                                    terminology_dict[word][target_lang] = column_matches[0]
                                else:
                                    # 如果没找到明确标注的，尝试从CSV格式中推断
                                    # 这里的处理比较复杂，简化为直接在内容中查找词后面的内容
                                    pass
        
        return QueryTerminologyNodeOutput(terminology_dict=terminology_dict)
    
    except Exception as e:
        # 如果知识库查询失败，返回空字典，不影响后续翻译流程
        print(f"知识库查询失败: {str(e)}")
        return QueryTerminologyNodeOutput(terminology_dict={})
