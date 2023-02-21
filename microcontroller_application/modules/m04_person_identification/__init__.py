"""
Module: 04. Person identification

This module is concerned with figuring out which trusted
user(s), if any, the human(s) in the room are.
"""

from asyncio import gather
import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromHumanDetectionToPersonIdentification,
    FromPersonIdentificationToAggregation,
    FromPersonIdentificationToControl,
    FromPersonIdentificationToProxy,
    FromProxyToPersonIdentification,
)
from microcontroller_application.log import get_logger


from .software_components import (
    sc03_face_recognition,
    sc04_intruder_alert,
    sc05_add_new_trusted_people,
)

LOGGER = get_logger(__name__)


async def run(
    *,
    from_human_detection: bounded_channel.Receiver[
        FromHumanDetectionToPersonIdentification
    ],
    from_proxy: bounded_channel.Receiver[FromProxyToPersonIdentification],
    to_aggregation: bounded_channel.Sender[FromPersonIdentificationToAggregation],
    to_proxy: bounded_channel.Sender[FromPersonIdentificationToProxy],
    to_control: bounded_channel.Sender[FromPersonIdentificationToControl],
):
    "Run the person identification module"

    LOGGER.debug("startup")

    sc03_face_recognition_task = sc03_face_recognition.run(
        from_human_detection=from_human_detection, to_control=to_control
    )

    await gather(
        sc03_face_recognition_task,
    )

    LOGGER.debug("shutdown")
