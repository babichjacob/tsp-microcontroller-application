"Camera recording component"

from asyncio import Event, gather
from microcontroller_application.log import get_logger
from pathlib import Path

import bounded_channel

from datetime import datetime

from microcontroller_application.interfaces.message_types import (
    FromProxyToAggregationRecordTheCamera,
    FromEnvironmentToAggregation,
)

from PIL import Image


LOGGER = get_logger(__name__)


async def run(
    *,
    from_environment: bounded_channel.Receiver[FromEnvironmentToAggregation],
    from_proxy_record_the_camera: bounded_channel.Receiver[
        FromProxyToAggregationRecordTheCamera
    ],
    history_folder: Path,
):
    LOGGER.debug("startup")

    recording = Event()

    await gather(
        receive_proxy_messages(
            from_proxy_record_the_camera=from_proxy_record_the_camera,
            recording=recording,
        ),
        record_camera_feed(
            from_environment=from_environment,
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
    history_folder: Path,
    recording: Event,
):

    frame_number = 0
    recording_folder = None

    while True:
        await recording.wait()

        # A recording has just been started this frame
        if recording_folder is None:
            # TODO: switch to Option rather than a bare None
            now = datetime.now()
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

        # Grab the current camera frame
        environment_message_option = await from_environment.recv()
        environment_message = (
            environment_message_option.unwrap()
        )  # TODO: I presume this can never be None?

        frame = environment_message.frame
        # Convert the frame (a numpy array) to a displayable image
        image = Image.fromarray(frame)
        # Save the image in the recording folder with the frame number as the name
        image.save(f"{frame}.jpeg")

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
