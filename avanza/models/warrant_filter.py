from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class WarrantUnderlying(BaseModel):
    name: str
    orderbookId: str
    instrumentType: str
    """ Example value: "INDEX" """
    countryCode: str


class FilteredWarrant(BaseModel):
    orderbookId: str
    countryCode: str
    name: str
    direction: str
    """ Example value: "long" or "short" """
    issuer: str
    """ Example value: "Morgan Stanley" """
    subType: str
    """ Example value: "KNOCK_OUT" """
    hasPosition: bool
    underlyingInstrument: WarrantUnderlying
    totalValueTraded: float
    stopLoss: float
    financingLevel: float
    """ The barrier level, matching keyIndicators.barrierLevel from get_warrant_info """
    spread: float
    """
    Relative spread as a fraction, not a percentage and not an absolute price.
    A buy of 1.85 against a sell of 1.87 is reported as 0.0108, i.e. 1.08%.
    """
    leverage: float
    buyPrice: float
    sellPrice: float
    oneDayChangePercent: Optional[float] = None
    """ Absent for instruments without a previous close to compare against """


class FilterOption(BaseModel):
    value: str
    displayName: str
    numberOfOrderbooks: int


class CategoryFilterOption(BaseModel):
    value: str
    """ Pipe-delimited path, e.g. "warrant_asset|equity|root" """
    displayName: str
    numberOfOrderbooks: str
    """
    A string here, unlike every other filter option, where it is an integer.
    Nests up to three levels deep via children.
    """
    children: Optional[List["CategoryFilterOption"]] = None


class WarrantFilterOptions(BaseModel):
    issuers: List[FilterOption]
    underlyingInstruments: List[FilterOption]
    endDates: List[FilterOption]
    subTypes: List[FilterOption]
    directions: List[FilterOption]
    categories: List[CategoryFilterOption]
    exposures: List[FilterOption]


class WarrantPagination(BaseModel):
    offset: int
    limit: int


class WarrantSortBy(BaseModel):
    field: str
    order: str


class WarrantFilterResult(BaseModel):
    warrants: List[FilteredWarrant]
    filter: Dict[str, Any]
    """ The filter as the server understood it, echoed back """
    pagination: WarrantPagination
    sortBy: WarrantSortBy
    totalNumberOfOrderbooks: int
    """ Total matching the filter, not the number returned -- use it to paginate """
    filterOptions: WarrantFilterOptions
