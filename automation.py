"""
automation.py
-------------
Core rule engine. Runs as a background loop, polling sensors and reacting
according to the current system mode (armed / disarmed) and simple
time-based automation rules (e.g. lights schedule).
"""
import threading
import time
import datetime

from src.sensors import MotionSensor, DoorSensor, TempHumiditySensor, SmokeSensor
from src.camera import Camera
from src.notifier import Notifier
from src.database import log_event, set_state, get_state, init_db


class AutomationEngine:
    def __init__(self, poll_interval: float = 2.0):
        init_db()
        self.poll_interval = poll_interval
        self.motion = MotionSensor()
        self.door = DoorSensor()
        self.climate = TempHumiditySensor()
        self.smoke = SmokeSensor()
        self.camera = Camera()
        self.notifier = Notifier(channels=["console"])

        self._running = False
        self._thread = None

        if get_state("armed") is None:
            set_state("armed", "false")
        if get_state("lights") is None:
            set_state("lights", "off")

    # ---- public controls (called from the web API) ----
    def arm(self):
        set_state("armed", "true")
        log_event("system", "armed", "Security system armed", "info")

    def disarm(self):
        set_state("armed", "false")
        log_event("system", "disarmed", "Security system disarmed", "info")

    def is_armed(self) -> bool:
        return get_state("armed") == "true"

    def set_lights(self, on: bool):
        set_state("lights", "on" if on else "off")
        log_event("automation", "lights", f"Lights turned {'on' if on else 'off'}", "info")

    # ---- background loop ----
    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            self._check_security()
            self._check_environment()
            self._check_schedule()
            time.sleep(self.poll_interval)

    def _check_security(self):
        armed = self.is_armed()

        if self.motion.is_triggered():
            log_event("motion_sensor", "motion_detected", "Motion detected", "info")
            if armed:
                snapshot = self.camera.capture_snapshot(tag="motion")
                self.notifier.send(
                    "Intruder Alert",
                    f"Motion detected while armed. Snapshot saved: {snapshot}",
                    severity="critical",
                )

        if self.door.is_open():
            log_event("door_sensor", "door_open", f"{self.door.name} opened", "info")
            if armed:
                self.notifier.send(
                    "Door Alert",
                    f"{self.door.name} opened while system armed",
                    severity="critical",
                )

        if self.smoke.is_alarm():
            self.notifier.send(
                "Smoke Alarm",
                "Smoke/gas levels above safe threshold",
                severity="critical",
            )

    def _check_environment(self):
        reading = self.climate.read()
        log_event(
            "climate_sensor",
            "reading",
            f"{reading['temperature_c']}C, {reading['humidity_pct']}% humidity",
            "info",
        )
        # Simple automation: auto-note if it's too hot (a real build could
        # trigger a smart fan/AC relay here)
        if reading["temperature_c"] > 28:
            log_event("automation", "climate_warning", "Temperature above 28C", "warning")

    def _check_schedule(self):
        hour = datetime.datetime.now().hour
        should_be_on = hour >= 18 or hour < 6
        currently_on = get_state("lights") == "on"
        if should_be_on and not currently_on:
            self.set_lights(True)
        elif not should_be_on and currently_on:
            self.set_lights(False)
