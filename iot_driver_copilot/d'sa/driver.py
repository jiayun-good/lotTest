import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

# Device configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))  # Port for the custom protocol (dsad)
HTTP_SERVER_HOST = os.environ.get('HTTP_SERVER_HOST', '0.0.0.0')
HTTP_SERVER_PORT = int(os.environ.get('HTTP_SERVER_PORT', '8080'))

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simulated device connection and protocol (dsad)
class DSADDeviceClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def fetch_data_points(self):
        # Simulate device returning XML format data
        # In real scenario, connect to the device using custom protocol
        xml_data = """
        <DeviceData>
            <DataPoint name="temperature" value="24.3"/>
            <DataPoint name="humidity" value="50"/>
            <DataPoint name="status" value="ok"/>
        </DeviceData>
        """
        return xml_data

    def send_command(self, command_xml):
        # Simulate sending XML command and receiving reply
        # In real scenario, send over the dsad protocol
        try:
            root = ET.fromstring(command_xml)
            action = root.findtext('Action')
            response = f"""
            <CommandResponse>
                <Action>{action}</Action>
                <Result>Success</Result>
            </CommandResponse>
            """
            return response
        except Exception as e:
            error_response = f"""
            <CommandResponse>
                <Result>Error</Result>
                <Message>{str(e)}</Message>
            </CommandResponse>
            """
            return error_response

client = DSADDeviceClient(DEVICE_IP, DEVICE_PORT)

class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type='application/xml'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            self._set_headers(200, 'application/json')
            info = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"]
            }
            import json
            self.wfile.write(json.dumps(info).encode('utf-8'))
        elif parsed_path.path == '/data':
            # Proxy/convert raw device data to HTTP/XML
            xml_data = client.fetch_data_points()
            self._set_headers(200, 'application/xml')
            self.wfile.write(xml_data.encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            # Expecting XML command
            try:
                command_xml = body.decode('utf-8')
                response_xml = client.send_command(command_xml)
                self._set_headers(200, 'application/xml')
                self.wfile.write(response_xml.encode('utf-8'))
            except Exception as e:
                self._set_headers(400, 'text/plain')
                self.wfile.write(f'Bad Request: {str(e)}'.encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'404 Not Found')

    def log_message(self, format, *args):
        return  # Silence server logs

def run_server():
    server_address = (HTTP_SERVER_HOST, HTTP_SERVER_PORT)
    httpd = HTTPServer(server_address, IoTDeviceHTTPRequestHandler)
    print(f"Serving HTTP on {HTTP_SERVER_HOST}:{HTTP_SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()