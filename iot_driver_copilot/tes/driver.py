import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Environment Variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))  # Port for ADAS protocol
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8000'))

# Simulated ADAS protocol communication with XML data
def adas_request(path, command=None):
    """
    Simulates communication with a device using the ADAS protocol.
    In a production driver, this would use sockets or a protocol-specific library.
    """
    # For demonstration, we return static XML. Replace with actual protocol communication.
    if path == '/info':
        data = f"""
        <DeviceInfo>
            <DeviceName>tes</DeviceName>
            <DeviceModel>sdssd</DeviceModel>
            <Manufacturer>ss</Manufacturer>
            <DeviceType>sd</DeviceType>
            <PrimaryProtocol>adas</PrimaryProtocol>
        </DeviceInfo>
        """
        return data.strip()
    elif path == '/data':
        data = """
        <DataPoints>
            <Point name="saddsa" value="42"/>
        </DataPoints>
        """
        return data.strip()
    elif path == '/cmd' and command:
        data = f"""
        <CommandResponse>
            <Command>{command}</Command>
            <Status>OK</Status>
        </CommandResponse>
        """
        return data.strip()
    else:
        return "<Error>Unknown Request</Error>"

def xml_to_dict(elem):
    """Recursively converts an XML element to a dictionary."""
    d = {}
    for child in elem:
        if len(child):
            d[child.tag] = xml_to_dict(child)
        else:
            d[child.tag] = child.text
    return d

class IoTDeviceHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            xml_data = adas_request('/info')
            root = ET.fromstring(xml_data)
            info = xml_to_dict(root)
            self._set_headers()
            self.wfile.write(bytes(str(info), 'utf-8'))
        elif self.path == '/data':
            xml_data = adas_request('/data')
            root = ET.fromstring(xml_data)
            data = xml_to_dict(root)
            self._set_headers()
            self.wfile.write(bytes(str(data), 'utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Endpoint not found"}')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            # Assume command is sent as raw string or JSON {"command":"xxx"}
            try:
                import json
                data = json.loads(post_data)
                command = data.get('command')
            except Exception:
                command = post_data.strip()
            xml_data = adas_request('/cmd', command)
            root = ET.fromstring(xml_data)
            resp = xml_to_dict(root)
            self._set_headers()
            self.wfile.write(bytes(str(resp), 'utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Endpoint not found"}')

    def log_message(self, format, *args):
        # Silence default HTTP server logging
        return

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, IoTDeviceHandler)
    print(f'Starting HTTP server at http://{SERVER_HOST}:{SERVER_PORT}')
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()