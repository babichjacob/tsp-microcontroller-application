"""
Module: 04. Person identification
Component: 03. Face recognition
"""

import csv
from asyncio import gather, to_thread
from pathlib import Path

import bounded_channel
import face_recognition
import numpy as np
from option_and_result import NONE, Option, Some
from store import Writable

from microcontroller_application.interfaces.message_types import (
    FromHumanDetectionToPersonIdentification,
    FromPersonIdentificationToControl,
    UserSlot,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_human_detection: bounded_channel.Receiver[
        FromHumanDetectionToPersonIdentification
    ],
    to_control: bounded_channel.Sender[FromPersonIdentificationToControl],
    identified_people_store: Writable[list[Option[UserSlot]], None],
    trusted_users_folder: Path,
    user_face_encodings: dict[UserSlot, list[list[float]]],
    use_demo_data: bool,
):
    "Run the face recognition component"

    LOGGER.debug("startup")

    for user_slot in UserSlot:
        # Open in read mode
        try:
            with open(
                trusted_users_folder / str(user_slot.value) / "face.csv",
                "r",
                encoding="utf8",
            ) as face_file:
                reader = csv.reader(face_file)

                all_their_encodings = []
                for line in reader:
                    all_their_encodings.append(line)

                user_face_encodings[user_slot] = all_their_encodings
        except FileNotFoundError:
            LOGGER.info(
                "not restoring %s's face encodings because none are saved", user_slot
            )

    async for message in from_human_detection:
        LOGGER.debug("received %r", message)

        if use_demo_data:
            number_of_humans = len(message.images_of_humans)

            if number_of_humans == 0:
                people = []
            elif number_of_humans == 1:
                people = [Some(UserSlot.TWO)]
            elif number_of_humans == 2:
                people = [Some(UserSlot.TWO), NONE()]
            else:
                people = [NONE() for _ in range(number_of_humans)]
        else:
            people = await gather(
                *[
                    find_matching_face(image, user_face_encodings)
                    for image in message.images_of_humans
                ]
            )

        LOGGER.debug("figured out %r", people)

        identified_people_store.set(people)

        await to_control.send(
            FromPersonIdentificationToControl(identified_people=people)
        )

    LOGGER.debug("shutdown")


async def find_matching_face(
    image_of_person: np.ndarray,
    user_face_encodings: dict[UserSlot, list[list[float]]] = {},
) -> Option[UserSlot]:
    this_image_face_encodings = await to_thread(
        face_recognition.face_encodings, image_of_person
    )

    for this_image_face_encoding in this_image_face_encodings:
        for (
            trusted_user,
            that_trusted_user_s_face_encodings,
        ) in user_face_encodings.items():
            matches = await to_thread(
                face_recognition.compare_faces,
                that_trusted_user_s_face_encodings,
                this_image_face_encoding,
            )

            LOGGER.debug("%r for %r", matches, trusted_user)

            if any(matches):
                return Some(trusted_user)

    return NONE()
