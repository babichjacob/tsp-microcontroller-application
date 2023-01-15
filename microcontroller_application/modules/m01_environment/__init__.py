"""
This module is concerned with collecting data
(ambient light, motion, video feed, and occupancy)
from the room.
"""


from bounded_channel import Sender

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToAggregation,
    FromEnvironmentToControl,
    FromEnvironmentToHumanDetection,
)


async def run(
    *,
    to_human_detection: Sender[FromEnvironmentToHumanDetection],
    to_control: Sender[FromEnvironmentToControl],
    to_aggregation: Sender[FromEnvironmentToAggregation],
):
    print("hello from the environment module")
