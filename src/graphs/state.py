from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from utils.file.file import File


# 语言名称标准化映射表
LANGUAGE_MAPPING: Dict[str, str] = {
    # 英文
    "英文": "英文",
    "英语": "英文",
    "english": "英文",
    "English": "英文",
    "en": "英文",
    # 日文
    "日文": "日文",
    "日语": "日文",
    "japanese": "日文",
    "Japanese": "日文",
    "ja": "日文",
    # 韩文
    "韩文": "韩文",
    "韩语": "韩文",
    "korean": "韩文",
    "Korean": "韩文",
    "ko": "韩文",
    # 法文
    "法文": "法文",
    "法语": "法文",
    "french": "法文",
    "French": "法文",
    "fr": "法文",
    # 德文
    "德文": "德文",
    "德语": "德文",
    "german": "德文",
    "German": "德文",
    "de": "德文",
    # 西班牙文
    "西班牙文": "西班牙文",
    "西班牙语": "西班牙文",
    "spanish": "西班牙文",
    "Spanish": "西班牙文",
    "es": "西班牙文",
    # 俄文
    "俄文": "俄文",
    "俄语": "俄文",
    "russian": "俄文",
    "Russian": "俄文",
    "ru": "俄文",
    # 意大利文
    "意大利文": "意大利文",
    "意大利语": "意大利文",
    "italian": "意大利文",
    "Italian": "意大利文",
    "it": "意大利文",
}


def normalize_language_names(languages_str: str) -> List[str]:
    """
    标准化语言名称
    
    Args:
        languages_str: 用顿号分隔的语言字符串，如"英文、韩语、English"
    
    Returns:
        标准化后的语言列表，如["英文", "韩文"]
    """
    # 按顿号、逗号、空格等分隔符分割
    import re
    raw_languages = re.split(r'[、,，\s]+', languages_str.strip())
    
    # 标准化每个语言名称
    normalized_languages = []
    seen = set()  # 避免重复
    
    for lang in raw_languages:
        if not lang:
            continue
        # 从映射表中查找标准名称
        standard_name = LANGUAGE_MAPPING.get(lang, lang)
        # 避免重复
        if standard_name not in seen:
            normalized_languages.append(standard_name)
            seen.add(standard_name)
    
    return normalized_languages


# 知识库列名映射：标准语言名称 → 知识库列名
KNOWLEDGE_BASE_COLUMN_MAPPING: Dict[str, str] = {
    "英文": "英语",
    "日文": "日语",
    "韩文": "韩语",
    "法文": "法语",
    "德文": "德语",
    "西班牙文": "西班牙语",
    "俄文": "俄语",
    "意大利文": "意大利语",
    "葡萄牙文": "葡萄牙语",
    "阿拉伯文": "阿拉伯语",
}


def get_knowledge_base_column(language: str) -> Optional[str]:
    """
    获取知识库中对应的列名
    
    Args:
        language: 标准化的语言名称，如"英文"
    
    Returns:
        知识库列名，如"英语"
    """
    return KNOWLEDGE_BASE_COLUMN_MAPPING.get(language)


class GlobalState(BaseModel):
    """全局状态定义"""
    csv_file: File = Field(..., description="输入的CSV文件")
    target_languages: str = Field(..., description="目标语言，用顿号分隔，如'英文、韩语'")
    knowledge_base_url: Optional[str] = Field(default="多语言翻译工具知识库", description="通用多语言知识库名称")
    csv_data: dict = Field(default={}, description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(default=[], description="CSV中识别出的中文列名列表")
    terminology_dict: dict = Field(default={}, description="从知识库检索到的专词字典")
    merged_data: dict = Field(default={}, description="合并后的完整数据（包含原始列和所有翻译列）")
    output_csv_url: str = Field(default="", description="输出CSV文件的URL")


class GraphInput(BaseModel):
    """工作流输入"""
    csv_file: File = Field(..., description="包含中文列的CSV文件")
    target_languages: str = Field(..., description="目标语言，用顿号分隔，如'英文、韩语、日文'。支持多种写法：英文/英语/English均可")


class GraphOutput(BaseModel):
    """工作流输出"""
    output_csv_url: str = Field(..., description="生成的翻译CSV文件URL")


class ReadCSVNodeInput(BaseModel):
    """CSV读取节点输入"""
    csv_file: File = Field(..., description="输入的CSV文件")
    target_languages: str = Field(..., description="目标语言，用顿号分隔，如'英文、韩语'")


class ReadCSVNodeOutput(BaseModel):
    """CSV读取节点输出"""
    csv_data: dict = Field(..., description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(..., description="识别出的中文列名列表")
    target_languages: List[str] = Field(..., description="标准化后的目标语言列表")


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
    target_languages: List[str] = Field(..., description="目标语言列表")
    knowledge_base_url: Optional[str] = Field(default="多语言翻译工具知识库", description="专词知识库名称")


class QueryTerminologyNodeOutput(BaseModel):
    """术语查询节点输出"""
    terminology_dict: dict = Field(..., description="检索到的专词字典，格式：{中文词: {目标语言: 翻译}}")


class ParallelTranslateNodeInput(BaseModel):
    """并行翻译节点输入"""
    csv_data: dict = Field(..., description="CSV原始数据（DataFrame转字典格式）")
    chinese_columns: List[str] = Field(..., description="需要翻译的中文列名列表")
    target_language: str = Field(..., description="单个目标语言")
    terminology_dict: dict = Field(default={}, description="专词字典")
    batch_id: Optional[str] = Field(default=None, description="批次ID")
    batch_index: Optional[int] = Field(default=0, description="批次索引")
    total_batches: Optional[int] = Field(default=1, description="总批次数")
    batch_data: Optional[List[dict]] = Field(default=None, description="批次数据（行数据列表）")


class ParallelTranslateNodeOutput(BaseModel):
    """并行翻译节点输出"""
    target_language: str = Field(..., description="已翻译的目标语言")
    translated_data: dict = Field(..., description="该语言的翻译结果")
    batch_id: Optional[str] = Field(default=None, description="批次ID")
    batch_index: Optional[int] = Field(default=0, description="批次索引")
    translated_batch_data: Optional[List[dict]] = Field(default=None, description="翻译后的批次数据")


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
