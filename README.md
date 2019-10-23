# Avanza

A Python library for the unofficial Avanza API. This library is based on the existing JavaScript library [Avanza](https://github.com/fhqvst/avanza).

Please note that this is only a proof of concept, hence not meant to be used by anyone.

It might also be valuable to note that I am not affiliated with Avanza Bank AB in any way. The underlying API can be taken down or changed without warning at any point in time.

## Getting a TOTP Secret

**NOTE: Since May 2018 two-factor authentication is required to log in.**

Here are the steps to get your TOTP Secret:

1. Go to Mina Sidor > Profil > Sajtinställningar > Tvåfaktorsinloggning and click "Återaktivera". (*Only do this step if you have already set up two-factor auth.*)
1. Click "Aktivera" on the next screen.
1. Select "Annan app för tvåfaktorsinloggning".
1. Click "Kan du inte scanna QR-koden?" to reveal your TOTP Secret.
1. Done! From now on all you have to do is supply your secret in the `authenticate()` function as in the example below.

## Example

Authenticate and fetch currently held positions:

```python
from avanza import Avanza
avanza = Avanza({
    'username': 'MY_USERNAME',
    'password': 'MY_PASSWORD',
    'totpSecret': 'MY_TOTP_SECRET'
})

overview = avanza.get_overview()
print(overview)
```

## LICENSE

MIT license. See the LICENSE file for details.

## RESPONSIBILITIES

The author of this software is not responsible for any indirect damages (foreseeable or unforeseeable), such as, if necessary, loss or alteration of or fraudulent access to data, accidental transmission of viruses or of any other harmful element, loss of profits or opportunities, the cost of replacement goods and services or the attitude and behavior of a third party.