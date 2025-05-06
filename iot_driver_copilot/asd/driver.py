import os
import csv
import io
from flask import Flask, jsonify, Response, request, abort

# Configuration from environment variables
DEVICE_NAME = os.environ.get("DEVICE_NAME", "asd")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "sda")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "sad")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "asd")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
DSA_DEVICE_IP = os.environ.get("DSA_DEVICE_IP", "127.0.0.1")
DSA_DEVICE_PORT = int(os.environ.get("DSA_DEVICE_PORT", "9000"))

# Simulate device data and command interface (as 'dsa' protocol is unspecified)
class DSASimulator:
    def __init__(self):
        self.data_points = [
            {"timestamp": "2024-01-01T00:00:00Z", "value": 100},
            {"timestamp": "2024-01-01T00:01:00Z", "value": 105},
            {"timestamp": "2024-01-01T00:02:00Z", "value": 110},
        ]
        self.commands = []

    def get_info(self):
        return {
            "device_name": DEVICE_NAME,
            "device_model": DEVICE_MODEL,
            "manufacturer": DEVICE_MANUFACTURER,
            "device_type": DEVICE_TYPE,
        }

    def get_data_csv(self):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "value"])
        writer.writeheader()
        for row in self.data_points:
            writer.writerow(row)
        return output.getvalue()

    def execute_command(self, cmd):
        self.commands.append(cmd)
        return {"result": "success", "command": cmd}

dsa_device = DSASimulator()

app = Flask(__name__)

@app.route("/info", methods=["GET"])
def get_info():
    return jsonify(dsa_device.get_info())

@app.route("/data", methods=["GET"])
def get_data():
    csv_data = dsa_device.get_data_csv()
    return Response(csv_data, mimetype='text/csv')

@app.route("/cmd", methods=["POST"])
def post_cmd():
    if not request.is_json:
        abort(400, description="Request must be JSON")
    content = request.get_json()
    if "command" not in content:
        abort(400, description="Missing 'command' in JSON body")
    result = dsa_device.execute_command(content["command"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)