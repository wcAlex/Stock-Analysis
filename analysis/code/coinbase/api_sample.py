# Coinbase API samples

# Coinbase Authentication
# https://docs.pro.coinbase.com/#authentication

# [Coinbase Official Doc] Get crypto coin history data
# https://docs.pro.coinbase.com/#get-historic-rates

# [Unofficial Coinbase Client SDK] https://github.com/danpaquin/coinbasepro-python
# Follow code examples there.

import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from auth_client import AuthenticatedClient
from public_client import PublicClient
# from analysis.code.coinbase.auth_client import AuthenticatedClient

### Option 1: use public restful api directly.

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')

        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

    #     def get_auth_headers(timestamp, message, api_key, secret_key, passphrase):
    # message = message.encode('ascii')
    # hmac_key = base64.b64decode(secret_key)
    # signature = hmac.new(hmac_key, message, hashlib.sha256)
    # signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
    # return {
    #     'Content-Type': 'Application/JSON',
    #     'CB-ACCESS-SIGN': signature_b64,
    #     'CB-ACCESS-TIMESTAMP': timestamp,
    #     'CB-ACCESS-KEY': api_key,
    #     'CB-ACCESS-PASSPHRASE': passphrase
    # }

# Making sure not checking this to git repo
API_KEY = 'xxx'
API_SECRET = 'xxxx'
API_PASS = 'xxxx'

api_url = 'https://api.pro.coinbase.com/'

auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)

# Get accounts
r = requests.get(api_url + 'accounts', auth=auth)
# print (r.json())
# [{"id": "a1b2c3d4", "balance":...

# Place an order
# order = {
#     'size': 1.0,
#     'price': 1.0,
#     'side': 'buy',
#     'product_id': 'BTC-USD',
# }
# r = requests.post(api_url + 'orders', json=order, auth=auth)
# print r.json()
# {"id": "0428b97b-bec1-429e-a94c-59992926778d"}


### Option 2: use python sdk, I copy the sdk code from https://github.com/danpaquin/coinbasepro-python and made some modification
# the main reason to do this is package conficts makes me couldn't install cbpro package fully.


auth_client = AuthenticatedClient(API_KEY, API_SECRET, API_PASS)

js = auth_client.get_accounts()
# print(js)

### Option 3, use public client to get crypto information

public_client = PublicClient()
eth_history_js = public_client.get_product_historic_rates(product_id='ETH-USD', start='2020-11-14T20:46:03.511254Z', end='2020-11-14T21:46:03.511254Z', granularity=60)
print(eth_history_js)

eth_trades_fetch = public_client.get_product_trades(product_id='ETH-USD')
res = eth_trades_fetch.send()
print(res)
