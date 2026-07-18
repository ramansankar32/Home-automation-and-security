"""
app.py
------
Flask entry point. Serves the live dashboard and a small REST API for
arming/disarming, toggling lights, and reading recent events.

Run:
    python app.py
Then open http://localhost:5000
"""
from flask import Flask, render_template, jsonify, request

from src.automation import AutomationEngine
from src.database import recent_events, get_state

app = Flask(__name__)
engine = AutomationEngine(poll_interval=2.0)
engine.start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    return jsonify(
        {
            "armed": engine.is_armed(),
            "lights": get_state("lights"),
            "events": recent_events(limit=25),
        }
    )


@app.route("/api/arm", methods=["POST"])
def api_arm():
    engine.arm()
    return jsonify({"armed": True})


@app.route("/api/disarm", methods=["POST"])
def api_disarm():
    engine.disarm()
    return jsonify({"armed": False})


@app.route("/api/lights", methods=["POST"])
def api_lights():
    on = request.json.get("on", False)
    engine.set_lights(on)
    return jsonify({"lights": "on" if on else "off"})


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
