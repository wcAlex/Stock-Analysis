from datetime import date, datetime
from base import TradeStrategy, Account, Decision
import pandas as pd
from typing import Tuple
from ta.trend import ADXIndicator
import time

class PremiumTrendIndicator(TradeStrategy):
    """
    This trading strategy only considers premium trend using ADX.
    """

    def __init__(self, memoryLenth: int = 24 * 60 * 3, sampleCnt: int = 10, delta: float = 1.00, buyThreshhold: int = 40, sellThreshold: int = 35, smoothedLen: int = 240) -> None:
        """
        memoryLenth: how many data points to consider in the past, 24 * 60 * 3 means minutes data from past 3 days.
        sampleCnt: how many samples to calculate buying and selling point, by default 10.
        delta: hyper parameter, customerized gap between purchase target and purchase premium, sell target and sell premium
        """

        super().__init__()
        self._memLenth = memoryLenth
        self._sampleCnt = sampleCnt
        self.delta = delta
        self.buyThreshhold = buyThreshhold
        self.sellThreshold = sellThreshold
        self.smoothedLen = smoothedLen

    def data_preparation(self, data: pd.DataFrame) -> pd.DataFrame:
        btc_per_share = 0.000944051

        data["nav_open_price"] = data["btc_open_price"] * \
            btc_per_share
        data["nav_close_price"] = data["btc_close_price"] * btc_per_share
        data["nav_high_price"] = data["btc_high_price"] * \
            btc_per_share
        data["nav_low_price"] = data["btc_low_price"] * \
            btc_per_share
     
        # Calculate premium high
        data["nav_high_price"] = data["btc_high_price"] * btc_per_share
        data["premium_high"] = (data["gbtc_high_price"] - data["nav_high_price"]) / data["nav_high_price"]
        data["premium_high"].dropna()

        # Calculate premium low
        data["nav_low_price"] = data["btc_low_price"] * btc_per_share
        data["premium_low"] = (data["gbtc_low_price"] - data["nav_low_price"]) / data["nav_low_price"]
        data["premium_low"].dropna()

        # Calculate premium close
        data["nav_close_price"] = data["btc_close_price"] * btc_per_share
        data["premium_close"] = (data["gbtc_close_price"] - data["nav_close_price"]) / data["nav_close_price"]
        data["premium_close"].dropna()
        
        data.dropna()
        return data


    def get_current_info(self, history: pd.DataFrame, newData: pd.DataFrame, isTD: bool = False) -> Tuple[float, float, float, float, float, datetime, pd.DataFrame]:
        """
        get the latest ADX, pos/neg indicator and date
        """

        history = history.dropna()

        newData = self.data_preparation(newData)
        history = history.append(newData)
        smoothed = 14
        
        adxI = ADXIndicator(history['premium_high'], history['premium_low'], history['premium_close'], smoothed, False)
        history['pos_directional_indicator'] = adxI.adx_pos()
        history['neg_directional_indicator'] = adxI.adx_neg()
        history['adx'] = adxI.adx() 

        adx = history.iloc[-1]['adx']
        posDI = history.iloc[-1]['pos_directional_indicator']
        negDI = history.iloc[-1]['neg_directional_indicator']
        marketPrice = history.iloc[-1]['gbtc_open_price']
        curPremium = history.iloc[-1]['premium_close']
        date =  history.index[-1]
        
        return (adx, posDI, negDI, marketPrice, curPremium, 
        datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') if not isTD else datetime.strptime(date, '%Y-%m-%d %H:%M:%S'), history)

    def get_top_bottom_n_premium(self, data: pd.DataFrame, n: int) -> Tuple[list, list]:

        premiumHighList = data['premium_high']
        premiumLowList = data['premium_low']

        return (sorted(premiumHighList, reverse=True)[:n], sorted(premiumLowList, reverse=False)[:n])

    def make_decision(self, account: Account, history: pd.DataFrame, newData: pd.DataFrame, context: dict, symbol: str = 'GBTC', isTD: bool = False):
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

        curADX, curPosDI, curNegDI, curMarketPrice, curPremium, recordDate, history = self.get_current_info(history, newData, isTD)

        topNPremiums, bottomNPremiums = self.get_top_bottom_n_premium(
            history[:240], self._sampleCnt)

        premiumBuyTarget = sum(bottomNPremiums)/self.smoothedLen
        premiumSellTareget = sum(topNPremiums)/self.smoothedLen
        avg = (premiumBuyTarget + premiumSellTareget)/2
        avg = avg * self.delta
        
        # Buy 
        if curADX > self.buyThreshhold and curNegDI > curPosDI and curPremium < avg:
            trade = account.buy(symbol, account.purchasePower,
                                curMarketPrice, date=recordDate)

            if trade:
                print("Buy {0} at {1}, price={2}, premium={3}, share={4}, total={5}, current premium avg={5}".format(
                    symbol, recordDate, curMarketPrice, curPremium, int(account.purchasePower/curMarketPrice), account.purchasePower, avg))

        lastOpenTrade = account.get_last_opentrade()

        # Sell
        if lastOpenTrade and curADX > self.sellThreshold and curPosDI > curNegDI and curMarketPrice > lastOpenTrade.buyPrice:
            sellPercentage = 1.0
            trade = account.sell(symbol, curMarketPrice,
                                 percentage=sellPercentage, date=recordDate)

            if trade:
                print("Sell {0} at {1}, price={2}, premium={3}, share={4}, total={5}, current premium avg={6}".format(
                    symbol, recordDate, curMarketPrice, curPremium, int(account.sharesOnHold * sellPercentage), lastOpenTrade.sellValue, avg))
            
        print("account total value")
        print(account.totalValue)
        print("curADX")
        print(curADX)
        if lastOpenTrade:
            print("last buy price")
            print(lastOpenTrade.buyValue)
            print("last sell price")
            print(lastOpenTrade.sellValue)
        print("Date")
        print(recordDate)

        account.updateAccountValue(curMarketPrice)
        return (curADX, history, recordDate, curPosDI, curNegDI)



    def make_decision_new(self, account: Account, history: pd.DataFrame, newData: pd.DataFrame, context: dict, symbol: str = 'GBTC', isTD: bool = False, sellDelta: float = 0.35, buyDelta: float = 0.45, sellPriceDelta: float = 1.1):
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

        curADX, curPosDI, curNegDI, curMarketPrice, curPremium, recordDate, history = self.get_current_info(history, newData, isTD)

        topNPremiums, bottomNPremiums = self.get_top_bottom_n_premium(
            history[:240], self._sampleCnt)

        premiumBuyTarget = sum(bottomNPremiums)/self.smoothedLen
        premiumSellTareget = sum(topNPremiums)/self.smoothedLen
        avg = (premiumBuyTarget + premiumSellTareget)/2
        avgPremiumBuy = avg * buyDelta
        avgPremiumSell = avg * sellDelta
        
        # Buy 
        if curADX > self.buyThreshhold and curNegDI > curPosDI and curPremium < avgPremiumBuy:
            trade = account.buy(symbol, account.purchasePower,
                                curMarketPrice, date=recordDate)

            if trade:
                print("Buy {0} at {1}, price={2}, premium={3}, share={4}, total={5}, current premium avg={5}".format(
                    symbol, recordDate, curMarketPrice, curPremium, int(account.purchasePower/curMarketPrice), account.purchasePower, avgBuy))

        lastOpenTrade = account.get_last_opentrade()

        # Sell
        if lastOpenTrade and curADX > self.sellThreshold and curPosDI > curNegDI and curMarketPrice >= (lastOpenTrade.buyPrice * sellPriceDelta) and curPremium > avgPremiumSell:
            sellPercentage = 1.0
            trade = account.sell(symbol, curMarketPrice,
                                 percentage=sellPercentage, date=recordDate)

            if trade:
                print("Sell {0} at {1}, price={2}, premium={3}, share={4}, total={5}, current premium avg={6}".format(
                    symbol, recordDate, curMarketPrice, curPremium, int(account.sharesOnHold * sellPercentage), lastOpenTrade.sellValue, avgSell))
        

        account.updateAccountValue(curMarketPrice)
        return (curADX, history, recordDate, curPosDI, curNegDI)
