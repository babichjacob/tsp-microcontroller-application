"""
Module: 07. Lighting
Component: 02x. Dimmer connector
"""

import bounded_channel

from microcontroller_application.interfaces.message_types import \
    FromControlToLighting
from microcontroller_application.log import get_logger

LOGGER = get_logger(__name__)


async def run(
    *,
    from_control: bounded_channel.Receiver[FromControlToLighting],
    use_real_hardware: bool
):
    LOGGER.debug("startup")

    if use_real_hardware:
        import RPi.GPIO as GPIO

        # Initialize PWM
        pwm_pin = 17
        GPIO.setup(pwm_pin, GPIO.OUT)
        pwm = GPIO.PWM(pwm_pin, 600)

        async for message in from_control:
            duty_cycle = message.duty_cycle * 100

            LOGGER.info("setting light to %f%%", duty_cycle)
            pwm.start(duty_cycle)

    else:
        LOGGER.warning("not outputting to the actual dimmer hardware")

        async for message in from_control:
            duty_cycle = message.duty_cycle

            LOGGER.info("(DRY RUN) setting light to %f", duty_cycle)

    LOGGER.debug("shutdown")
