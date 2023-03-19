"""
Module: 09x. Proxy connector

The real proxy module runs on a cloud server.

The point of this module is to pretend to be the proxy module
for the other tasks running on this microcontroller.

When it receives messages from other modules, it sends them
to the real proxy server.

When it receives messages from the real proxy server, it
sends them to the appropriate module
"""

from asyncio import gather
from io import BytesIO

import bounded_channel
from PIL.Image import Image

from microcontroller_application.interfaces.message_types import (
    FromAggregationToProxyCameraFrame,
    FromAggregationToProxyDutyCycle,
    FromPersonIdentificationToProxy,
    FromPreferencesToProxy,
    FromProxyToAggregationCameraFeedInterest,
    FromProxyToAggregationRecordTheCamera,
    FromProxyToAggregationRequestDutyCycle,
    FromProxyToPersonIdentification,
    FromProxyToPreferences,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


# Sadly, the plan of compiling the messages crate
# for use in Python has fallen through
FromMicrocontrollerToProxy = dict
FromProxyToMicrocontroller = dict
# These uncool types will have to suffice


async def run(
    *,
    from_aggregation_camera_frame: bounded_channel.Receiver[
        FromAggregationToProxyCameraFrame
    ],
    from_aggregation_duty_cycle: bounded_channel.Receiver[
        FromAggregationToProxyDutyCycle
    ],
    from_person_identification: bounded_channel.Receiver[
        FromPersonIdentificationToProxy
    ],
    from_preferences: bounded_channel.Receiver[FromPreferencesToProxy],
    to_aggregation_camera_feed_interest: bounded_channel.Sender[
        FromProxyToAggregationCameraFeedInterest
    ],
    to_aggregation_record_the_camera: bounded_channel.Sender[
        FromProxyToAggregationRecordTheCamera
    ],
    to_aggregation_request_duty_cycle: bounded_channel.Sender[
        FromProxyToAggregationRequestDutyCycle
    ],
    to_person_identification: bounded_channel.Sender[FromProxyToPersonIdentification],
    to_preferences: bounded_channel.Sender[FromProxyToPreferences],
    microcontroller_id: str,
    proxy_endpoint: str,
):
    "Run the proxy connector module"

    LOGGER.debug("startup")

    # TODO
    LOGGER.error("this hasn't been programmed yet")

    # TODO: create a task for each from_ channel
    # that converts the messages in the channel into a dict (JSON/msgpack-compatible)
    # then pushes them to a centralized channel

    # TODO: create a task that reads from the centralized channel
    # and serializes to msgpack (bytes)
    # and sends to the websocket

    # TODO: create a task that reads from the websocket
    # and deserializes the message to msgpack (dict)

    (
        converted_messages_sender,
        converted_messages_receiver,
    ) = bounded_channel.channel(32)

    convert_from_aggregation_camera_frame_task = convert_from_aggregation_camera_frame(
        from_aggregation_camera_frame, converted_messages_sender
    )
    convert_from_aggregation_duty_cycle_task = convert_from_aggregation_duty_cycle(
        from_aggregation_duty_cycle,
        converted_messages_sender,
    )

    convert_from_person_identification_task = convert_from_person_identification(
        from_person_identification,
        converted_messages_sender,
    )

    await gather(
        convert_from_aggregation_camera_frame_task,
        convert_from_aggregation_duty_cycle_task,
        convert_from_person_identification_task,
    )

    LOGGER.debug("shutdown")


def image_to_bytes(image: Image) -> bytes:
    image_bytes_io = BytesIO()
    image.save(image_bytes_io, format="JPG", quality=50)
    image_bytes = image_bytes_io.getvalue()

    return image_bytes


async def convert_from_aggregation_camera_frame(
    from_aggregation_camera_frame: bounded_channel.Receiver[
        FromAggregationToProxyCameraFrame
    ],
    converted_messages_sender: bounded_channel.Sender[FromMicrocontrollerToProxy],
):

    async for message in from_aggregation_camera_frame:
        converted_message = {
            "UserSpecificData": [
                {
                    "CameraFrame": {"image": image_to_bytes(message.frame)},
                },
                message.user_ids,
            ],
        }

        (await converted_messages_sender.send(converted_message)).expect("no receiver")


async def convert_from_aggregation_duty_cycle(
    from_aggregation_duty_cycle: bounded_channel.Receiver[
        FromAggregationToProxyDutyCycle
    ],
    converted_messages_sender: bounded_channel.Sender[FromMicrocontrollerToProxy],
):
    async for message in from_aggregation_duty_cycle:
        converted_message = {
            "BroadcastData": {
                "DutyCycle": {"duty_cycle": message.duty_cycle},
            },
        }

        (await converted_messages_sender.send(converted_message)).expect("no receiver")


async def convert_from_person_identification(
    from_person_identification: bounded_channel.Receiver[
        FromPersonIdentificationToProxy
    ],
    converted_messages_sender: bounded_channel.Sender[FromMicrocontrollerToProxy],
):
    async for message in from_person_identification:
        converted_message = {
            "BroadcastData": {
                "IntruderAlert": {
                    "image": image_to_bytes(message.image),
                    "timestamp": message.timestamp.isoformat(),
                },
            },
        }

        (await converted_messages_sender.send(converted_message)).expect("no receiver")


async def convert_from_preferences(
    from_preferences: bounded_channel.Receiver[FromPreferencesToProxy],
    converted_messages_sender: bounded_channel.Sender[FromMicrocontrollerToProxy],
):
    async for message in from_preferences:
        converted_timers = [
            {
                "effect": timer.effect,
                "weekday": timer.weekday,
                "hour": timer.hour,
                "minute": timer.minute,
            }
            for timer in message.preferences.timers
        ]

        converted_message = {
            "UserSpecificData": [
                {
                    "Preferences": {
                        "name": message.preferences.name,
                        "timers": converted_timers,
                    },
                },
                [message.user_id],
            ],
        }

        (await converted_messages_sender.send(converted_message)).expect("no receiver")
