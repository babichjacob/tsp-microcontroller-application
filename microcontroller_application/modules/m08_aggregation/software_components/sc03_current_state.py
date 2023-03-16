"""
Module: 08. Aggregation
Component: 03. Current state

The control module gives an output light amount
(a decimal duty cycle) as it changes.

Whenever a user browsing the site
(as learned by a message from the proxy module)
wants to see the current duty cycle, it is given.


It's a similar story with the camera feed from the environment module.

When requested (from the proxy module
(because of a user request while browsing the frontend website)
), it is given.
"""


from asyncio import Event, gather

import bounded_channel
from option_and_result import NONE, Option, Some
from PIL import Image

from microcontroller_application.interfaces.message_types import (
    FromAggregationToProxyCameraFrame,
    FromAggregationToProxyDutyCycle,
    FromControlToAggregationDutyCycle,
    FromEnvironmentToAggregation,
    FromProxyToAggregationCameraFeedInterest,
    FromProxyToAggregationRequestDutyCycle,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_environment: bounded_channel.Receiver[FromEnvironmentToAggregation],
    from_control_duty_cycle: bounded_channel.Receiver[
        FromControlToAggregationDutyCycle
    ],
    from_proxy_camera_feed_interest: bounded_channel.Receiver[
        FromProxyToAggregationCameraFeedInterest
    ],
    from_proxy_request_duty_cycle: bounded_channel.Receiver[
        FromProxyToAggregationRequestDutyCycle
    ],
    to_proxy_camera_frame: bounded_channel.Sender[FromAggregationToProxyCameraFrame],
    to_proxy_duty_cycle: bounded_channel.Sender[FromAggregationToProxyDutyCycle],
):
    "Run the current state software component"

    LOGGER.debug("startup")

    await gather(
        run_current_state_for_duty_cycle(
            from_control_duty_cycle=from_control_duty_cycle,
            from_proxy_request_duty_cycle=from_proxy_request_duty_cycle,
            to_proxy_duty_cycle=to_proxy_duty_cycle,
        ),
        run_current_state_for_camera_feed(
            from_environment=from_environment,
            from_proxy_camera_feed_interest=from_proxy_camera_feed_interest,
            to_proxy_camera_frame=to_proxy_camera_frame,
        ),
    )

    LOGGER.debug("shutdown")


async def run_current_state_for_duty_cycle(
    from_control_duty_cycle: bounded_channel.Receiver[
        FromControlToAggregationDutyCycle
    ],
    from_proxy_request_duty_cycle: bounded_channel.Receiver[
        FromProxyToAggregationRequestDutyCycle
    ],
    to_proxy_duty_cycle: bounded_channel.Sender[FromAggregationToProxyDutyCycle],
):
    current_duty_cycle_option: Option[float] = NONE()

    async def update_duty_cycle():
        nonlocal current_duty_cycle_option

        async for message in from_control_duty_cycle:
            current_duty_cycle_option = Some(message.duty_cycle)

    async def forward_duty_cycle():
        async for message in from_proxy_request_duty_cycle:
            if current_duty_cycle_option.is_some():
                message = FromAggregationToProxyDutyCycle(
                    # TODO: needing to unwrap feels weird
                    current_duty_cycle_option.unwrap()
                )

                await to_proxy_duty_cycle.send(message)

    await gather(update_duty_cycle(), forward_duty_cycle())


async def run_current_state_for_camera_feed(
    *,
    from_environment: bounded_channel.Receiver[FromEnvironmentToAggregation],
    from_proxy_camera_feed_interest: bounded_channel.Receiver[
        FromProxyToAggregationCameraFeedInterest
    ],
    to_proxy_camera_frame: bounded_channel.Sender[FromAggregationToProxyCameraFrame],
):

    users_interested_in_camera_feed: set[str] = set()

    # Used to only retrieve images from the camera when there’s interest
    any_user_interested_in_the_camera_feed = Event()

    # Run these tasks concurrently
    await gather(
        receive_proxy_messages(
            from_proxy_camera_feed_interest=from_proxy_camera_feed_interest,
            any_user_interested_in_the_camera_feed=any_user_interested_in_the_camera_feed,
            users_interested_in_camera_feed=users_interested_in_camera_feed,
        ),
        forward_camera_feed(
            from_environment=from_environment,
            to_proxy_camera_frame=to_proxy_camera_frame,
            any_user_interested_in_the_camera_feed=any_user_interested_in_the_camera_feed,
            users_interested_in_camera_feed=users_interested_in_camera_feed,
        ),
    )


async def receive_proxy_messages(
    *,
    from_proxy_camera_feed_interest: bounded_channel.Receiver[
        FromProxyToAggregationCameraFeedInterest
    ],
    any_user_interested_in_the_camera_feed: Event,
    users_interested_in_camera_feed: set[str],
):
    async for message in from_proxy_camera_feed_interest:
        if message.wants_camera_feed:
            users_interested_in_camera_feed.add(message.user_id)
        else:
            users_interested_in_camera_feed.remove(message.user_id)

        if users_interested_in_camera_feed:
            any_user_interested_in_the_camera_feed.set()
        else:
            any_user_interested_in_the_camera_feed.clear()


async def forward_camera_feed(
    *,
    from_environment: bounded_channel.Receiver[FromEnvironmentToAggregation],
    to_proxy_camera_frame: bounded_channel.Sender[FromAggregationToProxyCameraFrame],
    any_user_interested_in_the_camera_feed: Event,
    users_interested_in_camera_feed: set[str],
):
    while True:
        await any_user_interested_in_the_camera_feed.wait()
        # TODO: swap this out with the puller / pusher construct I need to implement
        environment_message_option = await from_environment.recv()
        # TODO: there's no reason I can think of this would be a None variant
        environment_message = environment_message_option.unwrap()

        frame = environment_message.frame
        # Convert the frame (a numpy array) to a displayable image
        image = Image.fromarray(frame)

        await to_proxy_camera_frame.send(
            FromAggregationToProxyCameraFrame(
                image,
                # So the proxy module knows who to send the live images to
                list(users_interested_in_camera_feed),
            )
        )
