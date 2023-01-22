"""
This module is concerned with deciding, all things considered,
what brightness the lights in the room should be.
"""


from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromActivityRecognitionToControl,
    FromControlToAggregation,
    FromEnvironmentToControl,
    FromPersonIdentificationToControl,
    FromPreferencesToControl,
)


async def run(
    *,
    from_activity_recognition: Receiver[FromActivityRecognitionToControl],
    from_person_identification: Receiver[FromPersonIdentificationToControl],
    from_environment: Receiver[FromEnvironmentToControl],
    from_preferences: Receiver[FromPreferencesToControl],
    # TODO: add a dimmer driver software component to the lighting module and
    # This is actually a hardware interface so it should be removed
    # to_lighting: Sender[FromControlToLighting],
    to_aggregation: Sender[FromControlToAggregation]
):
    "Run the control module"

    print("hello from the control module")
