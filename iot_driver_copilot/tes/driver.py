import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Environment Variables
DEVICE_IP = os.getenv('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.getenv('DEVICE_PORT', '9000'))
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '8080'))

# "Fake" device logic (simulate protocol "ttt" and XML return)
def fetch_device_info():
    info = {
        "device_name": "tes",
        "device_model": "tt",
        "manufacturer": "ttt",
        "device_type": "ttt",
        "connection_protocol": "ttt"
    }
    return info

def run_device_test():
    # Simulate a device test result
    return {"result": "success", "message": "Device connectivity and command processing OK."}

def fetch_device_data():
    # Simulate fetching XML-formatted data from the device
    root = ET.Element('DeviceData')
    datapoint = ET.SubElement(root, 'DataPoint')
    datapoint.text = "42"
    status = ET.SubElement(root, 'Status')
    status.text = "OK"
    return ET.tostring(root, encoding='utf-8', method='xml')

# HTTP Server Handler
class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers(200, 'application/json')
            info = fetch_device_info()
            self.wfile.write(bytes(str(info).replace("'", '"'), 'utf-8'))
        elif self.path == '/data':
            xml_data = fetch_device_data()
            self._set_headers(200, 'application/xml')
            self.wfile.write(xml_data)
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not found"}')

    def do_POST(self):
        if self.path == '/test':
            self._set_headers(200, 'application/json')
            result = run_device_test()
            self.wfile.write(bytes(str(result).replace("'", '"'), 'utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not found"}')

    def log_message(self, format, *args):
        # Suppress default logging
        return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, IoTDeviceHTTPRequestHandler)
    print(f"Starting IoT Device HTTP server on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()