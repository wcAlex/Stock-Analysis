from futu import *
import pandas as pd

# Fetch history minutes Kline data from FUTU


def fetch_stock_mink(symbol='US.GBTC', startDate='2019-09-11', endDate='2019-09-18', countPerPage=400) -> pd.DataFrame:

    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    ret, minK, page_req_key = quote_ctx.request_history_kline(
        symbol, start=startDate, end=endDate, ktype=KLType.K_1M, max_count=countPerPage)  # 每页5个，请求第一页
    if ret == RET_OK:
        print('page request key ' + str(page_req_key))
    else:
        print('error:', minK)
    while page_req_key != None:  # 请求后面的所有结果
        print('*************************************')
        ret, data, page_req_key = quote_ctx.request_history_kline(
            symbol, start=startDate, end=endDate, ktype=KLType.K_1M, max_count=countPerPage, page_req_key=page_req_key)  # 请求翻页后的数据
        if ret == RET_OK:
            minK = minK.append(data)
        else:
            print('error:', data)
    print('All pages are finished!')
    quote_ctx.close()

    # FUTU data is EDT timezone
    return minK.rename(columns={'time_key': 'date_edt'})


start = '2020-06-01'
end = '2020-06-02'
# end = '2021-05-06'

destLocPattern = "./analysis/data/raw/{0}_{1}_{2}_{3}.csv"

# GBTC
gbtcData = fetch_stock_mink(
    symbol='US.GBTC', startDate=start, endDate=end, countPerPage=400)
gbtcData.to_csv(destLocPattern.format('futu_gbtc', "minute", start, end))

# OBTC
# start = '2021-01-01'
# gbtcData = fetch_stock_mink(
#     symbol='US.OBTC', startDate=start, endDate=end, countPerPage=400)
# gbtcData.to_csv(destLocPattern.format('futu_obtc', "minute", start, end))

# # ETHE
# start = '2020-06-01'
# gbtcData = fetch_stock_mink(
#     symbol='US.ETHE', startDate=start, endDate=end, countPerPage=400)
# gbtcData.to_csv(destLocPattern.format('futu_ethe', "minute", start, end))
