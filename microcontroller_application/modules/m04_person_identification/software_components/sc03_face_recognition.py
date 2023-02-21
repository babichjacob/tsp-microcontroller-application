import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromHumanDetectionToPersonIdentification,
    FromPersonIdentificationToControl,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_human_detection: bounded_channel.Receiver[
        FromHumanDetectionToPersonIdentification
    ],
    to_control: bounded_channel.Sender[FromPersonIdentificationToControl],
):
    async for message in from_human_detection:
        for image in message.images_of_humans:
            LOGGER.warn(
                f"got {image=} but doing something with it is not implemented yet"
            )

    ...
