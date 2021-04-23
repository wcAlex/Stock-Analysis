from datetime import date, datetime
from base import TradeStrategy, Account, Decision
import pandas as pd
from typing import Tuple


class PremiumDynamic(TradeStrategy):
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

    def make_decision(self, account: Account, history: pd.DataFrame, context: dict, symbol: str = 'GBTC'):
        """
        account: use to fetch current stock account status
        history: past market trading data, minute level, expect to be up to date at minutes level
        context: context dictionary

        Algorithm:
        1) Use EMA of premium as trading baseline
        2) Stock trend strength measurement (Strong, Weak, Neutral) 
            MACD histogram value
            ADX DI+, DI-
        3) Oversold and overbought confirmation 
            RSI
        4) Buying signal:
             Premium is lower than {current EMA} - delta * current_strength / base
           Selling signal:
             Premium is higher than {current EMA} + delta * current_strength / base

            Or use current_strength * time decay function, buy or sell at the peak of momentum 

            May be three conditions:
                1) premium below or above {current EMA} - (decay function) * current_strength / base
                2) MACD peak 
                3) Overbought and oversold signal 
        """
