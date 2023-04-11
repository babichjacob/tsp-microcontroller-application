"""
Module: 05. Preferences
This module is concerned with keeping track
of each trusted user’s lighting preferences.
"""

import bounded_channel

from microcontroller_application.interfaces.message_types import (
    FromPreferencesToControl,
    FromPreferencesToProxy,
    FromProxyToPreferences,
    LightEffectDesiredBrightness,
    LightEffectForceEndBrightness,
    Preferences,
    Timer,
    UserSlot,
)
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_proxy: bounded_channel.Receiver[FromProxyToPreferences],
    to_proxy: bounded_channel.Sender[FromPreferencesToProxy],
    to_control: bounded_channel.Sender[FromPreferencesToControl],
    use_demo_data: bool,
):
    "Run the preferences module"

    LOGGER.debug("startup")

    if use_demo_data:
        user_preferences = {
            UserSlot.TWO: Preferences(
                name="J / Jacob",
                timers=[
                    Timer(
                        effect=LightEffectDesiredBrightness(lumens=600),
                        weekday=0,
                        hour=0,
                        minute=0,
                    ),
                    Timer(
                        effect=LightEffectDesiredBrightness(lumens=300),
                        weekday=2,
                        hour=11,
                        minute=20,
                    ),
                    Timer(
                        effect=LightEffectForceEndBrightness(lumens=600),
                        weekday=2,
                        hour=11,
                        minute=30,
                    ),
                    Timer(
                        effect=LightEffectForceEndBrightness(lumens=0),
                        weekday=2,
                        hour=11,
                        minute=40,
                    ),
                    Timer(
                        effect=LightEffectDesiredBrightness(lumens=300),
                        weekday=2,
                        hour=11,
                        minute=50,
                    ),
                    Timer(
                        effect=LightEffectForceEndBrightness(lumens=300),
                        weekday=2,
                        hour=12,
                        minute=00,
                    ),
                    Timer(
                        effect=LightEffectDesiredBrightness(lumens=600),
                        weekday=2,
                        hour=13,
                        minute=20,
                    ),
                    Timer(
                        effect=LightEffectForceEndBrightness(lumens=0),
                        weekday=2,
                        hour=13,
                        minute=21,
                    ),
                    Timer(
                        effect=LightEffectDesiredBrightness(lumens=900),
                        weekday=2,
                        hour=13,
                        minute=22,
                    ),
                    Timer(
                        effect=LightEffectDesiredBrightness(lumens=300),
                        weekday=2,
                        hour=13,
                        minute=23,
                    ),
                ],
            )
        }

        (await to_control.send(FromPreferencesToControl(preferences=user_preferences))).unwrap()

    else:
        # TODO
        LOGGER.error("this hasn't been programmed yet, so it doesn't do anything")

    LOGGER.debug("shutdown")
