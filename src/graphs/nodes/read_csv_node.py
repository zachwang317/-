import pandas as pd
import re
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import ReadCSVNodeInput, ReadCSVNodeOutput
from utils.file.file import FileOps


def read_csv_node(state: ReadCSVNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> ReadCSVNodeOutput:
    """
    title: CSV读取与中文列识别
    desc: 读取CSV文件，识别包含中文内容的列
    integrations: 文件处理
    """
    ctx = runtime.context
    
    # 1. 读取CSV文件内容
    csv_content = FileOps.extract_text(state.csv_file)
    
    # 2. 使用pandas读取CSV（从字符串）
    # 需要先将文本保存到临时文件，pandas才能正确读取
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        temp_file = f.name
    
    try:
        # 读取CSV文件
        df = pd.read_csv(temp_file, encoding='utf-8')
        
        # 3. 识别包含中文的列
        chinese_columns = []
        
        # 定义中文正则表达式
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        
        # 检查每一列
        for column in df.columns:
            # 获取该列的值（转为字符串）
            column_values = df[column].astype(str)
            
            # 检查是否有任何值包含中文
            has_chinese = bool(column_values.apply(lambda x: bool(chinese_pattern.search(x))).any())
            
            if has_chinese:
                chinese_columns.append(column)
        
        # 4. 将DataFrame转换为字典格式（便于后续处理）
        # 使用orient='records'格式，每行一个字典
        csv_data_dict = df.to_dict(orient='records')
        
        # 同时也保存列信息
        csv_data = {
            'columns': df.columns.tolist(),
            'data': csv_data_dict
        }
        
        return ReadCSVNodeOutput(
            csv_data=csv_data,
            chinese_columns=chinese_columns
        )
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)
