from typing import Optional
from datetime import datetime
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, CheckConstraint, func


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_no: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    father_name: Mapped[str] = mapped_column(String)
    fin_code: Mapped[str] = mapped_column(String(7))
    gender: Mapped[int] = mapped_column(Integer, nullable=False)
    identification: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    group_number: Mapped[Optional[str]] = mapped_column(String)
    group: Mapped[int] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint('gender IN (0, 1, 2)', name='check_gender'),
    )

    # gender 1 - male
    # gender 2 - female
    # gender 3 - not mentioned