from robin_stocks import *

import robin_stocks.robinhood as r
import pandas as pd

from datetime import date

# check below two places for how to use robinhood api.
# https://algotrading101.com/learn/robinhood-api-guide/
# https://robin-stocks.readthedocs.io/en/latest/quickstart.html 

# Don't check in your username and password
login = r.login("xxxx", "xxxxx")

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

    gbtc_daily_data= r.stocks.get_stock_historicals("GBTC", interval="day", span="year")
    gbtc_daily_dataframe = pd.DataFrame(gbtc_daily_data)

    btc_data = r.crypto.get_crypto_historicals("BTC", interval="hour", span="3month")
    btc_dataframe= pd.DataFrame(btc_data)
    # btc_dataframe.to_excel(output_excel, sheet_name="btc_hour_3m")

    combined_hour_dataframe = pd.merge(btc_dataframe, gbtc_dataframe, on="begins_at", how="left")
    
    btc_data = r.crypto.get_crypto_historicals("BTC", interval="5minute", span="week")
    btc_dataframe2= pd.DataFrame(btc_data)

    btc_daily_data = r.crypto.get_crypto_historicals("BTC", interval="day", span="year")
    btc_daily_dataframe = pd.DataFrame(btc_daily_data)

    # btc_dataframe2.to_excel(output_excel, sheet_name="btc_5min_1week")

    combined_5min_dataframe = pd.merge(btc_dataframe2, gbtc_dataframe2, on="begins_at", how="left")

    combined_daily_dataframe = pd.merge(btc_daily_dataframe, gbtc_daily_dataframe, on="begins_at", how="left")
    
    # Save combined data, leave the post-process a in separate notebook.
    combined_5min_dataframe.to_csv("data/btc_gbtc_5min_weekly_combined_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
    combined_hour_dataframe.to_csv("data/btc_gbtc_hour_3months_combined_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
    combined_daily_dataframe.to_csv("data/btc_gbtc_daily_year_combined_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)

    # Save gbtc data, use for verify the combined data.
    gbtc_dataframe2.to_csv("data/gbtc_5min_weekly_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
    gbtc_dataframe.to_csv("data/gbtc_hour_3months_" + date.today().strftime("%d_%m_%Y") + ".csv", index=False)
    
    # Stop use excel, the visualization is not that great!
    # with pd.ExcelWriter(output_excel) as writer:  
    #     # combined_hour_dataframe.to_excel(writer, sheet_name="combine_values")
    #     # gbtc_dataframe.to_excel(writer, sheet_name='gbtc_hour_3m')
    #     # gbtc_dataframe2.to_excel(writer, sheet_name='gbtc_5min_1week')
    #     # btc_dataframe.to_excel(writer, sheet_name='btc_hour_3m')
    #     # btc_dataframe2.to_excel(writer, sheet_name='btc_5min_1week')


    print("finished ...")

get_history_data()