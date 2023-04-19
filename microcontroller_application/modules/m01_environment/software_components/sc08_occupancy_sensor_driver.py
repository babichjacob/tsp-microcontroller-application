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
    to_human_detection: bounded_channel.Sender[
        FromEnvironmentToHumanDetectionOccupancy
    ],
    use_randomized_data: bool,
):
    LOGGER.debug("startup")

    if use_randomized_data:
        from random import getrandbits

        LOGGER.warning("using randomized data")

        last_occupancy_detected = NONE()
        while True:
            occupancy_detected = bool(getrandbits(1))

            LOGGER.info("(RANDOM) occupancy_detected: %s", occupancy_detected)

            some_occupancy_detected = Some(occupancy_detected)

            if some_occupancy_detected != last_occupancy_detected:
                message = FromEnvironmentToHumanDetectionOccupancy(
                    new_state=occupancy_detected
                )
                await to_human_detection.send(message)

            last_occupancy_detected = some_occupancy_detected

            await sleep(5)

    else:
        import serial

        # Initialize UART
        ser = serial.Serial("/dev/ttyS0", baudrate=115200)
        ser.flushInput()  # Clear UART Input buffer
        ser.flushOutput()  # Clear UART Output buffer

        last_occupancy_detected = NONE()
        while True:
            raw_response = ser.readline()
            response = raw_response.strip()
            occupancy_detected = response.find(b"1") != -1

            LOGGER.info("occupancy_detected: %s", occupancy_detected)

            some_occupancy_detected = Some(occupancy_detected)

            if some_occupancy_detected != last_occupancy_detected:
                message = FromEnvironmentToHumanDetectionOccupancy(
                    new_state=occupancy_detected
                )
                await to_human_detection.send(message)

            last_occupancy_detected = some_occupancy_detected

            await sleep(5)

    LOGGER.debug("shutdown")
