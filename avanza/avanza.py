
from typing import Callable, Sequence, Any

import hashlib

import requests
import pyotp

from datetime import date

from .constants import (
    ChannelType,
    HttpMethod,
    InstrumentType,
    ListType,
    OrderType,
    Route,
    TimePeriod
)

from .avanza_socket import AvanzaSocket

BASE_URL = 'https://www.avanza.se'
MIN_INACTIVE_MINUTES = 30
MAX_INACTIVE_MINUTES = 60 * 24


class Avanza:
    def __init__(self, credentials):
        self._authenticationTimeout = MAX_INACTIVE_MINUTES
        self._session = requests.Session()

        response_body, credentials = self.__authenticate(credentials)

        self._credentials = credentials
        self._authentication_session = response_body['authenticationSession']
        self._push_subscription_id = response_body['pushSubscriptionId']
        self._customer_id = response_body['customerId']

        self._socket = AvanzaSocket(
            self._push_subscription_id,
            self._session.cookies.get_dict()
        )

    def __authenticate(self, credentials):
        if not MIN_INACTIVE_MINUTES <= self._authenticationTimeout <= MAX_INACTIVE_MINUTES:
            raise ValueError(f'Session timeout not in range {MIN_INACTIVE_MINUTES} - {MAX_INACTIVE_MINUTES} minutes')

        data = {
            'maxInactiveMinutes': self._authenticationTimeout,
            'username': credentials['username'],
            'password': credentials['password']
        }

        response = self._session.post(
            f"{BASE_URL}{Route.AUTHENTICATION_PATH.value}",
            json=data
        )

        response.raise_for_status()

        response_body = response.json()

        # No second factor required, continue with normal login
        if response_body.get('twoFactorLogin') is None:
            return response_body, credentials

        tfa_method = response_body['twoFactorLogin'].get('method')

        if tfa_method != 'TOTP':
            raise ValueError(
                f'Unsupported two factor method {tfa_method}'
            )

        return self.__validate_2fa(credentials)

    def __validate_2fa(self, credentials):
        totp = pyotp.TOTP(credentials['totpSecret'], digest=hashlib.sha1)
        totp_code = totp.now()

        if totp_code is None:
            raise ValueError('Failed to get totp code')

        response = self._session.post(
            f"{BASE_URL}{Route.TOTP_PATH.value}",
            json={
                'method': 'TOTP',
                'totpCode': totp_code
            }
        )

        response.raise_for_status()

        self._security_token = response.headers.get('X-SecurityToken')

        response_body = response.json()

        return response_body, credentials

    def __call(self, method: HttpMethod, path: str, options=None):
        method_call = {
            HttpMethod.GET: self._session.get,
            HttpMethod.POST: self._session.post,
            HttpMethod.PUT: self._session.put,
            HttpMethod.DELETE: self._session.delete
        }.get(method)

        if method_call is None:
            raise ValueError(f'Unknown method type {method}')

        response = method_call(
            f'{BASE_URL}{path}',
            json=options,
            headers={
                'X-AuthenticationSession': self._authentication_session,
                'X-SecurityToken': self._security_token
            }
        )

        response.raise_for_status()

        return response.json()

    async def subscribe_to_id(
        self,
        channel: ChannelType,
        id: str,
        callback: Callable[[str, dict], Any]
    ):
        await self.subscribe_to_ids(channel, [id], callback)

    async def subscribe_to_ids(
        self,
        channel: ChannelType,
        ids: Sequence[str],
        callback: Callable[[str, dict], Any]
    ):
        if not callable(callback):
            raise ValueError('callback parameter has to be a function!')

        if not self._socket._connected:
            await self._socket.init()

        await self._socket.subscribe_to_ids(
            channel,
            ids,
            callback
        )

    def get_overview(self):
        return self.__call(HttpMethod.GET, Route.OVERVIEW_PATH.value)

    def get_account_overview(self, account_id: str):
        return self.__call(
            HttpMethod.GET,
            Route.ACCOUNT_OVERVIEW_PATH.value.format(
                account_id
            )
        )

    def get_watchlists(self):
        return self.__call(HttpMethod.GET, Route.WATCHLISTS_PATH.value)

    def add_to_watchlist(
        self,
        instrument_id: int,
        watchlist_id: int
    ):
        return self.__call(
            HttpMethod.PUT,
            Route.WATCHLISTS_ADD_DELETE_PATH.value.format(
                watchlist_id,
                instrument_id
            )
        )

    def remove_from_watchlist(
        self,
        instrument_id: int,
        watchlist_id: int
    ):
        return self.__call(
            HttpMethod.DELETE,
            Route.WATCHLISTS_ADD_DELETE_PATH.value.format(
                watchlist_id,
                instrument_id
            )
        )

    def get_instrument(
        self,
        instrument_type: InstrumentType,
        instrument_id: int
    ):
        return self.__call(
            HttpMethod.GET,
            Route.INSTRUMENT_PATH.value.format(
                instrument_type.value,
                instrument_id
            )
        )

    def get_order_book(
        self,
        order_book_id: str,
        instrument_type: InstrumentType
    ):
        return self.__call(
            HttpMethod.GET,
            Route.ORDERBOOK_PATH.value.format(
                instrument_type.value,
                order_book_id
            )
        )

    def get_order_books(
        self,
        order_book_ids: Sequence[str]
    ):
        return self.__call(
            HttpMethod.GET,
            Route.ORDERBOOK_LIST_PATH.value.format(
                ','.join(order_book_ids)
            )
        )

    def get_positions(self):
        return self.__call(HttpMethod.GET, Route.POSITIONS_PATH.value)

    def get_insights_report(
        self,
        account_id: str,
        time_period: TimePeriod
    ):
        return self.__call(
            HttpMethod.GET,
            Route.INSIGHTS_PATH.value.format(
                time_period.value,
                account_id
            )
        )

    def get_deals_and_orders(self):
        return self.__call(
            HttpMethod.GET,
            Route.DEALS_AND_ORDERS_PATH.value
        )

    def get_inspiration_lists(self):
        return self.__call(
            HttpMethod.GET,
            Route.INSPIRATION_LIST_PATH.value.format('')
        )

    def get_inspiration_list(self, list_type: ListType):
        return self.__call(
            HttpMethod.GET,
            Route.INSPIRATION_LIST_PATH.value.format(
                list_type.value
            )
        )

    def get_chart_data(self, order_book_id: str, period: TimePeriod):
        return self.__call(
            HttpMethod.GET,
            Route.CHARTDATA_PATH.value.format(
                order_book_id,
                period.value.lower()
            )
        )

    def place_order(
        self,
        account_id: str,
        order_book_id: str,
        order_type: OrderType,
        price: float,
        valid_until: date,
        volume: int
    ):
        return self.__call(
            HttpMethod.POST,
            Route.ORDER_PLACE_PATH.value,
            {
                'accountId': account_id,
                'orderbookId': order_book_id,
                'orderType': order_type.value,
                'price': price,
                'validUntil': valid_until.isoformat(),
                'volume': volume
            }
        )

    def get_order(
        self,
        instrument_type: InstrumentType,
        account_id: str,
        order_id: str
    ):
        return self.__call(
            HttpMethod.GET,
            Route.ORDER_GET_PATH.value.format(
                instrument_type.value,
                account_id,
                order_id
            )
        )

    def delete_order(
        self,
        account_id: str,
        order_id: str
    ):
        return self.__call(
            HttpMethod.DELETE,
            Route.ORDER_DELETE_PATH.value.format(
                account_id,
                order_id
            )
        )
