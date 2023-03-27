"""
Module: 01. Environment
Component: 04. Light sensor driver

This gets the ambient light intensity (in lux) every second or so.
"""

from asyncio import sleep

import bounded_channel
import numpy as np

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToControl,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    to_control: bounded_channel.Sender[FromEnvironmentToControl],
    use_randomized_data: bool,
):
    LOGGER.debug("startup")

    if use_randomized_data:
        LOGGER.warning("using randomized data")

        while True:
            lux = 2 ** (np.random.normal(10, 2))

            LOGGER.info("(RANDOM) lux: %f", lux)

            # This is just an approximation
            as_lumens = lux * (600 / 20000)

            await to_control.send(
                FromEnvironmentToControl(ambient_brightness=as_lumens)
            )

            await sleep(1)

    else:
        import board
        import busio
        import adafruit_tsl2591

        i2c = busio.I2C(board.SCL, board.SDA)

        light_sensor = adafruit_tsl2591.TSL2591(i2c)

        while True:
            lux = light_sensor.lux

            LOGGER.info("lux: %f", lux)

            # This is just an approximation
            as_lumens = lux * (600 / 20000)

            await to_control.send(
                FromEnvironmentToControl(ambient_brightness=as_lumens)
            )

            await sleep(1)

    LOGGER.debug("shutdown")
