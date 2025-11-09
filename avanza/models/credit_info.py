from pydantic import BaseModel
from typing import List, Optional

class CreditBreakPoint(BaseModel):
    interest: float
    upperLimit: float
    type: str

class CreditInfoEntry(BaseModel):
    accountId: str
    creditLimit: float
    ongoingOrders: Optional[float]
    currentUsedCredit: float
    currentInterest: float
    currentLeverage: float
    currentLtv: float
    currentTotalPotentialCollateralValue: float
    currentCreditBreakPoints: List[CreditBreakPoint]

class CreditInfo(BaseModel):
    creditInfos: List[CreditInfoEntry]