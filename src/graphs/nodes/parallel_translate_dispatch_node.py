from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    GlobalState,
    ParallelTranslateDispatchNodeInput,
    ParallelTranslateDispatchNodeOutput,
    MergeTranslationsNodeInput,
    MergeTranslationsNodeOutput
)
from graphs.loop_graph import subgraph, LoopState
from graphs.nodes.merge_translations_node import merge_translations_node


def parallel_translate_dispatch_node(
    state: ParallelTranslateDispatchNodeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ParallelTranslateDispatchNodeOutput:
    """
    title: 并行翻译分发
    desc: 为每个目标语言启动翻译任务
    integrations: -
    """
    ctx = runtime.context
    
    # 为每个目标语言调用子图
    translated_results = []
    
    for target_language in state.target_languages:
        # 构建子图输入
        loop_input = LoopState(
            csv_data=state.csv_data,
            chinese_columns=state.chinese_columns,
            target_language=target_language,
            terminology_dict=state.terminology_dict
        )
        
        # 调用子图
        result: Dict[str, Any] = subgraph.invoke(loop_input)
        # 从子图结果中提取翻译数据
        translated_data = result.get('translated_data', {})
        translated_results.append(translated_data)
    
    # 调用合并节点
    merge_input = MergeTranslationsNodeInput(
        csv_data=state.csv_data,
        chinese_columns=state.chinese_columns,
        target_languages=state.target_languages,
        translated_results=translated_results
    )
    
    merge_output = merge_translations_node(merge_input, config, runtime)
    
    # 返回合并后的数据
    return ParallelTranslateDispatchNodeOutput(merged_data=merge_output.merged_data)
