"""
camera.py
---------
Simulated security camera. On a real Pi, replace capture_snapshot() with
picamera2 or OpenCV VideoCapture(0) to grab a real frame.
"""
import os
import time
import random

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "snapshots")


class Camera:
    def __init__(self):
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    def capture_snapshot(self, tag: str = "motion") -> str:
        """Generates a placeholder 'captured frame' image with a timestamp
        overlay, standing in for a real camera capture in demo mode."""
        filename = f"{tag}_{int(time.time())}.png"
        filepath = os.path.join(SNAPSHOT_DIR, filename)

        if PIL_AVAILABLE:
            color = random.choice([(40, 44, 52), (30, 60, 80), (50, 30, 60)])
            img = Image.new("RGB", (320, 240), color=color)
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), f"SIMULATED CAPTURE\n{tag}", fill=(255, 255, 255))
            draw.text((10, 210), time.strftime("%Y-%m-%d %H:%M:%S"), fill=(200, 200, 200))
            img.save(filepath)
        else:
            with open(filepath, "w") as f:
                f.write("placeholder snapshot (PIL not installed)")

        return filepath
