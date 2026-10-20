"""OPNsense HAProxy API client and module base class."""

from .OpnsenseApi import (
    ConfigTestError,
    Haproxy,
    ObjectNotFoundError,
    ObjectTypeError,
    OpnsenseApiError,
)
from .OpnsenseModule import OpnsenseHaproxyModule

__all__ = [
    "ConfigTestError",
    "Haproxy",
    "ObjectNotFoundError",
    "ObjectTypeError",
    "OpnsenseApiError",
    "OpnsenseHaproxyModule",
]