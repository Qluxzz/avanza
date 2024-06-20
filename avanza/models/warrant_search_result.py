from typing import List
from pydantic import BaseModel


class WarrantTopHit(BaseModel):
    currency: str
    """ ISO 4217 """
    changePercent: float
    lastPrice: float
    name: str
    id: str
    flagCode: str
    """ ISO 3166-1 alpha-2 """
    tradable: bool
    tickerSymbol: str


class WarrantHit(BaseModel):
    instrumentType: str
    numberOfHits: int
    topHits: List[WarrantTopHit]


class WarrantSearchResult(BaseModel):
    totalNumberOfHits: int
    hits: List[WarrantHit]
