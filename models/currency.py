from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Currency(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    currency: str
    rate: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CurrencyCreate(SQLModel):
    currency: str
    rate: float


class CurrencyUpdate(SQLModel):
    currency: Optional[str] = None
    rate: Optional[float] = None


class CurrencyRead(SQLModel):
    id: int
    currency: str
    rate: float
    created_at: str
    updated_at: str


def to_read_model(obj: Currency) -> CurrencyRead:
    return CurrencyRead(
        id=obj.id,
        currency=obj.currency,
        rate=obj.rate,
        created_at=obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        updated_at=obj.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    )
