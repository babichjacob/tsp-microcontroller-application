"""
Module: 08. Aggregation
Component: 06. Camera recording
"""

from asyncio import Event, gather
from datetime import datetime
from pathlib import Path
from typing import Callable

import bounded_channel
from PIL import Image

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToAggregation,
    FromProxyToAggregationRecordTheCamera,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_environment: bounded_channel.Receiver[FromEnvironmentToAggregation],
    from_proxy_record_the_camera: bounded_channel.Receiver[
        FromProxyToAggregationRecordTheCamera
    ],
    get_current_time: Callable[[], datetime],
    history_folder: Path,
):
    "Run the camera recording component"

    LOGGER.debug("startup")

    recording = Event()

    await gather(
        receive_proxy_messages(
            from_proxy_record_the_camera=from_proxy_record_the_camera,
            recording=recording,
        ),
        record_camera_feed(
            from_environment=from_environment,
            get_current_time=get_current_time,
            history_folder=history_folder,
            recording=recording,
        ),
    )

    LOGGER.debug("shutdown")


async def receive_proxy_messages(
    *,
    from_proxy_record_the_camera: bounded_channel.Receiver[
        FromProxyToAggregationRecordTheCamera
    ],
    recording: Event,
):
    async for message in from_proxy_record_the_camera:
        if message.should_record:
            recording.set()
        else:
            recording.clear()


async def record_camera_feed(
    *,
    from_environment: bounded_channel.Receiver[FromEnvironmentToAggregation],
    get_current_time: Callable[[], datetime],
    history_folder: Path,
    recording: Event,
):

    frame_number = 0
    recording_folder = None

    while True:
        await recording.wait()

        # A recording has just been started this frame
        if recording_folder is None:
            now = get_current_time()

            LOGGER.info("starting a camera recording session for %s", now)

            # TODO: switch to Option rather than a bare None
            recording_folder = (
                history_folder
                / str(now.year)
                / str(now.month)
                / str(now.day)
                / "videos"
                / str(now.hour)
                / str(now.minute)
                / str(now.second)
            )

            recording_folder.mkdir(exist_ok=True, parents=True)

        # Grab the current camera frame
        environment_message_option = await from_environment.recv()
        environment_message = (
            environment_message_option.unwrap()
        )  # TODO: I presume this can never be None?

        frame = environment_message.frame
        # Convert the frame (a numpy array) to a displayable image
        image = Image.fromarray(frame)
        # Save the image in the recording folder with the frame number as the name
        destination = recording_folder / f"{frame_number}.jpeg"
        image.save(destination, quality=90)

        LOGGER.info("saved current frame to %s", destination)

        frame_number += 1

        # The recording was stopped during this frame.
        if not recording.is_set():
            # Get a list of all the files in the recording folder
            all_frames = list(recording_folder.iterdir())

            # Assemble a video from the captured frames
            await assemble_video(
                all_frames, recording_folder / "video.mkv"  # Inputs  # Output
            )

            # Reset the recording information
            frame_number = 0
            recording_folder = None


async def assemble_video(
    input_images: list[Path],
    output: Path,
):
    LOGGER.error("TODO: haven't set up ffmpeg arguments yet")
    await call_ffmpeg()


async def call_ffmpeg():
    LOGGER.error("TODO: calling ffmpeg hasn't been implemented yet")
