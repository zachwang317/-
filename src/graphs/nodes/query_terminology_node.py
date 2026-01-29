from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import KnowledgeClient
from graphs.state import QueryTerminologyNodeInput, QueryTerminologyNodeOutput


def query_terminology_node(state: QueryTerminologyNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> QueryTerminologyNodeOutput:
    """
    title: 术语查询（优化版）
    desc: 从知识库中批量检索专词，提升翻译准确率（仅在中译英时使用）
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
                    # 提取中文词（2个字及以上）
                    import re
                    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
                    all_chinese_words.update(chinese_words)
        
        # 如果没有中文词汇，直接返回
        if not all_chinese_words:
            return QueryTerminologyNodeOutput(terminology_dict={})
        
        # 优化：批量检索，而不是逐个检索
        # 将词汇列表分成批次，每批最多10个词
        batch_size = 10
        word_list = list(all_chinese_words)
        
        for i in range(0, len(word_list), batch_size):
            batch_words = word_list[i:i + batch_size]
            
            # 构建批量查询：用换行分隔多个词汇
            query = "\n".join([f"{word} 翻译" for word in batch_words])
            
            # 检索知识库
            response = kb_client.search(
                query=query,
                top_k=10,  # 增加返回数量以匹配多个词汇
                min_score=0.5  # 降低阈值，确保能检索到更多相关结果
            )
            
            if response.code == 0 and response.chunks:
                # 从检索结果中提取翻译
                for chunk in response.chunks:
                    content = chunk.content
                    # 解析知识库内容，提取翻译
                    # 假设知识库中的格式为："中文词 英文:xxx 日文:xxx"
                    import re
                    
                    # 匹配中文词
                    for word in batch_words:
                        if word not in content:
                            continue
                        
                        # 如果这个词还没有翻译，尝试提取
                        if word not in terminology_dict:
                            terminology_dict[word] = {}
                        
                        # 提取翻译信息，格式：英文:xxx 日文:xxx
                        pattern = r'(\w+):\s*([^,\s\n]+)'
                        matches = re.findall(pattern, content)
                        
                        for lang, trans in matches:
                            terminology_dict[word][lang] = trans
        
        return QueryTerminologyNodeOutput(terminology_dict=terminology_dict)
    
    except Exception as e:
        # 如果知识库查询失败，返回空字典，不影响后续翻译流程
        print(f"知识库查询失败: {str(e)}")
        return QueryTerminologyNodeOutput(terminology_dict={})
