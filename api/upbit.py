# -*- coding: utf-8 -*-

import os
import jwt
import uuid
import requests
import hashlib
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv(verbose=False)


class UPBitApi:
    """UPBIT api
    https://docs.upbit.com/reference
    """

    def __init__(self):
        self.access_key = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
        self.secret_key = os.environ["UPBIT_OPEN_API_SECRET_KEY"]
        self.server_url = os.environ["UPBIT_OPEN_API_SERVER_URL"]

    def get_market_all(self):
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

    def get_orders_chance(self, market):
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

    def get_accounts(self):
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

    def _request_get(self, url, params=None, headers=None):
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json()