from typing import Optional, Dict, List
import re
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk.database import get_session
from storage.database.translation_manager import TranslationKnowledgeManager
from graphs.state import QueryTerminologyNodeInput, QueryTerminologyNodeOutput

# 设置日志
logger = logging.getLogger(__name__)


def query_terminology_node(state: QueryTerminologyNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> QueryTerminologyNodeOutput:
    """
    title: 术语查询（数据库版）
    desc: 从数据库表"翻译知识库"中批量检索专词，支持多语言平铺列结构
    integrations: 数据库
    """
    ctx = runtime.context
    
    # 初始化数据库会话
    db = get_session()
    
    # 初始化翻译知识库管理器
    translation_mgr = TranslationKnowledgeManager()
    
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
        
        logger.info(f"开始从数据库查询术语翻译")
        logger.info(f"待查询的中文词汇数量: {len(all_chinese_words)}")
        logger.info(f"目标语言: {state.target_languages}")
        
        # 将词汇列表转换为有序列表
        word_list = list(all_chinese_words)
        
        # 为每个目标语言批量查询翻译
        for target_lang in state.target_languages:
            # 批量查询该语言的所有翻译
            translations = translation_mgr.get_translations_batch(
                db=db,
                chinese_terms=word_list,
                target_language=target_lang
            )
            
            # 构建术语字典
            for chinese_word, translation in translations.items():
                if translation:  # 只有当翻译存在时才添加
                    if chinese_word not in terminology_dict:
                        terminology_dict[chinese_word] = {}
                    terminology_dict[chinese_word][target_lang] = translation
                    logger.info(f"✓ 找到翻译: {chinese_word} -> {translation} ({target_lang})")
                else:
                    logger.debug(f"  未找到翻译: {chinese_word} ({target_lang})")
        
        # 打印汇总信息
        logger.info(f"数据库查询完成，共找到 {len(terminology_dict)} 个术语的翻译")
        for word, translations in terminology_dict.items():
            logger.info(f"  {word}: {translations}")
        
        return QueryTerminologyNodeOutput(terminology_dict=terminology_dict)
    
    except Exception as e:
        # 如果数据库查询失败，返回空字典，不影响后续翻译流程
        logger.error(f"数据库查询失败: {str(e)}", exc_info=True)
        return QueryTerminologyNodeOutput(terminology_dict={})
    finally:
        # 关闭数据库会话
        db.close()
