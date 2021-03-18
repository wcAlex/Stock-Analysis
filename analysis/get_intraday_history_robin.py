from robin_stocks import *

import robin_stocks.robinhood as r
import pandas as pd

from datetime import date

# check below two places for how to use robinhood api.
# https://algotrading101.com/learn/robinhood-api-guide/
# https://robin-stocks.readthedocs.io/en/latest/quickstart.html 

# Don't check in your username and password
login = r.login("xxxxx", "xxxx")

def list_my_stock_holdings():
    my_stocks = r.build_holdings()
    for key,value in my_stocks.items():
        print(key,value)

def get_history_data():

    # Sample of 
    # tesla_data= r.stocks.get_stock_historicals("TSLA", interval="hour", span="3month")
    # tesla_dataframe = pd.DataFrame(tesla_data)
    # tesla_dataframe.to_excel("stocks.xlsx", sheet_name="tsla_hour_3m_" + date.today().strftime("%d_%m_%Y"))

    output_excel = "stocks_"+ date.today().strftime("%d_%m_%Y") + ".xlsx"

    # Get GBTC hourly data, from testing, robinhood only allows querying hour interval data for last 3 month.
    # Will return error if you ask longer span.
    gbtc_data= r.stocks.get_stock_historicals("GBTC", interval="hour", span="3month")
    gbtc_dataframe = pd.DataFrame(gbtc_data)
    # gbtc_dataframe.to_excel(output_excel, sheet_name="gbtc_hour_3m")

    # We could only get a week data for 5 minutes interval.
    gbtc_data= r.stocks.get_stock_historicals("GBTC", interval="5minute", span="week")
    gbtc_dataframe2 = pd.DataFrame(gbtc_data)
    # gbtc_dataframe2.to_excel(output_excel, sheet_name="gbtc_5min_1week")

    btc_data = r.crypto.get_crypto_historicals("BTC", interval="hour", span="3month")
    btc_dataframe= pd.DataFrame(btc_data)
    # btc_dataframe.to_excel(output_excel, sheet_name="btc_hour_3m")

    btc_data = r.crypto.get_crypto_historicals("BTC", interval="5minute", span="week")
    btc_dataframe2= pd.DataFrame(btc_data)
    # btc_dataframe2.to_excel(output_excel, sheet_name="btc_5min_1week")

    with pd.ExcelWriter(output_excel) as writer:  
        gbtc_dataframe.to_excel(writer, sheet_name='gbtc_hour_3m')
        gbtc_dataframe2.to_excel(writer, sheet_name='gbtc_5min_1week')
        btc_dataframe.to_excel(writer, sheet_name='btc_hour_3m')
        btc_dataframe2.to_excel(writer, sheet_name='btc_5min_1week')

get_history_data()