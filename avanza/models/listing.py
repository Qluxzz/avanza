from pydantic import BaseModel


class Listing(BaseModel):
    shortName: str
    tickerSymbol: str
    countryCode: str
    """ ISO 3166-1 alpha-2 """
    currency: str
    """ ISO 4217 """
    marketPlaceCode: str
    marketPlaceName: str
    tickSizeListId: str
    marketTradesAvailable: bool
