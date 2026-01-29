from typing import List
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import MergeTranslationsNodeInput, MergeTranslationsNodeOutput

# 配置日志
logger = logging.getLogger(__name__)


def merge_translations_node(state: MergeTranslationsNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> MergeTranslationsNodeOutput:
    """
    title: 合并翻译结果
    desc: 将所有目标语言的翻译结果合并到一起，确保列名顺序正确
    integrations: -
    """
    ctx = runtime.context
    
    # 调试日志：检查输入数据的类型和结构
    logger.info(f"合并节点输入 - csv_data类型: {type(state.csv_data)}")
    logger.info(f"合并节点输入 - csv_data columns: {state.csv_data.get('columns', 'N/A')}")
    logger.info(f"合并节点输入 - csv_data data类型: {type(state.csv_data.get('data'))}")
    if state.csv_data.get('data'):
        logger.info(f"合并节点输入 - csv_data data第一行类型: {type(state.csv_data['data'][0])}")
        logger.info(f"合并节点输入 - csv_data data第一行内容: {state.csv_data['data'][0]}")
    
    logger.info(f"合并节点输入 - translated_results数量: {len(state.translated_results)}")
    
    # 1. 以原始数据为基础
    merged_rows = state.csv_data['data'].copy()
    
    # 2. 收集所有翻译列的信息（按目标语言顺序）
    all_translated_columns = []  # 格式：[{"original": "商品名称", "translated": "商品名称_英文_翻译", "lang": "英文"}, ...]
    
    for lang_result in state.translated_results:
        lang_data = lang_result.get('data', [])
        translated_columns = lang_result.get('translated_columns', [])
        target_language = lang_result.get('target_language', '')
        
        # 将该语言的所有翻译列信息添加到列表中
        for col_info in translated_columns:
            all_translated_columns.append({
                "original": col_info["original_column"],
                "translated": col_info["translated_column"],
                "lang": target_language
            })
        
        # 将翻译数据合并到merged_rows中
        for i, original_row in enumerate(merged_rows):
            if i < len(lang_data):
                lang_row = lang_data[i]
                
                # 将翻译列添加到原始行
                for col_info in translated_columns:
                    translated_col = col_info["translated_column"]
                    if translated_col in lang_row:
                        original_row[translated_col] = lang_row[translated_col]
    
    # 3. 构建正确的列名顺序：先原始列，然后按目标语言顺序添加翻译列
    merged_columns = []
    
    # 3.1 先添加所有原始列
    merged_columns.extend(state.csv_data['columns'])
    
    # 3.2 按目标语言顺序添加翻译列
    # 目标：对于每个目标语言，添加所有中文列对应的翻译列
    for target_lang in state.target_languages:
        # 找出该语言的所有翻译列
        lang_columns = [col for col in all_translated_columns if col["lang"] == target_lang]
        # 按原始列顺序添加翻译列
        for original_col in state.chinese_columns:
            for col_info in lang_columns:
                if col_info["original"] == original_col:
                    merged_columns.append(col_info["translated"])
                    break
    
    # 4. 构建输出数据
    merged_data = {
        'columns': merged_columns,  # 使用正确的列名顺序
        'data': merged_rows,
        'target_languages': state.target_languages,
        'chinese_columns': state.chinese_columns
    }
    
    return MergeTranslationsNodeOutput(merged_data=merged_data)
