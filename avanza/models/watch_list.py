from typing import List
from pydantic import BaseModel


class WatchList(BaseModel):
    editable: bool
    id: str
    name: str
    orderbooks: List[str]
