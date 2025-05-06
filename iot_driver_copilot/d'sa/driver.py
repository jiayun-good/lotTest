import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

DEVICE_IP = os.getenv("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.getenv("DEVICE_PORT", "8081"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

DEVICE_NAME = "d'sa"
DEVICE_MODEL = "dsad'sa"
DEVICE_MANUFACTURER = "dasdasdas"
DEVICE_TYPE = "dsa"

class MockDeviceConnection:
    # This mock simulates a device that talks XML over a TCP socket.
    # In a real case, this would connect to the device using the primary protocol.
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_data_points(self):
        # Simulate a request to the device and getting XML response
        # In real code, this would be a socket connection and protocol exchange
        # Example XML structure based on data_format
        data = '''<DataPoints>
    <Point name="temperature" value="24.5" unit="C"/>
    <Point name="humidity" value="60" unit="%"/>
</DataPoints>'''
        return data

    def send_command(self, command_xml):
        # In a real device, send the XML command and get XML response
        # Here, we mock a successful response
        response = '''<CommandResponse status="success" />'''
        return response

device_conn = MockDeviceConnection(DEVICE_IP, DEVICE_PORT)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": DEVICE_MANUFACTURER,
                "device_type": DEVICE_TYPE
            }
            self.wfile.write(bytes(str(info).replace("'", '"'), "utf-8"))
        elif self.path == '/data':
            self._set_headers(content_type="application/json")
            xml_data = device_conn.get_data_points()
            # Convert XML to dict for JSON response
            root = ET.fromstring(xml_data)
            data = []
            for point in root.findall('Point'):
                data.append({
                    "name": point.attrib.get("name"),
                    "value": point.attrib.get("value"),
                    "unit": point.attrib.get("unit")
                })
            import json
            self.wfile.write(bytes(json.dumps(data), "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not found"}')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Expecting XML command in body, but accept JSON for convenience
            try:
                import json
                body = json.loads(post_data.decode("utf-8"))
                # Convert to XML for the device
                cmd = ET.Element("Command")
                for k, v in body.items():
                    ET.SubElement(cmd, k).text = str(v)
                command_xml = ET.tostring(cmd, encoding="unicode")
            except Exception:
                # If not JSON, treat as raw XML
                command_xml = post_data.decode("utf-8")
            device_response = device_conn.send_command(command_xml)
            self._set_headers(content_type="application/xml")
            self.wfile.write(device_response.encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not found"}')

    def log_message(self, format, *args):
        return  # Silence standard logging

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), Handler)
    print(f"HTTP Server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()