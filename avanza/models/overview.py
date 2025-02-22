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
    name: str
    totalValue: Balance
    buyingPower: Balance
    id: str
    profit: Performance
    performance: dict[str, Performance]
    savingsGoalView: SavingsGoalView | None
    sortOrder: int


class Name(BaseModel):
    defaultName: str
    userDefinedName: str | None


class Account(BaseModel):
    id: str
    categoryId: str
    balance: Balance
    profit: Performance
    totalAcquiredValue: Balance
    type: str
    totalValue: Balance
    buyingPower: Balance
    buyingPowerWithoutCredit: Balance
    interestRate: Balance | None
    depositInterestRate: Balance | None
    loanInterestRate: Balance | None
    name: Name
    status: str
    errorStatus: str
    overmortgaged: bool
    overdrawn: bool
    performance: dict[str, Performance]
    settings: dict[str, bool]
    clearingNumber: Optional[str]
    accountNumber: Optional[str]
    urlParameterId: str
    owner: bool


class AccountsSummary(BaseModel):
    performance: dict[str, Performance]
    buyingPower: Balance
    totalValue: Balance


class Overview(BaseModel):
    categories: List[Category]
    accounts: List[Account]
    loans: List[Any]
    accountsSummary: AccountsSummary
