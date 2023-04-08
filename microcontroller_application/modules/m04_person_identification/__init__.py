"""
Module: 04. Person identification

This module is concerned with figuring out which trusted
user(s), if any, the human(s) in the room are.
"""

from asyncio import gather
from datetime import datetime
from pathlib import Path
from typing import Callable

import bounded_channel
from store import writable

from microcontroller_application.interfaces.message_types import (
    FromHumanDetectionToPersonIdentification,
    FromPersonIdentificationToAggregation,
    FromPersonIdentificationToControl,
    FromPersonIdentificationToProxy,
    FromProxyToPersonIdentification,
    UserSlot,
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
    trusted_users_folder: Path,
    get_current_time: Callable[[], datetime],
):
    "Run the person identification module"

    LOGGER.debug("startup")

    user_face_encodings: dict[UserSlot, list[list[float]]] = {}
    identified_people_store = writable([])

    sc03_face_recognition_task = sc03_face_recognition.run(
        from_human_detection=from_human_detection,
        to_control=to_control,
        trusted_users_folder=trusted_users_folder,
        user_face_encodings=user_face_encodings,
        identified_people_store=identified_people_store,
    )

    sc04_intruder_alert_task = sc04_intruder_alert.run(
        to_proxy=to_proxy,
        to_aggregation=to_aggregation,
        identified_people_store=identified_people_store,
        get_current_time=get_current_time,
    )

    # Bug hazard: Receives on from_human_detection which might cause the face recognition component to miss a message
    sc05_add_new_trusted_people_task = sc05_add_new_trusted_people.run(
        from_human_detection=from_human_detection,
        from_proxy_add_new_user=from_proxy,
        trusted_users_folder=trusted_users_folder,
        user_face_encodings=user_face_encodings,
    )

    await gather(
        sc03_face_recognition_task,
        sc04_intruder_alert_task,
        sc05_add_new_trusted_people_task,
    )

    LOGGER.debug("shutdown")
