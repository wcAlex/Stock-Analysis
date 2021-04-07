import unittest
import os
import pandas as pd
from premium_pure import PremiumWithShortMemory
from base import Decision, Account


class PremiumStrategyTest(unittest.TestCase):

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

    def test_run(self):
        strategy = PremiumWithShortMemory()

        account = Account(1000.0)
        strategy.make_decision(Account(), self.testData, {})
        trades = account.trades

    def test_get_current_premium(self):
        strategy = PremiumWithShortMemory()

        curPremium, curMarketPrice, recordDate = strategy.get_current_premium(
            self.testData)
        self.assertEqual(recordDate.strftime(
            '%Y-%m-%dT%H:%M:%SZ'), '2021-03-31T14:45:00Z')
        self.assertEqual(curMarketPrice, 50.279900)

    def test_get_top_bottom_n_premium(self):
        strategy = PremiumWithShortMemory()
        topTenPremiums, bottomTenPremiums = strategy.get_top_bottom_n_premium(
            self.testData, 10)
        self.assertEqual(len(topTenPremiums), 10)
        self.assertEqual(-0.08521801694398716, max(topTenPremiums))
        self.assertEqual(len(bottomTenPremiums), 10)
        self.assertEqual(-0.15799840726060543, min(bottomTenPremiums))

    def test_make_buy_decision_premium_short_memory(self):
        pass


if __name__ == '__main__':
    unittest.main()
