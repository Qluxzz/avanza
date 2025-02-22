from pydantic import BaseModel


class PriceAlert(BaseModel):
    alertId: str
    accountId: str
    price: float
    validUntil: str
    """ YYYY-MM-DD """
    direction: str
    """ ABOVE/BELOW """
    recurring: bool
    email: bool
    notification: bool
    sms: bool
