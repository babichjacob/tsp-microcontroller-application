"""
Module: 06. Control

Message types for channels ("interfaces") between components of this module
"""

from dataclasses import dataclass


@dataclass
class FromSynthesisToDutyCycle:
    "Current output light brightness in lumens"

    lumens: float


@dataclass
class FromDutyCycleToPowerDerivation:
    "Current output light duty cycle"

    duty_cycle: float
