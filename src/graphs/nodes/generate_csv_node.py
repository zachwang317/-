import os
import pandas as pd
import uuid
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk.s3 import S3SyncStorage
from graphs.state import GenerateCSVNodeInput, GenerateCSVNodeOutput


def generate_csv_node(state: GenerateCSVNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> GenerateCSVNodeOutput:
    """
    title: 生成并上传CSV
    desc: 将翻译后的数据生成CSV文件，并上传到对象存储
    integrations: 对象存储
    """
    ctx = runtime.context
    
    # 1. 初始化对象存储客户端
    storage = S3SyncStorage(
        endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
        access_key="",
        secret_key="",
        bucket_name=os.getenv("COZE_BUCKET_NAME"),
        region="cn-beijing",
    )
    
    # 2. 将字典数据转换为DataFrame
    data_rows = state.merged_data['data']
    df = pd.DataFrame(data_rows)
    
    # 3. 生成CSV文件到临时目录
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 生成唯一的文件名
    file_name = f"translated_{uuid.uuid4().hex[:8]}.csv"
    temp_file_path = os.path.join(temp_dir, file_name)
    
    # 保存为CSV文件
    df.to_csv(temp_file_path, index=False, encoding='utf-8-sig')
    
    # 4. 上传到对象存储
    try:
        # 读取文件内容
        with open(temp_file_path, 'rb') as f:
            file_content = f.read()
        
        # 上传文件
        file_key = storage.upload_file(
            file_content=file_content,
            file_name=file_name,
            content_type="text/csv"
        )
        
        # 5. 生成签名URL（有效期1小时）
        signed_url = storage.generate_presigned_url(
            key=file_key,
            expire_time=3600
        )
        
        return GenerateCSVNodeOutput(output_csv_url=signed_url)
    except Exception as e:
        raise Exception(f"上传CSV文件失败: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
