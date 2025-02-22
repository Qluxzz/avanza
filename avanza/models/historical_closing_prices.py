from typing import Optional
from pydantic import BaseModel


class HistoricalClosingPrices(BaseModel):
    oneDay: Optional[float] = None
    oneWeek: Optional[float] = None
    oneMonth: Optional[float] = None
    threeMonths: Optional[float] = None
    startOfYear: Optional[float] = None
    oneYear: Optional[float] = None
    threeYears: Optional[float] = None
    fiveYears: Optional[float] = None
    tenYears: Optional[float] = None
    start: float
    startDate: str
    """ YYYY-MM-DD """
