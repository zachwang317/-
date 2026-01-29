from typing import Optional, Dict, List
import re
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk.database import get_session
from coze_coding_dev_sdk import EmbeddingClient
from storage.database.translation_manager import TranslationKnowledgeManager
from graphs.state import QueryTerminologyNodeInput, QueryTerminologyNodeOutput

# 设置日志
logger = logging.getLogger(__name__)


def query_terminology_node(state: QueryTerminologyNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> QueryTerminologyNodeOutput:
    """
    title: 术语查询（数据库向量检索版）
    desc: 从数据库表"翻译知识库"中通过向量相似度检索专词，支持语义匹配
    integrations: 数据库
    """
    ctx = runtime.context
    
    # 初始化数据库会话
    db = get_session()
    
    # 初始化翻译知识库管理器
    translation_mgr = TranslationKnowledgeManager()
    
    # 初始化向量客户端
    embedding_client = EmbeddingClient(ctx=ctx)
    
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
            logger.info("没有找到中文词汇")
            return QueryTerminologyNodeOutput(terminology_dict={})
        
        logger.info(f"开始从数据库进行向量检索")
        logger.info(f"待查询的中文词汇数量: {len(all_chinese_words)}")
        logger.info(f"目标语言: {state.target_languages}")
        
        # 为每个目标语言进行向量检索
        for target_lang in state.target_languages:
            for chinese_word in all_chinese_words:
                # 使用向量相似度检索
                similar_results = translation_mgr.get_translations_by_similarity(
                    db=db,
                    query_text=chinese_word,
                    target_language=target_lang,
                    embedding_client=embedding_client,
                    top_k=1,  # 只取最相似的结果
                    min_similarity=0.3  # 相似度阈值（降低以提高匹配率）
                )
                
                # 如果找到相似的结果
                if similar_results:
                    best_match = similar_results[0]  # 取最相似的一个
                    original_term = best_match[0]
                    translation = best_match[1]
                    similarity_score = best_match[2]
                    
                    # 如果相似度足够高，使用该翻译
                    if similarity_score >= 0.7:
                        if chinese_word not in terminology_dict:
                            terminology_dict[chinese_word] = {}
                        terminology_dict[chinese_word][target_lang] = translation
                        logger.info(f"✓ 向量匹配: {chinese_word} → {translation} (相似度: {similarity_score:.3f}, 原术语: {original_term})")
                    else:
                        logger.debug(f"  相似度过低: {chinese_word} (分数: {similarity_score:.3f})")
                else:
                    logger.debug(f"  未找到匹配: {chinese_word} ({target_lang})")
        
        # 打印汇总信息
        logger.info(f"向量检索完成，共找到 {len(terminology_dict)} 个术语的翻译")
        for word, translations in terminology_dict.items():
            logger.info(f"  {word}: {translations}")
        
        return QueryTerminologyNodeOutput(terminology_dict=terminology_dict)
    
    except Exception as e:
        # 如果向量检索失败，返回空字典，不影响后续翻译流程
        logger.error(f"向量检索失败: {str(e)}", exc_info=True)
        return QueryTerminologyNodeOutput(terminology_dict={})
    finally:
        # 关闭数据库会话
        db.close()
