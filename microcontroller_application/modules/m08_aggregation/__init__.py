"""
This module is concerned with storing and providing
current and historical data.
"""


from asyncio import gather
from datetime import datetime
from pathlib import Path
from typing import Callable

import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromAggregationToProxyCameraFrame,
    FromAggregationToProxyDutyCycle,
    FromAggregationToProxyHistory,
    FromControlToAggregationDutyCycle,
    FromEnvironmentToAggregation,
    FromPersonIdentificationToAggregation,
    FromProxyToAggregationCameraFeedInterest,
    FromProxyToAggregationHistoryRequest,
    FromProxyToAggregationRecordTheCamera,
    FromProxyToAggregationRequestDutyCycle,
)
from microcontroller_application.log import get_logger

from .software_components import (
    sc03_current_state,
    sc04_history_compaction,
    sc05_history_expansion,
    sc06_camera_recording,
    sc07_camera_playback,
    sc08_save_intruder_alerts,
)

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
    from_proxy_camera_feed_interest: bounded_channel.Receiver[
        FromProxyToAggregationCameraFeedInterest
    ],
    from_proxy_record_the_camera: bounded_channel.Receiver[
        FromProxyToAggregationRecordTheCamera
    ],
    from_proxy_request_duty_cycle: bounded_channel.Receiver[
        FromProxyToAggregationRequestDutyCycle
    ],
    from_proxy_request_history: bounded_channel.Receiver[
        FromProxyToAggregationHistoryRequest
    ],
    to_proxy_camera_frame: bounded_channel.Sender[FromAggregationToProxyCameraFrame],
    to_proxy_duty_cycle: bounded_channel.Sender[FromAggregationToProxyDutyCycle],
    to_proxy_history: bounded_channel.Sender[FromAggregationToProxyHistory],
    history_folder: Path,
    get_current_time: Callable[[], datetime],
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

    sc04_history_compaction_task = sc04_history_compaction.run(
        from_control_duty_cycle=from_control_duty_cycle,
        get_current_time=get_current_time,
        history_folder=history_folder,
    )

    sc05_history_expansion_task = sc05_history_expansion.run(
        from_proxy_request_history=from_proxy_request_history,
        to_proxy=to_proxy_history,
        history_folder=history_folder,
    )

    sc06_camera_recording_task = sc06_camera_recording.run(
        from_environment=from_environment,
        from_proxy_record_the_camera=from_proxy_record_the_camera,
        get_current_time=get_current_time,
        history_folder=history_folder,
    )

    sc07_camera_playback_task = sc07_camera_playback.run(
        # TODO
    )

    sc08_save_intruder_alerts_task = sc08_save_intruder_alerts.run(
        from_person_identification=from_person_identification,
        history_folder=history_folder,
    )

    # Start of dropping extra references

    del from_person_identification
    del from_control_duty_cycle
    del from_environment
    del from_proxy_request_duty_cycle
    del to_proxy_duty_cycle

    # End of dropping extra references

    await gather(
        sc03_current_state_task,
        sc04_history_compaction_task,
        sc05_history_expansion_task,
        sc06_camera_recording_task,
        sc07_camera_playback_task,
        sc08_save_intruder_alerts_task,
    )

    LOGGER.debug("shutdown")
