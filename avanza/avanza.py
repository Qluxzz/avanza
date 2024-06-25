from datetime import date
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

import requests

from avanza.entities import StopLossOrderEvent, StopLossTrigger
from avanza.models import *

from .avanza_socket import AvanzaSocket
from .constants import (
    ChannelType,
    HttpMethod,
    InsightsReportTimePeriod,
    InstrumentType,
    ListType,
    OrderType,
    Resolution,
    Route,
    TimePeriod,
    TransactionsDetailsType,
)
from .credentials import BaseCredentials, backwards_compatible_serialization

BASE_URL = "https://www.avanza.se"
MIN_INACTIVE_MINUTES = 30
MAX_INACTIVE_MINUTES = 60 * 24


class Avanza:
    def __init__(self, credentials: Union[BaseCredentials, Dict[str, str]]):
        """

        Args:

            credentials: Login credentials. Can be multiple variations
                Either an instance of TokenCredentials or of SecretCredentials
                Or a dictionary as the following:
                Using TOTP secret:
                    {
                        'username': 'MY_USERNAME',
                        'password': 'MY_PASSWORD',
                        'totpSecret': 'MY_TOTP_SECRET'
                    }
                Using TOTP code:
                    {
                        'username': 'MY_USERNAME',
                        'password': 'MY_PASSWORD',
                        'totpCode': 'MY_TOTP_CODE'
                    }
        """
        if isinstance(credentials, dict):
            credentials: BaseCredentials = backwards_compatible_serialization(
                credentials
            )

        self._authenticationTimeout = MAX_INACTIVE_MINUTES
        self._session = requests.Session()

        response_body, credentials = self.__authenticate(credentials)

        self._credentials = credentials
        self._authentication_session = response_body["authenticationSession"]
        self._push_subscription_id = response_body["pushSubscriptionId"]
        self._customer_id = response_body["customerId"]

        self._socket = AvanzaSocket(
            self._push_subscription_id, self._session.cookies.get_dict()
        )

    def __authenticate(self, credentials: BaseCredentials):
        if (
            not MIN_INACTIVE_MINUTES
            <= self._authenticationTimeout
            <= MAX_INACTIVE_MINUTES
        ):
            raise ValueError(
                f"Session timeout not in range {MIN_INACTIVE_MINUTES} - {MAX_INACTIVE_MINUTES} minutes"
            )

        data = {
            "maxInactiveMinutes": self._authenticationTimeout,
            "username": credentials.username,
            "password": credentials.password,
        }

        response = self._session.post(
            f"{BASE_URL}{Route.AUTHENTICATION_PATH.value}", json=data
        )

        response.raise_for_status()

        response_body = response.json()

        # No second factor required, continue with normal login
        if response_body.get("twoFactorLogin") is None:
            self._security_token = response.headers.get("X-SecurityToken")
            return response_body["successfulLogin"], credentials

        tfa_method = response_body["twoFactorLogin"].get("method")

        if tfa_method != "TOTP":
            raise ValueError(f"Unsupported two factor method {tfa_method}")

        return self.__validate_2fa(credentials)

    def __validate_2fa(self, credentials: BaseCredentials):
        response = self._session.post(
            f"{BASE_URL}{Route.TOTP_PATH.value}",
            json={"method": "TOTP", "totpCode": credentials.totp_code},
        )

        response.raise_for_status()

        self._security_token = response.headers.get("X-SecurityToken")

        response_body = response.json()

        return response_body, credentials

    def __call(
        self, method: HttpMethod, path: str, options=None, return_content: bool = False
    ):
        method_call = {
            HttpMethod.GET: self._session.get,
            HttpMethod.POST: self._session.post,
            HttpMethod.PUT: self._session.put,
            HttpMethod.DELETE: self._session.delete,
        }.get(method)

        if method_call is None:
            raise ValueError(f"Unknown method type {method}")

        data = {}
        if method == HttpMethod.GET:
            data["params"] = options
        else:
            data["json"] = options

        response = method_call(
            f"{BASE_URL}{path}",
            headers={
                "X-AuthenticationSession": self._authentication_session,
                "X-SecurityToken": self._security_token,
            },
            **data,
        )

        response.raise_for_status()

        # Some routes like add/remove instrument from a watch list
        # only returns 200 OK with no further data about if the operation succeeded
        if len(response.content) == 0:
            return None

        if return_content:
            return response.content

        return response.json()

    async def subscribe_to_id(
        self, channel: ChannelType, id: str, callback: Callable[[str, dict], Any]
    ):
        await self.subscribe_to_ids(channel, [id], callback)

    async def subscribe_to_ids(
        self,
        channel: ChannelType,
        ids: Sequence[str],
        callback: Callable[[str, dict], Any],
    ):
        if not callable(callback):
            raise ValueError("callback parameter has to be a function!")

        if not self._socket._connected:
            await self._socket.init()

        await self._socket.subscribe_to_ids(channel, ids, callback)

    def get_overview(self) -> Overview:
        """Get account and category overviews"""
        return self.__call(HttpMethod.GET, Route.CATEGORIZED_ACCOUNTS.value)

    def get_accounts_positions(self) -> AccountPositions:
        """Get investment positions for all account"""

        return self.__call(HttpMethod.GET, Route.ACCOUNTS_POSITIONS_PATH.value)

    def get_account_performance_chart_data(
        self, url_parameters_ids: list[str], time_period: TimePeriod
    ) -> AccountPositions:
        """Get performance chart for accounts.

        Args:

            url_parameters_ids: Scrambled account ids.
                Can be found in the overview response.

            time_period: Time period to get chart data for

        """
        return self.__call(
            HttpMethod.POST,
            Route.ACCOUNT_PERFORMANCE_CHART_PATH.value,
            {
                "scrambledAccountIds": url_parameters_ids,
                "timePeriod": time_period.value,
            },
        )

    def get_watchlists(self) -> List[WatchList]:
        """Get your "Bevakningslistor" """
        return self.__call(HttpMethod.GET, Route.WATCHLISTS_PATH.value)

    def add_to_watchlist(self, instrument_id: str, watchlist_id: str) -> None:
        """Add an instrument to the specified watchlist

        This function returns None if the request was 200 OK,
        but there is no guarantee that the instrument was added to the list,
        verify this by calling get_watchlists()
        """
        return self.__call(
            HttpMethod.PUT,
            Route.WATCHLISTS_ADD_DELETE_PATH.value.format(watchlist_id, instrument_id),
        )

    def remove_from_watchlist(self, instrument_id: str, watchlist_id: str) -> None:
        """Remove an instrument to the specified watchlist

        This function returns None if the request was 200 OK,
        but there is no guarantee that the instrument was removed from the list,
        verify this by calling get_watchlists()
        """
        return self.__call(
            HttpMethod.DELETE,
            Route.WATCHLISTS_ADD_DELETE_PATH.value.format(watchlist_id, instrument_id),
        )

    def get_fund_info(self, fund_id: str) -> FundInfo:
        """Get info about a fund"""

        return self.__call(HttpMethod.GET, Route.FUND_PATH.value.format(fund_id))

    def get_stock_info(self, stock_id: str) -> StockInfo:
        """Returns info about a stock"""

        return self.get_instrument(InstrumentType.STOCK, stock_id)

    def get_certificate_info(self, certificate_id: str) -> CertificateInfo:
        """Returns info about a certificate"""

        return self.get_instrument(InstrumentType.CERTIFICATE, certificate_id)

    def get_certificate_details(self, certificate_id: str) -> CertificateDetails:
        """Returns additional info about a certificate"""

        return self.get_instrument_details(InstrumentType.CERTIFICATE, certificate_id)

    def get_warrant_info(self, warrant_id: str) -> WarrantInfo:
        """Returns info about a warrant"""

        return self.get_instrument(InstrumentType.WARRANT, warrant_id)

    def get_index_info(self, index_id: str) -> IndexInfo:
        """Returns info about an index"""

        # Works when sending InstrumentType.STOCK, but not InstrumentType.INDEX
        return self.get_instrument(InstrumentType.STOCK, index_id)

    def get_instrument(self, instrument_type: InstrumentType, instrument_id: str):
        """
        Get instrument info
        For more info on return models for this function see functions
        [
            get_stock_info(),
            get_fund_info(),
            get_certificate_info(),
            get_index_info(),
            get_warrant_info()
        ]
        """

        return self.__call(
            HttpMethod.GET,
            Route.INSTRUMENT_PATH.value.format(instrument_type.value, instrument_id),
        )

    def get_instrument_details(
        self, instrument_type: InstrumentType, instrument_id: str
    ):
        """
        Get additional instrument info
        For more info on return models for this function see functions
        [
            get_stock_info(),
            get_fund_info(),
            get_certificate_info(),
            get_index_info(),
            get_warrant_info()
        ]
        """

        return self.__call(
            HttpMethod.GET,
            Route.INSTRUMENT_DETAILS_PATH.value.format(
                instrument_type.value, instrument_id
            ),
        )

    def search_for_stock(self, query: str, limit: int = 10) -> StockSearchResult:
        """Search for a stock

        Args:

            query: can be a ISIN ('US0378331005'),
                name ('Apple'),
                tickerSymbol ('AAPL')

            limit: maximum number of results to return

        """
        return self.search_for_instrument(InstrumentType.STOCK, query, limit)

    def search_for_fund(self, query: str, limit: int = 10) -> FundSearchResult:
        """Search for a fund

        Args:

            query: can be a ISIN ('SE0012454338'),
                name ('Avanza'),
                tickerSymbol ('Avanza Europa')

            limit: maximum number of results to return

        """

        return self.search_for_instrument(InstrumentType.FUND, query, limit)

    def search_for_certificate(
        self, query: str, limit: int = 10
    ) -> CertificateSearchResult:
        """Search for a certificate

        Args:

            query: can be a ISIN, name or tickerSymbol

            limit: maximum number of results to return

        """

        return self.search_for_instrument(InstrumentType.CERTIFICATE, query, limit)

    def search_for_warrant(self, query: str, limit: int = 10) -> WarrantSearchResult:
        """Search for a warrant

        Args:

            query: can be a ISIN, name or tickerSymbol

            limit: maximum number of results to return

        """

        return self.search_for_instrument(InstrumentType.WARRANT, query, limit)

    def search_for_instrument(
        self, instrument_type: InstrumentType, query: str, limit: int = 10
    ):
        """Search for a specific instrument

        Args:

            instrument_type: can be STOCK, FUND, BOND etc

            query: can be a ISIN, name or tickerSymbol

            limit: maximum number of results to return

        """
        return self.__call(
            HttpMethod.GET,
            Route.INSTRUMENT_SEARCH_PATH.value.format(
                instrument_type.value.upper(), query, limit
            ),
        )

    def get_order_books(self, order_book_ids: Sequence[str]) -> List[OrderBook]:
        """Get info about multiple order books"""

        return self.__call(
            HttpMethod.GET,
            Route.ORDERBOOK_LIST_PATH.value.format(",".join(order_book_ids)),
        )

    def get_insights_report(
        self, account_id: str, time_period: InsightsReportTimePeriod
    ) -> InsightsReport:
        """Get report about the development of your owned positions during the specified timeperiod"""
        return self.__call(
            HttpMethod.GET,
            Route.INSIGHTS_PATH.value.format(time_period.value, account_id),
        )
   
    def get_deals(self):
        """ Get currently active deals """
        return self.__call(HttpMethod.GET, Route.DEALS_PATH.value)

    def get_orders(self):
        """ Get currently active orders """
        return self.__call(HttpMethod.GET, Route.ORDERS_PATH.value)
    
    def get_inspiration_lists(self) -> List[InspirationListItem]:
        """Get all available inspiration lists

        This returns lists similar to the ones found on:

        https://www.avanza.se/aktier/aktieinspiration.html

        https://www.avanza.se/fonder/fondinspiration.html

        """
        return self.__call(HttpMethod.GET, Route.INSPIRATION_LIST_PATH.value.format(""))

    def get_inspiration_list(self, list_id: Union[ListType, str]) -> InspirationList:
        """Get inspiration list

        Some lists have an id of an enum value described in ListType, but they can also just have a string id.
        An example is hhSK8W1o which corresponds to "Most owned stocks", which isn't described in the ListType enum

        """

        id = list_id.value if isinstance(list_id, ListType) else list_id

        return self.__call(HttpMethod.GET, Route.INSPIRATION_LIST_PATH.value.format(id))

    def get_chart_data(
        self,
        order_book_id: str,
        period: TimePeriod,
        resolution: Optional[Resolution] = None,
    ) -> ChartData:
        """Return chart data for an order book for the specified time period with given resolution"""
        options = {"timePeriod": period.value.lower()}

        if resolution is not None:
            options["resolution"] = resolution.value.lower()

        return self.__call(
            HttpMethod.GET, Route.CHARTDATA_PATH.value.format(order_book_id), options
        )

    def place_order(
        self,
        account_id: str,
        order_book_id: str,
        order_type: OrderType,
        price: float,
        valid_until: date,
        volume: int,
    ):
        """Place an order

        Returns:

            If the order was successfully placed:

            {
                message: str,
                orderId: str,
                orderRequestStatus: 'SUCCESS'
            }

            If the order was not placed:

            {
                message: str,
                orderRequestStatus: 'ERROR'
            }
        """

        return self.__call(
            HttpMethod.POST,
            Route.ORDER_PLACE_PATH.value,
            {
                "accountId": account_id,
                "orderbookId": order_book_id,
                "side": order_type.value,
                "price": price,
                "validUntil": valid_until.isoformat(),
                "volume": volume,
            },
        )

    def place_order_buy_fund(self, account_id: str, order_book_id: str, amount: float):
        """Place a buy order for a fund

        Returns:

            {
                message: str,
                orderId: str,
                accountId: str,
                orderRequestStatus: str
            }
        """

        return self.__call(
            HttpMethod.POST,
            Route.ORDER_PLACE_PATH_BUY_FUND.value,
            {"orderbookId": order_book_id, "accountId": account_id, "amount": amount},
        )

    def place_order_sell_fund(self, account_id: str, order_book_id: str, volume: float):
        """Place a sell order for a fund

        Returns:

            {
                message: str,
                orderId: str,
                accountId: str,
                orderRequestStatus: str
            }
        """

        return self.__call(
            HttpMethod.POST,
            Route.ORDER_PLACE_PATH_SELL_FUND.value,
            {"orderbookId": order_book_id, "accountId": account_id, "volume": volume},
        )

    def place_stop_loss_order(
        self,
        parent_stop_loss_id: str,
        account_id: str,
        order_book_id: str,
        stop_loss_trigger: StopLossTrigger,
        stop_loss_order_event: StopLossOrderEvent,
    ):
        """Place an stop loss order

        Args:

            parent_stop_loss_id: The id of the parent stop loss order. If this is the first stop loss order, this should be "0".

            account_id: A valid account id.

            order_book_id: The order book id of the instrument to place the stop loss order for.

            stop_loss_trigger: The stop loss trigger type.

            stop_loss_order_event: The stop loss order event type.

        Returns:

            If the order was successfully placed:

            {
                status: 'SUCCESS',
                stoplossOrderId: str
            }

            If the order was not placed:

            {
                status: str,
                stoplossOrderId: str
            }
        """

        return self.__call(
            HttpMethod.POST,
            Route.ORDER_PLACE_STOP_LOSS_PATH.value,
            {
                "parentStopLossId": parent_stop_loss_id,
                "accountId": account_id,
                "orderBookId": order_book_id,
                "stopLossTrigger": {
                    "type": stop_loss_trigger.type.value,
                    "value": stop_loss_trigger.value,
                    "validUntil": stop_loss_trigger.valid_until.isoformat(),
                    "valueType": stop_loss_trigger.value_type.value,
                    "triggerOnMarketMakerQuote": stop_loss_trigger.trigger_on_market_maker_quote,
                },
                "stopLossOrderEvent": {
                    "type": stop_loss_order_event.type.value,
                    "price": stop_loss_order_event.price,
                    "volume": stop_loss_order_event.volume,
                    "validDays": stop_loss_order_event.valid_days,
                    "priceType": stop_loss_order_event.price_type.value,
                    "shortSellingAllowed": stop_loss_order_event.short_selling_allowed,
                },
            },
        )

    def edit_order(
        self,
        instrument_type: InstrumentType,
        order_id: str,
        account_id: str,
        order_book_id: str,
        order_type: OrderType,
        price: float,
        valid_until: date,
        volume: int,
    ):
        """Update an existing order

        Returns:

            {
                messages: List[str],
                orderId: str,
                requestId: str,
                status: str
            }
        """

        return self.__call(
            HttpMethod.PUT,
            Route.ORDER_EDIT_PATH.value.format(instrument_type.value, order_id),
            {
                "accountId": account_id,
                "orderbookId": order_book_id,
                "orderType": order_type.value,
                "price": price,
                "validUntil": valid_until.isoformat(),
                "volume": volume,
            },
        )

    def get_order(self, account_id: str, order_id: str):
        """Get an existing order

        Returns:

            {
                'account': {
                    'buyingPower': float,
                    'id': str,
                    'name': str,
                    'totalBalance': float,
                    'type': str
                },
                'brokerTradeSummary': {
                    'items': [{
                        'brokerCode': str,
                        'buyVolume': int,
                        'netBuyVolume': int,
                        'sellVolume': int
                    }],
                    'orderbookId': str
                },
                'customer': {
                    'courtageClass': str,
                    'showCourtageClassInfoOnOrderPage': bool
                },
                'firstTradableDate': str,
                'hasInstrumentKnowledge': bool,
                'hasInvestmentFees': {'buy': bool, 'sell': bool},
                'hasShortSellKnowledge': bool,
                'lastTradableDate': str,
                'latestTrades': [{
                    'buyer': str,
                    'cancelled': bool,
                    'dealTime': str,
                    'matchedOnMarket': bool,
                    'price': float,
                    'seller': str,
                    'volume': int
                }],
                'marketMakerExpected': bool,
                'marketTrades': bool,
                'order': {
                    'orderCondition': str,
                    'orderType': str,
                    'price': float,
                    'validUntil': str,
                    'volume': int
                },
                'orderDepthLevels': List,
                'orderDepthReceivedTime': str,
                'orderbook': {
                    'change': float,
                    'changePercent': float,
                    'currency': str,
                    'exchangeRate': float,
                    'flagCode': str,
                    'highestPrice': float,
                    'id': str,
                    'lastPrice': float,
                    'lastPriceUpdated': str,
                    'lowestPrice': float,
                    'name': str,
                    'positionVolume': float,
                    'tickerSymbol': str,
                    'totalValueTraded': float,
                    'totalVolumeTraded': float,
                    'tradable': bool,
                    'tradingUnit': int,
                    'type': str,
                    'volumeFactor': float
                },
                'tickSizeRules': [{
                    'maxPrice': int,
                    'minPrice': int,
                    'tickSize': int
                }],
                'untradableDates': List[str]
            }
        """

        return self.__call(
            HttpMethod.GET,
            Route.ORDER_GET_PATH.value.format(
                # Have tried this with three different instrument types
                # (STOCK, FUND, CERTIFICATE)
                # and it only seems to work when sending the instrument type
                # as STOCK
                InstrumentType.STOCK.value,
                account_id,
                order_id,
            ),
        )

    def get_all_stop_losses(self):
        """Get open stop losses

        Returns:

            [{
                "id": str,
                "status": str,
                "account": {
                    "id": str,
                    "name": str,
                    "type": str,
                    "urlParameterId": str
                },
                "orderbook": {
                    "id": str,
                    "name": str,
                    "countryCode": str,
                    "currency": str,
                    "shortName": str,
                    "type": str
                },
                "hasExcludingChildren": bool,
                "message": str,
                "trigger": {
                    "value": int,
                    "type": str,
                    "validUntil": str,
                    "valueType": str
                },
                "order": {
                    "type": str,
                    "price": int,
                    "volume": int,
                    "shortSellingAllowed": bool,
                    "validDays": int,
                    "priceType": str,
                    "priceDecimalPrecision": 0
                },
                "editable": bool,
                "deletable": bool
            }]
        """
        return self.__call(HttpMethod.GET, Route.STOP_LOSS_PATH.value)

    def delete_stop_loss_order(self, account_id: str, stop_loss_id: str):
        """delete a stop loss order

        Args:

            stop_loss_id: The id of the stop loss order to delete.

            account_id: A valid account id.

        Returns:
            Nothing
        """

        return self.__call(
            HttpMethod.DELETE,
            Route.ORDER_DELETE_STOP_LOSS_PATH.value.format(
                account_id,
                stop_loss_id,
            ),
        )

    def delete_order(self, account_id: str, order_id: str):
        """Delete an existing order

        Returns:

            {
                messages: str,
                orderId: str,
                parameters: List[str],
                orderRequestStatus: str
            }
        """
        return self.__call(
            HttpMethod.POST,
            Route.ORDER_DELETE_PATH.value,
            {"accountId": account_id, "orderId": order_id},
        )

    def get_monthly_savings_by_account_id(self, account_id: str):
        """Get monthly savings at avanza for specific account

        Returns:

            {
                'monthlySavings': [{
                    'account': {
                        'id': str,
                        'name': str,
                        'type': str
                    },
                    'amount': float,
                    'cash': {'amount': float, 'percent': float},
                    'externalAccount': {
                        'accountNumber': str,
                        'bankName': str,
                        'clearingNumber': str
                    },
                    'fundDistributions': [{
                        'amount': float,
                        'orderbook': {
                            'buyable': bool,
                            'id': str,
                            'name': str
                        },
                        'percent': float
                    },
                    'id': str,
                    'name': str,
                    'purchaseDay': int,
                    'status': str,
                    'transferDay': int
                }],
                'totalAmount': float
            }
        """

        return self.__call(
            HttpMethod.GET, Route.MONTHLY_SAVINGS_PATH.value.format(account_id)
        )

    def get_all_monthly_savings(self):
        """Get your monthly savings at Avanza

        Returns:

            {
                'monthlySavings': [{
                    'account': {
                        'id': str,
                        'name': str,
                        'type': str
                    },
                    'amount': float,
                    'cash': {'amount': float, 'percent': float},
                    'externalAccount': {
                        'accountNumber': str,
                        'bankName': str,
                        'clearingNumber': str
                    },
                    'fundDistributions': [{
                        'amount': float,
                        'orderbook': {
                            'buyable': bool,
                            'id': str,
                            'name': str
                        },
                        'percent': float
                    },
                    'id': str,
                    'name': str,
                    'purchaseDay': int,
                    'status': str,
                    'transferDay': int
                }],
                'totalAmount': float
            }
        """

        return self.__call(HttpMethod.GET, Route.MONTHLY_SAVINGS_PATH.value.format(""))

    def pause_monthly_saving(self, account_id: str, monthly_savings_id: str):
        """Pause an active monthly saving

        Returns:
            'OK'

        """

        return self.__call(
            HttpMethod.PUT,
            Route.MONTHLY_SAVINGS_PAUSE_PATH.value.format(
                account_id, monthly_savings_id
            ),
        )

    def resume_monthly_saving(self, account_id: str, monthly_savings_id: str):
        """Resume a paused monthly saving

        Returns:
            'OK'

        """

        return self.__call(
            HttpMethod.PUT,
            Route.MONTHLY_SAVINGS_RESUME_PATH.value.format(
                account_id, monthly_savings_id
            ),
        )

    def delete_monthly_saving(self, account_id: str, monthly_savings_id: str) -> None:
        """Deletes a monthly saving

        Returns:
            None

        """

        return self.__call(
            HttpMethod.DELETE,
            Route.MONTHLY_SAVINGS_REMOVE_PATH.value.format(
                account_id, monthly_savings_id
            ),
        )

    def create_monthly_saving(
        self,
        account_id: str,
        amount: int,
        transfer_day_of_month: int,
        purchase_day_of_month: int,
        clearing_and_account_number: str,
        fund_distribution: Dict[str, int],
    ):
        """Create a monthly saving at Avanza

        Args:

            account_id: The Avanza account to which the withdrawn money should be transferred to

            amount: minimum amount 100 (SEK)
                the amount that should be withdrawn from the external account every month

            transfer_day_of_month: valid range (1-31)
                when the money should be withdrawn from the external account

            purchase_day_of_month: valid range (1-31)
                when the funds should be purchased,
                must occur after the transfer_day_of_month

            clearing_and_account_number: The external account from which the money for the monthly savings should be withdrawn from,
                has to be formatted as follows 'XXXX-XXXXXXXXX'

            fund_distrubution: the percentage distribution of the funds
                The key is the funds id and the value is the distribution of the amount in a whole percentage
                The sum of the percentages has to total 100

                Examples:
                    {'41567': 100}
                    {'41567': 50, '878733': 50}
                    {'41567': 25, '878733': 75}

        Returns:

            {
                'monthlySavingId': str,
                'status': str
            }

            monthlySavingId has the following format: 'XX^XXXXXXXXXXXXX^XXXXXX'
            status should have the value 'ACCEPTED' if the monthly saving was created successfully
        """

        if not 1 <= transfer_day_of_month <= 31:
            raise ValueError(
                "transfer_day_of_month is outside the valid range of (1-31)"
            )

        if not 1 <= purchase_day_of_month <= 31:
            raise ValueError(
                "purchase_day_of_month is outside the valid range of (1-31)"
            )

        if transfer_day_of_month >= purchase_day_of_month:
            raise ValueError(
                "transfer_day_of_month must occur before purchase_day_of_month"
            )

        if len(fund_distribution) == 0:
            raise ValueError("No founds were specified in the fund_distribution")

        if sum(fund_distribution.values()) != 100:
            raise ValueError("The fund_distribution values must total 100")

        return self.__call(
            HttpMethod.POST,
            Route.MONTHLY_SAVINGS_CREATE_PATH.value.format(account_id),
            {
                "amount": amount,
                "autogiro": {
                    "dayOfMonth": transfer_day_of_month,
                    "externalClearingAndAccount": clearing_and_account_number,
                },
                "fundDistribution": {
                    "dayOfMonth": purchase_day_of_month,
                    "fundDistributions": fund_distribution,
                },
            },
        )

    def get_transactions_details(
        self,
        transaction_details_types: Optional[Sequence[TransactionsDetailsType]] = [],
        transactions_from: Optional[date] = None,
        transactions_to: Optional[date] = None,
        isin: Optional[str] = None,
        max_elements: Optional[int] = 1000,
    ) -> Transactions:
        """Get transactions, optionally apply criteria.

        Args:

            transaction_types: One or more transaction types.

            transactions_from: Fetch transactions from this date.

            transactions_to: Fetch transactions to this date.

            isin: Only fetch transactions for specified isin.

            max_elements: Limit result to N transactions.
        """
        options = {}
        options["maxElements"] = max_elements

        if transaction_details_types:
            options["transactionTypes"] = ",".join(
                [type.value for type in transaction_details_types]
            )
        if transactions_from:
            options["from"] = transactions_from.isoformat()
        if transactions_to:
            options["to"] = transactions_to.isoformat()
        if isin:
            options["isin"] = isin

        return self.__call(
            HttpMethod.GET, Route.TRANSACTIONS_DETAILS_PATH.value, options
        )

    def get_note_as_pdf(self, url_parameter_id: str, note_id: str):
        return self.__call(
            HttpMethod.GET,
            Route.NOTE_PATH.value.format(url_parameter_id, note_id),
            return_content=True,
        )

    def set_price_alert(
        self,
        order_book_id: str,
        price: float,
        valid_until: date,
        notification: bool = True,
        email: bool = False,
        sms: bool = False,
    ):
        """
        Sets a price alert for the specified orderbook and returns all the existing alerts.

        Returns:

            [
                {
                    'alertId': str,
                    'accountId': str,
                    'price': float,
                    'validUntil': str,
                    'direction': str,
                    'email': bool,
                    'notification': bool,
                    'sms': bool,
                }
            ]
        """

        return self.__call(
            HttpMethod.POST,
            Route.PRICE_ALERT_PATH.value.format(order_book_id),
            {
                "price": price,
                "validUntil": valid_until.isoformat(),
                "notification": notification,
                "email": email,
                "sms": sms,
            },
        )

    def get_price_alert(self, order_book_id: str) -> List[PriceAlert]:
        """Gets all the price alerts for the specified orderbook"""

        return self.__call(
            HttpMethod.GET,
            Route.PRICE_ALERT_PATH.value.format(order_book_id),
        )

    def delete_price_alert(self, order_book_id: str, alert_id: str):
        """
        Deletes a price alert from the specified orderbook and returns the remaining alerts.

        Returns:

            [
                {
                    'alertId': str,
                    'accountId': str,
                    'price': float,
                    'validUntil': str,
                    'direction': str,
                    'email': bool,
                    'notification': bool,
                    'sms': bool,
                }
            ]
        """
        return self.__call(
            HttpMethod.DELETE,
            Route.PRICE_ALERT_PATH.value.format(order_book_id, alert_id)
            + f"/{alert_id}",
        )

    def get_offers(self) -> List[Offer]:
        """Return current offers"""

        return self.__call(HttpMethod.GET, Route.CURRENT_OFFERS_PATH.value)
