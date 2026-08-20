from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: Decimal
    status: str
    expires_at: datetime | None = None
    used_at: datetime | None = None
    created_at: datetime

    @field_serializer("amount")
    def _ser_amount(self, v: Decimal) -> float:
        return float(v)