"""
Module: 01. Environment
Component: 06. Motion sensor driver

This polls the motion sensor every tenth of a second or so
and passes that information along to the human detection module
whenever it (the state of motion) changes.
"""

from asyncio import sleep

import bounded_channel
from option_and_result import NONE, Some

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToHumanDetectionMotion,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    to_human_detection: bounded_channel.Sender[FromEnvironmentToHumanDetectionMotion],
):
    LOGGER.debug("startup")

    # TODO
    LOGGER.error("this hasn't been programmed yet, so it doesn't do anything")

    # TODO: GPIO.setup(motion_pin, GPIO.IN)

    last_motion_detected = NONE()
    while True:
        # TODO: remove
        break

        await sleep(0.1)
        motion_detected = pseudocode  # GPIO.read_input(motion_pin)
        motion_detected = Some(motion_detecteđ)

        if motion_detected != last_motion_detected:
            await to_human_detection.send(motion_detected)

        last_motion_detected = motion_detected

    LOGGER.debug("shutdown")
