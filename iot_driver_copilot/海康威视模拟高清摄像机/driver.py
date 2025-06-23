import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load configuration from environment variables
DEVICE_NAME = os.environ.get("DEVICE_NAME", "海康威视模拟高清摄像机")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "DS-2CE16D0T-IRF")
MANUFACTURER = os.environ.get("MANUFACTURER", "海康威视")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "监控摄像机")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Key characteristics (mocked as this camera is analog, not IP-based)
CAMERA_CONFIG = {
    "resolution": "1920x1080 (1080P)",
    "infrared_range": "20m",
    "lens_options": ["2.8mm", "3.6mm", "6mm"],
    "protection_rating": "IP66",
    "video_output": "TVI",
    "power_input": "12V DC ±25%"
}

# Simulated operational state
CAMERA_STATUS = {
    "operational": True,
    "last_restart": None
}

@app.route("/camera/status", methods=["GET"])
def get_camera_status():
    status = {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": MANUFACTURER,
        "device_type": DEVICE_TYPE,
        "operational": CAMERA_STATUS["operational"],
        "last_restart": CAMERA_STATUS["last_restart"]
    }
    return jsonify(status)

@app.route("/camera/config", methods=["GET"])
def get_camera_config():
    # Filtering by query parameters if provided
    params = request.args
    if not params:
        return jsonify(CAMERA_CONFIG)
    filtered = {}
    for key in params:
        if key in CAMERA_CONFIG:
            filtered[key] = CAMERA_CONFIG[key]
    return jsonify(filtered)

@app.route("/cam/info", methods=["GET"])
def get_cam_info():
    info = {
        "device_model": DEVICE_MODEL,
        "manufacturer": MANUFACTURER,
        "device_type": DEVICE_TYPE,
        "characteristics": {
            "resolution": CAMERA_CONFIG["resolution"],
            "infrared_range": CAMERA_CONFIG["infrared_range"],
            "lens_options": CAMERA_CONFIG["lens_options"],
            "protection_rating": CAMERA_CONFIG["protection_rating"],
            "video_output": CAMERA_CONFIG["video_output"],
            "power_input": CAMERA_CONFIG["power_input"]
        }
    }
    return jsonify(info)

@app.route("/cam/config", methods=["GET"])
def get_cam_config():
    # Support filtering as in /camera/config
    params = request.args
    if not params:
        return jsonify(CAMERA_CONFIG)
    filtered = {}
    for key in params:
        if key in CAMERA_CONFIG:
            filtered[key] = CAMERA_CONFIG[key]
    return jsonify(filtered)

@app.route("/cam/restart", methods=["POST"])
@app.route("/commands/restart", methods=["POST"])
def restart_camera():
    # Simulate restart by setting operational to False then True, and set last_restart
    from datetime import datetime
    CAMERA_STATUS["operational"] = False
    CAMERA_STATUS["operational"] = True
    CAMERA_STATUS["last_restart"] = datetime.utcnow().isoformat() + "Z"
    return jsonify({"message": "Camera restart command issued.", "status": "restarting", "last_restart": CAMERA_STATUS["last_restart"]}), 200

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)