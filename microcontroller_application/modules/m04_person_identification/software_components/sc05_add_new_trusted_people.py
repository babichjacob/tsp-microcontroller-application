"""
Module: 05. Preferences
Component: 05. Add new trusted people
"""

from asyncio import to_thread
import csv
from pathlib import Path

import bounded_channel
import face_recognition

from microcontroller_application.interfaces.message_types import (
    FromHumanDetectionToPersonIdentification,
    FromPreferencesToControl,
    FromPreferencesToProxy,
    FromProxyToPersonIdentification,
    FromProxyToPreferences,
    UserSlot,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_human_detection: bounded_channel.Receiver[
        FromHumanDetectionToPersonIdentification
    ],
    from_proxy_add_new_user: bounded_channel.Receiver[FromProxyToPersonIdentification],
    trusted_users_folder: Path,
    user_face_encodings: dict[UserSlot, list[list[float]]],
):
    "Run the add new trusted people software component"

    LOGGER.debug("startup")

    async for message in from_proxy_add_new_user:
        user_slot = message.user_slot

        LOGGER.info(
            "going to add the %r trusted user from current camera info", user_slot
        )

        limit = 30

        for attempt in range(limit):
            LOGGER.debug("on attempt %d", attempt)

            current_humans = (await from_human_detection.recv()).unwrap()
            images_of_humans = current_humans.images_of_humans

            number_of_humans = len(images_of_humans)
            if number_of_humans != 1:
                LOGGER.warning("%d humans were in frame though", number_of_humans)
                continue

            # It’s a list, but we know it has one entry (one human),
            # so get the one and only element
            image_of_person = images_of_humans[0]

            LOGGER.debug("now looking for faces")
            face_encodings = await to_thread(
                face_recognition.face_encodings, image_of_person
            )

            number_of_faces = len(face_encodings)
            if number_of_faces != 1:
                LOGGER.warning("%d faces were in frame though", number_of_faces)
                continue

            # It’s a list, but we know it has one entry (one face),
            # so get the one and only element
            face_encoding = face_encodings[0]

            face_encoding_as_list: list[float] = list(face_encoding)

            # Open in append mode
            with open(
                trusted_users_folder / str(user_slot) / "face.csv", "a", encoding="utf8"
            ) as face_file:
                writer = csv.writer(face_file)

                writer.writerow(face_encoding_as_list)

            user_face_encodings[user_slot].append(face_encoding_as_list)

            LOGGER.info(
                "saved %r as a face encoding for the %d trusted user",
                face_encoding_as_list,
                user_slot,
            )

            break
        else:
            LOGGER.error("failed to ever find a human")

    LOGGER.debug("shutdown")
