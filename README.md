# SENTRY — Home Automation & Security System

A Raspberry Pi–based home automation and security controller with a live web
dashboard, built in Python. It monitors motion, entry points, climate, and
smoke/gas levels, runs automation rules (armed-state alerting, dusk/dawn
lighting), and logs every event to SQLite.

**This repo runs standalone, with no Raspberry Pi required.** A mock GPIO
layer (`src/gpio_mock.py`) simulates realistic sensor data, so you can clone
it and see the full system working in under a minute. Swap one import to run
it on real hardware — see [`docs/architecture.md`](docs/architecture.md).


## Features

- **Live security dashboard** — arm/disarm, sensor status, event feed, all
  updating in real time in the browser.
- **Motion & entry detection** — PIR motion sensor and door/window reed
  switch, with alerting only when the system is armed.
- **Simulated camera capture** — a snapshot is generated automatically on an
  armed-motion event (swap for a real Pi camera module in production).
- **Climate monitoring** — temperature/humidity readings with a
  threshold-based warning.
- **Smoke/gas detection** — independent of the armed state, since safety
  alerts should never require the system to be armed.
- **Rule-based automation engine** — a background thread polls all sensors
  and applies rules (arming logic, dusk/dawn lighting schedule).
- **Persistent event log** — every reading and alert is stored in SQLite so
  history survives a restart.
- **Pluggable notifications** — console logging out of the box, with stub
  methods ready for email (SMTP) or SMS (Twilio) integration.

## Tech stack

`Python` · `Flask` · `SQLite` · `RPi.GPIO`-compatible mock layer · `Pillow`
· vanilla HTML/CSS/JS dashboard

## Quickstart

```bash
git clone https://github.com/<your-username>/home-automation-security.git
cd home-automation-security
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open **http://localhost:5000** — the dashboard updates every 2.5 seconds as
simulated sensors generate activity. Click **ARM SYSTEM** to see alerting
kick in on the next simulated motion or door event.

Run the test suite:

```bash
python3 tests/test_automation.py
```

## Project structure

```
home-automation-security/
├── app.py                  # Flask entry point + REST API
├── src/
│   ├── sensors.py          # Motion / door / climate / smoke sensor classes
│   ├── automation.py       # Rule engine + background polling loop
│   ├── camera.py           # Snapshot capture (simulated)
│   ├── notifier.py         # Alert dispatch (console, stubs for email/SMS)
│   ├── database.py         # SQLite event log + system state
│   └── gpio_mock.py        # RPi.GPIO-compatible mock for hardware-free demo
├── templates/               # Dashboard HTML
├── static/                  # Dashboard CSS/JS
├── tests/                   # Unit tests
├── docs/
│   └── architecture.md      # System diagram + demo-to-hardware guide
└── data/                     # SQLite DB + camera snapshots (gitignored)
```

See [`docs/architecture.md`](docs/architecture.md) for the full system
diagram and a table mapping each simulated component to the real hardware
part it stands in for.

## Roadmap

- [ ] Real hardware build on a Raspberry Pi 4 with PIR, reed switch, DHT22,
      and MQ-2 sensors
- [ ] Live camera feed via `picamera2`
- [ ] Email/SMS alerting wired up (SMTP / Twilio)
- [ ] Mobile-friendly PWA wrapper
- [ ] Multi-room support with per-zone arming

## License

MIT — see [LICENSE](LICENSE).
