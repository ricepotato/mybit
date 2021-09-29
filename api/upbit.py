# -*- coding: utf-8 -*-

import os
import jwt
import uuid
import requests
import hashlib
import enum
import logging
import functools
from urllib.parse import urlencode


log = logging.getLogger(f"mybit.{__name__}")


def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            log.error(e)
            raise

    return wrapper


class OrderType(enum.Enum):
    LIMIT = "limit"  # 지정가 주문
    PRICE = "price"  # 시장가 주문 (매수)
    MARKET = "market"  # 시장가 주문 (매도)


class Market(enum.Enum):
    KRW_BTC = "KRW-BTC"  # 원화/비트코인 마켓
    KRW_ETH = "KRW-ETH"  # 원화/이더리움 마켓


class Side(enum.Enum):
    BID = "bid"  # 매수
    ASK = "ask"  # 매도


class UPBitApi:
    """UPBIT api
    https://docs.upbit.com/reference
    """

    def __init__(self):
        self.access_key = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
        self.secret_key = os.environ["UPBIT_OPEN_API_SECRET_KEY"]
        self.server_url = os.environ["UPBIT_OPEN_API_SERVER_URL"]

    def get_market_all(self) -> list:
        """마켓 코드 조회
        업비트에서 거래 가능한 마켓 목록

        Returns:
          거래 가능 마켓 list

          [
                {
                    "market": "KRW-BTC",
                    "korean_name": "비트코인",
                    "english_name": "Bitcoin"
                },
                ...
            ]

        """
        return self._request_get(
            f"{self.server_url}/v1/market/all", params={"isDetails": "false"}
        )

    def get_orders_chance(self, market: str) -> dict:
        """주문 가능 정보
        마켓별 주문 가능 정보를 확인한다.

        Args:
          market:
            market id

        Returns:
          주문 가능정보 dict

          example:
          {
            "bid_fee": "0.0015",
            "ask_fee": "0.0015",
            "market": {
                "id": "KRW-BTC",
                "name": "BTC/KRW",
                "order_types": [
                "limit"
                ],
                "order_sides": [
                "ask",
                "bid"
                ],
                "bid": {
                "currency": "KRW",
                "price_unit": null,
                "min_total": 1000
                },
                "ask": {
                "currency": "BTC",
                "price_unit": null,
                "min_total": 1000
                },
                "max_total": "100000000.0",
                "state": "active",
            },
            "bid_account": {
                "currency": "KRW",
                "balance": "0.0",
                "locked": "0.0",
                "avg_buy_price": "0",
                "avg_buy_price_modified": false,
                "unit_currency": "KRW",
            },
            "ask_account": {
                "currency": "BTC",
                "balance": "10.0",
                "locked": "0.0",
                "avg_buy_price": "8042000",
                "avg_buy_price_modified": false,
                "unit_currency": "KRW",
            }
            }
        """
        query = {
            "market": market,
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4()),
            "query_hash": query_hash,
            "query_hash_alg": "SHA512",
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = "Bearer {}".format(jwt_token)
        headers = {"Authorization": authorize_token}
        return self._request_get(
            f"{self.server_url}/v1/orders/chance", params=query, headers=headers
        )

    def get_accounts(self) -> list:
        """전체 계좌 조회
        내가 보유한 자산 리스트를 보여줍니다.

        Returns:
          자산 리스트를 보여줍니다. list type

          example:
          [
            {
                "currency": "KRW",
                "balance": "19966.54137189",
                "locked": "0.0",
                "avg_buy_price": "0",
                "avg_buy_price_modified": true,
                "unit_currency": "KRW"
            },
            {
                "currency": "BTC",
                "balance": "0.00026823",
                "locked": "0.0",
                "avg_buy_price": "69890000",
                "avg_buy_price_modified": false,
                "unit_currency": "KRW"
            },
            {
                "currency": "DOGE",
                "balance": "56.54828508",
                "locked": "0.0",
                "avg_buy_price": "601.84",
                "avg_buy_price_modified": false,
                "unit_currency": "KRW"
            }
        ]
        """
        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = "Bearer {}".format(jwt_token)
        headers = {"Authorization": authorize_token}
        return self._request_get(f"{self.server_url}/v1/accounts", headers=headers)

    def deposits_krw(self, amount_krw: int):
        """원화 입금하기

        Args:
          amount_krw (int): 입금 금액(원)

        Returns:
        {
            "type": "deposit",
            "uuid": "9f432943-54e0-40b7-825f-b6fec8b42b79",
            "currency": "KRW",
            "txid": "ebe6937b-130e-4066-8ac6-4b0e67f28adc",
            "state": "processing",
            "created_at": "2018-04-13T11:24:01+09:00",
            "done_at": null,
            "amount": "10000",
            "fee": "0.0",
            "transaction_type": "default"
        }
        """

        query = {"amount": str(amount_krw)}
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4()),
            "query_hash": query_hash,
            "query_hash_alg": "SHA512",
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = "Bearer {}".format(jwt_token)
        headers = {"Authorization": authorize_token}
        return self._request_post(
            f"{self.server_url}/v1/deposits/krw", params=query, headers=headers
        )

    def order_bid(
        self,
        market: Market,
        order_type: OrderType,
        volume: int = None,
        price: int = None,
    ) -> dict:
        """매수 주문 요청

        price:
        KRW-BTC 마켓에서 1BTC 당 1,000 KRW 로 거래할 경우, 값은 1000
        KRW-BTC 마켓에서 1BTC 당 매도 1 호가가 500 KRW 인 경우, 시장가 매수 시 값을 1000으로 세팅하면 2BTC 가 매수됨
        최소 주문 가격 5,000 KRW

        order_type:
        - OrderType.LIMIT: 지정가 주문
        - OrderType.PRICE: 시장가 주문(매수)
        - OrderType.MARKET: 시장가 주문(매도)

        Args:
        market (Market): 마켓
        order_type (OrderType): 주문 타입
        volume (int): 주문 수량 (지정가, 시장가 매도 시 필수)
        price (int): 주문 가격 (지정가, 시장가 매수 시 필수)

        Return:
        {
            "uuid":"cdd92199-2897-4e14-9448-f923320408ad",
            "side":"bid",
            "ord_type":"limit",
            "price":"100.0",
            "avg_price":"0.0",
            "state":"wait",
            "market":"KRW-BTC",
            "created_at":"2018-04-10T15:42:23+09:00",
            "volume":"0.01",
            "remaining_volume":"0.01",
            "reserved_fee":"0.0015",
            "remaining_fee":"0.0015",
            "paid_fee":"0.0",
            "locked":"1.0015",
            "executed_volume":"0.0",
            "trades_count":0
        }

        """
        query = {"market": market.value, "side": "bid", "ord_type": order_type.value}
        if volume is not None:
            query["volume"] = str(volume)
        if price is not None:
            query["price"] = str(price)

        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4()),
            "query_hash": query_hash,
            "query_hash_alg": "SHA512",
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = "Bearer {}".format(jwt_token)
        headers = {"Authorization": authorize_token}
        return self._request_post(
            f"{self.server_url}/v1/orders", params=query, headers=headers
        )

    def _request_get(self, url, params=None, headers=None):
        return self._request_tmpl(requests.get, url, params, headers)

    def _request_post(self, url, params=None, headers=None):
        return self._request_tmpl(requests.post, url, params, headers)

    def _request_tmpl(self, req_func, url, params, headers):
        r = req_func(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json()
