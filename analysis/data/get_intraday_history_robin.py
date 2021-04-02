from robin_stocks import *

import robin_stocks.robinhood as r
import pandas as pd
import os

from datetime import date

# check below two places for how to use robinhood api.
# https://algotrading101.com/learn/robinhood-api-guide/
# https://robin-stocks.readthedocs.io/en/latest/quickstart.html 

# Don't check in your username and password
login = r.login("colorinpiano@gmail.com", "MoreMoneyMoreFree@2020")

def list_my_stock_holdings():
    my_stocks = r.build_holdings()
    for key,value in my_stocks.items():
        print(key,value)

def get_history_data(symbol, crypto_symbol, combine_with_crypto=True):
    
    symbol = symbol.upper()

    # hourly and daily data could give you a general trend
    stock_hourly_data= r.stocks.get_stock_historicals(symbol, interval="hour", span="3month")
    stock_hourly_dataframe = pd.DataFrame(stock_hourly_data)

    stock_daily_data= r.stocks.get_stock_historicals(symbol, interval="day", span="year")
    stock_daily_dataframe = pd.DataFrame(stock_daily_data)

    # The maximum time range for 5 minutes interval data is a week.
    stock_5min_data= r.stocks.get_stock_historicals(symbol, interval="5minute", span="week")
    stock_5min_dataframe = pd.DataFrame(stock_5min_data)

    symbol = symbol.lower()
    
    raw_data_dir = "data/raw"
    if not os.path.exists(raw_data_dir):
        os.makedirs(raw_data_dir)

    stock_hourly_dataframe.to_csv("{0}/{1}_hourly_3months_{2}.csv".format(raw_data_dir, symbol, date.today().strftime("%d_%m_%Y")), index=False)
    stock_daily_dataframe.to_csv("{0}/{1}_daily_1year_{2}.csv".format(raw_data_dir, symbol, date.today().strftime("%d_%m_%Y")), index=False)
    stock_5min_dataframe.to_csv("{0}/{1}_5min_1week_{2}.csv".format(raw_data_dir, symbol, date.today().strftime("%d_%m_%Y")), index=False)

    if combine_with_crypto:
        # join stock with crypto
        crypto_symbol = crypto_symbol.upper()

        crypto_hourly_data = r.crypto.get_crypto_historicals(crypto_symbol, interval="hour", span="3month")
        crypto_hourly_dataframe= pd.DataFrame(crypto_hourly_data)

        crypto_daily_data = r.crypto.get_crypto_historicals(crypto_symbol, interval="day", span="year")
        crypto_daily_dataframe = pd.DataFrame(crypto_daily_data)

        crypto_5min_data = r.crypto.get_crypto_historicals(crypto_symbol, interval="5minute", span="week")
        crypto_5min_dataframe= pd.DataFrame(crypto_5min_data)

        # join crypto price history with stock, crypto trades 24x7, so it's left join
        crypto_symbol = crypto_symbol.lower()

        crypto_stock_combined_hourly_dataframe = pd.merge(crypto_hourly_dataframe, stock_hourly_dataframe, on="begins_at", how="left")
        crypto_stock_combined_daily_dataframe = pd.merge(crypto_daily_dataframe, stock_daily_dataframe, on="begins_at", how="left")
        crypto_stock_combined_5min_dataframe = pd.merge(crypto_5min_dataframe, stock_5min_dataframe, on="begins_at", how="left")
        
        # Save combined data, leave the post-process a in separate notebook.
        data_dir = "data/{0}_{1}".format(crypto_symbol, symbol)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        crypto_stock_combined_5min_dataframe.to_csv("{0}/{1}_{2}_5min_weekly_combined_{3}.csv".format(data_dir, crypto_symbol, symbol, date.today().strftime("%d_%m_%Y")), index=False)
        crypto_stock_combined_hourly_dataframe.to_csv("{0}/{1}_{2}_hour_3months_combined_{3}.csv".format(data_dir, crypto_symbol, symbol, date.today().strftime("%d_%m_%Y")), index=False)
        crypto_stock_combined_daily_dataframe.to_csv("{0}/{1}_{2}_daily_year_combined_{3}.csv".format(data_dir, crypto_symbol, symbol, date.today().strftime("%d_%m_%Y")), index=False)

### Grayscale trust
# Grayscale Bitcoin Trust (OTCQX: GBTC), Grayscale Bitcoin Cash Trust (OTCQX: BCHG), 
# Grayscale Ethereum Trust, (OTCQX: ETHE), Grayscale Ethereum Classic Trust (OTCQX: ETCG), 
# Grayscale Litecoin Trust (OTCQX: LTCN), and Grayscale Digital Large Cap Fund (OTCQX: GDLC)

# Currently I could only get GBTC from robinhood and couldn't trade on it, probably need to move to futu api.
get_history_data("GBTC", "BTC")



# deprecated, left the code here for future reference
# def get_history_data():

#     # Sample of 
#     # tesla_data= r.stocks.get_stock_historicals("TSLA", interval="hour", span="3month")
#     # tesla_dataframe = pd.DataFrame(tesla_data)
#     # tesla_dataframe.to_excel("stocks.xlsx", sheet_name="tsla_hour_3m_" + date.today().strftime("%d_%m_%Y"))

#     # output_excel = "stocks_"+ date.today().strftime("%d_%m_%Y") + ".xlsx"

#     # Get GBTC hourly data, from testing, robinhood only allows querying hour interval data for last 3 month.
#     # Will return error if you ask longer span.
#     gbtc_data= r.stocks.get_stock_historicals("GBTC", interval="hour", span="3month")
#     gbtc_dataframe = pd.DataFrame(gbtc_data)
#     # gbtc_dataframe.to_excel(output_excel, sheet_name="gbtc_hour_3m")

#     obtc_data= r.stocks.get_stock_historicals("OBTC", interval="hour", span="3month")
#     obtc_dataframe = pd.DataFrame(obtc_data)

#     # We could only get a week data for 5 minutes interval.
#     gbtc_data= r.stocks.get_stock_historicals("GBTC", interval="5minute", span="week")
#     gbtc_dataframe2 = pd.DataFrame(gbtc_data)
#     # gbtc_dataframe2.to_excel(output_excel, sheet_name="gbtc_5min_1week")

#     # obtc is not on robinhood 
#     # obtc_data= r.stocks.get_stock_historicals("OBTC", interval="5minute", span="week")
#     # obtc_dataframe2 = pd.DataFrame(obtc_data)

#     gbtc_daily_data= r.stocks.get_stock_historicals("GBTC", interval="day", span="year")
#     gbtc_daily_dataframe = pd.DataFrame(gbtc_daily_data)

#     btc_data = r.crypto.get_crypto_historicals("BTC", interval="hour", span="3month")
#     btc_dataframe= pd.DataFrame(btc_data)
#     # btc_dataframe.to_excel(output_excel, sheet_name="btc_hour_3m")

#     btc_gbtc_combined_hour_dataframe = pd.merge(btc_dataframe, gbtc_dataframe, on="begins_at", how="left")
#     # btc_obtc_combined_hour_dataframe = pd.merge(btc_dataframe, obtc_dataframe, on="begins_at", how="left")

#     btc_data = r.crypto.get_crypto_historicals("BTC", interval="5minute", span="week")
#     btc_dataframe2= pd.DataFrame(btc_data)

#     btc_daily_data = r.crypto.get_crypto_historicals("BTC", interval="day", span="year")
#     btc_daily_dataframe = pd.DataFrame(btc_daily_data)

#     # btc_dataframe2.to_excel(output_excel, sheet_name="btc_5min_1week")

#     btc_gbtc_combined_5min_dataframe = pd.merge(btc_dataframe2, gbtc_dataframe2, on="begins_at", how="left")
#     # btc_obtc_combined_5min_dataframe = pd.merge(btc_dataframe2, obtc_dataframe2, on="begins_at", how="left")

#     combined_daily_dataframe = pd.merge(btc_daily_dataframe, gbtc_daily_dataframe, on="begins_at", how="left")
    
#     # Save combined data, leave the post-process a in separate notebook.
#     btc_gbtc_combined_5min_dataframe.to_csv("data/btc_gbtc_5min_weekly_combined_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
#     # btc_obtc_combined_5min_dataframe.to_csv("data/btc_obtc_5min_weekly_combined_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)

#     btc_gbtc_combined_hour_dataframe.to_csv("data/btc_gbtc_hour_3months_combined_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
#     # btc_obtc_combined_hour_dataframe.to_csv("data/btc_obtc_hour_3months_combined_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
    
#     combined_daily_dataframe.to_csv("data/btc_gbtc_daily_year_combined_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)

#     # Save gbtc and obtc data, use for verify the combined data.
#     gbtc_dataframe2.to_csv("data/gbtc_5min_weekly_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
#     gbtc_dataframe.to_csv("data/gbtc_hour_3months_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
    
    # obtc_dataframe2.to_csv("data/obtc_5min_weekly_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
    # obtc_dataframe.to_csv("data/obtc_hour_3months_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
    
    # Stop use excel, the visualization is not that great!
    # with pd.ExcelWriter(output_excel) as writer:  
    #     # combined_hour_dataframe.to_excel(writer, sheet_name="combine_values")
    #     # gbtc_dataframe.to_excel(writer, sheet_name='gbtc_hour_3m')
    #     # gbtc_dataframe2.to_excel(writer, sheet_name='gbtc_5min_1week')
    #     # btc_dataframe.to_excel(writer, sheet_name='btc_hour_3m')
    #     # btc_dataframe2.to_excel(writer, sheet_name='btc_5min_1week')


    # print("finished ...")

# get_history_data()