from pydantic import BaseModel

from .historical_closing_prices import HistoricalClosingPrices
from .listing import Listing


class Quote(BaseModel):
    last: float
    change: float
    changePercent: float
    timeOfLast: int
    """ Unix timestamp (milliseconds) """
    totalValueTraded: float
    totalVolumeTraded: float
    updated: int
    """ Unix timestamp (milliseconds) """


class KeyIndicators(BaseModel):
    leverage: float
    productLink: str
    """ URL """
    numberOfOwners: int
    isAza: bool


class CertificateInfo(BaseModel):
    orderbookId: str
    name: str
    isin: str
    tradable: str
    """ Example: BUYABLE_AND_SELLABLE """
    listing: Listing
    historicalClosingPrices: HistoricalClosingPrices
    keyIndicators: KeyIndicators
    quote: Quote
    type: str
    """ CERTIFICATE """
