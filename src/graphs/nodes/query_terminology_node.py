from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import KnowledgeClient
from graphs.state import QueryTerminologyNodeInput, QueryTerminologyNodeOutput


def query_terminology_node(state: QueryTerminologyNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> QueryTerminologyNodeOutput:
    """
    title: 术语查询
    desc: 从知识库中检索专词，提升翻译准确率（仅在中译英时使用）
    integrations: 知识库
    """
    ctx = runtime.context
    
    # 判断是否需要使用知识库（仅在中译英时使用）
    need_use_kb = "英文" in state.target_languages
    
    if not need_use_kb:
        # 如果不包含英文，直接返回空字典
        return QueryTerminologyNodeOutput(terminology_dict={})
    
    # 初始化知识库客户端
    kb_client = KnowledgeClient(ctx=ctx)
    
    # 构建术语字典
    terminology_dict = {}
    
    try:
        # 从CSV数据中提取需要翻译的中文词汇
        all_chinese_words = set()
        
        for row in state.csv_data['data']:
            for col in state.chinese_columns:
                if col in row:
                    text = str(row[col])
                    # 简单提取中文词（实际可以用更复杂的分词算法）
                    import re
                    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
                    all_chinese_words.update(chinese_words)
        
        # 对每个中文词进行知识库检索
        for word in all_chinese_words:
            query = f"{word} 翻译"
            
            # 检索知识库
            response = kb_client.search(
                query=query,
                top_k=3,
                min_score=0.6
            )
            
            if response.code == 0 and response.chunks:
                # 从检索结果中提取翻译
                # 假设知识库中的格式为："中文词 -> 目标语言: 翻译"
                for chunk in response.chunks:
                    content = chunk.content
                    # 解析知识库内容，提取翻译
                    # 这里简化处理，实际需要根据知识库的具体格式来解析
                    if word in content:
                        # 尝试提取翻译信息
                        import re
                        # 假设格式为：中文词 英文:xxx 日文:xxx
                        pattern = r'(\w+):\s*([^,\s]+)'
                        matches = re.findall(pattern, content)
                        
                        if matches:
                            if word not in terminology_dict:
                                terminology_dict[word] = {}
                            
                            for lang, trans in matches:
                                terminology_dict[word][lang] = trans
        
        return QueryTerminologyNodeOutput(terminology_dict=terminology_dict)
    
    except Exception as e:
        # 如果知识库查询失败，返回空字典，不影响后续翻译流程
        print(f"知识库查询失败: {str(e)}")
        return QueryTerminologyNodeOutput(terminology_dict={})
