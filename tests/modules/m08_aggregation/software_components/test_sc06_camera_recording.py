"""
Unit test
Module: 08. Aggregation
Component: 06. Camera recording
"""

from asyncio import create_task, sleep
from datetime import datetime
from pathlib import Path
from shutil import rmtree

import bounded_channel
from imagehash import phash
import numpy as np
import pytest
from PIL import Image

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToAggregation,
    FromProxyToAggregationRecordTheCamera,
)
from microcontroller_application.log import get_logger
from microcontroller_application.modules.m08_aggregation.software_components import (
    sc06_camera_recording,
)

THIS_FILE = Path(__file__)

SOFTWARE_COMPONENTS_FOLDER = THIS_FILE.parent
MODULE_FOLDER = SOFTWARE_COMPONENTS_FOLDER.parent

TEST_DATA_FOLDER = MODULE_FOLDER / "test_data"


LOGGER = get_logger(__name__)


def stem_as_number(path: Path) -> int:
    return int(path.stem)


@pytest.mark.asyncio
async def test_camera_recording_01():
    image_set = TEST_DATA_FOLDER / "images_01"

    all_images = list(image_set.iterdir())
    all_images_in_order = sorted(all_images, key=stem_as_number)

    history_folder = Path(
        ".test_artifacts/m08_aggregation/software_components/recording_01"
    )
    history_folder.mkdir(parents=True, exist_ok=True)

    # Remove artifacts from previous test runs to prevent interference
    rmtree(history_folder)

    (
        from_environment_sender,
        from_environment_receiver,
    ) = bounded_channel.channel(32)
    (
        from_proxy_record_the_camera_sender,
        from_proxy_record_the_camera_receiver,
    ) = bounded_channel.channel(32)

    test_timestamp = datetime(year=2022, month=8, day=17, hour=6, minute=43, second=25)

    sc06_camera_recording_coro = sc06_camera_recording.run(
        from_environment=from_environment_receiver,
        from_proxy_record_the_camera=from_proxy_record_the_camera_receiver,
        get_current_time=lambda: test_timestamp,
        history_folder=history_folder,
    )

    # Start of dropping extra references
    del from_environment_receiver
    del from_proxy_record_the_camera_receiver
    # End of dropping extra references

    sc06_camera_recording_task = create_task(sc06_camera_recording_coro)

    # Start funneling in test data

    # Start recording
    (
        await from_proxy_record_the_camera_sender.send(
            FromProxyToAggregationRecordTheCamera(should_record=True)
        )
        # Unwrap means to fail the test if an error is returned
    ).unwrap()

    for input_image_path in all_images_in_order:
        LOGGER.debug("sending %s", input_image_path)

        image = Image.open(input_image_path)

        frame = np.asarray(image)

        # Pretend that this image really came from the camera
        (
            await from_environment_sender.send(
                FromEnvironmentToAggregation(
                    frame=frame,
                )
            )
            # Fail the test if an error is returned
        ).unwrap()

    # Stop the recording
    (
        await from_proxy_record_the_camera_sender.send(
            FromProxyToAggregationRecordTheCamera(should_record=False)
        )
    ).unwrap()

    # Filesystems are weird - a short break like this is probably needed
    await sleep(0.5)

    recording_destination = (
        history_folder / "2022" / "8" / "17" / "videos" / "6" / "43" / "25"
    )

    assert recording_destination.exists()

    for input_image_path in all_images_in_order:
        stem = input_image_path.stem

        output_image_path = recording_destination / f"{stem}.jpeg"

        assert output_image_path.exists()

        input_image = Image.open(input_image_path)
        output_image = Image.open(output_image_path)

        assert input_image.width == output_image.width
        assert input_image.height == output_image.height

        input_image_hash = phash(input_image)
        output_image_hash = phash(output_image)

        difference = input_image_hash - output_image_hash

        threshold = 15

        assert (
            difference < threshold
        ), f"{input_image_path=} and {output_image_path=} are too dissimilar"

    # End the recording (shouldn't matter but it's good form)
    (
        await from_proxy_record_the_camera_sender.send(
            FromProxyToAggregationRecordTheCamera(should_record=False)
        )
    ).unwrap()

    # TODO: implement a graceful shutdown signal... maybe?
    # await sc06_camera_recording_task

    # Start of dropping extra references
    del from_environment_sender
    del from_proxy_record_the_camera_sender
    # End of dropping extra references
