from typing import Any, List, Literal, Union
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
    totalDevelopmentInPercent: Union[float, Literal["-"]]
    stake: float
    totalTurnover: float
    transactions: List[Any]
    transactionTotals: List[Any]
    totalBuyAmount: float
    totalSellAmount: float
    totalOtherAmount: float
    developmentPartOfTotalDevelopmentInPercent: Union[float, Literal["-"]]
    dividendsPartOfTotalDevelopmentInPercent: Union[float, Literal["-"]]
    dividends: float


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
    dividends: float


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
    totalAutogiro: float
    totalAll: float
    totalDeposits: float
    totalWithdraws: float


class TotalDevelopment(BaseModel):
    startValue: float
    totalChange: float
    currentValue: float


class OtherTransactions(BaseModel):
    otherTransactionsGroups: List[Any]
    total: float


class InsightsReport(BaseModel):
    developmentResponse: DevelopmentResponse
    transactionsResponse: TransactionsResponse
    totalDevelopment: TotalDevelopment
    otherTransactions: OtherTransactions
    fromDate: str
    """ YYYY-MM-DD """
    toDate: str
    """ YYYY-MM-DD """
    aggregatedPerformance: Union[float, Literal["-"]]
