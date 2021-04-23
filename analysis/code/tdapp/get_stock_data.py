from numpy.lib.npyio import save
from pandas.core.frame import DataFrame
from tda import auth, client
import json
import pandas as pd
import datetime
import time


"""
After research, I choose to use tda-api (https://tda-api.readthedocs.io/en/latest/index.html) as the trading sdk for 
communicating with td-ameritrade server.
"""


def get_tdaclient() -> client.Client:
    token_path = '/tmp/tdtrade/td_token'
    # DON'T checkin the api_key!! find key in td-ameritrade's developer account.  https://developer.tdameritrade.com/user/me/apps
    api_key = 'xxxxxxxx'
    redirect_uri = 'https://localhost:8080/snowtree/oauth/callback'
    try:
        # Try to use local cached token file
        c = auth.client_from_token_file(token_path, api_key)
    except FileNotFoundError:
        from selenium import webdriver
        # the driver need to match the local chrome version
        # https://chromedriver.chromium.org/downloads
        with webdriver.Chrome('/Users/chi.wang/workspace/cw/Stock-Analysis/analysis/code/tdapp/chromedriver') as driver:
            # This is for the initial local setup, login with trading account and store token to local.
            # See more details here: https://tda-api.readthedocs.io/en/latest/auth.html#fetching-a-token-and-creating-a-client
            c = auth.client_from_login_flow(
                driver, api_key, redirect_uri, token_path)

    return c


def get_history_sample():
    c = get_tdaclient()
    r = c.get_price_history('AAPL',
                            period_type=client.Client.PriceHistory.PeriodType.YEAR,
                            period=client.Client.PriceHistory.Period.TWENTY_YEARS,
                            frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
                            frequency=client.Client.PriceHistory.Frequency.DAILY)
    assert r.status_code == 200, r.raise_for_status()
    print(json.dumps(r.json(), indent=4))


# get_history_sample()

def get_gbtc():
    c = get_tdaclient()
    r = c.get_price_history('GBTC',
                            period_type=client.Client.PriceHistory.PeriodType.DAY,
                            period=client.Client.PriceHistory.Period.ONE_DAY,
                            frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE,
                            frequency=client.Client.PriceHistory.Frequency.EVERY_MINUTE)
    assert r.status_code == 200, r.raise_for_status()
    print(json.dumps(r.json(), indent=4))


def unix_time_millis(dt, baseEpoch):
    return (dt - baseEpoch).total_seconds() * 1000.0


def get_history_data(stockSymbol='GBTC', startDate='2021-03-31', endDate='2020-04-01', save=False, dest_location="./../data/raw") -> DataFrame:

    c = get_tdaclient()
    # epoch = datetime.datetime.utcfromtimestamp(0)

    data = []
    day_list = pd.date_range(startDate, endDate, freq='D')
    trades = list()
    for i, _ in enumerate(day_list):
        if i == 0:
            continue

        response = c.get_price_history(stockSymbol,
                                       frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE,
                                       frequency=client.Client.PriceHistory.Frequency.EVERY_MINUTE,
                                       start_datetime=day_list[i-1],
                                       end_datetime=day_list[i])
        #   start_datetime=int(
        #       unix_time_millis(day_list[i-1], epoch)),
        #   end_datetime=int(unix_time_millis(day_list[i], epoch)))

        time.sleep(1)

        if 200 != response.status_code:
            print("Fail to pull {} minute data between {} and {}".format(
                stockSymbol, day_list[i-1], day_list[i]))
            continue

        content = json.loads(response.content)
        if len(data):
            data['candles'].extend(content['candles'])
        else:
            data = content

    df = pd.DataFrame(data['candles'])
    df['date'] = pd.to_datetime(df['datetime']/1000, unit='s', utc=True)
    df = df.set_index("date")
    df = df.sort_index()
    df = df.drop_duplicates()

    if save:
        df.to_csv(dest_location)
        print("finish saving data {0}".format(dest_location))

    return df


destLocPattern = "./analysis/data/raw/{0}_{1}_{2}_{3}.csv"
start = '2020-12-01'
end = '2021-04-18'
# start = '2021-04-13'
# end = '2021-04-15'

stockSymbol = 'GBTC'
gbtcDf = get_history_data(stockSymbol=stockSymbol,
                          startDate=start, endDate=end, save=True,
                          dest_location=destLocPattern.format(stockSymbol.lower(), "minute", start, end))
print(gbtcDf)

stockSymbol = 'OBTC'
gbtcDf = get_history_data(stockSymbol=stockSymbol,
                          startDate=start, endDate=end, save=True,
                          dest_location=destLocPattern.format(stockSymbol.lower(), "minute", start, end))
print(gbtcDf)
