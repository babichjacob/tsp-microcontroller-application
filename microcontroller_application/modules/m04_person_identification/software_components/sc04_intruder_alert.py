"""
Module: 04. Person identification
Component: 04. Intruder alert
"""


from asyncio import get_event_loop
from datetime import datetime, timedelta
from typing import Callable
import bounded_channel
from option_and_result import NONE, Option
from store import Readable

from microcontroller_application.interfaces.message_types import (
    FromPersonIdentificationToAggregation,
    FromPersonIdentificationToProxy,
    UserSlot,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    to_proxy: bounded_channel.Sender[FromPersonIdentificationToProxy],
    to_aggregation: bounded_channel.Sender[FromPersonIdentificationToAggregation],
    identified_people_store: Readable[list[Option[UserSlot]]],
    get_current_time: Callable[[], datetime],
):
    "Run the intruder alert component"

    LOGGER.debug("startup")

    countdown = NONE()

    async def send_to_proxy_and_aggregation(data):
        camera_image, timestamp = data

        # Will result in a notification
        await to_proxy.send(
            FromPersonIdentificationToProxy(image=camera_image, timestamp=timestamp)
        )

        # Will be logged to the history
        await to_aggregation.send(
            FromPersonIdentificationToAggregation(
                image=camera_image, timestamp=timestamp
            )
        )

    def intruder_alert(data):
        countdown.cancel()
        # If this isn’t called again for 1 minute,
        # then the notification will be sent

        loop = get_event_loop()
        countdown = loop.call_later(
            timedelta(minutes=1).total_seconds(),
            send_to_proxy_and_aggregation,  # function
            (data,),  # arguments to the function
        )

    async for identified_people in values(identified_people_store):
        if any(identification.is_some() for identification in identified_people):
            # If an intruder alert was pending, cancel it, because a trusted person is in frame
            # (explained in the next code sample)
            countdown.cancel()

        # There’s an intruder if there’s a None variant in the list returned
        # But if there’s a recognized person in frame, then they are already
        # aware of the untrusted person in frame
        # (maybe they’re a friend the system wasn’t trained to recognize)
        # then there’s no reason to alert them
        elif any(identification.is_none() for identification in identified_people):
            # Recall this function is debounced to prevent repeat notifications
            intruder_alert((camera_image, timestamp))

    LOGGER.debug("shutdown")
