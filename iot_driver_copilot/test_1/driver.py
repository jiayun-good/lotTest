import os
import json
from flask import Flask, request, jsonify, Response, abort

app = Flask(__name__)

# Configuration from environment variables
DEVICE_NAME = os.environ.get("DEVICE_NAME", "test1")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "test1")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "test1")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "test1")
HTTP_HOST = os.environ.get("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8080"))

# Simulated device data and command execution (since protocol is 'test1')
DEVICE_DATA = [
    {"id": 1, "timestamp": "2024-06-01T12:00:00Z", "value": 123},
    {"id": 2, "timestamp": "2024-06-01T12:01:00Z", "value": 124},
    {"id": 3, "timestamp": "2024-06-01T12:02:00Z", "value": 125},
    {"id": 4, "timestamp": "2024-06-01T12:03:00Z", "value": 126},
    {"id": 5, "timestamp": "2024-06-01T12:04:00Z", "value": 127},
    {"id": 6, "timestamp": "2024-06-01T12:05:00Z", "value": 128},
    {"id": 7, "timestamp": "2024-06-01T12:06:00Z", "value": 129},
    {"id": 8, "timestamp": "2024-06-01T12:07:00Z", "value": 130},
    {"id": 9, "timestamp": "2024-06-01T12:08:00Z", "value": 131}
]
COMMAND_HISTORY = []

@app.route("/info", methods=["GET"])
def get_info():
    info = {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "device_type": DEVICE_TYPE
    }
    return jsonify(info), 200

@app.route("/cmd", methods=["POST"])
def post_cmd():
    if not request.is_json:
        return jsonify({"error": "Request payload must be JSON"}), 400
    cmd = request.get_json()
    # Simulate command execution
    result = {
        "status": "success",
        "executed_command": cmd,
        "message": f"Command executed on {DEVICE_NAME}"
    }
    COMMAND_HISTORY.append(cmd)
    return jsonify(result), 200

@app.route("/command", methods=["POST"])
def post_command():
    if not request.is_json:
        return jsonify({"error": "Request payload must be JSON"}), 400
    cmd = request.get_json()
    # Simulate command execution
    result = {
        "status": "success",
        "executed_command": cmd,
        "message": f"Command executed on {DEVICE_NAME}"
    }
    COMMAND_HISTORY.append(cmd)
    return jsonify(result), 200

@app.route("/data", methods=["GET"])
def get_data():
    # Handle pagination
    try:
        page = int(request.args.get("page", "1"))
        limit = int(request.args.get("limit", "5"))
    except ValueError:
        return jsonify({"error": "Invalid 'page' or 'limit' parameter"}), 400

    if page < 1 or limit < 1:
        return jsonify({"error": "'page' and 'limit' must be positive integers"}), 400

    start = (page - 1) * limit
    end = start + limit
    data_slice = DEVICE_DATA[start:end]
    total = len(DEVICE_DATA)
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "data": data_slice
    }), 200

if __name__ == "__main__":
    app.run(host=HTTP_HOST, port=HTTP_PORT)