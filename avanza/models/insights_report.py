from typing import Any, List
from pydantic import BaseModel


class TotalOutcome(BaseModel):
    total: float
    development: float
    dividends: float


class Link(BaseModel):
    type: str
    flagCode: str
    """ ISO 3166-1 alpha-2 """
    orderbookId: str
    urlDisplayName: str
    linkDisplay: str
    shortLinkDisplay: str
    tradeable: bool
    sellable: bool
    buyable: bool


class PositionListItemOutcome(BaseModel):
    total: float
    development: float
    balanceDevelopments: List[Any]
    totalDevelopmentInPercent: float
    stake: float
    totalTurnover: int
    transactions: List[Any]
    transactionTotals: List[Any]
    totalBuyAmount: int
    totalSellAmount: int
    totalOtherAmount: int
    developmentPartOfTotalDevelopmentInPercent: float
    dividendsPartOfTotalDevelopmentInPercent: float
    dividends: int


class PositionSummaryListItem(BaseModel):
    isin: str
    shortName: str
    link: Link
    outcome: PositionListItemOutcome
    currentPosition: float
    startValue: float
    endValue: float


class PositionSummaryOutcome(BaseModel):
    total: float
    development: float
    balanceDevelopments: List[Any]
    dividends: int


class PositionSummary(BaseModel):
    instrumentType: str
    outcome: PositionSummaryOutcome
    positions: List[PositionSummaryListItem]


class BestAndWorst(BaseModel):
    bestPositions: List[PositionSummary]
    worstPositions: List[PositionSummary]


class DevelopmentResponse(BaseModel):
    totalOutcome: TotalOutcome
    unknownPositionDevelopments: List[Any]
    totalOutcomeForUnknownDevelopments: TotalOutcome
    hasUnlistedInstrument: bool
    bestAndWorst: BestAndWorst


class ChartData(BaseModel):
    month: int
    year: int
    allTransactions: float
    deposit: float
    withdrawal: float
    autogiro: float


class TransactionsResponse(BaseModel):
    chartData: List[ChartData]
    allTransactions: List[Any]
    totalAutogiro: int
    totalAll: int
    totalDeposits: int
    totalWithdraws: int


class TotalDevelopment(BaseModel):
    startValue: float
    totalChange: float
    currentValue: float


class OtherTransactions(BaseModel):
    otherTransactionsGroups: List[Any]
    total: int


class InsightsReport(BaseModel):
    developmentResponse: DevelopmentResponse
    transactionsResponse: TransactionsResponse
    totalDevelopment: TotalDevelopment
    otherTransactions: OtherTransactions
    fromDate: str
    """ YYYY-MM-DD """
    toDate: str
    """ YYYY-MM-DD """
    aggregatedPerformance: float
