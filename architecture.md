# Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Raspberry Pi Node                        │
│                                                                   │
│   ┌──────────────┐   ┌──────────────────┐   ┌─────────────────┐  │
│   │   Sensors     │   │  Automation       │   │   Notifier      │  │
│   │  (sensors.py) │──▶│  Engine           │──▶│  (notifier.py)  │  │
│   │               │   │  (automation.py)  │   │                 │  │
│   │ • PIR motion  │   │                   │   │ • console (demo)│  │
│   │ • Door reed   │   │ Poll loop every   │   │ • email (stub)  │  │
│   │ • DHT22 temp  │   │ N sec, evaluate   │   │ • SMS (stub)    │  │
│   │ • MQ-2 smoke  │   │ rules, log events │   │                 │  │
│   └───────┬───────┘   └─────────┬─────────┘   └────────┬────────┘  │
│           │                     │                       │          │
│           ▼                     ▼                       ▼          │
│   ┌──────────────┐   ┌──────────────────┐   ┌─────────────────┐  │
│   │  gpio_mock.py │   │   database.py     │   │   camera.py     │  │
│   │ (swap for     │   │   SQLite events   │   │  snapshot on    │  │
│   │  RPi.GPIO)    │   │   + system state  │   │  motion+armed   │  │
│   └──────────────┘   └─────────┬─────────┘   └─────────────────┘  │
│                                 │                                   │
└─────────────────────────────────┼───────────────────────────────────┘
                                  ▼
                        ┌──────────────────┐
                        │   Flask app.py     │
                        │   REST API +        │
                        │   live dashboard     │
                        └─────────┬───────────┘
                                  ▼
                        ┌──────────────────┐
                        │  Browser dashboard │
                        │  (polls /api/status │
                        │   every 2.5s)        │
                        └──────────────────┘
```

## Components

- **sensors.py** — Thin classes over GPIO reads: `MotionSensor`, `DoorSensor`,
  `TempHumiditySensor`, `SmokeSensor`.
- **gpio_mock.py** — Drop-in stand-in for `RPi.GPIO`. Generates plausible
  simulated readings so the whole system runs on a laptop, in CI, or in a
  cloud sandbox. Swapping one import line switches to real hardware.
- **automation.py** — `AutomationEngine` runs a background thread that polls
  sensors on an interval, applies rules (arm/disarm logic, alerting, a basic
  dusk/dawn lighting schedule, temperature threshold check), and writes
  everything to the database.
- **camera.py** — Captures a snapshot on an armed-motion event. Simulated
  with Pillow-generated placeholder frames; swap for `picamera2` or OpenCV
  on real hardware.
- **notifier.py** — Single `send()` entry point; demo mode logs to console
  and DB. Stubs are included for email (`smtplib`) and SMS (Twilio) so
  real alerting is a small addition, not a redesign.
- **database.py** — SQLite persistence for the event log and system state
  (armed/disarmed, lights on/off), so state survives restarts.
- **app.py** — Flask REST API (`/api/status`, `/api/arm`, `/api/disarm`,
  `/api/lights`) plus the dashboard template.

## Data flow

1. `AutomationEngine._loop()` runs every `poll_interval` seconds.
2. It reads each sensor, logs raw readings, and applies rules.
3. Rule violations (e.g. motion while armed) call `Notifier.send()`, which
   logs a `critical` severity event and (in a real deployment) fires an
   email/SMS.
4. The dashboard polls `/api/status` and renders the latest state and the
   most recent 25 events.

## Moving from demo to real hardware

| Component        | Demo (this repo)         | Real Raspberry Pi                          |
|-------------------|---------------------------|---------------------------------------------|
| GPIO              | `gpio_mock.GPIO`          | `RPi.GPIO`                                   |
| Motion sensor     | Randomized simulation     | PIR sensor on BCM 17                         |
| Door sensor       | Randomized simulation     | Reed switch on BCM 27                        |
| Temp/humidity     | Randomized simulation     | DHT22 via `adafruit-circuitpython-dht`       |
| Camera            | Pillow placeholder image  | `picamera2` or `cv2.VideoCapture(0)`         |
| Notifications     | Console log                | SMTP email / Twilio SMS (stubs provided)     |
