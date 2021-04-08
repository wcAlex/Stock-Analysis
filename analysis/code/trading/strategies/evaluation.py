import pandas as pd
from typing import Tuple
from base import TradeStrategy, Account, Trade
# from strategies.premium_pure import PremiumWithShortMemory


def evaluate_strategy(data: pd.DataFrame, strategy: TradeStrategy, account: Account, output: str) -> Tuple[float, pd.DataFrame, pd.DataFrame]:
    data = data.sort_index(ascending=True)
    data = data.dropna()
    data = data.drop_duplicates()

    # strategy = PremiumWithShortMemory(memoryLenth=120, sampleCnt=10)
    for i in range(121, data.shape[0]):
        strategy.make_decision(
            account=account, history=data[:i], context={}, symbol='GBTC')

    buyDf, sellDf = account.create_trades_records()
    buyDf.to_csv(output + "-buy.csv")
    sellDf.to_csv(output + "-sell.csv")
