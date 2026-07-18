"""
gpio_mock.py
------------
A drop-in mock of RPi.GPIO so this project runs on any machine (laptop, CI,
cloud sandbox) without real Raspberry Pi hardware attached.

HOW TO GO FROM DEMO -> REAL HARDWARE:
    Replace this import in sensors.py:
        from src.gpio_mock import GPIO
    with:
        import RPi.GPIO as GPIO
    Everything else (pin numbers, setup calls, read/write calls) is written
    against the real RPi.GPIO API, so no other code changes are required.
"""
import random
import time

BCM = "BCM"
OUT = "OUT"
IN = "IN"
HIGH = 1
LOW = 0


class GPIO:
    """Mimics the subset of RPi.GPIO used in this project."""

    _pin_states = {}
    _pin_modes = {}

    @classmethod
    def setmode(cls, mode):
        pass

    @classmethod
    def setwarnings(cls, flag):
        pass

    @classmethod
    def setup(cls, pin, mode):
        cls._pin_modes[pin] = mode
        cls._pin_states.setdefault(pin, LOW)

    @classmethod
    def output(cls, pin, value):
        cls._pin_states[pin] = value

    @classmethod
    def input(cls, pin):
        """
        Simulates a live sensor reading. In demo mode we return believable
        randomized values so the dashboard has real activity to show.
        A real Pi build would read actual voltage state from the pin here.
        """
        if pin in ("PIR_MOTION",):
            return HIGH if random.random() < 0.12 else LOW
        if pin in ("DOOR_REED",):
            return HIGH if random.random() < 0.04 else LOW
        return cls._pin_states.get(pin, LOW)

    @classmethod
    def cleanup(cls):
        cls._pin_states.clear()
        cls._pin_modes.clear()
