"""
Module: 08. Aggregation
Component: 08. Save intruder alerts
"""


from pathlib import Path
import bounded_channel
from microcontroller_application.interfaces.message_types import (
    FromPersonIdentificationToAggregation,
)

from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_person_identification: bounded_channel.Receiver[
        FromPersonIdentificationToAggregation
    ],
    history_folder: Path,
):
    "Run the save intruder alerts software component"

    LOGGER.debug("startup")

    async for intruder_alert in from_person_identification:
        when = intruder_alert.timestamp

        destination_folder = (
            history_folder
            / str(when.year)
            / str(when.month)
            / str(when.day)
            / "intruder"
        )

        destination_path = (
            destination_folder / f"{when.hour}-{when.minute}-{when.second}.jpeg"
        )

        intruder_alert.image.save(destination_path)

    LOGGER.debug("shutdown")
