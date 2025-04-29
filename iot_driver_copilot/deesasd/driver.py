import os
from flask import Flask, request, Response, jsonify, stream_with_context
import threading
import queue
import time

# Mock device protocol API for demonstration (replace with actual protocol handler)
class DeesasdDevice:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.running = True

    def get_data_points(self):
        # Simulate fetching data from device
        return {
            "temperature": 23.5,
            "humidity": 60,
            "device_status": "OK"
        }

    def process_command(self, cmd_payload):
        # Simulate device command processing
        if not isinstance(cmd_payload, dict):
            return {"success": False, "error": "Payload must be a dict"}
        # Process the command here
        return {"success": True, "result": cmd_payload}

    def stream_data(self):
        # Simulate a continuous stream of device data
        while self.running:
            yield f"data: {self.get_data_points()}\n\n"
            time.sleep(1)

# Environment variable configuration
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

app = Flask(__name__)
device = DeesasdDevice(DEVICE_IP, DEVICE_PORT)

stream_clients = []

@app.route("/data", methods=["GET"])
def get_data():
    accept = request.headers.get("Accept", "")
    if "text/event-stream" in accept:
        def event_stream():
            for line in device.stream_data():
                yield line
        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")
    else:
        # Return a snapshot of device data in JSON
        data = device.get_data_points()
        return jsonify(data), 200

@app.route("/cmd", methods=["POST"])
def send_command():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
    result = device.process_command(payload)
    return jsonify(result), 200 if result.get("success") else 400

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)