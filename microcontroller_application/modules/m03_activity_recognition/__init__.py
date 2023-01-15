"""
This module is concerned with categorizing 
what each human in the room is doing.
"""

from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromActivityRecognitionToControl,
    FromHumanDetectionToActivityRecognition,
)


async def run(
    *,
    from_human_detection: Receiver[FromHumanDetectionToActivityRecognition],
    to_control: Sender[FromActivityRecognitionToControl],
):
    print("hello from the activity recognition module")
