from typing import Optional
from pydantic import BaseModel

from .listing import Listing
from .historical_closing_prices import HistoricalClosingPrices
from .underlying import Underlying


class KeyIndicators(BaseModel):
    parity: float
    barrierLevel: float
    financingLevel: float
    direction: str
    """ Example value: "Kort" """
    numberOfOwners: float
    subType: str
    """ Example value: "MINI_FUTURE" """


class Quote(BaseModel):
    last: float
    change: float
    changePercent: float
    timeOfLast: int
    """ unix timestamp (milliseconds) """
    totalValueTraded: float
    totalVolumeTraded: int
    updated: int
    """ unix timestamp (milliseconds) """


class WarrantInfo(BaseModel):
    orderbookId: str
    name: str
    isin: str
    tradable: str
    listing: Listing
    historicalClosingPrices: HistoricalClosingPrices
    keyIndicators: KeyIndicators
    quote: Quote
    type: str
    """ WARRANT """
    underlying: Optional[Underlying] = None
