from pydantic import BaseModel


class OrderBook(BaseModel):
    highestPrice: float
    lowestPrice: float
    change: float
    totalVolumeTraded: int
    updated: str
    """ Example 2011-11-11T11:11:11.504+0200 """
    currency: str
    """ ISO 4217 """
    priceThreeMonthsAgo: float
    flagCode: str
    """ ISO 3166-1 alpha-2 """
    lastPrice: float
    name: str
    id: str
    sellable: bool
    buyable: bool
    tradable: bool
    instrumentType: str
