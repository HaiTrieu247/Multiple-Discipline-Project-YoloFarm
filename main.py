"""
YoLo Farm – Flask web server entry point.
"""

import logging
import os
from flask import Flask, render_template
from communication.mqtt_client import connect as mqtt_connect
from controller import automation_engine
from web.routes import api

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
)

# ── Flask app ──
template_dir = os.path.join(os.path.dirname(__file__), "web", "templates")
app = Flask(__name__, template_folder=template_dir)
app.register_blueprint(api)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    mqtt_connect()
    automation_engine.start()
    app.run(host="0.0.0.0", port=5000, debug=True)