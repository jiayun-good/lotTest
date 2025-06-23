import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Load environment variables for configuration
CAMERA_DEVICE_IP = os.getenv("CAMERA_DEVICE_IP", "127.0.0.1")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

# Device constants based on provided info
DEVICE_MODEL = "DS-2CE16D0T-IRF"
MANUFACTURER = "海康威视"
DEVICE_TYPE = "监控摄像机"
RESOLUTION = "1920×1080 (1080P)"
INFRARED_RANGE = "20米"
LENS_OPTIONS = ["2.8mm", "3.6mm", "6mm"]
PROTECTION_LEVEL = "IP66"
VIDEO_OUTPUT = "TVI"
POWER_INPUT = "12V DC ±25%"

# Simulated device status & config, since analog camera via TVI has no programmatic status/config
SIMULATED_STATUS = {
    "device_model": DEVICE_MODEL,
    "manufacturer": MANUFACTURER,
    "device_type": DEVICE_TYPE,
    "operational_state": "online",
    "connectivity": "reachable",
    "health": "OK"
}

SIMULATED_CONFIG = {
    "resolution": RESOLUTION,
    "infrared_range": INFRARED_RANGE,
    "lens_options": LENS_OPTIONS,
    "protection_level": PROTECTION_LEVEL,
    "video_output": VIDEO_OUTPUT,
    "power_input": POWER_INPUT
}

@app.route("/camera/status", methods=["GET"])
def camera_status():
    return jsonify(SIMULATED_STATUS), 200

@app.route("/camera/config", methods=["GET"])
def camera_config():
    # Optional filtering via query params
    q = request.args.get("q")
    if q:
        keys = [k for k in SIMULATED_CONFIG.keys() if q.lower() in k.lower()]
        filtered = {k: SIMULATED_CONFIG[k] for k in keys}
        return jsonify(filtered), 200
    return jsonify(SIMULATED_CONFIG), 200

@app.route("/cam/info", methods=["GET"])
def cam_info():
    # Detailed device information
    info = {
        "device_model": DEVICE_MODEL,
        "manufacturer": MANUFACTURER,
        "device_type": DEVICE_TYPE,
        "characteristics": {
            "resolution": RESOLUTION,
            "infrared_range": INFRARED_RANGE,
            "lens_options": LENS_OPTIONS,
            "protection_level": PROTECTION_LEVEL,
            "video_output": VIDEO_OUTPUT,
            "power_input": POWER_INPUT
        }
    }
    return jsonify(info), 200

@app.route("/cam/config", methods=["GET"])
def cam_config():
    # Supports query filtering
    q = request.args.get("q")
    if q:
        keys = [k for k in SIMULATED_CONFIG.keys() if q.lower() in k.lower()]
        filtered = {k: SIMULATED_CONFIG[k] for k in keys}
        return jsonify(filtered), 200
    return jsonify(SIMULATED_CONFIG), 200

@app.route("/cam/restart", methods=["POST"])
@app.route("/commands/restart", methods=["POST"])
def cam_restart():
    # Simulated restart (TVI analog camera can't be restarted via protocol)
    # Return success message
    response = {
        "message": "Restart command issued to camera (simulated for analog TVI device).",
        "success": True
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)