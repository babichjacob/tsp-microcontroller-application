"""
Unit test
Module: 02. Human detection
Component: 02. AI human detection
"""


from pathlib import Path

from datetime import datetime, timedelta, timezone
import pytest


from microcontroller_application.log import get_logger

THIS_FILE = Path(__file__)

SOFTWARE_COMPONENTS_FOLDER = THIS_FILE.parent
MODULE_FOLDER = SOFTWARE_COMPONENTS_FOLDER.parent

TEST_DATA_FOLDER = MODULE_FOLDER / "test_data"


LOGGER = get_logger(__name__)




def test_no_humans():
    # TODO: load image with no humans in it into memory
    input_data = None

    time_started = datetime.now().astimezone(timezone.utc)

    actual_result = []  # TODO
    assert False, "actual_result is fake data"

    time_ended = datetime.now().astimezone(timezone.utc)

    expected_result = []

    assert actual_result == expected_result

    time_limit = timedelta(seconds=15)

    time_taken = time_ended - time_started

    assert time_taken < time_limit

    assert False, "test hasn't been programmed yet"  # TODO


@pytest.mark.asyncio
async def test_no_humans_without_blocking():
    "TODO: test that other tasks can run concurrently while this software component is running. Also expect that it returns no humans in this humanless example image"

    ...
    assert False, "test hasn't been programmed yet"  # TODO
