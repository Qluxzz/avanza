from typing import Any, List
from pydantic import BaseModel
from .underlying import Underlying


class Documents(BaseModel):
    kid: str
    prospectus: str


class Fee(BaseModel):
    totalMonetaryFee: float
    totalPercentageFee: float


class Order(BaseModel):
    price: float
    priceString: str
    volume: int


class OrderDepthLevels(BaseModel):
    buySide: Order
    sellSide: Order


class OrderDepth(BaseModel):
    levels: List[OrderDepthLevels]
    receivedTime: int
    """ Unix timestamp (milliseconds) """
    marketMakerLevelInBid: int
    marketMakerLevelInAsk: int


class CertificateDetails(BaseModel):
    underlying: Underlying
    assetCategory: str
    category: str
    subCategory: str
    issuer: str
    direction: str
    leverage: float
    documents: Documents
    fee: Fee
    trades: List[Any]
    orderDepth: OrderDepth
    brokerTradeSummaries: List[Any]
    collateralValue: float
