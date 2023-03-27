"""
Module: 05. Preferences
Component: 05. Add new trusted people
"""

from pathlib import Path
import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromPreferencesToControl,
    FromPreferencesToProxy,
    FromProxyToPersonIdentification,
    FromProxyToPreferences,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_proxy_add_new_user: bounded_channel.Receiver[FromProxyToPersonIdentification],
    trusted_users_folder: Path,
):
    "Run the add new trusted people software component"

    LOGGER.debug("startup")

    async for message in from_proxy_add_new_user:
        user_slot = message.user_slot

        current_camera_frame = await from_environment.recv()
        # Provided by the face-recognition library in real code
        face_encodings = get_face_encodings(current_camera_frame)

        if len(face_encodings) != 1:
            continue

        # It’s a list, but we know it has one entry (one face),
        # so get the one and only element
        face_encoding = face_encodings[0]

        # TRUSTED_USERS is a constant that is a directory to store the data like
        # /home/pi/trusted_users

        # Open in append mode
        with open(
            trusted_users_folder / str(user_slot) / "face.csv", "a", encoding="utf8"
        ) as face_file:
            csv_write_row(face_file, face_encoding)

        user_face_encodings[user_slot].append(face_encoding)

    LOGGER.debug("shutdown")
