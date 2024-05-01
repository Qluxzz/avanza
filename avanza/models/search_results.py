from typing import List
from pydantic import BaseModel


class SearchHit(BaseModel):
    changePercent: float
    currency: str
    """ ISO 4217 """
    lastPrice: float
    flagCode: str
    """ ISO 3166-1 alpha-2 """
    tradable: bool
    tickerSymbol: str
    name: str
    id: str


class SearchResult(BaseModel):
    instrumentType: str
    numberOfHits: int
    topHits: List[SearchHit]


class SearchResults(BaseModel):
    totalNumberOfHits: int
