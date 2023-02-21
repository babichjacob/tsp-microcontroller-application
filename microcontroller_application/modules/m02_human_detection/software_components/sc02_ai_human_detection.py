from asyncio import Event, gather, sleep, to_thread

from microcontroller_application.log import get_logger

import bounded_channel
import numpy as np
from option_and_result import MatchesNone, MatchesSome

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToHumanDetectionCameraFrame,
    FromEnvironmentToHumanDetectionMotion,
    FromEnvironmentToHumanDetectionOccupancy,
    FromHumanDetectionToActivityRecognition,
    FromHumanDetectionToPersonIdentification,
)
from utils.asynchronous import at_least_one


LOGGER = get_logger(__name__)


async def run(
    *,
    from_environment_motion: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionMotion
    ],
    from_environment_occupancy: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionOccupancy
    ],
    from_environment_camera_frame: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionCameraFrame
    ],
    to_activity_recognition: bounded_channel.Sender[
        FromHumanDetectionToActivityRecognition
    ],
    to_person_identification: bounded_channel.Sender[
        FromHumanDetectionToPersonIdentification
    ],
):
    "Run the AI human detection software component"

    requested_human_detection = Event()

    occupied = Event()

    # Run all the tasks concurrently
    await gather(
        check_motion_sensor(
            from_environment_motion=from_environment_motion,
            requested_human_detection=requested_human_detection,
        ),
        check_occupancy_sensor(
            from_environment_occupancy=from_environment_occupancy,
            occupied=occupied,
            requested_human_detection=requested_human_detection,
        ),
        interval_while_occupied(
            occupied=occupied,
            requested_human_detection=requested_human_detection,
        ),
        slow_interval(
            requested_human_detection=requested_human_detection,
        ),
        # This is defined in the next code sample
        do_human_detection_when_triggered(
            from_environment_camera_frame=from_environment_camera_frame,
            to_activity_recognition=to_activity_recognition,
            to_person_identification=to_person_identification,
            requested_human_detection=requested_human_detection,
        ),
    )


async def check_motion_sensor(
    *,
    from_environment_motion: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionMotion
    ],
    requested_human_detection: Event,
):
    async for message in from_environment_motion:
        # Run human detection once motion is detected
        if message.new_state:
            requested_human_detection.set()


async def check_occupancy_sensor(
    *,
    from_environment_occupancy: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionOccupancy
    ],
    occupied: Event,
    requested_human_detection: Event,
):
    async for message in from_environment_occupancy:
        # Run human detection once occupancy is detected
        if message.new_state:
            occupied.set()
            requested_human_detection.set()
        else:
            occupied.clear()


async def interval_while_occupied(
    *,
    occupied: Event,
    requested_human_detection: Event,
):
    while True:
        # Wait until the event is set
        await occupied.wait()
        await sleep(15)
        # The occupied event could have been cleared since, but that’s okay
        # It’s just one extra human detection scan that wasn’t needed
        requested_human_detection.set()


async def slow_interval(
    *,
    requested_human_detection: Event,
):
    while True:
        await sleep(5 * 60)
        requested_human_detection.set()


async def do_human_detection_when_triggered(
    *,
    from_environment_camera_frame: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionCameraFrame
    ],
    to_activity_recognition: bounded_channel.Sender[
        FromHumanDetectionToActivityRecognition
    ],
    to_person_identification: bounded_channel.Sender[
        FromHumanDetectionToPersonIdentification
    ],
    requested_human_detection: Event,
):
    while True:
        await requested_human_detection.wait()
        # This is expected to finish immediately in most situations
        message_option = (
            await from_environment_camera_frame.recv()
        )  # TODO: switch to the pusher/puller thing I need to make

        match message_option.to_matchable():
            case MatchesNone():
                break
            case MatchesSome(message):
                image = message.frame

                # This is a long (multi-second) astoundingly computationally expensive process
                # so calling it is sent to a new thread to prevent blocking the main thread.
                # Tasks are cooperatively scheduled, so diligence like this is needed.
                images_of_humans = await to_thread(do_human_detection, image)
                # do_human_detection is defined in the next code sample

                # events remain set until cleared
                requested_human_detection.clear()
                # clearing it now means that another human detection request can be serviced
                # next loop around (i.e. right after either one of these messages is sent:)

                to_activity_recognition_message = (
                    FromHumanDetectionToActivityRecognition(images_of_humans)
                )

                to_person_identification_message = (
                    FromHumanDetectionToPersonIdentification(images_of_humans)
                )

                await at_least_one(
                    [
                        to_activity_recognition.send(to_activity_recognition_message),
                        to_person_identification.send(to_person_identification_message),
                    ]
                )


def do_human_detection(image: np.ndarray):
    LOGGER.error(
        "was supposed to do human detection on %r but this is not implemented yet",
        image,
    )

    return []
