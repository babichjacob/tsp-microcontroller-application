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
    from_proxy: Receiver[FromProxyToPreferences],
    to_proxy: Sender[FromPreferencesToProxy],
    to_control: Sender[FromPreferencesToControl],
):
    "Run the preferences module"

    LOGGER.debug("startup")

    # TODO
    LOGGER.error("this hasn't been programmed yet, so it doesn't do anything")

    LOGGER.debug("shutdown")
