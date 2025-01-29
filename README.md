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

## Testing

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

Then you can do one of the following:
- To run all tests: `python -m unittest`.
- To run a single test, such as `test_overview`: `python3 -m unittest tests.test_endpoints.ReturnModelTest.test_overview`.

## Extending/updating the API

Suppose we want to add a new method `get_foo_bar` to the API defined by `avanza.py` along with a test that both
- shows that the request sent by our new method yields a successful response from the server, and
- starts failing whenever Avanza makes breaking changes (attribute removal or data type changes) to their API.

The steps are then roughly these:

1. Add the method to `avanza.py`, making it call a URI using a route that you add to `constants.py`.
1. Add a simple test to `tests/test_endpoints.py` which calls the method using the `get_or_cache`
   wrapper function (but does not yet validate the JSON response received).
1. Run the test (see `Testing` above). As part of running the test, the said wrapper function will generate the file `get_foo_bar.json`.
1. Generate Pydantic models corresponding to the JSON response using the tool `datamodel-code-generator`:
   1. Install the tool into your virtual environment using `pip install datamodel-code-generator`.
   1. Run
      ```
      datamodel-codegen --class-name=FooBar --enable-version-header --target-python-version=3.9 \
        --input get_foo_bar.json --input-file-type=json \
        --output avanza/models/foo_bar.py --output-model-type=pydantic_v2.BaseModel
      ```
      to generate a tree of models corresponding to the JSON response to the module
      `avanza/models/foo_bar.py`. Note: The `--target-python-version` should match whatever
      version `REQUIRES_PYTHON` in `setup.py` indicates.
   1. Add the necessary import to `avanza/models/__init__.py`.
1. Update the test to validate the JSON response against the newly created model by adding the
   appropriate `model_validate` call. This way, the test will fail if Avanza updates their API (by default,
   attribute removals and data type changes will cause a test failure, but not addition of new attributes).

## License

MIT license. See the LICENSE file for details.

## Responsibilities

The author of this software is not responsible for any indirect damages (foreseeable or unforeseeable), such as, if necessary, loss or alteration of or fraudulent access to data, accidental transmission of viruses or of any other harmful element, loss of profits or opportunities, the cost of replacement goods and services or the attitude and behavior of a third party.
