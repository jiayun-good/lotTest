import os
import json
from flask import Flask, request, jsonify, Response, abort

# Environment Configuration
DEVICE_NAME = os.environ.get("DEVICE_NAME", "test1")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "test1")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "test1")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "test1")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Mock device data storage (simulate in-memory data for /data endpoint)
DATA_POINTS = [
    {"timestamp": 1717939200, "value": 42, "unit": "test_unit"},
    {"timestamp": 1717939260, "value": 43, "unit": "test_unit"},
    {"timestamp": 1717939320, "value": 44, "unit": "test_unit"},
]

app = Flask(__name__)

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
        return jsonify({"error": "Payload must be in JSON format"}), 400
    cmd = request.get_json()
    # Simulate command execution and return the received command for demonstration
    result = {
        "status": "success",
        "received_command": cmd
    }
    return jsonify(result), 200

@app.route("/command", methods=["POST"])
def post_command():
    if not request.is_json:
        return jsonify({"error": "Payload must be in JSON format"}), 400
    cmd = request.get_json()
    # Simulate command execution and return the received command for demonstration
    result = {
        "status": "success",
        "received_command": cmd
    }
    return jsonify(result), 200

@app.route("/data", methods=["GET"])
def get_data():
    # Pagination and filtering support
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        if page < 1 or limit < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    start = (page - 1) * limit
    end = start + limit
    data_slice = DATA_POINTS[start:end]

    response = {
        "page": page,
        "limit": limit,
        "total": len(DATA_POINTS),
        "data": data_slice
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)