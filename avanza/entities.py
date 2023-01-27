from datetime import date

from .constants import OrderType, StopLossPriceType, StopLossTriggerType


class StopLossTrigger:
    def __init__(self, type: StopLossTriggerType, value: float, valid_until: date):
        self.type = type
        self.value = value
        self.valid_until = valid_until

class StopLossOrderEvent:
    def __init__(self, type: OrderType, price: float, volume: float, valid_days: int, price_type: StopLossPriceType, short_selling_allowed: bool):
        self.type = type
        self.price = price
        self.volume = volume
        self.valid_days = valid_days
        self.price_type = price_type
        self.short_selling_allowed = short_selling_allowed