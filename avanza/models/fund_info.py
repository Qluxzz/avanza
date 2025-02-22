from typing import List, Optional
from pydantic import BaseModel


class ChartData(BaseModel):
    name: str
    y: float
    type: str
    currency: str
    """ ISO 4217 """
    countryCode: Optional[str]
    """ ISO 3166-1 alpha-2 """
    isin: Optional[str]
    orderbookId: Optional[str]


class FundManager(BaseModel):
    name: str
    startDate: str
    """ YYYY-MM-DD """


class AdminCompany(BaseModel):
    name: str
    country: str
    url: str


class ProductInvolvement(BaseModel):
    product: str
    productDescription: str
    value: float


class FundRatingView(BaseModel):
    date: str
    """ Example: 2011-11-11T11:11:11 """
    fundRatingType: str
    """ Example: "THREE_YEARS" """
    fundRating: int


class FundInfo(BaseModel):
    isin: str
    name: str
    description: str
    nav: float
    navDate: str
    """ Example: 2011-11-11T11:11:11 """
    currency: str
    """ ISO 4217 """
    rating: int
    productFee: float
    managementFee: float
    risk: int
    riskText: str
    developmentOneDay: float
    developmentOneMonth: float
    developmentThreeMonths: float
    developmentSixMonths: float
    developmentOneYear: float
    developmentThisYear: float
    developmentThreeYears: float
    developmentFiveYears: float
    countryChartData: List[ChartData]
    holdingChartData: List[ChartData]
    sectorChartData: List[ChartData]
    lowCarbon: bool
    indexFund: bool
    sharpeRatio: float
    standardDeviation: float
    capital: float
    startDate: str
    """ YYYY-MM-DD """
    fundManagers: List[FundManager]
    adminCompany: AdminCompany
    pricingFrequency: str
    """ Example: "Dagligen" """
    prospectusLink: str
    """ Relative API URL """
    aumCoveredCarbon: Optional[bool]
    fossilFuelInvolvement: float
    carbonRiskScore: float
    categories: List[str]
    fundTypeName: str
    """ Example: EQUITY_FUND """
    hedgeFund: bool
    ucitsFund: bool
    recommendedHoldingPeriod: str
    portfolioDate: str
    """ YYYY-MM-DD """
    ppmCode: str
    superloanOrderbook: bool
    esgScore: float
    environmentalScore: float
    socialScore: float
    governanceScore: float
    controversyScore: Optional[float]
    carbonSolutionsInvolvement: float
    productInvolvements: List[ProductInvolvement]
    sustainabilityRating: int
    sustainabilityRatingCategoryName: str
    svanen: bool
    fundRatingViews: List[FundRatingView]
