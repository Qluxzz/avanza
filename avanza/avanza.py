
import hashlib
from datetime import date
from typing import Any, Callable, Dict, Optional, Sequence

import pyotp
import requests

from avanza.entities import StopLossOrderEvent, StopLossTrigger

from .avanza_socket import AvanzaSocket
from .constants import (ChannelType, HttpMethod, InstrumentType, ListType,
                        OrderType, Resolution, Route, TimePeriod,
                        TransactionsDetailsType, TransactionType)

BASE_URL = 'https://www.avanza.se'
MIN_INACTIVE_MINUTES = 30
MAX_INACTIVE_MINUTES = 60 * 24


class Avanza:
    def __init__(self, credentials: dict):
        """
        Args:
            credentials: Login credentials.
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
            f'{BASE_URL}{Route.AUTHENTICATION_PATH.value}',
            json=data
        )

        response.raise_for_status()

        response_body = response.json()

        # No second factor required, continue with normal login
        if response_body.get('twoFactorLogin') is None:
            self._security_token = response.headers.get('X-SecurityToken')
            return response_body['successfulLogin'], credentials

        tfa_method = response_body['twoFactorLogin'].get('method')

        if tfa_method != 'TOTP':
            raise ValueError(
                f'Unsupported two factor method {tfa_method}'
            )

        return self.__validate_2fa(credentials)

    def __validate_2fa(self, credentials):
        if 'totpSecret' in credentials:
            totp = pyotp.TOTP(credentials['totpSecret'], digest=hashlib.sha1)
            totp_code = totp.now()
        elif 'totpCode' in credentials:
            totp_code = credentials['totpCode']

        if totp_code is None:
            raise ValueError('Failed to get totp code')

        response = self._session.post(
            f'{BASE_URL}{Route.TOTP_PATH.value}',
            json={
                'method': 'TOTP',
                'totpCode': totp_code
            }
        )

        response.raise_for_status()

        self._security_token = response.headers.get('X-SecurityToken')

        response_body = response.json()

        return response_body, credentials

    def __call(self, method: HttpMethod, path: str, options=None, return_content: bool = False):
        method_call = {
            HttpMethod.GET: self._session.get,
            HttpMethod.POST: self._session.post,
            HttpMethod.PUT: self._session.put,
            HttpMethod.DELETE: self._session.delete
        }.get(method)

        if method_call is None:
            raise ValueError(f'Unknown method type {method}')

        data = {}
        if method == HttpMethod.GET:
            data['params'] = options
        else:
            data['json'] = options

        response = method_call(
            f'{BASE_URL}{path}',
            headers={
                'X-AuthenticationSession': self._authentication_session,
                'X-SecurityToken': self._security_token
            },
            **data
        )

        response.raise_for_status()

        # Some routes like add/remove instrument from a watchlist
        # only returns 200 OK with no further data about if the operation succeded
        if len(response.content) == 0:
            return None

        if return_content:
            return response.content

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
        """ Get account and category overviews

        Returns:

            {
                'categories': [
                    {
                        'name': str,
                        'totalValue': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'buyingPower': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'id': str,
                        'profit': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        },
                        'performance': {
                            'THREE_MONTHS': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'THREE_YEARS': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'ONE_WEEK': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'ONE_YEAR': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'ALL_TIME': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'THIS_YEAR': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'ONE_MONTH': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            }
                        },
                        'savingsGoalView': {
                            'goalAmount': float,
                            'percentCompleted': float,
                            'sharedGoal': bool
                        },
                        'sortOrder': int
                    }
                ],
                'accounts': [
                    {
                        'id': str,
                        'categoryId': str,
                        'balance': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'profit': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        },
                        'totalAcquiredValue': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'type': str,
                        'totalValue': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'buyingPower': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'buyingPowerWithoutCredit': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'interestRate': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'depositInterestRate': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'loanInterestRate': {
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                        },
                        'credit': null,
                        'name': {
                            'defaultName': str,
                            'userDefinedName': str
                        },
                        'status': str,
                        'errorStatus': str,
                        'overmortgaged': bool,
                        'overdrawn': bool,
                        'performance': {
                            'THREE_MONTHS': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'THREE_YEARS': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'ONE_WEEK': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'ONE_YEAR': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'ALL_TIME': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'THIS_YEAR': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'ONE_MONTH': {
                                'absolute': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'relative': {
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            }
                        },
                        'settings': {
                            'IS_HIDDEN': bool
                        },
                        'clearingNumber': str,
                        'accountNumber': str,
                        'urlParameterId': str,
                        'owner': bool
                    }
                ],
                'loans': [],
                'accountsSummary': {
                    'performance': {
                        'THREE_MONTHS': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        },
                        'THREE_YEARS': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        },
                        'ONE_WEEK': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        },
                        'ONE_YEAR': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        },
                        'ALL_TIME': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        },
                        'THIS_YEAR': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        },
                        'ONE_MONTH': {
                            'absolute': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            },
                            'relative': {
                                'value': float,
                                'unit': str,
                                'unitType': str,
                                'decimalPrecision': int
                            }
                        }
                    },
                    'buyingPower': {
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                    },
                    'totalValue': {
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                    }
                }
            }
        """
        return self.__call(HttpMethod.GET, Route.CATEGORIZED_ACCOUNTS.value)

    def get_accounts_positions(self):
        """Get investment positions for all account

        Returns:

            {
                'withOrderbook':[{
                    'account':{
                        'id': str,
                        'type': str,
                        'name': str,
                        'urlParameterId': str,
                        'hasCredit':bool
                    },
                    'instrument':{
                        'type': str,
                        'name': str,
                        'orderbook':{
                            'id': str,
                            'flagCode': str,
                            'name': str,
                            'type': str,
                            'tradeStatus': str,
                            'quote':{
                                'highest':{
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'lowest':{
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'buy':{
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'sell':{
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'latest':{
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                }
                            },
                            'turnover':{
                                'volume':{
                                    'value': float,
                                    'unit': str,
                                    'unitType': str,
                                    'decimalPrecision': int
                                },
                                'value': ?float
                            },
                            'lastDeal':{
                                'date': str,
                                'time': ?str
                            }
                        },
                        'currency': str,
                        'isin': str,
                        'volumeFactor': float
                    },
                    'volume':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                    },
                    'value':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                    },
                    'averageAcquiredPrice':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                    },
                    'acquiredValue':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                    },
                    'lastTradingDayPerformance':{
                       'absolute':{
                            'value': float,
                            'unit': str,
                            'unitType': str,
                            'decimalPrecision': int
                       },
                       'relative':{
                           'value': float,
                           'unit': str,
                           'unitType': str,
                           'decimalPrecision': int
                       }
                    },
                    'id': str
                }],
                'withoutOrderbook':[
                  {
                     'account':{
                        'id': str,
                        'type': str,
                        'name': str,
                        'urlParameterId': str,
                        'hasCredit': bool
                     },
                     'instrument':{
                        'type': str,
                        'name': str,
                        'orderbook': null (if not null, probably same as 'withOrderbook'),
                        'currency': str,
                        'isin': str,
                        'volumeFactor': int
                     },
                     'volume':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                     },
                     'value':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                     },
                     'averageAcquiredPrice':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                     },
                     'acquiredValue':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                     },
                     'lastTradingDayPerformance':null,
                     'id': str
                  }
               ],
               'cashPositions':[
                  {
                     'account':{
                        'id': str,
                        'type': str,
                        'name': str,
                        'urlParameterId': str,
                        'hasCredit': bool
                     },
                     'totalBalance':{
                        'value': float,
                        'unit': str,
                        'unitType': str,
                        'decimalPrecision': int
                     },
                     'id': str
                  },
               ]
            }
        """
        return self.__call(
            HttpMethod.GET,
            Route.ACCOUNTS_POSITIONS_PATH.value
        )

    def get_watchlists(self):
        """ Get your "Bevakningslistor"

        Returns:

            [{
                'editable': bool,
                'id': str,
                'name': str,
                'orderbooks': List[str]
            }]
        """
        return self.__call(HttpMethod.GET, Route.WATCHLISTS_PATH.value)

    def add_to_watchlist(
        self,
        instrument_id: str,
        watchlist_id: str
    ) -> None:
        """ Add an instrument to the specified watchlist

            This function returns None if the request was 200 OK,
            but there is no guarantee that the instrument was added to the list,
            verify this by calling get_watchlists()
        """
        return self.__call(
            HttpMethod.PUT,
            Route.WATCHLISTS_ADD_DELETE_PATH.value.format(
                watchlist_id,
                instrument_id
            )
        )

    def remove_from_watchlist(
        self,
        instrument_id: str,
        watchlist_id: str
    ) -> None:
        """ Remove an instrument to the specified watchlist

            This function returns None if the request was 200 OK,
            but there is no guarantee that the instrument was removed from the list,
            verify this by calling get_watchlists()
        """
        return self.__call(
            HttpMethod.DELETE,
            Route.WATCHLISTS_ADD_DELETE_PATH.value.format(
                watchlist_id,
                instrument_id
            )
        )

    def get_fund_info(
        self,
        fund_id: str
    ):
        """ Get info about a fund

        Returns:

            {
                "adminCompany": {
                    "country": str,
                    "name": str,
                    "url": str
                },
                "aumCoveredCarbon": float,
                "capital": float,
                "carbonRiskScore": float,
                "carbonSolutionsInvolvement": float,
                "categories": [
                    str
                ],
                "controversyScore": float,
                "countryChartData": [
                    {
                        "countryCode": str,
                        "currency": str,
                        "isin": str,
                        "name": str,
                        "orderbookId": str,
                        "type": str,
                        "y": float
                    }
                ],
                "currency": str,
                "description": str,
                "developmentFiveYears": float,
                "developmentOneDay": float,
                "developmentOneMonth": float,
                "developmentOneYear": float,
                "developmentSixMonths": float,
                "developmentThisYear": float,
                "developmentThreeMonths": float,
                "developmentThreeYears": float,
                "environmentalScore": float,
                "esgScore": float,
                "fossilFuelInvolvement": float,
                "fundManagers": [
                    {
                        "name": str,
                        "startDate": date
                    }
                ],
                "fundRatingViews": [
                    {
                        "date": date,
                        "fundRating": int,
                        "fundRatingType": str
                    }
                ],
                "fundType": str,
                "fundTypeName": str,
                "governanceScore": float,
                "hedgeFund": bool,
                "holdingChartData": [
                    {
                        "countryCode": str,
                        "currency": str,
                        "isin": str,
                        "name": str,
                        "orderbookId": str,
                        "type": str,
                        "y": float
                    }
                ],
                "indexFund": bool,
                "isin": str,
                "lowCarbon": bool,
                "managementFee": float,
                "nav": float,
                "navDate": date,
                "portfolioDate": date,
                "ppmCode": type(None),
                "pricingFrequency": str,
                "primaryBenchmark": str,
                "productFee": float,
                "productInvolvements": [
                    {
                        "product": str,
                        "productDescription": str,
                        "value": float
                    }
                ],
                "prospectusLink": str,
                "rating": int,
                "recommendedHoldingPeriod": str,
                "risk": int,
                "riskText": str,
                "sectorChartData": [
                    {
                        "countryCode": type(None),
                        "currency": str,
                        "isin": type(None),
                        "name": str,
                        "orderbookId": type(None),
                        "type": str,
                        "y": float
                    }
                ],
                "sharpeRatio": float,
                "socialScore": float,
                "standardDeviation": float,
                "superloanOrderbook": bool,
                "sustainabilityRating": int,
                "sustainabilityRatingCategoryName": str,
                "svanen": bool,
                "ucitsFund": bool
            }
        """

        return self.__call(
            HttpMethod.GET,
            Route.FUND_PATH.value.format(
                fund_id
            )
        )

    def get_stock_info(
        self,
        stock_id: str
    ):
        """ Returns info about a stock

        Returns:

            {
                'annualMeetings': [
                    {
                        'eventDate': str,
                        'extra': bool
                    }
                ],
                'brokerTradeSummary': {
                    'items': [
                        {
                            'brokerCode': str,
                            'buyVolume': int,
                            'netBuyVolume': int,
                            'sellVolume': int
                        }
                    ],
                    'orderbookId': str
                },
                'buyPrice': float,
                'change': float,
                'changePercent': float,
                'company': {
                    'CEO': str,
                    'chairman': str,
                    'description': str,
                    'id': str,
                    'marketCapital': int,
                    'marketCapitalCurrency': str,
                    'name': str,
                    'sector': str,
                    'stocks': [
                        {
                            'name': str,
                            'totalNumberOfShares': int
                        }
                    ],
                    'totalNumberOfShares': int
                },
                'companyReports': [{
                    'eventDate': str,
                    'reportType': str
                }],
                'country': str,
                'currency': str,
                'dividends': [{
                    'amountPerShare': float,
                    'currency': str,
                    'exDate': str,
                    'paymentDate': str
                }],
                'flagCode': str,
                'hasInvestmentFees': bool,
                'highestPrice': float,
                'id': str,
                'isin': str,
                'keyRatios': {
                    'directYield': float,
                    'priceEarningsRatio': float,
                    'volatility': float
                },
                'lastPrice': float,
                'lastPriceUpdated': str,
                'latestTrades': [],
                'loanFactor': float,
                'lowestPrice': float,
                'marketMakerExpected': bool,
                'marketPlace': str,
                'marketTrades': bool,
                'name': str,
                'numberOfOwners': int,
                'numberOfPriceAlerts': int,
                'orderDepthLevels': [
                    {
                        'buy': {
                            'percent': float,
                            'price': float,
                            'volume': int
                        },
                        'sell': {
                            'percent': float,
                            'price': float,
                            'volume': int
                        }
                    }
                ],
                'orderDepthReceivedTime': str,
                'positions': [],
                'positionsTotalValue': float,
                'priceAtStartOfYear': float,
                'priceFiveYearsAgo': float,
                'priceOneMonthAgo': float,
                'priceOneWeekAgo': float,
                'priceOneYearAgo': float,
                'priceSixMonthsAgo': float,
                'priceThreeMonthsAgo': float,
                'priceThreeYearsAgo': float,
                'pushPermitted': bool,
                'quoteUpdated': str,
                'relatedStocks': [{
                    'flagCode': str,
                    'id': str,
                    'lastPrice': float,
                    'name': str,
                    'priceOneYearAgo': float
                }],
                'sellPrice': float,
                'shortSellable': bool,
                'superLoan': bool,
                'tickerSymbol': str,
                'totalValueTraded': float,
                'totalVolumeTraded': int,
                'tradable': bool
            }
        """

        return self.get_instrument(
            InstrumentType.STOCK,
            stock_id
        )

    def get_certificate_info(
        self,
        certificate_id: str
    ):
        """ Returns info about a certificate

        Returns:

            {
                "historicalClosingPrices":{
                    "oneDay":"float",
                    "oneMonth":"float",
                    "oneWeek":"float",
                    "start":"float",
                    "startDate":"str",
                    "threeMonths":"float"
                },
                "isin":"str",
                "keyIndicators":{
                    "isAza":"bool",
                    "leverage":"float",
                    "numberOfOwners":"int",
                    "productLink":"str"
                },
                "listing":{
                    "countryCode":"str",
                    "currency":"str",
                    "marketPlaceCode":"str",
                    "marketPlaceName":"str",
                    "marketTradesAvailable":"bool",
                    "shortName":"str",
                    "tickSizeListId":"str",
                    "tickerSymbol":"str"
                },
                "name":"str",
                "orderbookId":"str",
                "quote":{
                    "change":"float",
                    "changePercent":"float",
                    "last":"float",
                    "timeOfLast":"int",
                    "totalValueTraded":"float",
                    "totalVolumeTraded":"int"
                },
                "tradable":"str",
                "type":"str"
            }
        """

        return self.get_instrument(
            InstrumentType.CERTIFICATE,
            certificate_id
        )

    def get_certificate_details(
        self,
        certificate_id: str
    ):
        """ Returns additional info about a certificate

        Returns:

            {
                "assetCategory":"str",
                "brokerTradeSummaries":"List",
                "category":"str",
                "collateralValue":"float",
                "direction":"str",
                "documents":{
                    "kid":"str",
                    "prospectus":"str"
                },
                "fee":{
                    "totalMonetaryFee":"float",
                    "totalPercentageFee":"float"
                },
                "holdings":{
                    "accountAndPositionsView":"List",
                    "acquiredPrice":"float",
                    "acquiredValue":"float",
                    "totalDevelopmentAmount":"float",
                    "totalDevelopmentPercent":"float",
                    "totalMarketValue":"float",
                    "totalVolume":"int"
                },
                "issuer":"str",
                "leverage":"float",
                "orderDepthLevels":"List",
                "ordersAndDeals":{
                    "accounts":"List",
                    "deals":"List",
                    "hasStoplossOrders":"bool",
                    "orders":"List"
                },
                "subCategory":"str",
                "trades":"List"
            }
        """

        return self.get_instrument_details(
            InstrumentType.CERTIFICATE,
            certificate_id
        )

    def get_warrant_info(
        self,
        warrant_id: str
    ):
        """ Returns info about a warrant

        Returns:

            {
                'callIndicator': str,
                'change': float,
                'changePercent': float,
                'currency': str,
                'direction': str,
                'endDate': str,
                'finalTerms': str,
                'flagCode': str,
                'hasInvestmentFees': bool,
                'highestPrice': float,
                'id': str,
                'isin': str,
                'issuerName': str,
                'lastPrice': float,
                'lastPriceUpdated': str,
                'lowestPrice': float,
                'marketPlace': str,
                'name': str,
                'numberOfPriceAlerts': int,
                'parity': float,
                'positions': [],
                'positionsTotalValue': float,
                'priceAtStartOfYear': float,
                'priceOneMonthAgo': float,
                'priceOneWeekAgo': float,
                'priceOneYearAgo': float,
                'priceSixMonthsAgo': float,
                'priceThreeMonthsAgo': float,
                'priipDocumentUrl': str,
                'pushPermitted': bool,
                'quoteUpdated': str,
                'strikePrice': int,
                'tickerSymbol': str,
                'totalValueTraded': float,
                'totalVolumeTraded': int,
                'tradable': bool,
                'underlyingCurrency': str,
                'underlyingOrderbook': {
                    'change': float,
                    'changePercent': float,
                    'currency': str,
                    'flagCode': str,
                    'highestPrice': float,
                    'id': str,
                    'lastPrice': float,
                    'lastPriceUpdated': str,
                    'lowestPrice': float,
                    'name': str,
                    'tickerSymbol': str,
                    'totalVolumeTraded': int,
                    'type': str,
                    'updated': str
                },
                'warrantType': str
            }
        """

        return self.get_instrument(
            InstrumentType.WARRANT,
            warrant_id
        )

    def get_index_info(
        self,
        index_id: str
    ):
        """ Returns info about an index

        Returns:

            {
                'change': float,
                'changePercent': float,
                'currency': str,
                'description': str,
                'flagCode': str
                'highestPrice': float,
                'id': str,
                'lastPrice': float,
                'lastPriceUpdated': str,
                'lowestPrice': float,
                'name': str,
                'numberOfPriceAlerts': int,
                'priceAtStartOfYear': float,
                'priceFiveYearsAgo': float,
                'priceOneMonthAgo': float,
                'priceOneWeekAgo': float,
                'priceOneYearAgo': float,
                'priceSixMonthsAgo': float,
                'priceThreeMonthsAgo': float,
                'priceThreeYearsAgo': float,
                'pushPermitted': bool,
                'quoteUpdated': str,
                'title': str
            }
        """

        return self.get_instrument(
            InstrumentType.INDEX,
            index_id
        )

    def get_instrument(
        self,
        instrument_type: InstrumentType,
        instrument_id: str
    ):
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
            Route.INSTRUMENT_PATH.value.format(
                instrument_type.value,
                instrument_id
            )
        )

    def get_instrument_details(
        self,
        instrument_type: InstrumentType,
        instrument_id: str
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
                instrument_type.value,
                instrument_id
            )
        )

    def search_for_stock(
        self,
        query: str,
        limit: int = 10
    ):
        """ Search for a stock

        Args:
            query: can be a ISIN ('US0378331005'),
                name ('Apple'),
                tickerSymbol ('AAPL')
            limit: maximum number of results to return

        Returns:

            {
                'totalNumberOfHits': int,
                'hits': [{
                    'instrumentType': 'STOCK',
                    'numberOfHits': int,
                    'topHits': [{
                        'currency': str,
                        'lastPrice': float,
                        'changePercent': float,
                        'tradable': bool,
                        'tickerSymbol': str,
                        'flagCode': Str,
                        'name': str,
                        'id': str
                    }]
                }]
            }
        """
        return self.search_for_instrument(
            InstrumentType.STOCK,
            query,
            limit
        )

    def search_for_fund(
        self,
        query: str,
        limit: int = 10
    ):
        """ Search for a fund

        Args:
            query: can be a ISIN ('SE0012454338'),
                name ('Avanza'),
                tickerSymbol ('Avanza Europa')
            limit: maximum number of results to return

        Returns:

            {
                'hits': [{
                    'instrumentType': 'FUND',
                    'numberOfHits': int,
                    'topHits': [{
                        'changeSinceOneDay': float,
                        'changeSinceOneYear': float,
                        'changeSinceThreeMonths': float,
                        'id': str,
                        'managementFee': float,
                        'name': str,
                        'risk': int,
                        'riskLevel': str,
                        'tickerSymbol': str,
                        'tradable': bool
                    }]
                }],
                'totalNumberOfHits': int
            }
        """

        return self.search_for_instrument(
            InstrumentType.FUND,
            query,
            limit
        )

    def search_for_certificate(
        self,
        query: str,
        limit: int = 10
    ):
        """ Search for a certificate

        Args:
            query: can be a ISIN, name or tickerSymbol
            limit: maximum number of results to return

        Returns:

            {
                'hits': [{
                    'instrumentType': 'CERTIFICATE',
                    'numberOfHits': int,
                    'topHits': [{
                        'changePercent': float,
                        'currency': str,
                        'flagCode': str,
                        'id': str,
                        'lastPrice': float,
                        'name': str,
                        'tickerSymbol': str,
                        'tradable': True
                    }]
                }],
                'totalNumberOfHits': 1
            }
        """

        return self.search_for_instrument(
            InstrumentType.CERTIFICATE,
            query,
            limit
        )

    def search_for_warrant(
        self,
        query: str,
        limit: int = 10
    ):
        """ Search for a warrant

        Args:
            query: can be a ISIN, name or tickerSymbol
            limit: maximum number of results to return

        Returns:

            {
                'hits': [{
                    'instrumentType': 'WARRANT',
                    'numberOfHits': int,
                    'topHits': [{
                        'changePercent': float,
                        'currency': str,
                        'flagCode': str,
                        'id': str,
                        'lastPrice': float,
                        'name': str,
                        'tickerSymbol': str,
                        'tradable': True
                    }]
                }],
                'totalNumberOfHits': int
            }
        """

        return self.search_for_instrument(
            InstrumentType.WARRANT,
            query,
            limit
        )

    def search_for_instrument(
        self,
        instrument_type: InstrumentType,
        query: str,
        limit: int = 10
    ):
        """ Search for a specific instrument

        Args:
            instrument_type: can be STOCK, FUND, BOND etc
            query: can be a ISIN, name or tickerSymbol
            limit: maximum number of results to return

        Returns:

            See the functions [
                search_for_stock(),
                search_for_fund(),
                search_for_certificate(),
                search_for_warrant()
            ]
            for more info about the return models
        """
        return self.__call(
            HttpMethod.GET,
            Route.INSTRUMENT_SEARCH_PATH.value.format(
                instrument_type.value.upper(),
                query,
                limit
            )
        )

    def get_order_book(
        self,
        order_book_id: str,
        instrument_type: InstrumentType
    ):
        """ Get order book info

        Returns:

            {
                'account': {
                    'buyingPower': float,
                    'id': str,
                    'name': str,
                    'totalBalance': float,
                    'type': str
                },
                'fund': {
                    'NAV': float,
                    'buyFee': float,
                    'buyTradeDate': str,
                    'buyVisibleDate': str,
                    'id': str,
                    'loanFactor': float,
                    'managementFee': float,
                    'minStartAmount': float,
                    'name': str,
                    'otherFees': str,
                    'otherOrderDescription': str,
                    'positionValue': float,
                    'positionVolume': float,
                    'prospectus': str,
                    'sellFee': float,
                    'sellTradeDate': str,
                    'sellVisibleDate': str,
                    'stopTime': str,
                    'tradable': bool,
                    'type': str
                }
            }
        """
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
        """ Get info about multiple order books

        Returns:

            [{
                'changePercentOneYear': float,
                'changePercentPeriod': float,
                'changePercentThreeMonths': float,
                'currency': str,
                'id': str,
                'instrumentType': str,
                'lastUpdated': str,
                'managementFee': float,
                'minMonthlySavingAmount': float,
                'name': str,
                'prospectus': str,
                'rating': int,
                'risk': int,
                'tradable': bool
            }]
        """

        return self.__call(
            HttpMethod.GET,
            Route.ORDERBOOK_LIST_PATH.value.format(
                ','.join(order_book_ids)
            )
        )

    def get_positions(self):
        """ Get owned positions

        Returns:

            {
                'instrumentPositions': [{
                    'instrumentType': str,
                    'positions': [{
                        'accountId': str,
                        'accountName': str,
                        'accountType': str,
                        'acquiredValue': float,
                        'averageAcquiredPrice': float,
                        'change': float,
                        'changePercent': float,
                        'changePercentPeriod': float,
                        'changePercentThreeMonths': float,
                        'currency': str,
                        'depositable': bool,
                        'lastPrice': float,
                        'lastPriceUpdated': str,
                        'name': str,
                        'orderbookId': str,
                        'profit': float,
                        'profitPercent': float,
                        'tradable': bool,
                        'value': float,
                        'volume': float
                        }],
                    'todaysProfitPercent': float,
                    'totalProfitPercent': float,
                    'totalProfitValue': float,
                    'totalValue': float
                }],
                'totalBalance': float,
                'totalBuyingPower': float,
                'totalOwnCapital': float,
                'totalProfit': float,
                'totalProfitPercent': float
            }
        """

        return self.__call(HttpMethod.GET, Route.POSITIONS_PATH.value)

    def get_insights_report(
        self,
        account_id: str,
        time_period: TimePeriod
    ):
        """ Get report about the development of your owned positions during the specified timeperiod

        Returns:

            {
                'developmentResponse': {
                    'chartData': [{
                        'development': float,
                        'dividends': float,
                        'month': int,
                        'total': float,
                        'year': int
                    }],
                    'hasUnlistedInstrument': bool,
                    'instruments': [{
                        'instrumentDisplayName': str,
                        'instrumentType': str,
                        'outcome': {
                            'balanceDevelopments': List,
                            'development': float,
                            'dividends': float,
                            'total': float
                        },
                        'positions': [{
                            'currentPosition': float,
                            'endValue': float,
                            'isin': str,
                            'link': {
                                'buyable': bool,
                                'flagCode': str,
                                'linkDisplay': str,
                                'orderbookId': str,
                                'sellable': bool,
                                'shortLinkDisplay': str,
                                'tradeable': bool,
                                'type': str,
                                'urlDisplayName': str
                            },
                            'outcome': {
                                'balanceDevelopments': List,
                                'development': float,
                                'developmentPartOfTotalDevelopmentInPercent': float,
                                'dividends': float,
                                'dividendsPartOfTotalDevelopmentInPercent': float,
                                'stake': float,
                                'total': float,
                                'totalBuyAmount': float,
                                'totalDevelopmentInPercent': float,
                                'totalOtherAmount': float,
                                'totalSellAmount': float,
                                'totalTurnover': float,
                                'transactionTotals': [{
                                    'count': int,
                                    'presentableTransactionType': str,
                                    'totalAmount': str,
                                    'transactionType': str
                                }],
                                'transactions': [{
                                    'accountName': str,
                                    'amount': str,
                                    'date': str,
                                    'isin': str,
                                    'price': float,
                                    'type': str,
                                    'volume': float
                                }]
                            },
                            'shortName': str,
                            'startValue': float
                        }],
                        'totalOutcome': {
                            'development': float,
                            'dividends': float,
                            'total': float
                        },
                        'totalOutcomeForUnknownDevelopments': {
                            'development': float,
                            'dividends': float,
                            'total': float
                        },
                        'unknownPositionDevelopments': List
                    }],
                    'fromDate': str,
                    'otherTransactions': {
                        'otherTransactionsGroups': List,
                        'total': int
                    },
                    'totalDevelopment': {
                        'currentValue': float,
                        'startValue': float,
                        'totalChange': float
                    },
                    'transactionsResponse': {
                        'allTransactions': [{
                            'month': int,
                            'total': float,
                            'totalAutogiro': float,
                            'totalDeposits': float,
                            'totalWithdrawals': float,
                            'transactions': [{
                                'accountName': str,
                                'accountTypeName': str,
                                'amount': float,
                                'date': str,
                                'description': str,
                                'transactionType': str,
                                'transactionTypeName': str
                            }],
                            'year': int,
                            'yearMonth': str
                        }],
                        'chartData': [{
                            'allTransactions': float,
                            'autogiro': float,
                            'deposit': float,
                            'month': int,
                            'withdrawal': float,
                            'year': int
                        }],
                        'totalAll': float,
                        'totalAutogiro': float,
                        'totalDeposits': float,
                        'totalWithdraws': float
                    }
                }
            }
        """
        return self.__call(
            HttpMethod.GET,
            Route.INSIGHTS_PATH.value.format(
                time_period.value,
                account_id
            )
        )

    def get_deals_and_orders(self):
        """ Get currently active deals and orders

        Returns:

            {
                'accounts': [{'id': str, 'name': str', 'type': str}],
                'deals': [{
                    'account': {'id': str, 'name': str, 'type': str},
                    'dealId': str,
                    'dealTime': str,
                    'marketTransaction': bool,
                    'orderId': str,
                    'orderbook': {
                        'currency': str,
                        'id': str,
                        'marketPlace': str,
                        'name': str,
                        'type': str
                    },
                    'price': float,
                    'sum': float,
                    'type': str,
                    'volume': float
                }],
                'orders': [{
                    'account': {'id': str, 'name': str, 'type': str},
                    'deletable': bool,
                    'marketTransaction': bool,
                    'modifyAllowed': bool,
                    'orderDateTime': str,
                    'orderId': str,
                    'orderbook': {
                        'currency': str,
                        'id': str,
                        'marketPlace': str,
                        'name': str,
                        'type': str
                    },
                    'price': float,
                    'rawStatus': str,
                    'status': str,
                    'statusDescription': str,
                    'sum': float,
                    'transactionFees': {
                        'commission': float,
                        'fundOrderFee': {'rate': float, 'sum': float},
                        'marketFees': float,
                        'totalFees': float,
                        'totalSum': float,
                        'totalSumWithoutFees': float
                    },
                    'type': str,
                    'visibleOnAccountDate': str
                }],
                'reservedAmount': float
            }
        """
        return self.__call(
            HttpMethod.GET,
            Route.DEALS_AND_ORDERS_PATH.value
        )

    def get_inspiration_lists(self):
        """ Get all available inspiration lists

        This returns lists similar to the ones found on:

        https://www.avanza.se/aktier/aktieinspiration.html

        https://www.avanza.se/fonder/fondinspiration.html

        Returns:

            [{
                'averageChange': float,
                'averageChangeSinceThreeMonths': float,
                'highlightField': {'label': str, 'percent': bool},
                'id': str,
                'imageUrl': str,
                'information': str,
                'instrumentType': str,
                'name': str,
                'orderbooks': [{
                    'change': float,
                    'changePercent': float,
                    'currency': str,
                    'flagCode': str,
                    'highlightValue': int,
                    'id': str,
                    'lastPrice': float,
                    'name': str,
                    'priceOneYearAgo': float,
                    'priceThreeMonthsAgo': float,
                    'updated': str
                }],
                'statistics': {
                    'negativeCount': int,
                    'negativePercent': float,
                    'neutralCount': int,
                    'neutralPercent': float,
                    'positiveCount': int,
                    'positivePercent': float
                }
            }]
        """
        return self.__call(
            HttpMethod.GET,
            Route.INSPIRATION_LIST_PATH.value.format('')
        )

    def get_inspiration_list(self, list_type: ListType):
        """ Get inspiration list

        Returns:

            {
                'averageChangeSinceThreeMonths': float,
                'highlightField': {'label': str, 'percent': bool},
                'id': str,
                'imageUrl': str,
                'information': str,
                'instrumentType': str,
                'name': str,
                'orderbooks': [{
                    'changeSinceOneDay': float,
                    'changeSinceOneYear': float,
                    'changeSinceThreeMonths': float,
                    'highlightValue': int,
                    'id': str,
                    'lastUpdated': str,
                    'name': str
                }],
                'statistics': {
                    'negativeCount': int,
                    'negativePercent': float,
                    'neutralCount': int,
                    'neutralPercent': float,
                    'positiveCount': int,
                    'positivePercent': float
                }
            }
        """
        return self.__call(
            HttpMethod.GET,
            Route.INSPIRATION_LIST_PATH.value.format(
                list_type.value
            )
        )

    def get_chart_data(self, order_book_id: str, period: TimePeriod, resolution: Optional[Resolution] = None):
        """ Return chart data for an order book for the specified time period with given resolution

        Returns:

            {
                'ohlc': [{'timestamp': int, 'open': float, 'close': float, 'low': float, 'high': float, 'totalVolumeTraded': int}]
                'metadata':
                { 'resolution' : {'chartResolution': str,
                                  'availableResolutions': [str]}
                }
                'from' : str,
                'to' : str,
                'previousClosingPrice' : float
            }
        """
        options = {
            'timePeriod': period.value.lower()
        }

        if resolution is not None:
            options['resolution'] = resolution.value.lower()

        return self.__call(
            HttpMethod.GET,
            Route.CHARTDATA_PATH.value.format(order_book_id),
            options
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
        """ Place an order

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
                'accountId': account_id,
                'orderbookId': order_book_id,
                'side': order_type.value,
                'price': price,
                'validUntil': valid_until.isoformat(),
                'volume': volume
            }
        )

    def place_order_buy_fund(
        self,
        account_id: str,
        order_book_id: str,
        amount: float
    ):
        """ Place a buy order for a fund

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
            {
                'orderbookId': order_book_id,
                'accountId': account_id,
                'amount': amount
            }
        )

    def place_order_sell_fund(
        self,
        account_id: str,
        order_book_id: str,
        volume: float
    ):
        """ Place a sell order for a fund

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
            {
                'orderbookId': order_book_id,
                'accountId': account_id,
                'volume': volume
            }
        )

    def place_stop_loss_order(
        self,
        parent_stop_loss_id: str,
        account_id: str,
        order_book_id: str,
        stop_loss_trigger: StopLossTrigger,
        stop_loss_order_event: StopLossOrderEvent,
    ):
        """ Place an stop loss order

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
                'parentStopLossId': parent_stop_loss_id,
                'accountId': account_id,
                'orderBookId': order_book_id,
                'stopLossTrigger': {
                    'type': stop_loss_trigger.type,
                    'value': stop_loss_trigger.value,
                    'validUntil': stop_loss_trigger.valid_until.isoformat()
                },
                'stopLossOrderEvent': {
                    'type': stop_loss_order_event.type,
                    'price': stop_loss_order_event.price,
                    'volume': stop_loss_order_event.volume,
                    'validDays': stop_loss_order_event.valid_days,
                    'priceType': stop_loss_order_event.price_type,
                    'shortSellingAllowed': stop_loss_order_event.short_selling_allowed
                }
            }
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
        volume: int
    ):
        """ Update an existing order

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
            Route.ORDER_EDIT_PATH.value.format(
                instrument_type.value,
                order_id
            ),
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
        account_id: str,
        order_id: str
    ):
        """ Get an existing order

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
                order_id
            )
        )

    def get_all_stop_losses(
        self
    ):
        """ Get open stop losses

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
        return self.__call(
            HttpMethod.GET,
            Route.STOP_LOSS_PATH.value
        )

    def delete_order(
        self,
        account_id: str,
        order_id: str
    ):
        """ Delete an existing order

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
            {
                'accountId': account_id,
                'orderId': order_id
            }
        )

    def get_monthly_savings_by_account_id(
        self,
        account_id: str
    ):
        """ Get monthly savings at avanza for specific account

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
            HttpMethod.GET,
            Route.MONTHLY_SAVINGS_PATH.value.format(account_id)
        )

    def get_all_monthly_savings(
        self
    ):
        """ Get your monthly savings at Avanza

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
            HttpMethod.GET,
            Route.MONTHLY_SAVINGS_PATH.value.format('')
        )

    def pause_monthly_saving(
        self,
        account_id: str,
        monthly_savings_id: str
    ):
        """ Pause an active monthly saving

        Returns:
            'OK'

        """

        return self.__call(
            HttpMethod.PUT,
            Route.MONTHLY_SAVINGS_PAUSE_PATH.value.format(
                account_id,
                monthly_savings_id
            )
        )

    def resume_monthly_saving(
        self,
        account_id: str,
        monthly_savings_id: str
    ):
        """ Resume a paused monthly saving

        Returns:
            'OK'

        """

        return self.__call(
            HttpMethod.PUT,
            Route.MONTHLY_SAVINGS_RESUME_PATH.value.format(
                account_id,
                monthly_savings_id
            )
        )

    def delete_monthly_saving(
        self,
        account_id: str,
        monthly_savings_id: str
    ) -> None:
        """ Deletes a monthly saving

        Returns:
            None

        """

        return self.__call(
            HttpMethod.DELETE,
            Route.MONTHLY_SAVINGS_REMOVE_PATH.value.format(
                account_id,
                monthly_savings_id
            )
        )

    def create_monthly_saving(
        self,
        account_id: str,
        amount: int,
        transfer_day_of_month: int,
        purchase_day_of_month: int,
        clearing_and_account_number: str,
        fund_distribution: Dict[str, int]
    ):
        """ Create a monthly saving at Avanza

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
                "transfer_day_of_month is outside the valid range of (1-31)")

        if not 1 <= purchase_day_of_month <= 31:
            raise ValueError(
                "purchase_day_of_month is outside the valid range of (1-31)")

        if transfer_day_of_month >= purchase_day_of_month:
            raise ValueError(
                "transfer_day_of_month must occur before purchase_day_of_month")

        if len(fund_distribution) == 0:
            raise ValueError(
                "No founds were specified in the fund_distribution"
            )

        if sum(fund_distribution.values()) != 100:
            raise ValueError("The fund_distribution values must total 100")

        return self.__call(
            HttpMethod.POST,
            Route.MONTHLY_SAVINGS_CREATE_PATH.value.format(account_id),
            {
                'amount': amount,
                'autogiro': {
                    'dayOfMonth': transfer_day_of_month,
                    'externalClearingAndAccount': clearing_and_account_number
                },
                'fundDistribution': {
                    'dayOfMonth': purchase_day_of_month,
                    'fundDistributions': fund_distribution
                }
            }
        )

    def get_transactions(
        self,
        account_id: str = None,
        transaction_type: TransactionType = None,
        transactions_from: date = None,
        transactions_to: date = None,
        min_amount: int = None,
        max_amount: int = None,
        order_book_ids: Sequence[str] = []
    ):
        """ Get transactions, optionally apply search criteria.

        Args:
            account_id: A valid account id.

            transaction_type: A transaction type.
                Any combination of account id and transaction type is valid.
                E.g. it is fully optional to provide account_id and/or transaction_type.

            transactions_from: Fetch transactions from this date.

            transactions_to: Fetch transactions to this date.

            min_amount: Only fetch transactions of at least this value.

            max_amount: Only fetch transactions of at most this value.

            order_book_ids: Only fetch transactions involving this/these orderbooks.

        Returns:

            {
                'transactions': [
                    {
                        'account': {
                            'type': str,
                            'name': str,
                            'id': int
                        },
                        'noteId': str,
                        'transactionType': str,
                        'verificationDate': str,
                        'sum': float,
                        'description': str,
                        'currency': str,
                        'amount': float,
                        'orderbook': {
                            'isin': str,
                            'currency': str,
                            'name': str,
                            'id': int,
                            'type': str
                        },
                        'price': float,
                        'volume': float,
                        'id': str
                    },
                ],
                'totalNumberOfTransactions': int,
                'totalAmounts': {
                    str: {
                        'total': float,
                        'BUY': {
                            'total': float,
                            'orderbooks': [
                                {
                                    'total': float,
                                    'isin': str,
                                    'currency': str,
                                    'name': str,
                                    'flagCode': str,
                                    'id': int,
                                    'type': str
                                },
                            ]
                        },
                        'SELL': {
                            'total': float,
                            'orderbooks': [
                                {
                                    'total': float,
                                    'isin': str,
                                    'currency': str,
                                    'name': str,
                                    'flagCode': str,
                                    'id': int,
                                    'type': str
                                },
                            ]
                        }
                    }
                }
            }
        """
        options = {}

        if transactions_from:
            options['from'] = transactions_from.isoformat()
        if transactions_to:
            options['to'] = transactions_to.isoformat()
        if min_amount:
            options['minAmount'] = min_amount
        if max_amount:
            options['maxAmount'] = max_amount
        if order_book_ids:
            options['orderbookId'] = ','.join(order_book_ids)

        return self.__call(
            HttpMethod.GET,
            Route.TRANSACTIONS_PATH.value.format('/'.join(filter(None, [account_id, transaction_type.value if transaction_type else None]))),
            options
        )

    def get_transactions_details(
        self,
        transaction_details_types: Sequence[TransactionsDetailsType] = [],
        transactions_from: date = None,
        transactions_to: date = None,
        isin: str = None,
        max_elements: int = 1000
    ):
        """ Get transactions, optionally apply criterias.

        Args:
            transaction_types: One or more transaction types.

            transactions_from: Fetch transactions from this date.

            transactions_to: Fetch transactions to this date.

            isin: Only fetch transactions for specified isin.

            max_elements: Limit result to N transactions.

        Returns:

            {
                'firstTransactionDate': str,
                'transactionsFilter': {
                    'accountIds: null|str,
                    'dateRange': {
                        'from': str,
                        'to': str
                    }
                    'isin': null|str,
                    'transacitonTypes': null|array[str],
                }
                'transactionsAfterFiltering' int,
                'transactions': [
                    {
                        'account': {
                            'type': str,
                            'name': str,
                            'id': int,
                            'urlParameterId': str,
                        },
                        'amount': {
                            'decimalPrecision': int,
                            'unit': str,
                            'unitType': str,
                            'value': int,
                        },
                        'availabilityDate': str,
                        'comission': null|?,
                        'currencyRate': null|?,
                        'date': str,
                        'description': str,
                        'foreignTaxRate': null|?,
                        'id': str,
                        'instrumentName': str,
                        'intraday': bool,
                        'isin': str,
                        'noteId': null|str
                        'onCreditAccount': bool,
                        'orderbook': {
                            'isin': str,
                            'currency': str,
                            'flagCode': null|str,
                            'name': str,
                            'id': int,
                            'type': str,
                            'volumeFactor': int,
                            'flagCode': null|str,
                        },
                        'priceInAccountCurrency': {
                            'decimalPrecision': int,
                            'unit': str,
                            'unitType': str,
                            'value': float,
                        },
                        'priceInTradedCurrency': {
                            'decimalPrecision': int,
                            'unit': str,
                            'unitType': str,
                            'value': float,
                        },
                        'settlementDate: str,
                        'type': str,
                        'volume': {
                            'decimalPrecision': int,
                            'unit': str,
                            'unitType': str,
                            'value': float,
                        }
                    },
                ],
            }
        """
        options = {}
        options['maxElements'] = max_elements

        if transaction_details_types:
            options['transactionTypes'] = ','.join(transaction_details_types)
        if transactions_from:
            options['from'] = transactions_from.isoformat()
        if transactions_to:
            options['to'] = transactions_to.isoformat()
        if isin:
            options['isin'] = isin

        return self.__call(
            HttpMethod.GET,
            Route.TRANSACTIONS_DETAILS_PATH.value,
            options
        )

    def get_note_as_pdf(self, url_parameter_id: str, note_id: str):
        return self.__call(
            HttpMethod.GET,
            Route.NOTE_PATH.value.format(url_parameter_id, note_id),
            return_content=True
        )

    def set_price_alert(
        self,
        order_book_id: str,
        price: float,
        valid_until: date,
        notification: bool = True,
        email: bool = False,
        sms: bool = False
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
                'price': price,
                'validUntil': valid_until.isoformat(),
                "notification": notification,
                "email": email,
                "sms": sms
            }
        )

    def get_price_alert(self, order_book_id: str):
        """
        Gets all the price alerts for the specified orderbook.

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
            Route.PRICE_ALERT_PATH.value.format(order_book_id, alert_id)+f"/{alert_id}",
        )

    def get_offers(self):
        """ Return current offers

        Returns:

            [
                {
                    "customerOfferId": str,
                    "title": str,
                    "lastResponseDate": str,
                    "type": str,
                    "hasResponded": bool
                }
            ]
        """

        return self.__call(
            HttpMethod.GET,
            Route.CURRENT_OFFERS_PATH.value
        )
