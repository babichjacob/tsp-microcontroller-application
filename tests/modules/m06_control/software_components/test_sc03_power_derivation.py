from math import isclose

from microcontroller_application.modules.m06_control.software_components.sc03_power_derivation import (
    convert_duty_cycle_to_watts,
)


def test_power_derivation_1():
    output_dc = 0.3

    output_w = convert_duty_cycle_to_watts(output_dc)

    # TODO: update with newly found data
    assert isclose(output_w, 4.25)


def test_power_derivation_2():
    output_dc = 0.8

    output_w = convert_duty_cycle_to_watts(output_dc)

    # TODO: update with newly found data
    assert isclose(output_w, 8.4)
