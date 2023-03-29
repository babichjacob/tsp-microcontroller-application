"""
Module: 08. Aggregation
Component: 05. History expansion
"""

import csv
from bisect import insort
from pathlib import Path
import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromProxyToAggregationHistoryRequest,
    FromAggregationToProxyHistory,
    Time,
    TimelineEvent,
    TimelineEventBrightness,
    TimelineEventEnergy,
    TimelineEventIntruder,
)

from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_proxy_request_history: bounded_channel.Receiver[
        FromProxyToAggregationHistoryRequest
    ],
    to_proxy: bounded_channel.Sender[FromAggregationToProxyHistory],
    history_folder: Path,
):
    LOGGER.debug("startup")

    async for message in from_proxy_request_history:
        date = message.date
        year = date.year
        month = date.month
        day = date.day

        brightness_history_file_path = (
            history_folder / str(year) / str(month) / str(day) / "brightness.csv"
        )
        energy_history_file_path = (
            history_folder / str(year) / str(month) / str(day) / "energy.csv"
        )
        intruders_folder = (
            history_folder / str(year) / str(month) / str(day) / "intruders"
        )

        timeline: list[tuple[int, int, int, TimelineEvent]] = []

        with open(
            brightness_history_file_path, "r", encoding="utf8"
        ) as brightness_history_file:
            reader = csv.reader(brightness_history_file)

            for line in reader:
                hour, minute, second, brightness = line

                int_hour = int(hour)
                int_minute = int(minute)
                int_second = int(second)

                time = Time(hour=int_hour, minute=int_minute, second=int_second)

                # insort uses binary searching to assemble a sorted list incrementally
                insort(
                    timeline,
                    (
                        int_hour,
                        int_minute,
                        int_second,
                        TimelineEventBrightness(time=time, bucket=brightness),
                    ),
                )

        with open(
            energy_history_file_path, "r", encoding="utf8"
        ) as energy_history_file:
            reader = csv.reader(energy_history_file)

            for line in reader:
                hour, energy = line
                # Energy is only tracked per hour, and on the frontend website
                # we want to see the energy used across an hour showing up
                # at the beginning of the hour in the timeline
                minute = 0
                second = 0

                int_hour = int(hour)
                int_minute = int(minute)
                int_second = int(second)

                time = Time(hour=int_hour, minute=int_minute, second=int_second)

                insort(
                    timeline,
                    (
                        int_hour,
                        int_minute,
                        int_second,
                        TimelineEventEnergy(time=time, energy=float(energy)),
                    ),
                )

        intruder_alerts = list(intruders_folder.iterdir())
        for intruder_alert in intruder_alerts:
            # Retrieve the hour, minute, and second back from the filename
            hour, minute, second = intruder_alert.stem.split("-")

            int_hour = int(hour)
            int_minute = int(minute)
            int_second = int(second)

            time = Time(hour=int_hour, minute=int_minute, second=int_second)

            # TODO: probably open the intruder alert file and pass it along here

            insort(
                timeline,
                (
                    int_hour,
                    int_minute,
                    int_second,
                    TimelineEventIntruder(time=time, intruder_alert=intruder_alert),
                ),
            )
        
        timeline_just_events = [event for (hour, minute, second, event) in timeline]

        await to_proxy.send(
            FromAggregationToProxyHistory(user_id=message.user_id, timeline=timeline_just_events)
        )

    LOGGER.debug("shutdown")
