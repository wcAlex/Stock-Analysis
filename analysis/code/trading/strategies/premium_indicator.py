from datetime import date, datetime
from base import TradeStrategy, Account, Decision
import pandas as pd
from typing import Tuple


class PremiumTrendIndicator(TradeStrategy):
    """
    This trading strategy only considers premium trend using ADX.
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

    def get_current_info(self, history: pd.DataFrame) -> Tuple[float, float, float, datetime]:
        """
        get the latest premium, pos/neg indicator and date
        """

        history = history.dropna()
        history = history.sort_index(ascending=False)

        return (history['premium_high'][0], history['pos_directional_indicator'][0], 
        history['neg_directional_indicator'][0], datetime.strptime(history.index[0], '%Y-%m-%dT%H:%M:%SZ'))

    def get_top_bottom_n_premium(self, data: pd.DataFrame, n: int) -> Tuple[list, list]:

        premiumList = data['premium']
        return (sorted(premiumList, reverse=True)[:n], sorted(premiumList, reverse=False)[:n])

    def make_decision(self, account: Account, history: pd.DataFrame, context: dict, symbol: str = 'GBTC'):
        """
        account: use to fetch current stock account status
        history: past market trading data, minute level, expect to be up to date at minutes level
        context: context dictionary

        Algorithm:
        1) Pick the memoryLenth of validate (stock record not null) data points from history
        2) Calculate ADX based on the latest premium info
        3) Calculate buy/sell targets by getting the latest premium ADX
        4) Return decision
            a) Buy when current premium once ADX is above threshold and postive indicator is greater than negative indicator
            b) Sell when current premium ADX is above threshold and postive indicator is lower than negative indicator
            c) No action for the rest of the cases
        """

        history = history.dropna()
        history = history.sort_index(ascending=False)

        # Get current ADx
        curADX, posDI, negDI, recordDate = self.get_current_adx(history)
        threshold = 35

        # Buy 
        if curADX > threshold and negDI > posDI:
            trade = account.buy(symbol, account.purchasePower,
                                curMarketPrice, date=recordDate)

            if trade:
                print("Buy {0} at {1}, price={2}, premium={3}, share={4}, total={5}, current premium average={5}".format(
                    symbol, recordDate, curMarketPrice, curPremium, int(account.purchasePower/curMarketPrice), account.purchasePower, average))

        lastOpenTrade = account.get_last_opentrade()

        # Sell
        if lastOpenTrade and curADX > threshold and posDI > negDI and curMarketPrice > lastOpenTrade.buyPrice:
            sellPercentage = 1.0
            trade = account.sell(symbol, curMarketPrice,
                                 percentage=sellPercentage, date=recordDate)

            if trade:
                print("Sell {0} at {1}, price={2}, premium={3}, share={4}, total={5}, current premium average={6}".format(
                    symbol, recordDate, curMarketPrice, curPremium, int(account.sharesOnHold * sellPercentage), lastOpenTrade.sellValue, average))

        account.updateAccountValue(curMarketPrice)
