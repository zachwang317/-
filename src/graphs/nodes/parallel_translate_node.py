import os
import json
from jinja2 import Template
from typing import Dict
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from graphs.state import ParallelTranslateNodeInput, ParallelTranslateNodeOutput


def parallel_translate_node(state: ParallelTranslateNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> ParallelTranslateNodeOutput:
    """
    title: 并行翻译
    desc: 将CSV中的中文列翻译成单个目标语言，生成对应翻译列
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 1. 读取大模型配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        llm_cfg = json.load(fd)
    
    # 2. 准备输入数据
    rows_data = state.csv_data['data']
    columns = state.csv_data['columns']
    
    # 构建需要翻译的数据结构
    translate_items = []
    for row in rows_data:
        item = {}
        for col in state.chinese_columns:
            if col in row:
                item[col] = row[col]
        translate_items.append(item)
    
    # 3. 构建术语提示（如果有）
    terminology_hint = ""
    if state.terminology_dict:
        terminology_hint = "\n# 专词翻译参考\n以下专词请按参考翻译：\n"
        for chinese_word, translations in state.terminology_dict.items():
            lang_translation = translations.get(state.target_language, "")
            if lang_translation:
                terminology_hint += f"{chinese_word} → {lang_translation}\n"
    
    # 4. 构建提示词
    model_config = llm_cfg.get("config", {})
    sp_template = llm_cfg.get("sp", "")
    up_template = llm_cfg.get("up", "")
    
    # 渲染系统提示词
    sp = Template(sp_template).render({
        "target_language": state.target_language,
        "chinese_columns": state.chinese_columns,
        "terminology_hint": terminology_hint
    })
    
    # 渲染用户提示词
    up = Template(up_template).render({
        "translate_items": translate_items[:50],  # 限制每次翻译数量
        "chinese_columns": state.chinese_columns,
        "target_language": state.target_language,
        "terminology_hint": terminology_hint,
        "total_items": len(translate_items)
    })
    
    # 5. 调用大模型
    llm_client = LLMClient(ctx=ctx)
    
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=up)
    ]
    
    response = llm_client.invoke(
        messages=messages,
        model=model_config.get("model", "doubao-seed-1-8-251228"),
        temperature=model_config.get("temperature", 0.3),
        max_completion_tokens=model_config.get("max_completion_tokens", 32768),
        thinking=model_config.get("thinking", "disabled")
    )
    
    # 6. 解析响应
    response_text = response.content if isinstance(response.content, str) else str(response.content)
    
    # 尝试解析JSON
    try:
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
        else:
            result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {"translated_items": translate_items}
    
    # 7. 构建翻译后的数据，生成符合要求的列名
    translated_rows = []
    translated_items = result.get("translated_items", translate_items)
    
    # 生成列名：列名_目标语言_翻译
    translated_columns = []
    
    for col in state.chinese_columns:
        new_col_name = f"{col}_{state.target_language}_翻译"
        translated_columns.append({
            "original_column": col,
            "translated_column": new_col_name
        })
    
    # 合并原始数据和翻译数据
    for i, original_row in enumerate(rows_data):
        translated_row = original_row.copy()
        
        if i < len(translated_items):
            translated_item = translated_items[i]
            # 添加翻译后的列
            for col_info in translated_columns:
                original_col = col_info["original_column"]
                translated_col = col_info["translated_column"]
                
                # 从翻译结果中提取对应的值
                if translated_col in translated_item:
                    translated_row[translated_col] = translated_item[translated_col]
                elif original_col in translated_item:
                    translated_row[translated_col] = translated_item[original_col]
        
        translated_rows.append(translated_row)
    
    # 8. 构建输出数据
    translated_data = {
        'columns': columns,
        'data': translated_rows,
        'translated_columns': translated_columns,
        'target_language': state.target_language
    }
    
    return ParallelTranslateNodeOutput(
        target_language=state.target_language,
        translated_data=translated_data
    )
