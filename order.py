import json

import dotenv
import logging
from api.upbit import UPBitApi, Market, OrderType

dotenv.load_dotenv(verbose=False)
log = logging.getLogger(f"mybit.{__name__}")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

api = UPBitApi()

# KRW-BTC 10,000 KRW 매수
response = api.order_bid(Market.KRW_BTC, OrderType.PRICE, price=10000)
print(json.dumps(response, indent=4))
# KRW-ETH 10,000 KRW 매수
response = api.order_bid(Market.KRW_ETH, OrderType.PRICE, price=10000)
print(json.dumps(response, indent=4))
