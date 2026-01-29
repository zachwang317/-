from typing import List, Dict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from graphs.state import GlobalState
from graphs.nodes.parallel_translate_node import parallel_translate_node


# 定义子图的状态（用于单个语言翻译）
class LoopState(BaseModel):
    """子图状态定义"""
    csv_data: dict = Field(..., description="CSV原始数据")
    chinese_columns: List[str] = Field(..., description="中文列名列表")
    target_language: str = Field(..., description="当前处理的目标语言")
    terminology_dict: dict = Field(default={}, description="专词字典")
    translated_data: dict = Field(default={}, description="翻译结果")


# 创建子图（单个语言翻译）
loop_builder = StateGraph(LoopState, input_schema=LoopState, output_schema=LoopState)

# 添加翻译节点
loop_builder.add_node("parallel_translate", parallel_translate_node, metadata={"type": "agent", "llm_cfg": "config/translate_llm_cfg.json"})

# 设置入口点
loop_builder.set_entry_point("parallel_translate")

# 设置结束点
loop_builder.add_edge("parallel_translate", END)

# 编译子图
subgraph = loop_builder.compile()
