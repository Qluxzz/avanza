from typing import List
from pydantic import BaseModel


class CustomerId(BaseModel):
    id: int


class UserId(BaseModel):
    customerId: CustomerId


class WatchList(BaseModel):
    watchListId: str
    userId: UserId
    orderbookIds: List[str]
    created: str
    """ ISO 8601 """
    modified: str
    """ ISO 8601 """
    name: str
    urlName: str
