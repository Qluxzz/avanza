from typing import List
from pydantic import BaseModel, Field


class Ohlc(BaseModel):
    timestamp: int
    """ Unix timestamp (millisecond) """
    open: float
    close: float
    low: float
    high: float
    totalVolumeTraded: int


class Resolution(BaseModel):
    chartResolution: str
    availableResolutions: List[str]


class Metadata(BaseModel):
    resolution: Resolution


class ChartData(BaseModel):
    ohlc: List[Ohlc]
    metadata: Metadata
    from_: str = Field(..., alias="from")
    to: str
    previousClosingPrice: float
