"""
Module: 06. Control
Component: 02. Synthesis

It uses the current ambient brightness,
the identified people (or unidentified people) in the room,
the recognized activity each person is doing,
and the preferences of the identified people
in order to come up with a final brightness the system’s lights should be.

This information is fed into an algorithm / formula to calculate output light brightness
from the inputs (identified people, recognized activity, ambient light, and user preferences).

This algorithm results in a brightness value (in lumens).

That resulting brightness value is given to the aggregation module
(and to the components within this module).
"""


from asyncio import gather, get_event_loop
from bisect import bisect
from datetime import datetime, timedelta

import bounded_channel
from option_and_result import NONE, Option, Some
from store import Writable, writable

from microcontroller_application.interfaces.message_types import (
    Activity,
    FromActivityRecognitionToControl,
    FromEnvironmentToControl,
    FromPersonIdentificationToControl,
    FromPreferencesToControl,
    IdentifiedPerson,
    LightEffectDesiredBrightness,
    LightEffectForceEndBrightness,
    Preferences,
    UserSlot,
)
from microcontroller_application.log import get_logger
from microcontroller_application.modules.m06_control.message_types import (
    FromSynthesisToDutyCycle,
)
from utils.iterables import average
from utils.stores import derived_with_time, values

LOGGER = get_logger(__name__)


async def run(
    *,
    from_environment: bounded_channel.Receiver[FromEnvironmentToControl],
    from_activity_recognition: bounded_channel.Receiver[
        FromActivityRecognitionToControl
    ],
    from_person_identification: bounded_channel.Receiver[
        FromPersonIdentificationToControl
    ],
    from_preferences: bounded_channel.Receiver[FromPreferencesToControl],
    to_duty_cycle: bounded_channel.Sender[FromSynthesisToDutyCycle],
):
    LOGGER.debug("startup")

    # TODO: extract these to top level functions with parameters

    ambient_brightness_store: Writable[Option[float], None] = writable(NONE())

    async def put_ambient_brightness_in_store():
        async for message in from_environment:
            ambient_brightness = message.ambient_brightness
            ambient_brightness_store.set(Some(ambient_brightness))

    activities_store: Writable[Option[list[Activity]], None] = writable(NONE())

    async def put_activities_in_store():
        async for message in from_activity_recognition:
            activities = message.activities_of_humans
            activities_store.set(Some(activities))

    identified_people_store: Writable[Option[list[IdentifiedPerson]], None] = writable(
        NONE()
    )

    async def put_trusted_people_in_store():
        async for message in from_person_identification:
            identified_people = message.identified_people
            identified_people_store.set(Some(identified_people))

    preferences_store: Writable[Option[dict[UserSlot, Preferences]], None] = writable(
        NONE()
    )

    async def put_preferences_in_store():
        async for message in from_preferences:
            preferences = message.preferences
            preferences_store.set(Some(preferences))

    loop = get_event_loop()

    synthesized_brightness_store = derived_with_time(
        [
            ambient_brightness_store,
            activities_store,
            identified_people_store,
            preferences_store,
        ],
        synthesize_if_initialized,
        loop=loop,
        # Recalculate at least every 15 seconds
        get_max_period=lambda: timedelta(seconds=15),
    )

    async def send_synthesized_brightness():
        async for synthesized_brightness_option in values(synthesized_brightness_store):

            if synthesized_brightness_option.is_some():
                synthesized_brightness = synthesized_brightness_option.unwrap()

                await to_duty_cycle.send(
                    FromSynthesisToDutyCycle(synthesized_brightness)
                )

    await gather(
        put_ambient_brightness_in_store(),
        put_activities_in_store(),
        put_trusted_people_in_store(),
        put_preferences_in_store(),
        send_synthesized_brightness(),
    )

    LOGGER.debug("shutdown")


def synthesize_if_initialized(
    ambient_brightness_option: Option[float],
    activities_option: Option[list[Activity]],
    identified_people_option: Option[list[IdentifiedPerson]],
    preferences_option: Option[dict[UserSlot, Preferences]],
) -> Option[float]:
    if (
        ambient_brightness_option.is_some()
        and activities_option.is_some()
        and identified_people_option.is_some()
        and preferences_option.is_some()
    ):
        ambient_brightness = ambient_brightness_option.unwrap()
        activities = activities_option.unwrap()
        identified_people = identified_people_option.unwrap()
        preferences = preferences_option.unwrap()

        now = datetime.now()

        return Some(
            calculate_synthesized_light_brightness(
                activities=activities,
                ambient_light_lumens=ambient_brightness,
                now=now,
                people_in_room=identified_people,
                user_preferences=preferences,
            )
        )

    return NONE()


def calculate_brightness_for_user(
    *,
    activity: Activity,
    ambient_light_lumens: float,
    now: datetime,
    preferences: Preferences,
) -> float:
    # Finds the schedule entry that starts before now
    corresponding_timer_index = bisect(
        preferences.timers, (now.weekday, now.hour, now.minute)
    )

    corresponding_timer = preferences.timers[corresponding_timer_index]

    if isinstance(corresponding_timer.effect, LightEffectForceEndBrightness):
        exact_lumens = corresponding_timer.effect.lumens
        return exact_lumens
    elif isinstance(corresponding_timer.effect, LightEffectDesiredBrightness):
        desired_lumens = corresponding_timer.effect.lumens

        if activity == Activity.WORKING:
            # Ensure there’s at least 300 lumens of light
            # being emitted to work with
            desired_lumens += 300
        elif activity == Activity.LYING:
            # Make it up to 300 lumens (about 50%) darker
            # to make it easier to relax and sleep
            desired_lumens -= 300
            # Better values may be found from experimentation

            difference_between_desired_and_ambient = (
                desired_lumens - ambient_light_lumens
            )

            if difference_between_desired_and_ambient < 0:
                # If it’s bright enough (according to the ambient light sensor)
                # it should be off
                return 0

            # Only a maximum of 600 lumens can be emitted per requirements
            elif difference_between_desired_and_ambient > 600:
                return 600

            # This represents a non-full and non-off amount of light
            # (between 0% to 100% duty cycle)
            return difference_between_desired_and_ambient
    else:
        raise RuntimeError("unreachable")


def calculate_synthesized_light_brightness(
    *,
    activities: list[Activity],
    ambient_light_lumens: float,
    now: datetime,
    people_in_room: list[Option[UserSlot]],
    user_preferences: dict[UserSlot, Preferences],
) -> float:

    # If no one’s there, it should be off
    if len(people_in_room) == 0:
        return 0.0

    trusted_people = [
        (index, person.unwrap())
        for (index, person) in enumerate(people_in_room)
        if person.is_some()
    ]

    # There is at least one untrusted person in the room
    # and no trusted people in the room
    if len(trusted_people) == 0:
        # What brightness lights should be in this scenario is unspecified,
        # but (approximately) half of max brightness (600) is a good start.
        # Maybe we'll change this.
        return 300.0

    brightnesses = []

    for (index, person) in trusted_people:
        preferences = user_preferences[person]

        activity = activities[index]

        brightness = calculate_brightness_for_user(
            activity=activity,
            ambient_light_lumens=ambient_light_lumens,
            now=now,
            preferences=preferences,
        )

        brightnesses.append(brightness)

    # Cannot be a None variant because this list has at least one element
    average_brightness = average(brightnesses).unwrap()

    return average_brightness
