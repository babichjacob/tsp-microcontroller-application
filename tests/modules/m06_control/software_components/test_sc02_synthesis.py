from datetime import datetime

from microcontroller_application.modules.m06_control.software_components.sc02_synthesis import (
    calculate_synthesized_light_brightness,
)


def test_nobody_is_there_and_no_preferences_forcing_light_on_1():
    """
    When nobody is in the room,
    and there are no preferences that force the light to be on now,
    even if nobody is home,
    then the lights should be off
    """

    calculation = calculate_synthesized_light_brightness(
        activities=[],
        ambient_light_lumens=0,
        now=datetime.now(),
        people_in_room=[],
        user_preferences={},
    )

    assert calculation == 0


def test_nobody_is_there_and_no_preferences_forcing_light_on_2():
    """
    When nobody is in the room,
    and there are no preferences that force the light to be on now,
    even if nobody is home,
    then the lights should be off
    """

    calculation = calculate_synthesized_light_brightness(
        activities=[],
        ambient_light_lumens=300,
        now=datetime.now(),
        people_in_room=[],
        user_preferences={},
    )

    assert calculation == 0


def test_nobody_is_there_and_no_preferences_forcing_light_on_3():
    """
    When nobody is in the room,
    and there are no preferences that force the light to be on now,
    even if nobody is home,
    then the lights should be off
    """

    calculation = calculate_synthesized_light_brightness(
        activities=[],
        ambient_light_lumens=900,
        now=datetime.now(),
        people_in_room=[],
        user_preferences={},
    )

    assert calculation == 0
