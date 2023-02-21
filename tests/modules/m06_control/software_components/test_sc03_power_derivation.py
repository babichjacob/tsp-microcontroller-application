"""
Unit test
Module: 06. Control
Component: 03. Power derivation
"""

from math import isclose

from microcontroller_application.modules.m06_control.software_components.sc03_power_derivation import (
    convert_duty_cycle_to_watts,
)


def test_power_derivation_mid_value_1():
    duty_cycle = 0.3

    watts = convert_duty_cycle_to_watts(duty_cycle)

    # TODO: update with newly found data
    assert isclose(watts, 4.25)


def test_power_derivation_mid_value_2():
    duty_cycle = 0.8

    watts = convert_duty_cycle_to_watts(duty_cycle)

    # TODO: update with newly found data
    assert isclose(watts, 8.4)


def test_power_derivation_low_value_0():
    "Ensure that the lower endpoint of the range (0.0) can be used"

    duty_cycle = 0.0

    watts = convert_duty_cycle_to_watts(duty_cycle)

    # TODO: update with newly found data
    assert isclose(watts, 0.0)


def test_power_derivation_high_value_1():
    "Ensure that the upper endpoint of the range (1.0) can be used"

    duty_cycle = 1.0

    watts = convert_duty_cycle_to_watts(duty_cycle)

    # TODO: update with newly found data
    assert isclose(watts, 10.0)


# TODO: test out of range values (<0 or >1)
