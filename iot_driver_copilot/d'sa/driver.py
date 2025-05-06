import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import xml.etree.ElementTree as ET

DEVICE_NAME = os.environ.get('DEVICE_NAME', "d'sa")
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', "dsad'sa")
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', "dasdasdas")
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', "dsa")
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))

SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Simulated device connection and data
class DSADDeviceClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def fetch_data(self):
        # Simulate device data in XML format
        data = '''<device>
    <name>{}</name>
    <model>{}</model>
    <manufacturer>{}</manufacturer>
    <type>{}</type>
    <status>
        <datapoint name="dsa" value="42"/>
    </status>
</device>'''.format(DEVICE_NAME, DEVICE_MODEL, DEVICE_MANUFACTURER, DEVICE_TYPE)
        return data

    def send_command(self, command_xml):
        # Simulate device command response in XML
        try:
            root = ET.fromstring(command_xml)
            command = root.findtext('command')
        except Exception:
            command = None
        response = '''<response>
    <command>{}</command>
    <result>success</result>
</response>'''.format(command if command else 'unknown')
        return response

    def get_info(self):
        # Return device information as a dictionary
        return {
            "device_name": DEVICE_NAME,
            "device_model": DEVICE_MODEL,
            "manufacturer": DEVICE_MANUFACTURER,
            "device_type": DEVICE_TYPE
        }


device_client = DSADDeviceClient(DEVICE_IP, DEVICE_PORT)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DSADHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, code=200, content_type='application/xml'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            # Fetch and proxy device data (XML), convert to HTTP response
            xml_data = device_client.fetch_data()
            self._set_headers(200, 'application/xml')
            self.wfile.write(xml_data.encode('utf-8'))
        elif self.path == '/info':
            info = device_client.get_info()
            self._set_headers(200, 'application/json')
            import json
            self.wfile.write(json.dumps(info).encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Expects command in XML
            response_xml = device_client.send_command(post_data.decode('utf-8'))
            self._set_headers(200, 'application/xml')
            self.wfile.write(response_xml.encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'404 Not Found')

def run():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DSADHTTPRequestHandler)
    print(f"Starting DSAD HTTP server at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == '__main__':
    run()