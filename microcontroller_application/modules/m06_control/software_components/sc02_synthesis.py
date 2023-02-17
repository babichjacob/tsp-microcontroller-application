from option_and_result import MatchesSome, MatchesNone, NONE, Option, Some

from bisect import bisect
from datetime import datetime

from microcontroller_application.interfaces.message_types import (
    Activity,
    Preferences,
    UserSlot,
)


def calculate_synthesized_light_brightness(
    *,
    ambient_light_lumens: float,
    now: datetime,
    people_in_room: list[Option[UserSlot]],
    user_preferences: dict[UserSlot, Preferences]
) -> float:
    if not people_in_room:
        # If no one’s there, it should be off.
        return 0

    # Just pick the first person in the room's light preferences
    person_in_room = next(
        (person for person in people_in_room if person.is_some()), NONE()
    )

    # The variable has to be initialized here for it to work
    # (despite there being no reachable path after this block
    #  where preferences_for_person_in_room is not defined...)
    preferences_for_person_in_room = NONE()
    match person_in_room.to_matchable():
        case MatchesSome(trusted_person):
            preferences_for_person_in_room = Some(user_preferences[trusted_person])

    now = datetime.now()

    match preferences_for_person_in_room.to_matchable():
        case MatchesSome(preferences):
            # Finds the schedule entry that starts before now
            corresponding_timer_index = bisect(
                preferences.timers, (now.weekday, now.hour, now.minute)
            )

            corresponding_timer = preferences.timers[corresponding_timer_index]

            if corresponding_timer.light_effect == LightEffect.ForceBrightness:
                return corresponding_timer.brightness

            # otherwise
            desired_lumens = preferences_for_person_in_room.timers[
                corresponding_timer_index
            ].brightness

            if activity_category == ActivityCategory.Working:
                # Ensure there’s at least 300 lumens of light being emitted to work with
                desired_lumens += 300
            elif activity_category == ActivityCategory.Lying:
                # Make it up to 300 lumens (about 50%) darker to make it easier to relax and sleep
                desired_lumens -= 300
                # Better values may be found from experimentation

            difference_between_desired_and_ambient = (
                desired_lumens - ambient_light_lumens
            )

            if difference_between_desired_and_ambient < 0:
                # If it’s bright enough (according to the ambient light sensor), it should be off.
                return 0

            # Only a maximum of 600 lumens can be emitted per requirements
            elif difference_between_desired_and_ambient > 600:
                return 600

            # This represents a non-full and non-off amount of light (between 0% to 100% duty cycle)
            return difference_between_desired_and_ambient
