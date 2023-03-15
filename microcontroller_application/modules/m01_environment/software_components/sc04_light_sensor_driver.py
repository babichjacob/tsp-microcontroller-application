"""
Module: 01. Environment
Component: 04. Light sensor driver

This gets the ambient light intensity (in lux) every second or so.
"""

import bounded_channel
from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToControl,
)

from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    to_control: bounded_channel.Sender[FromEnvironmentToControl],
):
    LOGGER.debug("startup")

    # TODO
    LOGGER.error("this hasn't been programmed yet, so it doesn't do anything")

    LOGGER.debug("shutdown")
