"""
This module is concerned with keeping track
of each trusted user’s lighting preferences.
"""

from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromPreferencesToControl,
    FromPreferencesToProxy,
    FromProxyToPreferences,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_proxy_module: Receiver[FromProxyToPreferences],
    to_proxy_module: Sender[FromPreferencesToProxy],
    to_control_module: Sender[FromPreferencesToControl],
):
    "Run the preferences module"

    LOGGER.debug("startup")

    LOGGER.debug("shutdown")
