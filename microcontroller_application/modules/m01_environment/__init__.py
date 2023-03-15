"""
Module: 01. Environment

This module is concerned with collecting data
(ambient light, motion, video feed, and occupancy)
from the room.
"""


from asyncio import gather

import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToAggregation,
    FromEnvironmentToControl,
    FromEnvironmentToHumanDetectionCameraFrame,
    FromEnvironmentToHumanDetectionMotion,
    FromEnvironmentToHumanDetectionOccupancy,
)
from microcontroller_application.log import get_logger

from .software_components import (
    sc02_camera_driver,
    sc04_light_sensor_driver,
    sc06_motion_sensor_driver,
    sc08_occupancy_sensor_driver,
)

LOGGER = get_logger(__name__)


async def run(
    *,
    to_human_detection_motion: bounded_channel.Sender[
        FromEnvironmentToHumanDetectionMotion
    ],
    to_human_detection_occupancy: bounded_channel.Sender[
        FromEnvironmentToHumanDetectionOccupancy
    ],
    to_human_detection_camera_frame: bounded_channel.Sender[
        FromEnvironmentToHumanDetectionCameraFrame
    ],
    to_control: bounded_channel.Sender[FromEnvironmentToControl],
    to_aggregation: bounded_channel.Sender[FromEnvironmentToAggregation],
):
    "Run the environment module"

    LOGGER.debug("startup")

    sc02_camera_driver_task = sc02_camera_driver.run(
        to_human_detection=to_human_detection_camera_frame,
        to_aggregation=to_aggregation,
    )

    sc04_light_sensor_driver_task = sc04_light_sensor_driver.run(
        to_control=to_control,
    )

    sc06_motion_sensor_driver_task = sc06_motion_sensor_driver.run(
        to_human_detection=to_human_detection_motion,
    )

    sc08_occupancy_sensor_driver_task = sc08_occupancy_sensor_driver.run(
        to_human_detection=to_human_detection_occupancy,
    )

    await gather(
        sc02_camera_driver_task,
        sc04_light_sensor_driver_task,
        sc06_motion_sensor_driver_task,
        sc08_occupancy_sensor_driver_task,
    )

    LOGGER.debug("shutdown")
