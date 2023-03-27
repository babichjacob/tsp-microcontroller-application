"""
Module: 07. Lighting

This module is concerned with lighting the room up (if told to do so) and to what extent.
"""

from asyncio import gather

import bounded_channel

from microcontroller_application.interfaces.message_types import FromControlToLighting
from microcontroller_application.log import get_logger

from .software_components import sc02x_dimmer_connector

LOGGER = get_logger(__name__)


async def run(
    *,
    from_control: bounded_channel.Receiver[FromControlToLighting],
    use_real_hardware: bool
):
    LOGGER.debug("startup")

    sc02x_dimmer_connector_task = sc02x_dimmer_connector.run(
        from_control=from_control, use_real_hardware=use_real_hardware
    )

    await gather(sc02x_dimmer_connector_task)

    LOGGER.debug("shutdown")
