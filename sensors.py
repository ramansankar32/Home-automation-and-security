"""
sensors.py
----------
Sensor abstractions for the home automation & security system.

In DEMO mode, gpio_mock.GPIO generates realistic simulated readings.
On a real Raspberry Pi, swap the import below for RPi.GPIO and wire:
    PIR motion sensor  -> GPIO pin (BCM 17 default)
    Door/window reed   -> GPIO pin (BCM 27 default)
    DHT22 temp/humidity-> GPIO pin (BCM 4 default)
    MQ-2 smoke sensor  -> GPIO/ADC pin (BCM 22 default)
"""
import random
import time

from src.gpio_mock import GPIO, BCM, IN, HIGH


PIN_MOTION = "PIR_MOTION"
PIN_DOOR = "DOOR_REED"


class MotionSensor:
    def __init__(self, pin=PIN_MOTION):
        self.pin = pin
        GPIO.setup(self.pin, IN)

    def is_triggered(self) -> bool:
        return GPIO.input(self.pin) == HIGH


class DoorSensor:
    def __init__(self, pin=PIN_DOOR, name="Front Door"):
        self.pin = pin
        self.name = name
        GPIO.setup(self.pin, IN)

    def is_open(self) -> bool:
        return GPIO.input(self.pin) == HIGH


class TempHumiditySensor:
    """Simulated DHT22 reading. Swap for adafruit_dht on real hardware."""

    def __init__(self):
        self._base_temp = 23.5
        self._base_humidity = 45.0

    def read(self):
        temp = round(self._base_temp + random.uniform(-1.5, 1.5), 1)
        humidity = round(self._base_humidity + random.uniform(-5, 5), 1)
        return {"temperature_c": temp, "humidity_pct": humidity}


class SmokeSensor:
    """Simulated MQ-2 gas/smoke sensor. Returns ppm-like value."""

    def read_level(self) -> int:
        # Rare spike to simulate a smoke event for demo purposes
        if random.random() < 0.01:
            return random.randint(300, 600)
        return random.randint(5, 40)

    def is_alarm(self) -> bool:
        return self.read_level() > 250
