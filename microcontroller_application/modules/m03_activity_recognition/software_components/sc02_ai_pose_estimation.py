"""
Module: 03. Activity recognition
Component: 02. AI pose estimation
"""

import bounded_channel

from microcontroller_application.interfaces.message_types import (
    Activity,
    FromActivityRecognitionToControl,
    FromHumanDetectionToActivityRecognition,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_human_detection: bounded_channel.Receiver[
        FromHumanDetectionToActivityRecognition
    ],
    to_control: bounded_channel.Sender[FromActivityRecognitionToControl],
):
    "Run the AI pose estimation software component"

    LOGGER.debug("startup")

    async for message in from_human_detection:
        humans = message.images_of_humans

        activities_of_humans = [Activity.NEITHER for _human in humans]

        await to_control.send(
            FromActivityRecognitionToControl(activities_of_humans=activities_of_humans)
        )

    LOGGER.debug("shutdown")
