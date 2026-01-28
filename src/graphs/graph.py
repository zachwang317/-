from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)
from graphs.nodes.read_csv_node import read_csv_node
from graphs.nodes.translate_node import translate_node
from graphs.nodes.generate_csv_node import generate_csv_node

# 创建状态图，指定工作流的入参和出参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("read_csv", read_csv_node)
builder.add_node("translate", translate_node, metadata={"type": "agent", "llm_cfg": "config/translate_llm_cfg.json"})
builder.add_node("generate_csv", generate_csv_node)

# 设置入口点
builder.set_entry_point("read_csv")

# 添加边（线性流程）
builder.add_edge("read_csv", "translate")
builder.add_edge("translate", "generate_csv")
builder.add_edge("generate_csv", END)

# 编译图
main_graph = builder.compile()
