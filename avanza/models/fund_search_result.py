from typing import List
from pydantic import BaseModel


class FundTopHit(BaseModel):
    changeSinceOneDay: float
    changeSinceThreeMonths: float
    changeSinceOneYear: float
    riskLevel: str
    rating: int
    managementFee: float
    risk: int
    name: str
    id: str
    tradable: bool
    tickerSymbol: str


class FundHit(BaseModel):
    instrumentType: str
    numberOfHits: int
    topHits: List[FundTopHit]


class FundSearchResult(BaseModel):
    totalNumberOfHits: int
    hits: List[FundHit]
