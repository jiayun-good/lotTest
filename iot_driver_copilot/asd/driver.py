import os
from flask import Flask, Response, jsonify, request, stream_with_context
import csv
import io
import threading
import time

# Get configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))  # Port for dsa protocol
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Device static information
DEVICE_INFO = {
    "device_name": "asd",
    "device_model": "sda",
    "manufacturer": "sad",
    "device_type": "asd"
}

# Simulated device data points and commands (for demonstration)
DATA_POINTS = [
    {"timestamp": int(time.time()), "value": 100, "status": "OK"},
    {"timestamp": int(time.time()) + 1, "value": 105, "status": "OK"},
    {"timestamp": int(time.time()) + 2, "value": 99, "status": "WARN"}
]

COMMANDS = ["START", "STOP", "DIAGNOSTIC"]

# Simulated device storage (thread-safe)
device_lock = threading.Lock()
device_state = {"running": False}

# Simulated raw DSA protocol connection and CSV stream
def connect_to_dsa_and_stream_csv():
    """
    Simulate a connection to a DSA protocol device and yield CSV rows as a stream.
    Replace this with actual protocol implementation as needed.
    """
    # Simulate real-time data
    while True:
        with device_lock:
            if not device_state["running"]:
                break
            data_point = {
                "timestamp": int(time.time()),
                "value": 100 + int(time.time()) % 10,
                "status": "OK" if int(time.time()) % 5 != 0 else "WARN"
            }
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "value", "status"])
        writer.writerow(data_point)
        yield output.getvalue()
        time.sleep(1)

app = Flask(__name__)

@app.route("/info", methods=["GET"])
def get_info():
    return jsonify(DEVICE_INFO)

@app.route("/data", methods=["GET"])
def get_data():
    stream = request.args.get("stream", "false").lower() == "true"
    if stream:
        def generate():
            # Stream real-time CSV data from device
            with device_lock:
                device_state["running"] = True
            try:
                # Write CSV header
                header_output = io.StringIO()
                writer = csv.DictWriter(header_output, fieldnames=["timestamp", "value", "status"])
                writer.writeheader()
                yield header_output.getvalue()
                for csv_row in connect_to_dsa_and_stream_csv():
                    yield csv_row
            finally:
                with device_lock:
                    device_state["running"] = False
        return Response(stream_with_context(generate()), mimetype="text/csv")
    else:
        # Return latest snapshot as CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "value", "status"])
        writer.writeheader()
        for dp in DATA_POINTS:
            writer.writerow(dp)
        return Response(output.getvalue(), mimetype="text/csv")

@app.route("/cmd", methods=["POST"])
def post_command():
    cmd = request.json.get("command", "").upper()
    if cmd not in COMMANDS:
        return jsonify({"status": "error", "message": "Unknown command"}), 400
    with device_lock:
        if cmd == "START":
            device_state["running"] = True
            result = {"status": "ok", "message": "Device started"}
        elif cmd == "STOP":
            device_state["running"] = False
            result = {"status": "ok", "message": "Device stopped"}
        elif cmd == "DIAGNOSTIC":
            # Simulate diagnostic info
            result = {"status": "ok", "message": "Diagnostic complete", "diagnostic": {"uptime": int(time.time()) % 1000, "errors": 0}}
        else:
            result = {"status": "ok", "message": f"Executed {cmd}"}
    return jsonify(result)

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)