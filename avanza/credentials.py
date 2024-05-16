from typing import Dict

from pydantic import BaseModel, Field
import pyotp
import hashlib
import abc


class BaseCredentials(BaseModel, abc.ABC):
    username: str
    password: str

    class Config:
        arbitrary_types_allowed = True

    @property
    @abc.abstractmethod
    def totp_code(self) -> str:
        pass

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls is BaseCredentials:
            raise TypeError("Cannot instantiate BaseCredentials directly")
        super().__init_subclass__(**kwargs)


class SecretCredentials(BaseCredentials):
    # It would've been nice to let this be a private var
    # but all pydantic versions don't support multiple aliases,
    # so we can't use both snake case and camel case then
    totp_secret: str = Field(..., alias="totpSecret")

    class Config:
        allow_mutation = False

    @property
    def totp_code(self) -> str:
        return pyotp.TOTP(self.totp_secret, digest=hashlib.sha1).now()


class TokenCredentials(BaseCredentials):
    # It would've been nice to let this be a private var
    # but all pydantic versions don't support multiple aliases,
    # so we can't use both snake case and camel case then
    totp_token: str = Field(..., alias="totpToken")

    class Config:
        allow_mutation = False

    @property
    def totp_code(self):
        return self.totp_token


def backwards_compatible_serialization(d: Dict[str, str]) -> BaseCredentials:
    """
    Will try to find the correct subclass based on which totp method is supplied,
    throws ValueError if none is present
    """
    keys = d.keys()
    if "totp_secret" in keys or "totpSecret" in keys:
        return SecretCredentials(**d)
    if "totp_token" in keys or "totpToken" in keys:
        return TokenCredentials(**d)
    raise ValueError("Could not find totp_secret or totp_token")
