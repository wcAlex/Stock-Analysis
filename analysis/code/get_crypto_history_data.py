from coinbase.public_client import PublicClient
import pandas as pd
import datetime
import time


class MinuteK(object):
    def __init__(self, time, low, high, open, close, volume):
        self.date = datetime.datetime.utcfromtimestamp(time)
        self.low_price = low
        self.high_price = high
        self.close_price = close
        self.open_price = open
        self.volume = volume
        self.time = time

# fetch crypto history data from Coinbase


def get_history_data(cryptoId='BTC-USD', startDate='2021-03-31', endDate='2020-04-01', intervalInS=60, save=False, dest_location="./../data/raw"):

    public_client = PublicClient()

    hour_list = pd.date_range(startDate, endDate, freq='H')
    trades = list()
    for i, _ in enumerate(hour_list):
        if i == 0:
            continue

        hourly_minute_trades = public_client.get_product_historic_rates(product_id=cryptoId,
                                                                        start=(
                                                                            hour_list[i-1]).isoformat(),
                                                                        end=(
                                                                            hour_list[i]).isoformat(),
                                                                        granularity=intervalInS)
        trades.extend(hourly_minute_trades)

        time.sleep(0.5)

        print("fetched {0} data during {1} and {2}".format(
            cryptoId, (hour_list[i-1]).isoformat(), (hour_list[i]).isoformat()))

        # [
        #     [ time, low, high, open, close, volume ],
        #     [ 1415398768, 0.32, 4.2, 0.35, 4.2, 12.3 ],
        #     ...
        # ]

    # set date as index, sort and remove duplicates.
    df = pd.DataFrame(
        [vars(MinuteK(t[0], t[1], t[2], t[3], t[4], t[5])) for t in trades])
    df = df.set_index("date")
    df = df.sort_index()
    df = df.drop_duplicates()

    if save:
        df.to_csv(dest_location)
        print("finish saving data {0}".format(dest_location))

    return df


destLocPattern = "./analysis/data/raw/{0}_{1}_{2}_{3}.csv"
start = '2020-06-01'
# start = '2020-12-01'
# end = '2020-12-02'
end = '2021-04-18'

cryptoSymbol = 'BTC-USD'
btcDf = get_history_data(cryptoId=cryptoSymbol, startDate=start, endDate=end,
                         intervalInS=60, save=True, dest_location=destLocPattern.format(cryptoSymbol.lower(), "minute", start, end))
# print(pd)

cryptoSymbol = 'ETH-USD'
ethDf = get_history_data(cryptoId=cryptoSymbol, startDate=start, endDate=end,
                         intervalInS=60, save=True, dest_location=destLocPattern.format(cryptoSymbol.lower(), "minute", start, end))
