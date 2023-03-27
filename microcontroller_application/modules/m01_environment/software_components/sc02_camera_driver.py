"""
Module: 01. Environment
Component: 02. Camera driver

Every frame, we can capture a frame to memory as a numpy array.
This format is chosen because it's right for a neural network to work on,
and it'll be easy for the aggregation module to convert it to a PIL Image
when it's recording the feed.
"""

import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToAggregation,
    FromEnvironmentToHumanDetectionCameraFrame,
)
from microcontroller_application.log import get_logger

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

    # TODO
    LOGGER.error("this hasn't been programmed yet, so it doesn't do anything")

    LOGGER.debug("shutdown")
