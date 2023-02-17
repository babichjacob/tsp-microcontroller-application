"""
This module is concerned with determining how many humans
are present in the room and where they are.
"""

from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToHumanDetection,
    FromHumanDetectionToActivityRecognition,
    FromHumanDetectionToPersonIdentification,
)


async def run(
    *,
    from_environment: Receiver[FromEnvironmentToHumanDetection],
    to_activity_recognition: Sender[FromHumanDetectionToActivityRecognition],
    to_person_identification: Sender[FromHumanDetectionToPersonIdentification],
):
    "Run the human detection module"

    print("hello from the human detection module")
