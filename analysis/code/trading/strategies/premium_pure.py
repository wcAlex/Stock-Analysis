from datetime import date, datetime
from base import TradeStrategy, Account, Decision
import pandas as pd
from typing import Tuple


class PremiumWithShortMemory(TradeStrategy):
    """
    This trading strategy only considers premium in the past to decide buy and sell point.
    There is no trend detection, no internal state, just make trade decision base on the average of
    top N highest and lowest premium percentage.
    """

    def __init__(self, memoryLenth: int = 24 * 60 * 3, sampleCnt: int = 10, delta=0.001) -> None:
        """
        memoryLenth: how many data points to consider in the past, 24 * 60 * 3 means minutes data from past 3 days.
        sampleCnt: how many samples to calculate buying and selling point, by default 10.
        delta: hyper parameter, customerized gap between purchase target and purchase premium, sell target and sell premium
        """

        super().__init__()
        self._memLenth = memoryLenth
        self._sampleCnt = sampleCnt
        self._delta = delta

    def get_current_premium(self, history: pd.DataFrame) -> Tuple[float, float, datetime]:
        """
        get the latest premium, price and date
        """

        history = history.dropna()
        history = history.sort_index(ascending=False)

        return (history['premium'][0], history['open_price_y'][0], datetime.strptime(history.index[0], '%Y-%m-%dT%H:%M:%SZ'))

    def get_top_bottom_n_premium(self, data: pd.DataFrame, n: int) -> Tuple[list, list]:

        premiumList = data['premium']
        return (sorted(premiumList, reverse=True)[:n], sorted(premiumList, reverse=False)[:n])

    def make_decision(self, account: Account, history: pd.DataFrame, context: dict):
        """
        account: use to fetch current stock account status
        history: past market trading data, minute level, expect to be up to date at minutes level
        context: context dictionary

        Algorithm:
        1) Pick the memoryLenth of validate (stock record not null) data points from history.
        2) Calculate premium columns with percentage, sort on preimum percentage.
        3) Calculate buy target by averaging the top sampleCnt highest premium precentage.
        4) Calculate sell target by averaging the bottom lowest premium percentage
        5) Return decision
            a) Buy when current premium percentage is lower than the buy target and there is no holdings.
            b) Sell when current premium percentage is higher than the sell target and there is one holdings.
            c) No action for the rest of the cases.
        """

        history = history.dropna()
        history = history.sort_index(ascending=False)

        # We might need consider permium average later.
        premiumColumn = history["premium"]
        premiumPast120 = premiumColumn[:120]
        average = sum(premiumPast120)/120

        topNPremiums, bottomNPremiums = self.get_top_bottom_n_premium(
            history[:120], self._sampleCnt)

        premiumBuyTarget = sum(topNPremiums)/self._sampleCnt
        premiumSellTareget = sum(bottomNPremiums)/self._sampleCnt

        curPremium, curMarketPrice, recordDate = self.get_current_premium()
        if curPremium < premiumBuyTarget - self._delta:
            account.buy(account.purchasePower, curMarketPrice, recordDate)
            print("Buy GBTC at {0}, price={1}, premium={2}, share={3}, total={4}, current premium average={5}".format(
                recordDate, curMarketPrice, curPremium, int(account.purchasePower/curMarketPrice), account.purchasePower, average))

        lastOpenTrade = account.get_last_opentrade()
        if lastOpenTrade and curPremium > premiumSellTareget + self._delta and curMarketPrice > lastOpenTrade.buyPrice:
            sellPercentage = 1.0
            account.sell(curMarketPrice, percentage=sellPercentage)
            print("Sell GBTC at {0}, price={1}, premium={2}, share={3}, total={4}, current premium average={5}".format(
                recordDate, curMarketPrice, curPremium, int(self.sharesOnHold * sellPercentage), lastOpenTrade.sellAmount, average))
