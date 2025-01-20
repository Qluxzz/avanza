import enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field, TypeAdapter


class SearchInstrumentType(enum.Enum):
    # Similar to InstrumentType, but results are uppercase
    STOCK = "STOCK"
    FUND = "FUND"
    BOND = "BOND"
    OPTION = "OPTION"
    FUTURE_FORWARD = "FUTURE_FORWARD"
    CERTIFICATE = "CERTIFICATE"
    WARRANT = "WARRANT"
    EXCHANGE_TRADED_FUND = "EXCHANGE_TRADED_FUND"
    INDEX = "INDEX"
    PREMIUM_BOND = "PREMIUM_BOND"
    SUBSCRIPTION_OPTION = "SUBSCRIPTION_OPTION"
    EQUITY_LINKED_BOND = "EQUITY_LINKED_BOND"
    CONVERTIBLE = "CONVERTIBLE"


class SearchPrice(BaseModel):
    # Most values are returned as strings.
    # null values are returned as "null"
    last: str | None
    currency: str | None
    todayChangePercent: str | None
    todayChangeValue: str | None
    todayChangeDirection: int
    threeMonthsAgoChangePercent: str | None
    threeMonthsAgoChangeDirection: int
    spread: str | None


class StockSector(BaseModel):
    # Most values are returned as strings.
    # null values are returned as "null"
    id: int
    level: int
    name: str
    englishName: str
    highlightedName: str | None


class FundTag(BaseModel):
    title: str
    category: str
    tagCategory: str
    highlightedTitle: str | None


class SearchResult(BaseModel):
    # type_: SearchInstrumentType|str = Field(alias='type')
    title: str
    highlightedTitle: str
    description: str
    highlightedDescription: str
    path: str | None
    urlSlugName: str
    tradeable: bool
    sellable: bool
    buyable: bool
    price: SearchPrice
    stockSectors: List[StockSector]
    fundTags: List[FundTag]
    marketPlaceName: str
    subType: Any | None
    highlightedSubType: str | None


SearchResults = TypeAdapter(List[SearchResult])
