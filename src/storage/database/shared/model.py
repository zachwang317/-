from coze_coding_dev_sdk.database import Base

from sqlalchemy import PrimaryKeyConstraint, String
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

class 翻译知识库(Base):
    __tablename__ = '翻译知识库'
    __table_args__ = (
        PrimaryKeyConstraint('中文', name='翻译知识库_pkey'),
    )

    中文: Mapped[str] = mapped_column(String, primary_key=True)
    英语: Mapped[Optional[str]] = mapped_column(String)
    日语: Mapped[Optional[str]] = mapped_column(String)
    韩语: Mapped[Optional[str]] = mapped_column(String)
