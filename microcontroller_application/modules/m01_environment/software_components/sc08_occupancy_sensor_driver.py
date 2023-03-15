"""
Module: 01. Environment
Component: 08. Occupancy sensor driver

This polls the occupancy sensor every 5 seconds
and passes that information along to the human detection module
whenever it (the state of occupancy) changes.
"""

from asyncio import sleep

import bounded_channel
from option_and_result import NONE, Some

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToHumanDetectionOccupancy,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    to_human_detection: bounded_channel.Sender[FromEnvironmentToHumanDetectionOccupancy],
):
    LOGGER.debug("startup")

    # TODO
    LOGGER.error("this hasn't been programmed yet, so it doesn't do anything")

    # TODO: GPIO.setup(occupancy_pin, GPIO.IN)

    last_occupancy_detected = NONE()
    while True:
        # TODO: remove
        break

        await sleep(5)
        occupancy_detected = pseudocode  # GPIO.read_input(occupancy_pin)
        occupancy_detected = Some(occupancy_detected)

        if occupancy_detected != last_occupancy_detected:
            await to_human_detection.send(occupancy_detected)

        last_occupancy_detected = occupancy_detected

    LOGGER.debug("shutdown")
