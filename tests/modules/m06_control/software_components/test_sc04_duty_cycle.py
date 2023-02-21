from math import isclose

from microcontroller_application.modules.m06_control.software_components.sc04_duty_cycle import (
    convert_lumens_to_duty_cycle,
)


def test_duty_cycle_mid_value_1():
    output_lumens = 350

    output_dc = convert_lumens_to_duty_cycle(output_lumens)

    # TODO: update with newly found data
    assert isclose(output_dc, 0.4)
