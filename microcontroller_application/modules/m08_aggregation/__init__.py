"""
This module is concerned with storing and providing
current and historical data.
"""


from asyncio import gather
from microcontroller_application.log import get_logger
import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromAggregationToProxyCameraFrame,
    FromAggregationToProxyDutyCycle,
    FromControlToAggregationDutyCycle,
    FromEnvironmentToAggregation,
    FromPersonIdentificationToAggregation,
    FromProxyToAggregationCameraFeedInterest,
    FromProxyToAggregationRequestDutyCycle,
)

from .software_components import sc03_current_state


LOGGER = get_logger(__name__)


async def run(
    *,
    from_person_identification: bounded_channel.Receiver[
        FromPersonIdentificationToAggregation
    ],
    from_control_duty_cycle: bounded_channel.Receiver[
        FromControlToAggregationDutyCycle
    ],
    from_environment: bounded_channel.Receiver[FromEnvironmentToAggregation],
    from_proxy_request_duty_cycle: bounded_channel.Receiver[
        FromProxyToAggregationRequestDutyCycle
    ],
    from_proxy_camera_feed_interest: bounded_channel.Receiver[
        FromProxyToAggregationCameraFeedInterest
    ],
    to_proxy_camera_frame: bounded_channel.Sender[FromAggregationToProxyCameraFrame],
    to_proxy_duty_cycle: bounded_channel.Sender[FromAggregationToProxyDutyCycle],
):
    "Run the aggregation module"

    LOGGER.debug("startup")

    sc03_current_state_task = sc03_current_state.run(
        from_environment=from_environment,
        from_control_duty_cycle=from_control_duty_cycle,
        from_proxy_camera_feed_interest=from_proxy_camera_feed_interest,
        from_proxy_request_duty_cycle=from_proxy_request_duty_cycle,
        to_proxy_camera_frame=to_proxy_camera_frame,
        to_proxy_duty_cycle=to_proxy_duty_cycle,
    )

    del from_person_identification
    del from_control_duty_cycle
    del from_environment
    del from_proxy_request_duty_cycle
    del to_proxy_duty_cycle

    await gather(sc03_current_state_task)

    LOGGER.debug("shutdown")
