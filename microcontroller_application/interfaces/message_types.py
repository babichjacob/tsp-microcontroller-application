"""
Type definitions for messages that will be sent
between modules (actors) across interfaces (channels)
"""


from dataclasses import dataclass
from enum import Enum
from typing import Any

from option_and_result import Option

# Any is used as a placeholder for all the types we expect to write at a later time
# They will use @dataclass and the | operator
# discussed in the low level design specification document

# Interface 01.1
FromPreferencesToProxy = Any
# Interface 01.2
class UserSlot(Enum):
    # The system only has to support 4 users (requirement 3.5.5)
    One = 1
    Two = 2
    Three = 3
    Four = 4


@dataclass
class FromProxyToPreferences:
    user_slot: UserSlot
    # The Preferences definition from 4.3.7 (below)
    preferences: "Preferences"


# Interface 02
FromAggregationToProxy = Any
# Interface 03
FromHumanDetectionToActivityRecognition = Any
# Interface 04
FromHumanDetectionToPersonIdentification = Any
# Interface 05
class Activity(Enum):
    # These numbers don’t matter; you just have to give enum variants a value
    Working = 0
    Lying = 1
    Neither = 2


@dataclass
class FromActivityRecognitionToControl:
    activities_of_humans: list[Activity]


# Interface 06
# An Option has two variants:
# * None, which doesn’t have a value
# * Some(x), where x is the value
# Here, a None value means that a person could not be identified
# and a Some value contains which trusted user was identified
IdentifiedPerson = Option[UserSlot]  # Reusing the UserSlot definition in 4.3.1.2


@dataclass
class FromPersonIdentificationToControl:
    identified_people: list[IdentifiedPerson]


# Interface 07
@dataclass
class LightEffectDesiredBrightness:
    """
    The person wants the brightness in the room to “end up” being this value,
    taking into account the ambient light already present in it.
    They are also allowing the system to manipulate the desired brightness
    depending on the activity they are doing.
    """

    lumens: float  # 0 (pitch black) to 2000
    # (a guesstimate for sunlight going through a window into the room)
    # The system will do its best to bridge the gap between wanting it to be bright
    # on a dark and cloudy day, for example, when working with just a light bulb
    # (600 lumens (requirement 3.1.3))


@dataclass
class LightEffectForceEndBrightness:
    """
    The person wants to completely override the “smart” functionality of the system
    and just make the brightness the light bulb emits this exact value.
    """

    lumens: int  # 0 (for off) to 600 (the maximum per requirement 3.1.3)


# A light effect can be either of these two
LightEffect = LightEffectDesiredBrightness | LightEffectForceEndBrightness


@dataclass
class Timer:
    effect: LightEffect
    weekday: int  # 0 to 6
    hour: int  # 0 to 23
    minute: int  # 0 to 59


@dataclass
class Preferences:
    name: str
    timers: list[Timer]


@dataclass
class FromPreferencesToControl:
    "The preferences of each person in the room"

    preferences: list[Preferences]  # sorted by weekday, then day, then hour


# Interface 08
FromProxyToPersonIdentification = Any
# Interface 09
FromPersonIdentificationToProxy = Any
# Interface 10
FromPersonIdentificationToAggregation = Any
# Interface 11
FromControlToAggregation = Any
# Interface 12
# Interface 13
FromEnvironmentToHumanDetection = Any
# Interface 14
FromEnvironmentToControl = Any
# Interface 15
FromEnvironmentToAggregation = Any
