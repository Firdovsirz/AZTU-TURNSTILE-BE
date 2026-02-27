from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class UserAccess(Base):
    __tablename__ = "user_access"

    id: Mapped[str] = mapped_column(String(256), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(256), nullable=False)
    access_date_time: Mapped[str] = mapped_column(String(256), nullable=False)
    access_date: Mapped[str] = mapped_column(String(256), nullable=False)
    access_time: Mapped[str] = mapped_column(String(256), nullable=False)
    device_name: Mapped[str] = mapped_column(String(256), nullable=False)
    device_serial_number: Mapped[str] = mapped_column(String(256), nullable=False)
    person_name: Mapped[str] = mapped_column(String(256), nullable=False)
    card_no: Mapped[str] = mapped_column(String(256), nullable=False)
    direction: Mapped[str] = mapped_column(String(256), nullable=False)
