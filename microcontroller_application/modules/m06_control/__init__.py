from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromPreferencesToControl,
)


async def run(
    *,
    from_activity_recognition: Receiver[FromActivityRecognitionToControl],
    from_person_identification: Receiver[FromPersonIdentificationToControl],
    from_environment: Receiver[FromEnvironmentToControl],
    from_preferences: Receiver[FromPreferencesToControl],
    # This is actually a hardware interface so it should be removed
    # to_lighting: Sender[FromControlToLighting],
    to_aggregation: Sender[FromControlToAggregation]
):
    print("hello from the control module")
