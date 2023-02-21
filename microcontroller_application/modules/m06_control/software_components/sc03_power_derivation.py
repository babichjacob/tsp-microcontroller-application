"""
Module: 06. Control
Component: 03. Power derivation

This component receives a duty cycle (float ranging from 0.0 to 10)
from the duty cycle component stating how much light is being outputted.

This component converts this value from a duty cycle to a wattage
(the amount of power consumed in order to light at that level of brightness)
through a lookup table with (linear) interpolation.
"""


import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromControlToAggregationPower,
)
from microcontroller_application.log import get_logger
from utils.lookup_table import lerp_from_table

from ..message_types import FromDutyCycleToPowerDerivation

LOGGER = get_logger(__name__)


async def run(
    *,
    from_duty_cycle: bounded_channel.Receiver[FromDutyCycleToPowerDerivation],
    to_aggregation_power: bounded_channel.Sender[FromControlToAggregationPower],
):
    "Run the power derivation software component"

    LOGGER.debug("startup")

    async for message in from_duty_cycle:
        duty_cycle = message.duty_cycle
        watts = convert_duty_cycle_to_watts(duty_cycle)

        await to_aggregation_power.send(FromControlToAggregationPower(watts))

    LOGGER.debug("shutdown")


# Examples of values that would be found from experimentation
# TODO: these will be changed after collecting samples
DUTY_CYCLE_TO_WATTS = [
    (0.0, 0.0),
    (0.2, 3.5),
    (0.4, 5.0),
    (0.6, 7.2),
    (0.8, 8.4),
    (1.0, 10.0),
]


def convert_duty_cycle_to_watts(duty_cycle: float) -> float:
    return lerp_from_table(DUTY_CYCLE_TO_WATTS, duty_cycle)
