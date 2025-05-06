import os
import csv
import io
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# Device info (could be loaded from environment if needed)
DEVICE_INFO = {
    "device_name": os.getenv("DEVICE_NAME", "asd"),
    "device_model": os.getenv("DEVICE_MODEL", "sda"),
    "manufacturer": os.getenv("MANUFACTURER", "sad"),
    "device_type": os.getenv("DEVICE_TYPE", "asd"),
}

# Server config
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))

# Simulated device connection config for DSA protocol
DSA_DEVICE_IP = os.getenv("DSA_DEVICE_IP", "127.0.0.1")
DSA_DEVICE_PORT = int(os.getenv("DSA_DEVICE_PORT", "9001"))

# Simulated device state
DEVICE_STATE = {
    "status": "idle",
    "last_command": None
}

def get_device_data():
    """
    Simulate retrieving real-time CSV data from the device using DSA protocol.
    Replace this with actual device communication logic as needed.
    """
    # Simulate device data points
    data_points = [
        ["timestamp", "temperature", "humidity", "voltage"],
        ["2024-06-01T12:00:00Z", "25.4", "48.7", "3.7"],
        ["2024-06-01T12:00:01Z", "25.5", "49.0", "3.7"],
        ["2024-06-01T12:00:02Z", "25.7", "49.2", "3.6"],
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data_points)
    return output.getvalue()

def send_device_command(command):
    """
    Simulate sending a command to the device over DSA protocol.
    Replace with actual device command logic as needed.
    """
    # Acceptable commands for simulation: start, stop, diagnostic
    command = command.lower()
    if command not in ["start", "stop", "diagnostic"]:
        return False, "Unsupported command"
    DEVICE_STATE["last_command"] = command
    if command == "start":
        DEVICE_STATE["status"] = "running"
    elif command == "stop":
        DEVICE_STATE["status"] = "stopped"
    elif command == "diagnostic":
        DEVICE_STATE["status"] = "diagnostic"
    return True, f"Command '{command}' executed"

@app.route("/info", methods=["GET"])
def info():
    return jsonify({
        "device_name": DEVICE_INFO["device_name"],
        "device_model": DEVICE_INFO["device_model"],
        "manufacturer": DEVICE_INFO["manufacturer"],
        "device_type": DEVICE_INFO["device_type"],
        "status": DEVICE_STATE["status"],
        "last_command": DEVICE_STATE["last_command"]
    })

@app.route("/data", methods=["GET"])
def data():
    csv_data = get_device_data()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "inline; filename=device_data.csv"}
    )

@app.route("/cmd", methods=["POST"])
def cmd():
    req = request.get_json(force=True, silent=True)
    if not req or "command" not in req:
        return jsonify({"error": "Missing 'command' in request"}), 400
    success, msg = send_device_command(req["command"])
    if not success:
        return jsonify({"error": msg}), 400
    return jsonify({"result": msg, "status": DEVICE_STATE["status"]})

if __name__ == "__main__":
    app.run(host=HTTP_HOST, port=HTTP_PORT)