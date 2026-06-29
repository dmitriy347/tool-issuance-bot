from datetime import date

from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(100))
    contract_number: Mapped[str] = mapped_column(String(100))
    contract_date: Mapped[date] = mapped_column(Date)
    document_type: Mapped[str] = mapped_column(String(100))
    id_series: Mapped[str] = mapped_column(String(10))
    id_number: Mapped[str] = mapped_column(String(20))
    id_issued_date: Mapped[date] = mapped_column(Date)
    issued_by: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))

