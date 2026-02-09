from app.core.database import Base
from datetime import datetime, date, time
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Date, Time, CheckConstraint

class UserAccess(Base):
    __tablename__ = "user_access"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    access_date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    access_date: Mapped[date] = mapped_column(Date, nullable=False)
    access_time: Mapped[time] = mapped_column(Time, nullable=False)
    device_name: Mapped[str] = mapped_column(String, nullable=False)
    device_serial_number: Mapped[str] = mapped_column(String, nullable=False)
    person_name: Mapped[str] = mapped_column(String, nullable=False)
    card_no: Mapped[str] = mapped_column(String, nullable=False)
    direction: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('direction IN (1, 2)', name='check_direction'),
    )