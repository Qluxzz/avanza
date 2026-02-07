from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator

from avanza.models.quote import Quote


class MarketDataQuote(Quote):
    spread: float | None = None
    timeOfLast: datetime  # override ms -> datetime
    updated: datetime  # override ms -> datetime

    @field_validator("timeOfLast", "updated", mode="before")
    @classmethod
    def parse_dt(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v


class OrderDepthSide(BaseModel):
    price: float
    volume: int
    priceString: str


class OrderDepthLevel(BaseModel):
    buySide: OrderDepthSide
    sellSide: OrderDepthSide


class OrderDepth(BaseModel):
    receivedTime: int
    levels: List[OrderDepthLevel]
    marketMakerExpected: bool


class MarketData(BaseModel):
    quote: MarketDataQuote
    orderDepth: OrderDepth
    trades: List[dict]
