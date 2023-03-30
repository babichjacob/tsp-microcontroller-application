"""
Module: 01. Environment
Component: 02. Camera driver

Every frame, we can capture a frame to memory as a numpy array.
This format is chosen because it's right for a neural network to work on,
and it'll be easy for the aggregation module to convert it to a PIL Image
when it's recording the feed.
"""

from asyncio import sleep

import bounded_channel
import numpy as np

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToAggregation,
    FromEnvironmentToHumanDetectionCameraFrame,
)
from microcontroller_application.log import get_logger
from utils.asynchronous import at_least_one

LOGGER = get_logger(__name__)


async def run(
    *,
    to_human_detection: bounded_channel.Sender[
        FromEnvironmentToHumanDetectionCameraFrame
    ],
    to_aggregation: bounded_channel.Sender[FromEnvironmentToAggregation],
    use_randomized_data: bool,
):
    LOGGER.debug("startup")

    if use_randomized_data:
        LOGGER.warning("using randomized data")
        LOGGER.error("this hasn't been programmed yet, so it doesn't do anything")

    else:
        from picamera import PiCamera

        camera = PiCamera()

        width = 768
        height = 576

        camera.resolution = (width, height)
        camera.framerate = 24

        while True:
            frame = np.empty((height, width, 3), dtype=np.uint8)
            camera.capture(frame, "rgb")

            LOGGER.info("captured camera frame %r", frame)

            await at_least_one(
                [
                    to_human_detection.send(
                        FromEnvironmentToHumanDetectionCameraFrame(frame=frame)
                    ),
                    to_aggregation.send(FromEnvironmentToAggregation(frame=frame)),
                ]
            )

            await sleep(1 / 30)

    LOGGER.debug("shutdown")
