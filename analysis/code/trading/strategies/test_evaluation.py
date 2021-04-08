import unittest
import os
import pandas as pd
from premium_pure import PremiumWithShortMemory
from base import Decision, Account
from evaluation import *


class StrategyEvaluationTest(unittest.TestCase):

    def setUp(self) -> None:
        curDir = os.path.dirname(__file__)

        data = pd.read_csv(
            os.path.join(curDir, "../../../data/btc_gbtc/btc_gbtc_5min_weekly_combined_31_03_2021.csv"), sep=",", index_col='begins_at')

        self.testData = self.preprocess_data(data)

        return super().setUp()

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        btc_per_share = 0.00094607

        data["nav_open_price"] = data["open_price_x"] * \
            btc_per_share
        data["nav_close_price"] = data["close_price_x"] * btc_per_share
        data["nav_high_price"] = data["high_price_x"] * \
            btc_per_share
        data["nav_low_price"] = data["low_price_x"] * \
            btc_per_share

        data["premium"] = (data["open_price_y"] -
                           data["nav_open_price"]) / data["nav_open_price"]
        data = data.dropna()

        return data

    def test_evaluate_premium_with_shortmemory(self):

        acct = Account(totalValue=10000)
        strategy = PremiumWithShortMemory(memoryLenth=120, sampleCnt=10)

        evaluate_strategy(data=self.testData, account=acct, strategy=strategy,
                          output="trades-1")

        self.assertAlmostEqual(10352.599999999999, acct.purchasePower)
        self.assertEqual(0, acct.sharesOnHold)
        self.assertAlmostEqual(10352.599999999999, acct.totalValue)

    def test_evaluate_premium_with_shortmemory_with_more_data(self):

        curDir = os.path.dirname(__file__)

        df_5min_21_03_2021 = pd.read_csv(
            os.path.join(curDir, "../../../data/btc_gbtc/btc_gbtc_5min_weekly_combined_21_03_2021.csv"), sep=",", index_col='begins_at')
        df_5min_21_03_2021.index.astype('datetime64[ns]')

        df_5min_28_03_2021 = pd.read_csv(
            os.path.join(curDir, "../../../data/btc_gbtc/btc_gbtc_5min_weekly_combined_28_03_2021.csv"), sep=",", index_col='begins_at')
        df_5min_28_03_2021.index.astype('datetime64[ns]')

        df_5min_31_03_2021 = pd.read_csv(
            os.path.join(curDir, "../../../data/btc_gbtc/btc_gbtc_5min_weekly_combined_31_03_2021.csv"), sep=",", index_col='begins_at')
        df_5min_31_03_2021.index.astype('datetime64[ns]')

        df_5min_08_04_2021 = pd.read_csv(
            os.path.join(curDir, "../../../data/btc_gbtc/btc_gbtc_5min_weekly_combined_08_04_2021.csv"), sep=",", index_col='begins_at')
        df_5min_08_04_2021.index.astype('datetime64[ns]')

        df_5min = pd.concat([df_5min_21_03_2021, df_5min_28_03_2021, df_5min_31_03_2021, df_5min_08_04_2021]
                            ).drop_duplicates().sort_index(ascending=True)

        data = self.preprocess_data(df_5min)

        acct = Account(totalValue=10000)
        strategy = PremiumWithShortMemory(memoryLenth=180, sampleCnt=15)

        evaluate_strategy(data=data, account=acct, strategy=strategy,
                          output="analysis/data/trade_records/trade-180-15")

        self.assertAlmostEqual(10124.609999999999, acct.totalValue)
