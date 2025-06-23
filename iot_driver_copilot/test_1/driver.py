import os
from flask import Flask, request, jsonify, Response, abort
import json
from threading import Lock

# Configuration from environment variables
DEVICE_IP = os.getenv("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.getenv("DEVICE_PORT", "8001"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

app = Flask(__name__)

# In-memory storage for device data and state simulation
device_state_lock = Lock()
device_data = {
    "temperature": 23.5,
    "humidity": 55,
    "status": "normal"
}
device_config = {}

@app.route("/cmd", methods=["POST"])
def send_command():
    """
    Send a command to the device for control or configuration.
    The command payload should be provided in JSON format.
    """
    if not request.is_json:
        return jsonify({"error": "Request payload must be JSON"}), 400

    cmd_payload = request.get_json()
    if not isinstance(cmd_payload, dict) or "command" not in cmd_payload:
        return jsonify({"error": "Missing 'command' in payload"}), 400

    command = cmd_payload["command"]
    params = cmd_payload.get("params", {})

    # Simulate command execution and update device config/state
    with device_state_lock:
        if command == "set_config":
            if not isinstance(params, dict):
                return jsonify({"error": "'params' must be a JSON object"}), 400
            device_config.update(params)
            return jsonify({"result": "Configuration updated", "device_config": device_config})
        elif command == "reset":
            device_config.clear()
            device_data.update({
                "temperature": 23.5,
                "humidity": 55,
                "status": "normal"
            })
            return jsonify({"result": "Device reset", "device_data": device_data})
        else:
            return jsonify({"error": f"Unknown command '{command}'"}), 400

@app.route("/data", methods=["GET"])
def get_data():
    """
    Retrieve current data points from the device.
    Supports query parameters for filtering and pagination if multiple data entries exist.
    """
    with device_state_lock:
        # Support filtering by query parameters
        filtered_data = device_data.copy()
        for key in request.args:
            if key in filtered_data:
                filtered_data = {key: filtered_data[key]}
            else:
                return jsonify({"error": f"Data point '{key}' not found"}), 404
        return Response(json.dumps(filtered_data), mimetype='application/json')

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)