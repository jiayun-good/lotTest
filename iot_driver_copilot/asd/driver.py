import os
import csv
from io import StringIO
from flask import Flask, jsonify, Response, request, abort

# Device configuration from environment variables
DEVICE_NAME = os.environ.get('DEVICE_NAME', 'asd')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', 'sda')
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', 'sad')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', 'asd')

SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Simulate device data and commands for illustration
def get_device_data():
    # Example CSV data as list of dicts (simulate real device data retrieval)
    data_points = [
        {'timestamp': '2024-01-01T00:00:00Z', 'value': '123', 'status': 'OK'},
        {'timestamp': '2024-01-01T00:00:01Z', 'value': '124', 'status': 'OK'},
        {'timestamp': '2024-01-01T00:00:02Z', 'value': '125', 'status': 'WARN'},
    ]
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data_points[0].keys())
    writer.writeheader()
    for d in data_points:
        writer.writerow(d)
    return output.getvalue()

def send_device_command(command):
    # Simulate sending a command to the device and returning status
    valid_commands = ['start', 'stop', 'diagnostic']
    if command in valid_commands:
        return {'status': 'success', 'command': command}
    else:
        return {'status': 'error', 'message': 'Unknown command'}

app = Flask(__name__)

@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        'device_name': DEVICE_NAME,
        'device_model': DEVICE_MODEL,
        'manufacturer': DEVICE_MANUFACTURER,
        'device_type': DEVICE_TYPE
    })

@app.route('/data', methods=['GET'])
def data():
    csv_data = get_device_data()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'inline; filename="device_data.csv"'}
    )

@app.route('/cmd', methods=['POST'])
def cmd():
    if not request.is_json:
        abort(400, description="Request must be JSON")
    req_json = request.get_json()
    command = req_json.get('command')
    if not command:
        abort(400, description="Missing 'command' in request body")
    result = send_device_command(command)
    if result.get('status') == 'error':
        return jsonify(result), 400
    return jsonify(result)

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT)