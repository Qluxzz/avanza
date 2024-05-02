# Avanza

A Python library for the unofficial Avanza API. This library is based on the existing JavaScript library [Avanza](https://github.com/fhqvst/avanza).

Please note that this is only a proof of concept, hence not meant to be used by anyone.

It might also be valuable to note that I am not affiliated with Avanza Bank AB in any way. The underlying API can be taken down or changed without warning at any point in time.

## Installation

[![](https://img.shields.io/pypi/v/avanza-api?style=flat-square&logo=pypi "Shiprock, New Mexico by Beau Rogers")](https://pypi.org/project/avanza-api/)

```python
pip install avanza-api
```

## Getting a TOTP Secret

**NOTE: Since May 2018 two-factor authentication is required to log in.**

Here are the steps to get your TOTP Secret:

1. Go to Profil > Inställningar > Sajtinställningar > Inloggning och utloggning > Användarnamn > Tvåfaktorsinloggning and click "Återaktivera". (_Only do this step if you have already set up two-factor auth._)
1. Click "Aktivera" on the next screen.
1. Select "Annan app för tvåfaktorsinloggning".
1. Click "Kan du inte scanna QR-koden?" to reveal your TOTP Secret.
1. Generate the TOTP code using the python code below and paste the TOTP code in the field below where you found the TOTP Secret.
1. Done! From now on all you have to do is supply your secret in the constructor as in the examples below.

#### Generate TOTP code:

```Python
import hashlib
import pyotp
totp = pyotp.TOTP('MY_TOTP_SECRET', digest=hashlib.sha1)
print(totp.now())
```

## Example

Authenticate and fetch account overview:

```python
from avanza import Avanza
avanza = Avanza({
    'username': 'MY_USERNAME',
    'password': 'MY_PASSWORD',
    'totpSecret': 'MY_TOTP_SECRET'
})

overview = avanza.get_overview()
```

Get info about a certain account

```python
from avanza import Avanza, TimePeriod

avanza = Avanza({
    'username': 'MY_USERNAME',
    'password': 'MY_PASSWORD',
    'totpSecret': 'MY_TOTP_SECRET'
})

report = avanza.get_insights_report(
    account_id='XXXXXXX',
    time_period=TimePeriod.ONE_WEEK
)
```

Place an order

```python
from avanza import Avanza, OrderType

avanza = Avanza({
    'username': 'MY_USERNAME',
    'password': 'MY_PASSWORD',
    'totpSecret': 'MY_TOTP_SECRET'
})

result = avanza.place_order(
    account_id='XXXXXXX',
    order_book_id='XXXXXX',
    order_type=OrderType.BUY,
    price=13.37,
    valid_until=date.fromisoformat('2011-11-11'),
    volume=42
)
```

Subscribe to real time data

```python
import asyncio
from avanza import Avanza, ChannelType

def callback(data):
    # Do something with the quotes data here
    print(data)

async def subscribe_to_channel(avanza: Avanza):
    await avanza.subscribe_to_id(
        ChannelType.QUOTES,
        "19002", # OMX Stockholm 30
        callback
    )

def main():
    avanza = Avanza({
        'username': 'MY_USERNAME',
        'password': 'MY_PASSWORD',
        'totpSecret': 'MY_TOTP_SECRET'
    })

    asyncio.get_event_loop().run_until_complete(
        subscribe_to_channel(avanza)
    )
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
```

## TESTING

Tests are stored in [/tests](https://github.com/Qluxzz/avanza/tree/master/tests)

The tests are using [Pydanctic](https://github.com/pydantic/pydantic) models which are used to validate that the response model is what's expected

There are tests that call all available GET endpoints and validates that the response model of these endpoints are correct and that the endpoint still exists

To run the tests you first need to create a `.env` file and have the following keys in it:

```
USERNAME=
PASSWORD=
TOTP_SECRET=
ACCOUNT_ID=
PRICE_ALERT_ORDER_BOOK_ID=
```

Then you can run the tests using `python -m unittest`

## LICENSE

MIT license. See the LICENSE file for details.

## RESPONSIBILITIES

The author of this software is not responsible for any indirect damages (foreseeable or unforeseeable), such as, if necessary, loss or alteration of or fraudulent access to data, accidental transmission of viruses or of any other harmful element, loss of profits or opportunities, the cost of replacement goods and services or the attitude and behavior of a third party.
