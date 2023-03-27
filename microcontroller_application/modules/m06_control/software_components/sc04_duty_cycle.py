"""
Module: 06. Control
Component: 04. Duty cycle

This component receives a light value (in lumens) 
from the synthesis component stating how much light should be output.

This component converts this value from lumens to a percentage
(duty cycle) through a lookup table with (linear) interpolation.
"""

import bounded_channel
from microcontroller_application.interfaces.message_types import (
    FromControlToAggregationDutyCycle,
    FromControlToLighting,
)

from microcontroller_application.log import get_logger
from utils.lookup_table import lerp_from_table
from utils.asynchronous import at_least_one

from ..message_types import FromDutyCycleToPowerDerivation, FromSynthesisToDutyCycle

LOGGER = get_logger(__name__)


async def run(
    *,
    from_synthesis: bounded_channel.Receiver[FromSynthesisToDutyCycle],
    to_power_derivation: bounded_channel.Sender[FromDutyCycleToPowerDerivation],
    to_aggregation_duty_cycle: bounded_channel.Sender[
        FromControlToAggregationDutyCycle
    ],
    to_lighting: bounded_channel.Sender[FromControlToLighting]
):
    "Run the duty cycle software component"

    LOGGER.debug("startup")

    async for message in from_synthesis:
        lumens = message.lumens
        duty_cycle = convert_lumens_to_duty_cycle(lumens)

        await at_least_one(
            [
                to_lighting.send(FromControlToLighting(duty_cycle=duty_cycle)),
                to_power_derivation.send(
                    FromDutyCycleToPowerDerivation(duty_cycle=duty_cycle)
                ),
                to_aggregation_duty_cycle.send(
                    FromControlToAggregationDutyCycle(duty_cycle=duty_cycle)
                ),
            ]
        )

    LOGGER.debug("shutdown")


# Examples of values that would be found from experimentation
LUMENS_TO_DUTY_CYCLE = [
    (000.0, 0.00),
    (100.0, 0.11),
    (200.0, 0.17),
    (300.0, 0.30),
    (400.0, 0.50),
    (500.0, 0.70),
    (600.0, 1.00),
]
# These will be “hardcoded” written just in the code like this


def convert_lumens_to_duty_cycle(lumens: float) -> float:
    return lerp_from_table(LUMENS_TO_DUTY_CYCLE, lumens)
