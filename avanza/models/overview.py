from typing import Any, List, Optional
from pydantic import BaseModel


class PerformanceInfo(BaseModel):
    value: float
    unit: str
    unitType: str
    decimalPrecision: int


class Performance(BaseModel):
    absolute: PerformanceInfo
    relative: PerformanceInfo


class SavingsGoalView(BaseModel):
    goalAmount: float
    percentCompleted: float
    sharedGoal: bool


class Balance(BaseModel):
    value: float
    unit: str
    unitType: str
    decimalPrecision: int


class Category(BaseModel):
    id: str
    name: str
    totalValue: Balance
    performance: dict[str, Performance]
    savingsGoalView: SavingsGoalView | None


class Name(BaseModel):
    defaultName: str
    userDefinedName: str | None


class Account(BaseModel):
    id: str
    categoryId: str
    balance: Balance
    profit: Performance
    type: str
    totalValue: Balance
    buyingPower: Balance
    buyingPowerWithoutCredit: Balance
    depositInterestRate: Balance | None
    loanInterestRate: Balance | None
    name: Name
    status: str
    errorStatus: str
    overmortgaged: Optional[bool]
    overdrawn: List[Any]
    performance: dict[str, Performance]
    settings: dict[str, bool]
    clearingAccountNumber: Optional[str]
    urlParameterId: str
    owner: bool


class Overview(BaseModel):
    categories: List[Category]
    accounts: List[Account]
    loans: List[Any]
