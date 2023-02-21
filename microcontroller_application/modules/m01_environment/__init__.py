"""
This module is concerned with collecting data
(ambient light, motion, video feed, and occupancy)
from the room.
"""


from bounded_channel import Sender

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToAggregation,
    FromEnvironmentToControl,
    FromEnvironmentToHumanDetectionCameraFrame,
    FromEnvironmentToHumanDetectionMotion,
    FromEnvironmentToHumanDetectionOccupancy,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    to_human_detection_motion: Sender[FromEnvironmentToHumanDetectionMotion],
    to_human_detection_occupancy: Sender[FromEnvironmentToHumanDetectionOccupancy],
    to_human_detection_camera_frame: Sender[FromEnvironmentToHumanDetectionCameraFrame],
    to_control: Sender[FromEnvironmentToControl],
    to_aggregation: Sender[FromEnvironmentToAggregation],
):
    "Run the environment module"

    LOGGER.debug("startup")
    LOGGER.debug("shutdown")
