from typing import List
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import MergeTranslationsNodeInput, MergeTranslationsNodeOutput


def merge_translations_node(state: MergeTranslationsNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> MergeTranslationsNodeOutput:
    """
    title: 合并翻译结果
    desc: 将所有目标语言的翻译结果合并到一起
    integrations: -
    """
    ctx = runtime.context
    
    # 1. 以原始数据为基础
    merged_rows = state.csv_data['data'].copy()
    
    # 2. 遍历每个语言的翻译结果，将翻译列添加到merged_rows中
    for lang_result in state.translated_results:
        lang_data = lang_result.get('data', [])
        translated_columns = lang_result.get('translated_columns', [])
        
        for i, original_row in enumerate(merged_rows):
            if i < len(lang_data):
                lang_row = lang_data[i]
                
                # 将翻译列添加到原始行
                for col_info in translated_columns:
                    translated_col = col_info["translated_column"]
                    if translated_col in lang_row:
                        original_row[translated_col] = lang_row[translated_col]
    
    # 3. 构建输出数据
    merged_data = {
        'columns': state.csv_data['columns'],
        'data': merged_rows,
        'target_languages': state.target_languages,
        'chinese_columns': state.chinese_columns
    }
    
    return MergeTranslationsNodeOutput(merged_data=merged_data)
