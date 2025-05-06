import os
import json
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Environment Variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "12345"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
DEVICE_NAME = os.environ.get("DEVICE_NAME", "asdads")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "ads")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "asddas")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "asd")
DEVICE_PROTOCOL = os.environ.get("DEVICE_PROTOCOL", "asd")
DATA_POINTS = os.environ.get("DATA_POINTS", "asd")
COMMANDS = os.environ.get("COMMANDS", "dsa")

# Simulate device communication for demonstration.
import socket

def fetch_device_data():
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(b'GET_DATA\n')
            data = s.recv(4096)
            return data.decode('utf-8')
    except Exception as e:
        return json.dumps({"error": str(e)})

def send_device_command(cmd_payload):
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(b'CMD:' + json.dumps(cmd_payload).encode('utf-8') + b'\n')
            data = s.recv(4096)
            return data.decode('utf-8')
    except Exception as e:
        return json.dumps({"error": str(e)})

@app.route("/info", methods=["GET"])
def device_info():
    info = {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "device_type": DEVICE_TYPE,
        "connection_protocol": DEVICE_PROTOCOL
    }
    return jsonify(info)

@app.route("/data", methods=["GET"])
def device_data():
    raw = fetch_device_data()
    try:
        data = json.loads(raw)
    except Exception:
        data = {"raw": raw}
    return jsonify(data)

@app.route("/cmd", methods=["POST"])
def device_command():
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "Invalid command payload"}), 400
    result = send_device_command(payload)
    try:
        resp = json.loads(result)
    except Exception:
        resp = {"raw": result}
    return jsonify(resp)

@app.route("/stream", methods=["GET"])
def device_stream():
    def stream_generator():
        try:
            with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
                s.sendall(b'STREAM\n')
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            yield json.dumps({"error": str(e)}).encode('utf-8')
    return Response(stream_generator(), mimetype="application/octet-stream")

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)