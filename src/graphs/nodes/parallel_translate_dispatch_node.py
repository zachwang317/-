import uuid
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    GlobalState,
    ParallelTranslateDispatchNodeInput,
    ParallelTranslateDispatchNodeOutput,
    ParallelTranslateNodeInput,
    ParallelTranslateNodeOutput,
    MergeTranslationsNodeInput,
    MergeTranslationsNodeOutput
)
from graphs.nodes.merge_translations_node import merge_translations_node


def parallel_translate_dispatch_node(
    state: ParallelTranslateDispatchNodeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ParallelTranslateDispatchNodeOutput:
    """
    title: 并行翻译分发（批次化）
    desc: 将数据按行数拆分成多个批次，并行处理每个批次的翻译
    integrations: -
    """
    ctx = runtime.context
    
    # 配置批次大小（每批次处理的行数）
    BATCH_SIZE = 20  # 每批处理20行，可根据实际情况调整
    
    # 为每个目标语言处理翻译
    all_translated_results = []
    
    for target_language in state.target_languages:
        # 1. 提取需要翻译的数据
        rows_data = state.csv_data.get('data', [])
        
        # 2. 按行数拆分成多个批次
        batches = []
        for i in range(0, len(rows_data), BATCH_SIZE):
            batch_data = rows_data[i:i + BATCH_SIZE]
            batches.append({
                'batch_id': str(uuid.uuid4()),
                'batch_index': i // BATCH_SIZE,
                'total_batches': (len(rows_data) + BATCH_SIZE - 1) // BATCH_SIZE,
                'data': batch_data
            })
        
        print(f"[INFO] 目标语言: {target_language}, 总行数: {len(rows_data)}, 批次数: {len(batches)}, 每批次: {BATCH_SIZE}行")
        
        # 3. 并行处理所有批次
        translated_batches = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:  # 最多3个并发任务
            # 创建所有翻译任务
            future_to_batch = {}
            for batch in batches:
                # 构建批次输入
                batch_input = ParallelTranslateNodeInput(
                    csv_data=state.csv_data,
                    chinese_columns=state.chinese_columns,
                    target_language=target_language,
                    terminology_dict=state.terminology_dict,
                    batch_id=batch['batch_id'],
                    batch_index=batch['batch_index'],
                    total_batches=batch['total_batches'],
                    batch_data=batch['data']
                )
                
                # 提交任务到线程池
                future = executor.submit(
                    translate_batch,
                    batch_input,
                    config,
                    runtime
                )
                future_to_batch[future] = batch
            
            # 收集结果
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    result = future.result()
                    translated_batches.append(result)
                    print(f"[INFO] 批次 {result.batch_index + 1}/{result.total_batches} 完成: {target_language}")
                except Exception as e:
                    print(f"[ERROR] 批次 {batch['batch_index']} 失败: {str(e)}")
                    # 使用原始数据作为fallback
                    translated_batches.append({
                        'batch_index': batch['batch_index'],
                        'translated_batch_data': batch['data'],
                        'error': str(e)
                    })
        
        # 4. 合并所有批次的翻译结果（按批次索引排序）
        translated_batches.sort(key=lambda x: x.get('batch_index', 0))
        
        # 拼接所有批次的数据
        all_translated_rows = []
        for batch in translated_batches:
            all_translated_rows.extend(batch.get('translated_batch_data', []))
        
        # 5. 构建该语言的完整翻译数据
        translated_data = {
            'columns': state.csv_data.get('columns', []),
            'data': all_translated_rows,
            'target_language': target_language
        }
        
        all_translated_results.append(translated_data)
        print(f"[INFO] 语言 {target_language} 翻译完成，总行数: {len(all_translated_rows)}")
    
    # 6. 调用合并节点，合并所有语言的结果
    merge_input = MergeTranslationsNodeInput(
        csv_data=state.csv_data,
        chinese_columns=state.chinese_columns,
        target_languages=state.target_languages,
        translated_results=all_translated_results
    )
    
    merge_output = merge_translations_node(merge_input, config, runtime)
    
    print(f"[INFO] 所有翻译完成，最终合并数据行数: {len(merge_output.merged_data.get('data', []))}")
    
    # 返回合并后的数据
    return ParallelTranslateDispatchNodeOutput(merged_data=merge_output.merged_data)


def translate_batch(
    batch_input: ParallelTranslateNodeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> Dict[str, Any]:
    """
    处理单个批次的翻译
    
    Args:
        batch_input: 批次输入数据
        config: RunnableConfig
        runtime: Runtime[Context]
    
    Returns:
        批次翻译结果字典
    """
    # 调用翻译节点
    result = parallel_translate_node(batch_input, config, runtime)
    
    return {
        'batch_id': result.batch_id,
        'batch_index': result.batch_index,
        'translated_batch_data': result.translated_batch_data
    }
