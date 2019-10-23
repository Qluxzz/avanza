import hashlib

import requests
import pyotp

from constants import CONSTANTS

BASE_URL = 'https://www.avanza.se'
MIN_INACTIVE_MINUTES = 30
MAX_INACTIVE_MINUTES = 60 * 24


class Avanza:
    def __init__(self, credentials):
        self._authenticationTimeout = MAX_INACTIVE_MINUTES
        self._authenticated = False
        self._session = requests.Session()

        response_body, credentials = self.__authenticate(credentials)

        self._authenticated = True
        self._credentials = credentials
        self._authentication_session = response_body['authenticationSession']
        self._push_subscription_id = response_body['pushSubscriptionId']
        self._customer_id = response_body['customerId']

    def __authenticate(self, credentials):
        if not MIN_INACTIVE_MINUTES <= self._authenticationTimeout <= MAX_INACTIVE_MINUTES:
            return ValueError(f'Session timeout not in range {MIN_INACTIVE_MINUTES} - {MAX_INACTIVE_MINUTES} minutes')

        data = {
            'maxInactiveMinutes': self._authenticationTimeout,
            'username': credentials['username'],
            'password': credentials['password']
        }

        response = self._session.post(
            f"{BASE_URL}{CONSTANTS['paths']['AUTHENTICATION_PATH']}",
            json=data
        )

        response_body = response.json()

        # No second factor required, continue with normal login
        if response_body['twoFactorLogin'] is None:
            return response_body, credentials

        tfa_method = response_body['twoFactorLogin']['method']

        if tfa_method != 'TOTP':
            raise ValueError(
                f"Unsupported two factor method {tfa_method}"
            )

        return self.__validate_2fa(credentials)

    def __validate_2fa(self, credentials):
        totp = pyotp.TOTP(credentials['totpSecret'], digest=hashlib.sha1)

        totp_code = totp.now() if credentials['totpSecret'] else credentials['totp']

        if totp_code is None:
            raise ValueError('Missing totp or totpSecret')

        response = self._session.post(
            '{}{}'.format(BASE_URL, CONSTANTS['paths']['TOTP_PATH']),
            json={
                'method': 'TOTP',
                'totpCode': totp_code
            }
        )

        response_body = response.json()

        return response_body, credentials

    def __call(self, method, path):
        method_call = {
            'GET': self._session.get,
            'POST': self._session.post
        }[method]

        if method_call is None:
            raise ValueError(f'Unknown method type {method}')

        response = method_call(f'{BASE_URL}{path}')

        if not response:
            return

        return response.json()

    def get_overview(self):
        return self.__call('GET', CONSTANTS['paths']['OVERVIEW_PATH'])

    def get_insights_report(self, time_period, account_id):
        return self.__call(
            'GET',
            CONSTANTS['paths']['INSIGHTS_PATH'].format(
                time_period,
                account_id
            )
        )
