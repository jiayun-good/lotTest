import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import urllib.parse
import xml.etree.ElementTree as ET

DEVICE_NAME = os.environ.get('DEVICE_NAME', "d'sa")
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', "dsad'sa")
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', "dasdasdas")
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', "dsa")

DEVICE_DSAD_IP = os.environ.get('DEVICE_DSAD_IP', '127.0.0.1')
DEVICE_DSAD_PORT = int(os.environ.get('DEVICE_DSAD_PORT', '7000'))

HTTP_SERVER_HOST = os.environ.get('HTTP_SERVER_HOST', '0.0.0.0')
HTTP_SERVER_PORT = int(os.environ.get('HTTP_SERVER_PORT', '8080'))

# Dummy function to simulate device data over dsad protocol (which is unknown, so we mock)
def fetch_device_data():
    # Simulate fetching XML data from the device
    # In real driver, you would use socket/socketserver or a protocol handler
    # Here, we'll just return a static XML
    data = ET.Element('DeviceData')
    dp = ET.SubElement(data, 'DataPoint')
    dp.set('name', 'temperature')
    dp.text = '23.5'
    dp2 = ET.SubElement(data, 'DataPoint')
    dp2.set('name', 'humidity')
    dp2.text = '48'
    return ET.tostring(data, encoding='utf-8')

def send_device_command(cmd_payload: bytes):
    # Simulate sending command to the device and getting an XML response
    root = ET.Element('CommandResult')
    status = ET.SubElement(root, 'Status')
    status.text = 'OK'
    received = ET.SubElement(root, 'Received')
    received.text = cmd_payload.decode('utf-8', errors='replace')
    return ET.tostring(root, encoding='utf-8')

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DSADHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='application/xml', code=200):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/info':
            self._set_headers('application/json')
            self.wfile.write((
                '{'
                f'"device_name": "{DEVICE_NAME}",'
                f'"device_model": "{DEVICE_MODEL}",'
                f'"manufacturer": "{DEVICE_MANUFACTURER}",'
                f'"device_type": "{DEVICE_TYPE}"'
                '}'
            ).encode('utf-8'))
        elif parsed_path.path == '/data':
            # Connect to device and fetch XML data
            # In a real implementation, would use the DSAD protocol
            xml_data = fetch_device_data()
            self._set_headers('application/xml')
            self.wfile.write(xml_data)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Send this command to device and return XML response
            xml_resp = send_device_command(post_data)
            self._set_headers('application/xml')
            self.wfile.write(xml_resp)
        else:
            self.send_error(404, "Not Found")

def run_server():
    server_address = (HTTP_SERVER_HOST, HTTP_SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, DSADHTTPRequestHandler)
    print(f"Serving HTTP on {HTTP_SERVER_HOST}:{HTTP_SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()