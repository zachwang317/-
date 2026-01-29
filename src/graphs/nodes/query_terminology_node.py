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
    title: 术语查询（精确匹配）
    desc: 从数据库表"翻译知识库"中精确查询专词翻译
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
        
        logger.info(f"开始从数据库进行术语查询")
        logger.info(f"待查询的中文词汇数量: {len(all_chinese_words)}")
        logger.info(f"目标语言: {state.target_languages}")
        
        match_count = 0
        
        # 为每个目标语言进行精确匹配查询
        for target_lang in state.target_languages:
            for chinese_word in all_chinese_words:
                # 精确匹配
                translation = translation_mgr.get_translation(db, chinese_word, target_lang)
                if translation:
                    if chinese_word not in terminology_dict:
                        terminology_dict[chinese_word] = {}
                    terminology_dict[chinese_word][target_lang] = translation
                    match_count += 1
                    logger.info(f"✓ 匹配: {chinese_word} -> {translation} ({target_lang})")
        
        # 打印汇总信息
        logger.info(f"术语查询完成，共找到 {len(terminology_dict)} 个术语的翻译")
        logger.info(f"  - 匹配数量: {match_count} 个")
        for word, translations in terminology_dict.items():
            logger.info(f"  {word}: {translations}")
        
        return QueryTerminologyNodeOutput(terminology_dict=terminology_dict)
    
    except Exception as e:
        # 如果查询失败，返回空字典，不影响后续翻译流程
        logger.error(f"术语查询失败: {str(e)}", exc_info=True)
        return QueryTerminologyNodeOutput(terminology_dict={})
    finally:
        # 关闭数据库会话
        db.close()
