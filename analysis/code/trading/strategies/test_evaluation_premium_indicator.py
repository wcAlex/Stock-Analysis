import unittest
import os
import pandas as pd
from premium_indicator import PremiumTrendIndicator
from base import Decision, Account
from evaluation import *


class PremiumIndicatorStrategyEvaluationTest(unittest.TestCase):

    def setUp(self) -> None:
        curDir = os.path.dirname(__file__)

        data = pd.read_csv(
            os.path.join(curDir, "../../../data/btc_gbtc/btc_gbtc_minute_2021.csv"), sep=",", index_col='datetime')

        cleanData = self.data_cleanup(data)
        self.pastData = self.preprocess_data(cleanData.iloc[:250])
        self.newData = self.data_cleanup(cleanData.iloc[250:])

        return super().setUp()


    def data_cleanup(self, data: pd.DataFrame) -> pd.DataFrame:
        data.drop(data[data['gbtc_open_price'].isnull()].index, inplace=True)
        return data


    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:

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

    def test_evaluate_premium_with_shortmemory(self):

        acct = Account(totalValue=10000)
        strategy = PremiumTrendIndicator(memoryLenth=120, sampleCnt=10)

        evaluate_strategy_premium_indicator(pastData=self.pastData, newData=self.newData, account=acct, strategy=strategy,
                          output="trades-1")

        print("account purchase power")
        print(acct.purchasePower)
        print("account total value")
        print(acct.totalValue)
        print("account share hold")
        print(acct.sharesOnHold)
        # self.assertAlmostEqual(10352.599999999999, acct.purchasePower)
        # self.assertEqual(0, acct.sharesOnHold)
        # self.assertAlmostEqual(10352.599999999999, acct.totalValue)

if __name__ == '__main__':
        unittest.main()