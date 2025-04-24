import os
import json
from flask import Flask, request, jsonify
from threading import Lock

app = Flask(__name__)

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "8000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "5000"))

# Simulated shared state (normally would be maintained by device responses)
device_state = {
    "subsystems": {
        "1": {"status": "disarmed"},
        "2": {"status": "armed"}
    },
    "alarms": [],
    "zones": {
        "1": {"bypassed": False},
        "2": {"bypassed": False},
        "3": {"bypassed": False}
    },
    "sensors": {
        "water": 0,
        "dust": 0,
        "noise": 0,
        "environmental": {}
    },
    "battery_voltage": 12.6
}
state_lock = Lock()

@app.route("/subsys", methods=["POST"])
def manage_subsystem():
    data = request.get_json(force=True)
    subsystem_id = data.get("subsystem_id")
    action = data.get("action")
    if not subsystem_id or not action:
        return jsonify({"error": "subsystem_id and action are required"}), 400

    with state_lock:
        if subsystem_id not in device_state["subsystems"]:
            return jsonify({"error": "Invalid subsystem_id"}), 404

        if action not in ("arm", "disarm", "clear_alarm"):
            return jsonify({"error": "Action must be one of: arm, disarm, clear_alarm"}), 400

        if action == "arm":
            device_state["subsystems"][subsystem_id]["status"] = "armed"
        elif action == "disarm":
            device_state["subsystems"][subsystem_id]["status"] = "disarmed"
        elif action == "clear_alarm":
            before = len(device_state["alarms"])
            device_state["alarms"] = [a for a in device_state["alarms"] if a.get("subsystem_id") != subsystem_id]
            after = len(device_state["alarms"])
            device_state["subsystems"][subsystem_id]["status"] = "disarmed"

    return jsonify({"result": "ok", "subsystem_id": subsystem_id, "action": action})

@app.route("/alarm/clear", methods=["POST"])
def clear_alarms():
    with state_lock:
        cleared = len(device_state["alarms"])
        device_state["alarms"].clear()
        for s in device_state["subsystems"].values():
            s["status"] = "disarmed"
    return jsonify({"result": "ok", "cleared": cleared})

@app.route("/status", methods=["GET"])
def get_status():
    with state_lock:
        status = {
            "alarm_state": "active" if device_state["alarms"] else "clear",
            "alarms": list(device_state["alarms"]),
            "subsystems": device_state["subsystems"],
            "zones": device_state["zones"],
            "sensors": device_state["sensors"],
            "battery_voltage": device_state["battery_voltage"]
        }
    return jsonify(status)

@app.route("/zone/bypass", methods=["POST"])
def zone_bypass():
    data = request.get_json(force=True)
    zone_id = data.get("zone_id")
    action = data.get("action")
    if not zone_id or not action:
        return jsonify({"error": "zone_id and action are required"}), 400

    with state_lock:
        if zone_id not in device_state["zones"]:
            return jsonify({"error": "Invalid zone_id"}), 404
        if action not in ("bypass", "reinstate"):
            return jsonify({"error": "Action must be one of: bypass, reinstate"}), 400

        if action == "bypass":
            device_state["zones"][zone_id]["bypassed"] = True
        elif action == "reinstate":
            device_state["zones"][zone_id]["bypassed"] = False

    return jsonify({"result": "ok", "zone_id": zone_id, "bypassed": device_state["zones"][zone_id]["bypassed"]})

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)