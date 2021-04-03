import pandas as pd
from enum import Enum
from typing import Tuple


class Decision(Enum):
    BuyLimitOrder = 1
    BuyAtMarket = 2
    NoAction = 3
    SellAtMarket = 4
    SellLimitOrder = 5


class Account:
    def __init__(self, ) -> None:
        self.amount_available = 0
        self.total = 0
        self.orders = list()


class Orders:
    def __init__(self) -> None:
        pass


class TradeStrategy:
    def __init__(self) -> None:
        pass

    def make_decision(self, account: Account, history: pd.DataFrame, context: dict) -> Tuple[Decision, int]:
        pass
