import os
import csv
import io
from flask import Flask, jsonify, Response, request, stream_with_context

app = Flask(__name__)

# Device info from environment variables (with defaults for testing)
DEVICE_NAME = os.environ.get("DEVICE_NAME", "asd")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "sda")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "sad")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "asd")
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "12345"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Dummy device backend for demonstration (replace with real device protocol handling)
def fetch_device_csv_data():
    # Simulate real-time data streaming from device in CSV format
    # In real case, connect to the device using its proprietary 'dsa' protocol
    # and yield CSV-formatted data rows as they arrive.
    # Here, just demonstrate streaming with static/dynamic data.
    fieldnames = ["timestamp", "value1", "value2"]
    yield ','.join(fieldnames) + '\n'
    import time
    import random
    for _ in range(1000):
        row = [str(int(time.time())), str(random.randint(0,100)), str(random.uniform(0,1))]
        yield ','.join(row) + '\n'
        time.sleep(0.1)  # Simulate data arrival

def send_command_to_device(command):
    # Simulate sending a command to the device and getting a result.
    # Here you'd implement the "dsa" protocol to send/receive commands.
    # For demonstration, return a mock response.
    return {"status": "success", "command": command}

@app.route("/info", methods=["GET"])
def get_device_info():
    info = {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "device_type": DEVICE_TYPE,
        "ip": DEVICE_IP,
        "port": DEVICE_PORT
    }
    return jsonify(info)

@app.route("/data", methods=["GET"])
def get_device_data():
    # Stream CSV data from device via HTTP
    return Response(stream_with_context(fetch_device_csv_data()), mimetype="text/csv")

@app.route("/cmd", methods=["POST"])
def post_command():
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400
    data = request.get_json()
    command = data.get("command")
    if not command:
        return jsonify({"error": "Missing 'command' in request body"}), 400
    result = send_command_to_device(command)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)