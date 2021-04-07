import pandas as pd
from enum import Enum
from typing import Tuple
from collections import deque


class Decision(Enum):
    BuyLimitOrder = 1
    BuyAtMarket = 2
    NoAction = 3
    SellAtMarket = 4
    SellLimitOrder = 5


class Account:
    def __init__(self, totalValue) -> None:
        self.purchasePower = totalValue
        self.sharesOnHold = 0
        self.totalValue = totalValue
        self.trades = deque()

    def sync():
        """
        Sync trading account to update local acount information, such as purchase power, order, stock share ...
        """
        pass

    def buy(self, amount, price, date=None):
        """
        There is only one open buy order allowed.
        """
        if len(self.trades) != 0 and not self.trades[-1].isComplete():
            # has open order unfilled.
            return None

        if amount > self.purchasePower:
            return None

        sharesToBuy = amount / price
        # TODO, actual buy from FUTU
        print("...")

        self.sharesOnHold += sharesToBuy
        self.purchasePower -= amount

        openTrade = Trade(shares=sharesToBuy, buyAmount=amount,
                          buyPrice=price, buyDate=date)
        self.trades.append(openTrade)
        return openTrade

    def buy_at_market(self, amount):
        """
        Buy with market order
        """
        pass

    def sell(self, price, percentage=1.0, date=None):
        if len(self.trades) == 0 or self.trades[-1].isComplete():
            # has open order unfilled.
            return None

        # TODO actual sell at FUTU
        print("....")

        sharesToSell = int(self.sharesOnHold * percentage)
        lastTrade = self.trades[-1]
        self.sharesOnHold -= sharesToSell
        lastTrade.sellPrice = price
        lastTrade.sellDate = date
        lastTrade.sellAmount = sharesToSell * price

        self.purchasePower += (sharesToSell * price -
                               lastTrade.buyPrice * lastTrade.buyAmount)
        return lastTrade

    def sell_at_market(self):
        """
        Sell with market order.
        """
        pass

    def get_last_opentrade(self):
        if len(self.trades) != 0 and not self.trades[-1].isComplete():
            return self.trades[-1]
        else:
            return None


class Trade:
    def __init__(self, shares, buyPrice, buyAmount, buyDate=None, sellPrice=None, sellAmount=None, sellDate=None) -> None:
        self.shares = shares
        self.buyPrice = buyPrice
        self.buyDate = buyDate
        self.buyAmount = buyAmount
        self.sellPrice = sellPrice
        self.sellDate = sellDate
        self.sellAmount = sellAmount

    def isComplete(self):
        """
        Trade is completed when it has both sell and buy price.
        """
        return self.buyPrice and self.sellPrice


class TradeStrategy:
    def __init__(self) -> None:
        pass

    def make_decision(self, account: Account, history: pd.DataFrame, context: dict):
        """
        account represents trading account (ex: FUTU), use to fetch account status, orders, open trades and execute buy and sell.
        history is 2D table, contains securities' trade records (from past to current), index is date.
        context provides special data for each different strategy

        each trading strategy will buy, sell stocks or no action when this function get called.
        Its activities should be logged and saved into account trades records. 
        """
        pass
