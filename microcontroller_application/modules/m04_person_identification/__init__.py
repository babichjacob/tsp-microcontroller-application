"""
This module is concerned with figuring out which trusted
user(s), if any, the human(s) in the room are.
"""

from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromHumanDetectionToPersonIdentification,
    FromPersonIdentificationToAggregation,
    FromPersonIdentificationToControl,
    FromPersonIdentificationToProxy,
    FromProxyToPersonIdentification,
)


async def run(
    *,
    from_human_detection: Receiver[FromHumanDetectionToPersonIdentification],
    from_proxy: Receiver[FromProxyToPersonIdentification],
    to_aggregation: Sender[FromPersonIdentificationToAggregation],
    to_proxy: Sender[FromPersonIdentificationToProxy],
    to_control: Sender[FromPersonIdentificationToControl],
):
    "Run the person identification module"

    print("hello from the person identification module")
