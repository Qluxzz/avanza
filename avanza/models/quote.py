from pydantic import BaseModel


class Quote(BaseModel):
    buy: float
    sell: float
    last: float
    highest: float
    lowest: float
    change: float
    changePercent: float
    spread: float
    timeOfLast: int
    """ Unix timestamp (milliseconds) """
    totalValueTraded: float
    totalVolumeTraded: float
    updated: int
    """ Unix timestamp (milliseconds) """
    volumeWeightedAveragePrice: float
