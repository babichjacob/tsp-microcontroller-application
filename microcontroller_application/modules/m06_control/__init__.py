"""
Module: 06. Control

This module is concerned with deciding, all things considered,
what brightness the lights in the room should be.
"""


from asyncio import gather

import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromActivityRecognitionToControl,
    FromControlToAggregationDutyCycle,
    FromControlToAggregationPower,
    FromControlToLighting,
    FromEnvironmentToControl,
    FromPersonIdentificationToControl,
    FromPreferencesToControl,
)
from microcontroller_application.log import get_logger

from .software_components import sc02_synthesis, sc03_power_derivation, sc04_duty_cycle

LOGGER = get_logger(__name__)


async def run(
    *,
    from_environment: bounded_channel.Receiver[FromEnvironmentToControl],
    from_activity_recognition: bounded_channel.Receiver[
        FromActivityRecognitionToControl
    ],
    from_person_identification: bounded_channel.Receiver[
        FromPersonIdentificationToControl
    ],
    from_preferences: bounded_channel.Receiver[FromPreferencesToControl],
    to_aggregation_duty_cycle: bounded_channel.Sender[
        FromControlToAggregationDutyCycle
    ],
    to_aggregation_power: bounded_channel.Sender[FromControlToAggregationPower],
    to_lighting: bounded_channel.Sender[FromControlToLighting],
    use_randomized_data: bool,
):
    "Run the control module"

    LOGGER.debug("startup")

    to_duty_cycle, from_synthesis = bounded_channel.channel(32)
    to_power_derivation, from_duty_cycle = bounded_channel.channel(32)

    sc02_synthesis_task = sc02_synthesis.run(
        from_environment=from_environment,
        from_activity_recognition=from_activity_recognition,
        from_person_identification=from_person_identification,
        from_preferences=from_preferences,
        to_duty_cycle=to_duty_cycle,
        use_randomized_data=use_randomized_data,
    )
    sc03_power_derivation_task = sc03_power_derivation.run(
        from_duty_cycle=from_duty_cycle,
        to_aggregation_power=to_aggregation_power,
    )
    sc04_duty_cycle_task = sc04_duty_cycle.run(
        from_synthesis=from_synthesis,
        to_power_derivation=to_power_derivation,
        to_aggregation_duty_cycle=to_aggregation_duty_cycle,
        to_lighting=to_lighting,
    )

    await gather(
        sc02_synthesis_task,
        sc03_power_derivation_task,
        sc04_duty_cycle_task,
    )

    LOGGER.debug("shutdown")
