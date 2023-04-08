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
from msgpack import dumps, loads
from PIL.Image import Image
from websockets.client import WebSocketClientProtocol
from websockets.legacy.client import Connect

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
    UserSlot,
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

    (
        converted_microcontroller_messages_sender,
        converted_microcontroller_messages_receiver,
    ) = bounded_channel.channel(32)

    convert_from_aggregation_camera_frame_task = convert_from_aggregation_camera_frame(
        from_aggregation_camera_frame, converted_microcontroller_messages_sender
    )

    convert_from_aggregation_duty_cycle_task = convert_from_aggregation_duty_cycle(
        from_aggregation_duty_cycle,
        converted_microcontroller_messages_sender,
    )

    convert_from_person_identification_task = convert_from_person_identification(
        from_person_identification,
        converted_microcontroller_messages_sender,
    )

    convert_from_preferences_task = convert_from_preferences(
        from_preferences,
        converted_microcontroller_messages_sender,
    )

    (
        converted_proxy_messages_sender,
        converted_proxy_messages_receiver,
    ) = bounded_channel.channel(32)

    convert_from_proxy_task = convert_from_proxy(
        converted_proxy_messages_receiver=converted_proxy_messages_receiver,
        to_aggregation_camera_feed_interest=to_aggregation_camera_feed_interest,
        to_aggregation_record_the_camera=to_aggregation_record_the_camera,
        to_aggregation_request_duty_cycle=to_aggregation_request_duty_cycle,
        to_person_identification=to_person_identification,
        to_preferences=to_preferences,
        bad_form_to_proxy=converted_microcontroller_messages_sender,
    )

    manage_connection_task = manage_connection(
        proxy_endpoint=proxy_endpoint,
        microcontroller_id=microcontroller_id,
        from_microcontroller=converted_microcontroller_messages_receiver,
        to_microcontroller=converted_proxy_messages_sender,
    )

    await gather(
        convert_from_aggregation_camera_frame_task,
        convert_from_aggregation_duty_cycle_task,
        convert_from_person_identification_task,
        convert_from_preferences_task,
        convert_from_proxy_task,
        manage_connection_task,
    )

    LOGGER.debug("shutdown")


async def manage_connection(
    *,
    proxy_endpoint: str,
    microcontroller_id: str,
    from_microcontroller: bounded_channel.Receiver[FromMicrocontrollerToProxy],
    to_microcontroller: bounded_channel.Sender[FromProxyToMicrocontroller],
):
    LOGGER.debug("start of managing connection")

    connection = Connect(proxy_endpoint)

    async with connection as client_protocol:
        await do_registration_sequence(
            client_protocol=client_protocol, microcontroller_id=microcontroller_id
        )

        await gather(
            producer(
                client_protocol=client_protocol,
                from_microcontroller=from_microcontroller,
            ),
            consumer(
                client_protocol=client_protocol,
                to_microcontroller=to_microcontroller,
            ),
        )

    LOGGER.debug("end of managing connection")


async def do_registration_sequence(
    *,
    client_protocol: WebSocketClientProtocol,
    microcontroller_id: str,
):
    registration_message = {
        "Register": {
            "microcontroller_id": microcontroller_id,
        }
    }

    encoded_registration_message = dumps(registration_message)
    if encoded_registration_message is None:
        raise RuntimeError(f"{registration_message} encoded as None somehow?!")

    LOGGER.info("registering as %s", microcontroller_id)
    await client_protocol.send(encoded_registration_message)

    encoded_message_back = await client_protocol.recv()
    message_back = loads(encoded_message_back)

    if message_back != "UsersAreOffline":
        raise RuntimeError(
            f"could not register with the proxy; got {message_back} instead"
        )

    LOGGER.info("registered as %s", microcontroller_id)


async def producer(
    *,
    client_protocol: WebSocketClientProtocol,
    from_microcontroller: bounded_channel.Receiver[FromMicrocontrollerToProxy],
):
    LOGGER.debug("startup")

    async for message in from_microcontroller:
        LOGGER.debug("will send %r", message)
        encoded_message = dumps(message)
        LOGGER.debug("which encodes into %r", encoded_message)

        if encoded_message is None:
            raise RuntimeError(f"{message} encoded as None somehow?!")

        await client_protocol.send(encoded_message)

    LOGGER.debug("shutdown")


async def consumer(
    *,
    client_protocol: WebSocketClientProtocol,
    to_microcontroller: bounded_channel.Sender[FromProxyToMicrocontroller],
):
    LOGGER.debug("startup")
    async for encoded_message in client_protocol:
        LOGGER.debug("received %r from the connection", encoded_message)

        message = loads(encoded_message)

        LOGGER.debug("which decodes into %r", message)

        (await to_microcontroller.send(message)).expect("no receiver")

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
    converted_microcontroller_messages_sender: bounded_channel.Sender[
        FromMicrocontrollerToProxy
    ],
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

        (
            await converted_microcontroller_messages_sender.send(converted_message)
        ).expect("no receiver")


async def convert_from_aggregation_duty_cycle(
    from_aggregation_duty_cycle: bounded_channel.Receiver[
        FromAggregationToProxyDutyCycle
    ],
    converted_microcontroller_messages_sender: bounded_channel.Sender[
        FromMicrocontrollerToProxy
    ],
):
    async for message in from_aggregation_duty_cycle:
        converted_message = {
            "BroadcastData": {
                "DutyCycle": {"duty_cycle": message.duty_cycle},
            },
        }

        (
            await converted_microcontroller_messages_sender.send(converted_message)
        ).expect("no receiver")


async def convert_from_person_identification(
    from_person_identification: bounded_channel.Receiver[
        FromPersonIdentificationToProxy
    ],
    converted_microcontroller_messages_sender: bounded_channel.Sender[
        FromMicrocontrollerToProxy
    ],
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

        (
            await converted_microcontroller_messages_sender.send(converted_message)
        ).expect("no receiver")


async def convert_from_preferences(
    from_preferences: bounded_channel.Receiver[FromPreferencesToProxy],
    converted_microcontroller_messages_sender: bounded_channel.Sender[
        FromMicrocontrollerToProxy
    ],
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

        (
            await converted_microcontroller_messages_sender.send(converted_message)
        ).expect("no receiver")


async def convert_from_proxy(
    converted_proxy_messages_receiver: bounded_channel.Receiver[
        FromProxyToMicrocontroller
    ],
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
    bad_form_to_proxy: bounded_channel.Sender[FromMicrocontrollerToProxy],
):
    async for message in converted_proxy_messages_receiver:
        LOGGER.debug("got %r", message)

        if message == "UsageError":
            raise RuntimeError("usage error when communicating with the proxy")

        if isinstance(message, dict):

            # This should've been its own software component, or something, but oh well, it's too late
            if "LoginRequest" in message:
                [login_info, user_id] = message["LoginRequest"]

                [username, password] = login_info

                # username = login_info["username"]
                # password = login_info["password"]

                if username == "jacob" and password == "password":
                    LOGGER.info(
                        "%s just signed in as %s with %s", user_id, username, password
                    )

                    response = {"LoginResponse": [True, user_id]}
                else:
                    LOGGER.info(
                        "%s failed to sign in as %s with %s",
                        user_id,
                        username,
                        password,
                    )

                    response = {"LoginResponse": [False, user_id]}

                (await bad_form_to_proxy.send(response)).expect("no receiver")

            if "Command" in message:
                [command, user_id] = message["Command"]

                LOGGER.error("TODO: switch / if / elif on the message contents")

                if "AddNewTrustedUser" in command:
                    add_new_trusted_user = command["AddNewTrustedUser"]
                    [user_slot] = add_new_trusted_user

                    user_slot_as_enum = UserSlot(user_slot)

                    converted_message = FromProxyToPersonIdentification(
                        user_slot=user_slot_as_enum
                    )

                    await to_person_identification.send(converted_message)

                if "CameraFeedInterest" in command:
                    camera_feed_interest = command["CameraFeedInterest"]
                    [wants_camera_feed] = camera_feed_interest

                    converted_message = FromProxyToAggregationCameraFeedInterest(
                        wants_camera_feed=wants_camera_feed,
                        user_id=user_id,
                    )

                    await to_aggregation_camera_feed_interest.send(converted_message)

        else:
            LOGGER.error("received %r but am not programmed to handle it", message)

        # (
        #     await to_aggregation_camera_feed_interest.send(converted_message_dataclass)
        # ).expect("no receiver")
