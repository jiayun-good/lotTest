import os
import json
from flask import Flask, request, jsonify, Response
from functools import wraps

# --- Device SDK Communication Layer (Simulated/Stub for this driver) ---
# In real deployment, this would use the Hikvision HCNetSDK Python bindings or a proper SDK wrapper.
# Here, we simulate device communication for demonstration.

class HikvisionAlarmHost:
    def __init__(self, ip, port, username, password):
        self.device_ip = ip
        self.device_port = port
        self.username = username
        self.password = password
        # Simulate device connection/session
        self.session = True

    def get_status(self):
        # Simulate device status response
        return {
            "alarm_state": "normal",
            "zones": [
                {"id": 1, "status": "armed"},
                {"id": 2, "status": "bypassed"},
                {"id": 3, "status": "alarm"}
            ],
            "battery_voltage": 12.7,
            "sensors": {
                "water": "dry",
                "dust": "normal",
                "noise": 32.4,
                "environmental": {"temp": 23.1, "humidity": 45.2}
            }
        }

    def clear_alarm(self):
        # Simulate clearing alarms
        return {"result": "success", "message": "Alarms cleared"}

    def manage_subsystem(self, subsystem_id, action):
        # Simulate arm/disarm/clear alarm for subsystems
        allowed_actions = ["arm", "disarm", "clear"]
        if action not in allowed_actions:
            return {"result": "error", "message": "Invalid action"}
        return {"result": "success", "subsystem_id": subsystem_id, "action": action}

    def bypass_zone(self, zone_id, bypass=True):
        return {
            "result": "success",
            "zone_id": zone_id,
            "bypassed": bypass
        }

# --- Flask App Initialization ---

def get_env_var(key, default=None, required=False):
    val = os.environ.get(key, default)
    if required and val is None:
        raise RuntimeError(f"Environment variable {key} is required.")
    return val

app = Flask(__name__)

# --- Environment Configuration ---

DEVICE_IP = get_env_var("DEVICE_IP", required=True)
DEVICE_PORT = int(get_env_var("DEVICE_PORT", 8000))
DEVICE_USERNAME = get_env_var("DEVICE_USERNAME", "admin")
DEVICE_PASSWORD = get_env_var("DEVICE_PASSWORD", "12345")

SERVER_HOST = get_env_var("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(get_env_var("SERVER_PORT", 8080))

# --- Device Session Instance ---
device = HikvisionAlarmHost(DEVICE_IP, DEVICE_PORT, DEVICE_USERNAME, DEVICE_PASSWORD)

# --- API Helpers ---

def json_content_type(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        resp = f(*args, **kwargs)
        if isinstance(resp, Response):
            return resp
        return Response(
            json.dumps(resp, ensure_ascii=False),
            mimetype='application/json'
        )
    return decorated

# --- API Endpoints ---

@app.route("/status", methods=["GET"])
@json_content_type
def get_status():
    status = device.get_status()
    return status

@app.route("/alarm/clear", methods=["POST"])
@json_content_type
def clear_alarm():
    result = device.clear_alarm()
    return result

@app.route("/subsys", methods=["POST"])
@json_content_type
def manage_subsystem():
    data = request.get_json(force=True)
    subsystem_id = data.get("subsystem_id")
    action = data.get("action")
    if subsystem_id is None or action is None:
        return {"result": "error", "message": "Missing subsystem_id or action"}, 400
    result = device.manage_subsystem(subsystem_id, action)
    return result

@app.route("/zone/bypass", methods=["POST"])
@json_content_type
def bypass_zone():
    data = request.get_json(force=True)
    zone_id = data.get("zone_id")
    bypass = data.get("bypass", True)
    if zone_id is None:
        return {"result": "error", "message": "Missing zone_id"}, 400
    result = device.bypass_zone(zone_id, bypass)
    return result

# --- Main Entrypoint ---

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)