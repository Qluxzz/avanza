from pydantic import BaseModel
from .quote import Quote
from .listing import Listing


class Underlying(BaseModel):
    orderbookId: str
    name: str
    instrumentType: str
    """ Example: STOCK """
    quote: Quote
    listing: Listing
    previousClosingPrice: float
