"""
Type definitions for messages that will be sent
between modules (actors) across interfaces (channels)
"""


from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Union

import numpy as np
from option_and_result import Option
from PIL.Image import Image

# Any is used as a placeholder for all the types we expect to write at a later time
# They will use @dataclass and the | operator (actually Union because of Python version requirements)
# discussed in the low level design specification document

# Interface 01.1
@dataclass
class FromPreferencesToProxy:
    # So the proxy module knows which user to forward the message to
    user_id: str
    # The Preferences definition from 4.3.7 (below)
    preferences: "Preferences"


# Interface 01.2
class UserSlot(Enum):
    # The system only has to support 4 users (requirement 3.5.5)
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


@dataclass
class FromProxyToPreferences:
    user_slot: UserSlot
    # The Preferences definition from  interface 07 (below)
    preferences: "Preferences"


# Interface 02
@dataclass
class FromAggregationToProxyDutyCycle:
    duty_cycle: float


@dataclass
class FromAggregationToProxyCameraFrame:
    frame: Image

    user_ids: list[str]


@dataclass
class Time:
    hour: int
    minute: int
    second: int


@dataclass
class TimelineEventBrightness:
    time: Time
    bucket: Any  # TODO: extract out the type definition for this from the history compaction component


@dataclass
class TimelineEventEnergy:
    time: Time
    energy: float


@dataclass
class TimelineEventIntruder:
    time: Time
    intruder_alert: Any  # TODO: I think it should be a photo


TimelineEvent = Union[
    TimelineEventBrightness, TimelineEventEnergy, TimelineEventIntruder
]


@dataclass
class Date:
    year: int
    month: int
    day: int


@dataclass
class FromProxyToAggregationHistoryRequest:
    date: Date

    user_id: str


@dataclass
class FromAggregationToProxyHistory:
    timeline: list[TimelineEvent]

    user_id: str


# Interface 03
@dataclass
class FromHumanDetectionToActivityRecognition:
    images_of_humans: list[np.ndarray]


# Interface 04
@dataclass
class FromHumanDetectionToPersonIdentification:
    images_of_humans: list[np.ndarray]


# Interface 05
class Activity(Enum):
    # These numbers don’t matter; you just have to give enum variants a value
    WORKING = 0
    LYING = 1
    NEITHER = 2


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
LightEffect = Union[LightEffectDesiredBrightness, LightEffectForceEndBrightness]


@dataclass
class Timer:
    effect: LightEffect
    weekday: int  # 0 to 6
    hour: int  # 0 to 23
    minute: int  # 0 to 59


@dataclass
class Preferences:
    name: str
    timers: list[Timer]  # sorted by weekday, then day, then hour


@dataclass
class FromPreferencesToControl:
    "The preferences of all users in the system"

    preferences: dict[UserSlot, Preferences]


# Interface 08
FromProxyToPersonIdentification = Any

# Interface 09
@dataclass
class FromPersonIdentificationToProxy:
    "An intruder alert"

    image: Image
    timestamp: datetime


# Interface 10
@dataclass
class FromPersonIdentificationToAggregation:
    "An intruder alert"

    image: Image
    timestamp: datetime


# Interface 11
@dataclass
class FromControlToAggregationDutyCycle:
    duty_cycle: float


@dataclass
class FromControlToAggregationPower:
    watts: float


# Interface 12 is not defined here because it exists between the proxy and frontend,
# so the microcontroller application isn't involved at all


# Interface 13
@dataclass
class FromEnvironmentToHumanDetectionMotion:
    "Motion sensor state changes"

    new_state: bool  # motion detected is a binary yes/no


@dataclass
class FromEnvironmentToHumanDetectionOccupancy:
    "Occupancy sensor state changes"

    new_state: bool  # occupancy sensed is a binary yes/no


@dataclass
class FromEnvironmentToHumanDetectionCameraFrame:
    "Camera feed frames"

    frame: np.ndarray


# Interface 14
@dataclass
class FromEnvironmentToControl:
    ambient_brightness: float


# Interface 15
@dataclass
class FromEnvironmentToAggregation:
    "Camera feed frames"

    frame: np.ndarray


# Interface 16
@dataclass
class FromProxyToAggregationCameraFeedInterest:
    "Whether the given user wants to see the live camera feed anymore"

    wants_camera_feed: bool
    user_id: str


@dataclass
class FromProxyToAggregationRequestDutyCycle:
    "Request the current duty cycle of the lights"


@dataclass
class FromProxyToAggregationRecordTheCamera:
    "Whether or not the camera should record to the filesystem"

    should_record: bool
