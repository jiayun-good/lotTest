import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import xml.etree.ElementTree as ET

DEVICE_NAME = os.environ.get('DEVICE_NAME', "d'sa")
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', "dsad'sa")
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', "dasdasdas")
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', "dsa")

DEVICE_HOST = os.environ.get('DEVICE_HOST', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))

SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Simulate device connection and data for this protocol.
class DSADDeviceClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_data_points(self):
        # In real implementation, connect to device and fetch XML data.
        # Here, return a sample XML data as bytes.
        root = ET.Element('data')
        dp = ET.SubElement(root, 'point')
        dp.set('name', 'temperature')
        dp.text = '23.4'
        dp2 = ET.SubElement(root, 'point')
        dp2.set('name', 'humidity')
        dp2.text = '56'
        return ET.tostring(root, encoding='utf-8')

    def send_command(self, command_xml):
        # In real implementation, send command XML to device and get response.
        # Here, simulate command exec and return XML.
        resp = ET.Element('response')
        status = ET.SubElement(resp, 'status')
        status.text = 'success'
        cmd = ET.SubElement(resp, 'command')
        cmd.text = command_xml
        return ET.tostring(resp, encoding='utf-8')

device_client = DSADDeviceClient(DEVICE_HOST, DEVICE_PORT)

class IoTHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            self._set_headers(200, "application/xml")
            data = device_client.get_data_points()
            self.wfile.write(data)
        elif self.path == '/info':
            self._set_headers(200, "application/json")
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": DEVICE_MANUFACTURER,
                "device_type": DEVICE_TYPE,
            }
            import json
            self.wfile.write(json.dumps(info).encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            try:
                # Accept XML or raw text as command
                command_xml = post_data.decode('utf-8')
                response = device_client.send_command(command_xml)
                self._set_headers(200, "application/xml")
                self.wfile.write(response)
            except Exception as e:
                self._set_headers(400, "text/plain")
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        # Overridden to suppress default console logging
        pass

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, IoTHTTPRequestHandler)
    print(f"Serving on {SERVER_HOST}:{SERVER_PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()