from pydantic import BaseModel


class Offer(BaseModel):
    customerOfferId: str
    title: str
    lastResponseDate: str
    type: str
    hasResponded: bool
