"""
Module: 01. Environment
Component: 06. Motion sensor driver

This polls the motion sensor every tenth of a second or so
and passes that information along to the human detection module
whenever it (the state of motion) changes.
"""

from asyncio import sleep

import bounded_channel
from option_and_result import NONE, Option, Some

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToHumanDetectionMotion,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    to_human_detection: bounded_channel.Sender[FromEnvironmentToHumanDetectionMotion],
    use_randomized_data: bool,
):
    LOGGER.debug("startup")

    if use_randomized_data:
        from random import getrandbits

        LOGGER.warning("using randomized data")

        last_motion_detected = NONE()

        while True:
            motion_detected = bool(getrandbits(1))

            LOGGER.info("(RANDOM) motion_detected: %s", motion_detected)

            some_motion_detected = Some(motion_detected)

            if motion_detected != last_motion_detected:
                message = FromEnvironmentToHumanDetectionMotion(
                    new_state=motion_detected
                )
                await to_human_detection.send(message)

            last_motion_detected = some_motion_detected
            await sleep(0.3)

    else:
        import RPi.GPIO as GPIO

        motion_pin = 25
        GPIO.setup(motion_pin, GPIO.IN)

        last_motion_detected: Option[bool] = NONE()

        while True:
            motion_detected = GPIO.input(motion_pin) == 1

            LOGGER.info("motion_detected: %s", motion_detected)

            some_motion_detected = Some(motion_detected)

            if motion_detected != last_motion_detected:
                message = FromEnvironmentToHumanDetectionMotion(
                    new_state=motion_detected
                )
                await to_human_detection.send(message)

            last_motion_detected = some_motion_detected
            await sleep(0.3)

    LOGGER.debug("shutdown")
