from decimal import Decimal

from sqlalchemy import String, Integer, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_name: Mapped[str] = mapped_column(String(255))
    tool_name: Mapped[str] = mapped_column(String(100))
    tool_code: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric)