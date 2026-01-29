from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from storage.database.shared.model import 翻译知识库


class TranslationKnowledgeManager:
    """翻译知识库管理器：根据中文术语查询多语言翻译"""

    # 语言名称到数据库列名的映射
    LANGUAGE_COLUMN_MAPPING: Dict[str, str] = {
        "英文": "英语",
        "英语": "英语",
        "english": "英语",
        "English": "英语",
        "en": "英语",
        "日文": "日语",
        "日语": "日语",
        "japanese": "日语",
        "Japanese": "日语",
        "ja": "日语",
        "韩文": "韩语",
        "韩语": "韩语",
        "korean": "韩语",
        "Korean": "韩语",
        "ko": "韩语",
        "法文": "法语",
        "法语": "法语",
        "french": "法语",
        "French": "法语",
        "fr": "法语",
        "德文": "德语",
        "德语": "德语",
        "german": "德语",
        "German": "德语",
        "de": "德语",
        "西班牙文": "西班牙语",
        "西班牙语": "西班牙语",
        "spanish": "西班牙语",
        "Spanish": "西班牙语",
        "es": "西班牙语",
        "俄文": "俄语",
        "俄语": "俄语",
        "russian": "俄语",
        "Russian": "俄语",
        "ru": "俄语",
        "意大利文": "意大利语",
        "意大利语": "意大利语",
        "italian": "意大利语",
        "Italian": "意大利语",
        "it": "意大利语",
        "葡萄牙文": "葡萄牙语",
        "葡萄牙语": "葡萄牙语",
        "portuguese": "葡萄牙语",
        "Portuguese": "葡萄牙语",
        "pt": "葡萄牙语",
    }

    def get_translation(
        self,
        db: Session,
        chinese_term: str,
        target_language: str
    ) -> Optional[str]:
        """
        查询单个中文术语的指定语言翻译

        Args:
            db: 数据库会话
            chinese_term: 中文术语
            target_language: 目标语言（如"英文"、"日文"）

        Returns:
            翻译结果，如果不存在或数据库中没有该语言列则返回None
        """
        # 标准化语言名称并获取列名
        column_name = self._get_column_name(target_language)
        if not column_name:
            return None

        # 查询数据库
        result = db.query(翻译知识库).filter(翻译知识库.中文 == chinese_term).first()
        if not result:
            return None

        # 动态获取对应列的值
        translation = getattr(result, column_name, None)
        return translation

    def get_translations_batch(
        self,
        db: Session,
        chinese_terms: List[str],
        target_language: str
    ) -> Dict[str, Optional[str]]:
        """
        批量查询中文术语的指定语言翻译

        Args:
            db: 数据库会话
            chinese_terms: 中文术语列表
            target_language: 目标语言（如"英文"、"日文"）

        Returns:
            字典：{中文术语: 翻译结果}，如果翻译不存在则值为None
        """
        # 标准化语言名称并获取列名
        column_name = self._get_column_name(target_language)
        if not column_name:
            return {term: None for term in chinese_terms}

        # 批量查询
        results = db.query(翻译知识库).filter(翻译知识库.中文.in_(chinese_terms)).all()
        
        # 构建结果字典
        translations = {term: None for term in chinese_terms}
        for result in results:
            translation = getattr(result, column_name, None)
            translations[result.中文] = translation

        return translations

    def _get_column_name(self, language: str) -> Optional[str]:
        """
        根据语言名称获取数据库列名

        Args:
            language: 语言名称（如"英文"、"English"、"en"）

        Returns:
            数据库列名（如"英语"、"日语"），如果不存在则返回None
        """
        return self.LANGUAGE_COLUMN_MAPPING.get(language)

    def get_available_languages(self, db: Session) -> List[str]:
        """
        获取数据库中可用的语言列名

        Args:
            db: 数据库会话

        Returns:
            可用的语言列名列表（如["英语", "日语", "韩语"]）
        """
        # 获取表的所有列名
        inspector = db.get_bind()
        from sqlalchemy import inspect
        columns = inspect(inspector).get_columns(翻译知识库.__tablename__)
        
        # 排除主键"中文"，只返回语言列
        return [col['name'] for col in columns if col['name'] != '中文']

    def add_translation(
        self,
        db: Session,
        chinese_term: str,
        translations: Dict[str, Optional[str]]
    ) -> 翻译知识库:
        """
        添加或更新翻译术语

        Args:
            db: 数据库会话
            chinese_term: 中文术语
            translations: 翻译字典 {语言: 翻译结果}，如{"英语": "Apple", "日语": "リンゴ"}

        Returns:
            创建或更新后的翻译知识库对象
        """
        # 查询是否存在
        existing = db.query(翻译知识库).filter(翻译知识库.中文 == chinese_term).first()
        
        if existing:
            # 更新
            for lang, translation in translations.items():
                if hasattr(existing, lang):
                    setattr(existing, lang, translation)
            db.add(existing)
            try:
                db.commit()
                db.refresh(existing)
                return existing
            except Exception as e:
                db.rollback()
                raise Exception(f"更新翻译失败: {e}")
        else:
            # 创建
            data = {"中文": chinese_term}
            data.update(translations)
            new_term = 翻译知识库(**data)
            db.add(new_term)
            try:
                db.commit()
                db.refresh(new_term)
                return new_term
            except Exception as e:
                db.rollback()
                raise Exception(f"添加翻译失败: {e}")
