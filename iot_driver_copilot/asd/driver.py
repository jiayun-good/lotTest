import os
import csv
import io
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# Environment variable configuration
DEVICE_NAME = os.environ.get('DEVICE_NAME', 'asd')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', 'sda')
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', 'sad')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', 'asd')

SERVER_HOST = os.environ.get('HTTP_SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('HTTP_SERVER_PORT', 8080))

# DSA Device Configuration (all from env)
DSA_DEVICE_IP = os.environ.get('DSA_DEVICE_IP', '127.0.0.1')
DSA_DEVICE_PORT = int(os.environ.get('DSA_DEVICE_PORT', 9000))

# Simulated device data and command handling for demo purposes
def get_device_data():
    # This function should connect to the DSA device and retrieve real-time data in CSV format.
    # Here, we simulate the data as an example. Replace with real device integration.
    data_points = [
        ['timestamp', 'temperature', 'humidity'],
        ['2024-06-10T12:00:00Z', '23.5', '45.1'],
        ['2024-06-10T12:01:00Z', '23.6', '44.9'],
        ['2024-06-10T12:02:00Z', '23.7', '44.7']
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data_points)
    return output.getvalue()

def send_device_command(command):
    # This function should connect to the DSA device and send the command.
    # Here, we simulate the response as an example. Replace with real device integration.
    return {'status': 'success', 'command': command}

@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        'device_name': DEVICE_NAME,
        'device_model': DEVICE_MODEL,
        'manufacturer': DEVICE_MANUFACTURER,
        'device_type': DEVICE_TYPE,
        'status': 'online'
    })

@app.route('/data', methods=['GET'])
def data():
    # Get live device data in CSV format and stream as HTTP text/csv
    csv_data = get_device_data()
    return Response(csv_data, mimetype='text/csv')

@app.route('/cmd', methods=['POST'])
def cmd():
    cmd_data = request.get_json(silent=True)
    if not cmd_data or 'command' not in cmd_data:
        return jsonify({'status': 'error', 'message': 'Missing command'}), 400
    result = send_device_command(cmd_data['command'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT)