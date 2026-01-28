from typing import Optional, List
from pydantic import BaseModel, Field
from utils.file.file import File


class GlobalState(BaseModel):
    """全局状态定义"""
    csv_file: File = Field(..., description="输入的CSV文件")
    target_languages: List[str] = Field(..., description="目标语言列表，如['英文', '日文']")
    csv_data: dict = Field(default={}, description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(default=[], description="CSV中识别出的中文列名列表")
    translated_data: dict = Field(default={}, description="翻译后的数据（DataFrame转字典格式）")
    output_csv_url: str = Field(default="", description="输出CSV文件的URL")


class GraphInput(BaseModel):
    """工作流输入"""
    csv_file: File = Field(..., description="包含中文列的CSV文件")
    target_languages: List[str] = Field(..., description="目标语言列表，如['英文', '日文', '韩文']")


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


class TranslateNodeInput(BaseModel):
    """翻译节点输入"""
    csv_data: dict = Field(..., description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(..., description="需要翻译的中文列名列表")
    target_languages: List[str] = Field(..., description="目标语言列表")


class TranslateNodeOutput(BaseModel):
    """翻译节点输出"""
    translated_data: dict = Field(..., description="翻译后的数据（DataFrame转字典格式）")


class GenerateCSVNodeInput(BaseModel):
    """生成CSV节点输入"""
    translated_data: dict = Field(..., description="翻译后的数据（DataFrame转字典格式）")


class GenerateCSVNodeOutput(BaseModel):
    """生成CSV节点输出"""
    output_csv_url: str = Field(..., description="生成的CSV文件URL")
