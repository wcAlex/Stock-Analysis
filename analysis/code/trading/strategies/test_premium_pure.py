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

    def test_make_decision(self):

        # prepare data
        data = [
            ["2021-03-18T16:15:00Z", 55.5, 0.5],
            ["2021-03-18T16:16:00Z", 56.5, 0.6],
            ["2021-03-18T16:17:00Z", 53.5, 0.3],
            ["2021-03-18T16:18:00Z", 52.5, 0.2],
        ]

        df = pd.DataFrame(
            data, columns=["date", "open_price_y", "premium"])
        df = df.set_index('date')
        self.assertEqual(2, len(df.columns))
        self.assertEqual(4, df.shape[0])

        # time to buy
        acct = Account(totalValue=100)
        strategy = PremiumWithShortMemory(memoryLenth=4, sampleCnt=2)
        curPremium, curMarketPrice, recordDate = strategy.get_current_premium(
            df)
        self.assertEqual(52.5, curMarketPrice)
        self.assertEqual(0.2, curPremium)

        topTwoPremiums, bottomTwoPremiums = strategy.get_top_bottom_n_premium(
            df, 2)
        self.assertSequenceEqual([0.6, 0.5], topTwoPremiums)
        self.assertSequenceEqual([0.2, 0.3], bottomTwoPremiums)
        strategy.make_decision(acct, df, {}, 'GBTC')

        trades = acct.trades
        self.assertEqual(1, len(trades))
        self.assertFalse(trades[-1].isComplete())
        self.assertEqual(52.5, trades[-1].buyPrice)
        self.assertEqual(47.5, acct.purchasePower)
        self.assertEqual(1, acct.sharesOnHold)
        self.assertEqual(recordDate, trades[-1].buyDate)

        # time to do nothing
        strategy.make_decision(acct, df, {}, 'GBTC')
        trades = acct.trades
        self.assertEqual(1, len(trades))
        self.assertFalse(trades[-1].isComplete())
        self.assertIsNone(trades[-1].sellPrice)

        # time to do nothing (premium is good, but price is lower)
        newData = pd.DataFrame([["2021-03-18T16:19:00Z", 51.5, 0.7]],
                               columns=["date", "open_price_y", "premium"])
        df = df.append(newData.set_index("date"))
        strategy.make_decision(acct, df, {}, 'GBTC')
        trades = acct.trades
        self.assertEqual(1, len(trades))
        self.assertFalse(trades[-1].isComplete())
        self.assertIsNone(trades[-1].sellPrice)
        self.assertEqual(1, acct.sharesOnHold)

        # time to sell
        newData = pd.DataFrame([["2021-03-18T16:20:00Z", 59.5, 0.8]],
                               columns=["date", "open_price_y", "premium"])
        df = df.append(newData.set_index("date"))

        curPremium, curMarketPrice, recordDate = strategy.get_current_premium(
            df)

        strategy.make_decision(acct, df, {}, 'GBTC')
        trades = acct.trades

        # Verify trade record
        self.assertEqual(1, len(trades))
        self.assertTrue(trades[-1].isComplete())
        self.assertEqual(59.5, trades[-1].sellPrice)
        self.assertEqual(59.5, trades[-1].sellValue)
        self.assertEqual(recordDate, trades[-1].sellDate)

        # Verify account status after buy and sell
        self.assertEqual(0, acct.sharesOnHold)
        self.assertEqual(100 - 52.5 + 59.5, acct.purchasePower)


if __name__ == '__main__':
    unittest.main()
