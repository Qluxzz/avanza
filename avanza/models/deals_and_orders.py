from typing import Any, List
from pydantic import BaseModel


class Account(BaseModel):
    type: str
    name: str
    id: str


class DealsAndOrders(BaseModel):
    orders: List[Any]
    deals: List[Any]
    accounts: List[Account]
    reservedAmount: float
