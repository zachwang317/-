from typing import Optional, List
from pydantic import BaseModel, Field
from utils.file.file import File


class GlobalState(BaseModel):
    """全局状态定义"""
    csv_file: File = Field(..., description="输入的CSV文件")
    target_languages: List[str] = Field(..., description="目标语言列表，如['英文', '日文']")
    knowledge_base_url: Optional[str] = Field(default=None, description="专词知识库的URL（可选）")
    csv_data: dict = Field(default={}, description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(default=[], description="CSV中识别出的中文列名列表")
    terminology_dict: dict = Field(default={}, description="从知识库检索到的专词字典")
    merged_data: dict = Field(default={}, description="合并后的完整数据（包含原始列和所有翻译列）")
    output_csv_url: str = Field(default="", description="输出CSV文件的URL")


class GraphInput(BaseModel):
    """工作流输入"""
    csv_file: File = Field(..., description="包含中文列的CSV文件")
    target_languages: List[str] = Field(..., description="目标语言列表，如['英文', '日文', '韩文']")
    knowledge_base_url: Optional[str] = Field(default=None, description="专词知识库的URL（可选），用于提升翻译准确率")


class GraphOutput(BaseModel):
    """工作流输出"""
    output_csv_url: str = Field(..., description="生成的翻译CSV文件URL")


class ReadCSVNodeInput(BaseModel):
    """CSV读取节点输入"""
    csv_file: File = Field(..., description="输入的CSV文件")


class ReadCSVNodeOutput(BaseModel):
    """CSV读取节点输出"""
    csv_data: dict = Field(..., description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(..., description="识别出的中文列名列表")


class GenerateCSVNodeInput(BaseModel):
    """生成CSV节点输入"""
    merged_data: dict = Field(..., description="合并后的完整数据（DataFrame转字典格式）")


class GenerateCSVNodeOutput(BaseModel):
    """生成CSV节点输出"""
    output_csv_url: str = Field(..., description="生成的CSV文件URL")


class QueryTerminologyNodeInput(BaseModel):
    """术语查询节点输入"""
    csv_data: dict = Field(..., description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(..., description="需要翻译的中文列名列表")
    knowledge_base_url: Optional[str] = Field(default=None, description="专词知识库的URL")


class QueryTerminologyNodeOutput(BaseModel):
    """术语查询节点输出"""
    terminology_dict: dict = Field(..., description="检索到的专词字典，格式：{中文词: {目标语言: 翻译}}")


class ParallelTranslateNodeInput(BaseModel):
    """并行翻译节点输入"""
    csv_data: dict = Field(..., description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(..., description="需要翻译的中文列名列表")
    target_language: str = Field(..., description="单个目标语言")
    terminology_dict: dict = Field(default={}, description="专词字典")


class ParallelTranslateNodeOutput(BaseModel):
    """并行翻译节点输出"""
    target_language: str = Field(..., description="已翻译的目标语言")
    translated_data: dict = Field(..., description="该语言的翻译结果")


class MergeTranslationsNodeInput(BaseModel):
    """合并翻译结果节点输入"""
    csv_data: dict = Field(..., description="CSV原始数据")
    chinese_columns: List[str] = Field(..., description="中文列名列表")
    target_languages: List[str] = Field(..., description="目标语言列表")
    translated_results: List[dict] = Field(..., description="所有语言的翻译结果列表")


class MergeTranslationsNodeOutput(BaseModel):
    """合并翻译结果节点输出"""
    merged_data: dict = Field(..., description="合并后的完整数据，包含原始列和所有翻译列")


class ParallelTranslateDispatchNodeInput(BaseModel):
    """并行翻译分发节点输入"""
    csv_data: dict = Field(..., description="CSV原始数据")
    chinese_columns: List[str] = Field(..., description="中文列名列表")
    target_languages: List[str] = Field(..., description="目标语言列表")
    terminology_dict: dict = Field(default={}, description="专词字典")


class ParallelTranslateDispatchNodeOutput(BaseModel):
    """并行翻译分发节点输出"""
    merged_data: dict = Field(..., description="合并后的完整数据")
