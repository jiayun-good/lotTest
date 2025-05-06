import os
import threading
import http.server
import socketserver
import xml.etree.ElementTree as ET
from io import BytesIO

# Load configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device Info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Mock function to connect to the device and fetch XML data points
def fetch_device_data():
    # This should be replaced with actual device communication using the 'dsad' protocol.
    # Simulating a response for demonstration.
    # Example XML: <data><point name="temp" value="23.5"/><point name="humidity" value="40"/></data>
    xml_data = """<?xml version="1.0"?>
    <data>
        <point name="temp" value="23.5"/>
        <point name="humidity" value="40"/>
    </data>"""
    return xml_data.encode('utf-8')

# Mock function to send command to the device and get XML response
def send_device_command(command_xml):
    # This should be replaced with actual command sending logic using the 'dsad' protocol.
    # Example response:
    response_xml = f"""<?xml version="1.0"?><response status="success" received="{command_xml.strip()}"/>"""
    return response_xml.encode('utf-8')

class DeviceHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        elif self.path == '/data':
            # Fetch data from the device and convert XML to JSON-like dict for HTTP consumption
            device_xml = fetch_device_data()
            root = ET.fromstring(device_xml)
            data_points = {}
            for point in root.findall('point'):
                name = point.get('name')
                value = point.get('value')
                data_points[name] = value
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(str(data_points).replace("'", '"'), 'utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Expecting XML command payload
            try:
                command_xml = post_data.decode('utf-8')
                # Validate XML
                ET.fromstring(command_xml)
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(f'{{"error": "Invalid XML: {str(e)}"}}', 'utf-8'))
                return
            # Send command to device and get XML response
            response_xml = send_device_command(command_xml)
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(response_xml)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence the default logging
        return

def run_server():
    with socketserver.ThreadingTCPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()