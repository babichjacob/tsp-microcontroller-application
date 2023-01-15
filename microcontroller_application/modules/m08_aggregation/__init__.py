"""
This module is concerned with storing and providing
current and historical data.
"""


from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromPersonIdentificationToAggregation,
    FromControlToAggregation,
    FromEnvironmentToAggregation,
    FromAggregationToProxy,
)


async def run(
    *,
    from_person_identification: Receiver[FromPersonIdentificationToAggregation],
    from_control: Receiver[FromControlToAggregation],
    from_environment: Receiver[FromEnvironmentToAggregation],
    to_proxy: Sender[FromAggregationToProxy],
):
    print("hello from the aggregation module")
