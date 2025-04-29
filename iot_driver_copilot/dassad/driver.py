import os
from flask import Flask, jsonify

DEVICE_NAME = os.environ.get('DEVICE_NAME', 'dassad')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', 'das')
MANUFACTURER = os.environ.get('MANUFACTURER', 'sad')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', 'sad')
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

app = Flask(__name__)

@app.route('/info', methods=['GET'])
def get_info():
    return jsonify({
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": MANUFACTURER,
        "device_type": DEVICE_TYPE
    })

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT)