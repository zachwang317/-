import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from graphs.state import TranslateNodeInput, TranslateNodeOutput


def translate_node(state: TranslateNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> TranslateNodeOutput:
    """
    title: 批量翻译
    desc: 将CSV中的中文列翻译成多种目标语言，生成对应的翻译列
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 1. 读取大模型配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        llm_cfg = json.load(fd)
    
    # 2. 准备输入数据
    # 提取需要翻译的数据
    rows_data = state.csv_data['data']
    columns = state.csv_data['columns']
    
    # 构建需要翻译的数据结构
    # 格式：[{列名: 值, ...}, ...]
    translate_items = []
    for row in rows_data:
        item = {}
        for col in state.chinese_columns:
            if col in row:
                item[col] = row[col]
        translate_items.append(item)
    
    # 3. 构建提示词
    # 获取配置
    model_config = llm_cfg.get("config", {})
    sp_template = llm_cfg.get("sp", "")
    up_template = llm_cfg.get("up", "")
    
    # 渲染系统提示词
    sp = Template(sp_template).render({
        "target_languages": state.target_languages,
        "chinese_columns": state.chinese_columns
    })
    
    # 渲染用户提示词
    up = Template(up_template).render({
        "translate_items": translate_items[:50],  # 限制每次翻译数量，避免超出token限制
        "chinese_columns": state.chinese_columns,
        "target_languages": state.target_languages,
        "total_items": len(translate_items)
    })
    
    # 4. 调用大模型
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
    
    # 5. 解析响应
    response_text = response.content if isinstance(response.content, str) else str(response.content)
    
    # 尝试解析JSON
    try:
        # 提取JSON部分（可能包含其他文本）
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
        else:
            result = json.loads(response_text)
    except json.JSONDecodeError:
        # 如果解析失败，返回原始数据
        result = {"translated_items": translate_items}
    
    # 6. 构建翻译后的数据
    translated_rows = []
    translated_items = result.get("translated_items", translate_items)
    
    # 合并原始数据和翻译数据
    for i, original_row in enumerate(rows_data):
        translated_row = original_row.copy()
        
        if i < len(translated_items):
            translated_item = translated_items[i]
            # 添加翻译后的列
            for lang in state.target_languages:
                lang_key = f"{lang}_翻译"
                if lang_key in translated_item:
                    translated_row[lang_key] = translated_item[lang_key]
        
        translated_rows.append(translated_row)
    
    # 7. 构建输出数据
    translated_data = {
        'columns': columns,
        'data': translated_rows
    }
    
    return TranslateNodeOutput(translated_data=translated_data)
