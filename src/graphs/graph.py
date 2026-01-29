from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)
from graphs.nodes.read_csv_node import read_csv_node
from graphs.nodes.query_terminology_node import query_terminology_node
from graphs.nodes.parallel_translate_dispatch_node import parallel_translate_dispatch_node
from graphs.nodes.generate_csv_node import generate_csv_node

# 创建状态图，指定工作流的入参和出参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("read_csv", read_csv_node)
builder.add_node("query_terminology", query_terminology_node)
builder.add_node("parallel_translate_dispatch", parallel_translate_dispatch_node, metadata={"type": "looparray"})
builder.add_node("generate_csv", generate_csv_node)

# 设置入口点
builder.set_entry_point("read_csv")

# 添加边（线性流程）
builder.add_edge("read_csv", "query_terminology")
builder.add_edge("query_terminology", "parallel_translate_dispatch")
builder.add_edge("parallel_translate_dispatch", "generate_csv")
builder.add_edge("generate_csv", END)

# 编译图
main_graph = builder.compile()
