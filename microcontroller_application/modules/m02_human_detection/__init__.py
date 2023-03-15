"""
Module: 02. Human detection

This module is concerned with determining how many humans
are present in the room and where they are.
"""

from asyncio import gather

from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToHumanDetectionCameraFrame,
    FromEnvironmentToHumanDetectionMotion,
    FromEnvironmentToHumanDetectionOccupancy,
    FromHumanDetectionToActivityRecognition,
    FromHumanDetectionToPersonIdentification,
)
from microcontroller_application.log import get_logger

from .software_components import sc02_ai_human_detection

LOGGER = get_logger(__name__)


async def run(
    *,
    from_environment_motion: Receiver[FromEnvironmentToHumanDetectionMotion],
    from_environment_occupancy: Receiver[FromEnvironmentToHumanDetectionOccupancy],
    from_environment_camera_frame: Receiver[FromEnvironmentToHumanDetectionCameraFrame],
    to_activity_recognition: Sender[FromHumanDetectionToActivityRecognition],
    to_person_identification: Sender[FromHumanDetectionToPersonIdentification],
):
    "Run the human detection module"

    LOGGER.debug("startup")

    sc02_ai_human_detection_task = sc02_ai_human_detection.run(
        from_environment_motion=from_environment_motion,
        from_environment_occupancy=from_environment_occupancy,
        from_environment_camera_frame=from_environment_camera_frame,
        to_activity_recognition=to_activity_recognition,
        to_person_identification=to_person_identification,
    )

    await gather(sc02_ai_human_detection_task)

    LOGGER.debug("shutdown")
