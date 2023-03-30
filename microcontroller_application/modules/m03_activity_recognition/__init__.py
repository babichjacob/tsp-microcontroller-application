"""
Module: 03. Activity recognition

This module is concerned with categorizing
what each human in the room is doing.
"""

from asyncio import gather
import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromActivityRecognitionToControl,
    FromHumanDetectionToActivityRecognition,
)
from microcontroller_application.log import get_logger

from .software_components import sc02_ai_pose_estimation

LOGGER = get_logger(__name__)


async def run(
    *,
    from_human_detection: bounded_channel.Receiver[
        FromHumanDetectionToActivityRecognition
    ],
    to_control: bounded_channel.Sender[FromActivityRecognitionToControl],
):
    "Run the activity recognition module"

    LOGGER.debug("startup")

    sc02_ai_pose_estimation_task = sc02_ai_pose_estimation.run(
        from_human_detection=from_human_detection,
        to_control=to_control,
    )

    await gather(sc02_ai_pose_estimation_task)

    LOGGER.debug("shutdown")
