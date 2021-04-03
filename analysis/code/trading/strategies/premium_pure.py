from .base import TradeStrategy, Account, Decision
import pandas as pd
from typing import Tuple


class PremiumWithShortMemory(TradeStrategy):
    """
    This trading strategy only considers premium in the past to decide buy and sell point.
    There is no trend detection, no internal state, just make trade decision base on the average of
    top N highest and lowest premium percentage.
    """

    def __init__(self, memoryLenth: int = 24 * 60 * 3, sampleCnt: int = 10) -> None:
        """
        memoryLenth: how many data points to consider in the past, 24 * 60 * 3 means minutes data from past 3 days.
        sampleCnt: how many samples to calculate buying and selling point, by default 10.
        """

        super().__init__()
        self._memLenth = memoryLenth
        self._sampleCnt = sampleCnt

    def make_decision(self, account: Account, history: pd.DataFrame, context: dict) -> Tuple[Decision, int]:
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

        #

        #
