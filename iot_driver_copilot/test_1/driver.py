import os
import json
from flask import Flask, request, jsonify, Response, abort

app = Flask(__name__)

# Load device configuration from environment variables
DEVICE_NAME = os.getenv("DEVICE_NAME", "test1")
DEVICE_MODEL = os.getenv("DEVICE_MODEL", "test1")
DEVICE_MANUFACTURER = os.getenv("DEVICE_MANUFACTURER", "test1")
DEVICE_TYPE = os.getenv("DEVICE_TYPE", "test1")
HTTP_SERVER_HOST = os.getenv("HTTP_SERVER_HOST", "0.0.0.0")
HTTP_SERVER_PORT = int(os.getenv("HTTP_SERVER_PORT", "8080"))

# Simulated in-memory device state and datapoints
device_state = {
    "status": "online",
    "last_command": None,
    "data_points": [
        {"id": 1, "timestamp": "2024-06-10T10:00:00Z", "value": 42.0},
        {"id": 2, "timestamp": "2024-06-10T10:01:00Z", "value": 43.5},
        {"id": 3, "timestamp": "2024-06-10T10:02:00Z", "value": 41.8},
    ]
}

def paginate_data(data, page, limit):
    start = (page - 1) * limit
    end = start + limit
    return data[start:end]

@app.route("/info", methods=["GET"])
def info():
    info = {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "device_type": DEVICE_TYPE,
        "status": device_state["status"]
    }
    return jsonify(info)

@app.route("/cmd", methods=["POST"])
def cmd():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400
    # Simulate command processing
    device_state["last_command"] = payload
    resp = {
        "result": "success",
        "received_command": payload
    }
    return jsonify(resp)

@app.route("/command", methods=["POST"])
def command():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400
    # Simulate command handling
    device_state["last_command"] = payload
    resp = {
        "result": "success",
        "received_command": payload
    }
    return jsonify(resp)

@app.route("/data", methods=["GET"])
def get_data():
    # Pagination and filtering
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
    except Exception:
        return jsonify({"error": "Invalid page or limit parameter"}), 400

    data = device_state["data_points"]
    paged = paginate_data(data, page, limit)
    result = {
        "page": page,
        "limit": limit,
        "total": len(data),
        "data": paged
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host=HTTP_SERVER_HOST, port=HTTP_SERVER_PORT)