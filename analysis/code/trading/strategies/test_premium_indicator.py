import numpy as np
import pandas as pd
import unittest
import os
from ta.trend import ADXIndicator
import matplotlib.pyplot as plt
from csv import reader
from premium_indicator import PremiumTrendIndicator
from base import Decision, Account

class PremiumTrendIndicatorTest(unittest.TestCase):

    def setUp(self) -> None:

        curDir = os.path.dirname(__file__)

        data1 = pd.read_csv(
            os.path.join(curDir, "../../../data/btc_gbtc/btc_gbtc_5min_weekly_combined_31_03_2021.csv"), sep=",", index_col='begins_at')

        data2 = pd.read_csv(os.path.join(curDir, "../../../data/btc_gbtc/btc_gbtc_5min_weekly_combined_08_04_2021.csv"), sep=",", index_col='begins_at')

        self.lowPriceTestData = self.data_cleanup(data1) 
        self.highPricetestData = self.data_cleanup(data2)
    
        return super().setUp()      


    def data_cleanup(self, data: pd.DataFrame) -> pd.DataFrame:
        data.drop(data[data['open_price_y'].isnull()].index, inplace=True)
        return data  
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        btc_per_share = 0.00094498

        data["nav_open_price"] = data["open_price_x"] * \
            btc_per_share
        data["nav_close_price"] = data["close_price_x"] * btc_per_share
        data["nav_high_price"] = data["high_price_x"] * \
            btc_per_share
        data["nav_low_price"] = data["low_price_x"] * \
            btc_per_share

        # data["premium"] = (data["open_price_y"] -
        #                    data["nav_open_price"]) / data["nav_open_price"]

        # Calculate premium high
        data["nav_high_price"] = data["high_price_x"] * btc_per_share
        data["premium_high"] = (data["high_price_y"] - data["nav_high_price"]) / data["nav_high_price"]
        data["premium_high"].dropna()

        # Calculate premium low
        data["nav_low_price"] = data["low_price_x"] * btc_per_share
        data["premium_low"] = (data["low_price_y"] - data["nav_low_price"]) / data["nav_low_price"]
        data["premium_low"].dropna()

        # Calculate premium close
        data["nav_close_price"] = data["close_price_x"] * btc_per_share
        data["premium_close"] = (data["close_price_y"] - data["nav_close_price"]) / data["nav_close_price"]
        data["premium_close"].dropna()

        # Calculate ADX, pos/neg direction indicators
        smoothed = 70
        adxI = ADXIndicator(data['premium_high'], data['premium_low'], data['premium_close'], smoothed, False)
        data['pos_directional_indicator'] = adxI.adx_pos()
        data['neg_directional_indicator'] = adxI.adx_neg()
        data['adx'] = adxI.adx()

        data.dropna()    
        return data


    def dataFrame_builder(self, row: tuple) -> pd.DataFrame():
        data = []
        temp = []
        for x in row:
            temp.append(x)
        data.append(temp)

        df = pd.DataFrame(
            data, columns=
            ["begins_at", "open_price_x", "close_price_x", "high_price_x", "low_price_x", "volume_x", "session_x",
             "interpolated_x", "symbol_x", "open_price_y", "close_price_y", "high_price_y", "low_price_y", 
             "volume_y", "session_y", "interpolated_y", "symbol_y"])
        df = df.set_index('begins_at')

        return df
        
    def test_get_current_info(self):
        strategy = PremiumTrendIndicator()
        count = 0
        # prevent modifying orignal test data
        temp_test_data = self.preprocess_data(self.lowPriceTestData)
        for row in self.highPricetestData.itertuples():
            curTestData = self.dataFrame_builder(row)
            if count == 0:
                break
            curADX, curPosDI, curNegDI, curMarketPrice, curPremium, recordDate, temp_test_data = strategy.get_current_info(temp_test_data, curTestData)
            self.assertEqual(recordDate.strftime('%Y-%m-%dT%H:%M:%SZ'), curTestData.index[-1])
            count -= 1

    def test_get_top_bottom_n_premium(self):
        # prevent modifying orignal test data
        temp_test_data = self.preprocess_data(self.lowPriceTestData)
        strategy = PremiumTrendIndicator()
        topTenPremiums, bottomTenPremiums = strategy.get_top_bottom_n_premium(
            temp_test_data, 10)
        self.assertEqual(len(topTenPremiums), 10)
        self.assertEqual(-0.08296262677424213, max(topTenPremiums))
        self.assertEqual(len(bottomTenPremiums), 10)
        self.assertEqual(-0.15575200130009603, min(bottomTenPremiums))

    def test_make_decision_buying(self):

        # name data for buying
        past_data = self.preprocess_data(self.highPricetestData)
        new_coming_data = self.lowPriceTestData
        print(new_coming_data.to_string())
        # verify new coming data for buying
        self.assertEqual(16, len(new_coming_data.columns))
        self.assertEqual(328, new_coming_data.shape[0])
    
        # keep streaming new data until desired price shows up for buying
        acct = Account(totalValue=100)
        strategy = PremiumTrendIndicator(memoryLenth=4, sampleCnt=2)
        threshold = 40

        curADX, curPosDI, curNegDI, rowCount = 0, 0 ,0, 0
        for row in new_coming_data.itertuples():

            curTestData = self.dataFrame_builder(row)
            curADX, past_data, recordDate, curPosDI, curNegDI = strategy.make_decision(acct, past_data, curTestData, {}, 'GBTC')
            trades = acct.trades
            if curADX >= threshold and curPosDI < curNegDI:
                self.assertTrue(curADX >= threshold)
                self.assertEqual(1, len(trades))
                self.assertFalse(trades[-1].isComplete())
                self.assertEqual(41.29, trades[-1].buyPrice)
                self.assertEqual(17.42, acct.purchasePower)
                self.assertEqual(2, acct.sharesOnHold)
                self.assertEqual(recordDate, trades[-1].buyDate)
                sellTestData = new_coming_data[rowCount+1:]
                break
            else:
                self.assertEqual(0, len(trades))
                rowCount += 1
        
        strategy = PremiumTrendIndicator(memoryLenth=4, sampleCnt=2)
        print(sellTestData.to_string())
        for row in sellTestData.itertuples():

            curTestData = self.dataFrame_builder(row)
            curADX, past_data, recordDate, curPosDI, curNegDI = strategy.make_decision(acct, past_data, curTestData, {}, 'GBTC')
            trades = acct.trades

            if curADX >= threshold and curPosDI > curNegDI:
                self.assertTrue(curADX >= threshold)
                self.assertEqual(1, len(trades))
                self.assertFalse(trades[-1].isComplete())
                self.assertEqual(41.29, trades[-1].buyPrice)
                self.assertEqual(17.42, acct.purchasePower)
                self.assertEqual(2, acct.sharesOnHold)
                self.assertEqual(recordDate, trades[-1].buyDate)
                break
            else:
                self.assertEqual(1, len(trades))
        # print(curADX)

        # # time to sell
        # newData = pd.DataFrame([["2021-03-18T16:20:00Z", 59.5, 0.8]],
        #                        columns=["date", "open_price_y", "premium"])
        # df = df.append(newData.set_index("date"))

        # curPremium, curMarketPrice, recordDate = strategy.get_current_premium(
        #     df)

        # strategy.make_decision(acct, df, {}, 'GBTC')
        # trades = acct.trades

        # # Verify trade record
        # self.assertEqual(1, len(trades))
        # self.assertTrue(trades[-1].isComplete())
        # self.assertEqual(59.5, trades[-1].sellPrice)
        # self.assertEqual(59.5, trades[-1].sellValue)
        # self.assertEqual(recordDate, trades[-1].sellDate)

        # # Verify account status after buy and sell
        # self.assertEqual(0, acct.sharesOnHold)
        # self.assertEqual(100 - 52.5 + 59.5, acct.purchasePower)

        # buyDf, sellDf = acct.create_trades_records()
        # self.assertEqual(1, buyDf.shape[0])
        # self.assertEqual(52.5, buyDf["purchase_price"][0])
        # self.assertEqual(1, sellDf.shape[0])
        # self.assertEqual(59.5, sellDf["sell_price"][0])

    
if __name__ == '__main__':
        unittest.main()