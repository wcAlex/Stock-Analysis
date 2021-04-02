from futu import *

# Futu api and sdk: https://openapi.futunn.com/futu-api-doc/intro/authority.html
# Here are some useful samples

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)  # 创建行情对象
print(quote_ctx.get_market_snapshot('HK.00700'))  # 获取港股 HK.00700 的快照数据
quote_ctx.close() # 关闭对象，防止连接条数用尽

trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)  # 创建交易对象
print(trd_ctx.place_order(price=500.0, qty=100, code="HK.00700", trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE))  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）

trd_ctx.close()  # 关闭对象，防止连接条数用尽

# Acquire stock history data
# Try it after buying the Nasdaq Basic <Nasdaq Basic - Monthly Card>  
# https://qtcard.fututrade.com/buy?market_id=2&qtcard_channel=2&good_type=1022#/

# Doc: https://openapi.futunn.com/futu-api-doc/quote/request-history-kline.html
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data, page_req_key = quote_ctx.request_history_kline('TSLA', start='2019-09-11', end='2019-09-18', ktype=KLType.K_1M, max_count=50)  # 每页5个，请求第一页
if ret == RET_OK:
    print(data)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['close'].values.tolist())   # 第一页收盘价转为 list
else:
    print('error:', data)
while page_req_key != None:  # 请求后面的所有结果
    print('*************************************')
    ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2019-09-11', end='2019-09-18', max_count=5, page_req_key=page_req_key) # 请求翻页后的数据
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)
print('All pages are finished!')
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽