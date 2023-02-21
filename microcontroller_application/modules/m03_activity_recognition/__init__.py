"""
This module is concerned with categorizing
what each human in the room is doing.
"""

from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromActivityRecognitionToControl,
    FromHumanDetectionToActivityRecognition,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_human_detection: Receiver[FromHumanDetectionToActivityRecognition],
    to_control: Sender[FromActivityRecognitionToControl],
):
    "Run the activity recognition module"

    LOGGER.debug("startup")
    LOGGER.debug("shutdown")
