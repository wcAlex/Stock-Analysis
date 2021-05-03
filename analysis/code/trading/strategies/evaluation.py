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

def dataFrame_builder_td(row: tuple) -> pd.DataFrame():
        data = []
        temp = []
        for x in row:
            temp.append(x)
        data.append(temp)

        df = pd.DataFrame(
            data, columns=
            ["datetime", "btc_low_price", "btc_high_price", "btc_close_price", "btc_open_price", "btc_volume",
            "time", "gbtc_open_price", "gbtc_high_price", "gbtc_low_price", "gbtc_close_price", "gbtc_volume",
            "nav_open_price", "nav_close_price", "nav_high_price", "nav_low_price", "premium", "premium_high", 
            "premium_open", "premium_close", "premium_low"])
        df = df.set_index('datetime')

        return df 

def evaluate_strategy_premium_indicator(pastData: pd.DataFrame, newData: pd.DataFrame, strategy: TradeStrategy, account: Account, output: str) -> Tuple[float, pd.DataFrame, pd.DataFrame]:
    # data = data.sort_index(ascending=True)
    pastData = pastData.drop_duplicates()
    newData = newData.drop_duplicates()
    rowCount = 0

    for row in newData.itertuples():
        # if rowCount > newData.shape[0]//10:
        #     break
        curNewData = dataFrame_builder_td(row)
        curADX, pastData, recordDate, curPosDI, curNegDI = strategy.make_decision(account, pastData, curNewData, {}, 'GBTC', True)
        rowCount += 1

    buyDf, sellDf = account.create_trades_records()
    buyDf.to_csv(output + "-buy.csv")
    sellDf.to_csv(output + "-sell.csv")

