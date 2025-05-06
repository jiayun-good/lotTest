import os
import threading
import http.server
import socketserver
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs

# Environment variable configuration
DEVICE_IP = os.getenv('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.getenv('DEVICE_PORT', '8001'))
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '8080'))

# Device info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Dummy XML data for data points
DUMMY_XML_DATA = """<?xml version="1.0"?>
<datapoints>
    <point>
        <name>temperature</name>
        <value>23.5</value>
        <unit>C</unit>
    </point>
    <point>
        <name>humidity</name>
        <value>45</value>
        <unit>%</unit>
    </point>
</datapoints>
"""

class DeviceConnection:
    """Simulate a connection to the device."""

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def fetch_data(self):
        # Simulate fetching XML data from device
        # In a real driver, connect via socket, send protocol request, parse response
        return DUMMY_XML_DATA

    def send_command(self, command_xml):
        # Simulate sending a command and getting XML response
        # In a real driver, connect via socket, send protocol command, parse response
        try:
            root = ET.fromstring(command_xml)
            cmd = root.find('command').text if root.find('command') is not None else "unknown"
            response = f"""<?xml version="1.0"?><response><status>success</status><executed>{cmd}</executed></response>"""
            return response
        except Exception as e:
            response = f"""<?xml version="1.0"?><response><status>error</status><message>{str(e)}</message></response>"""
            return response

class Handler(http.server.BaseHTTPRequestHandler):
    device_conn = DeviceConnection(DEVICE_IP, DEVICE_PORT)

    def _send_response(self, content, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/info":
            self._send_response(self._device_info_xml(), content_type="application/xml")
        elif parsed_path.path == "/data":
            xml_data = self.device_conn.fetch_data()
            self._send_response(xml_data, content_type="application/xml")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len).decode('utf-8')
            response_xml = self.device_conn.send_command(post_body)
            self._send_response(response_xml, content_type="application/xml")
        else:
            self.send_error(404, "Not Found")

    def _device_info_xml(self):
        return f"""<?xml version="1.0"?>
<device>
    <name>{DEVICE_INFO['device_name']}</name>
    <model>{DEVICE_INFO['device_model']}</model>
    <manufacturer>{DEVICE_INFO['manufacturer']}</manufacturer>
    <type>{DEVICE_INFO['device_type']}</type>
</device>
"""

def run_server():
    with socketserver.TCPServer((SERVER_HOST, SERVER_PORT), Handler) as httpd:
        print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT} ...")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()