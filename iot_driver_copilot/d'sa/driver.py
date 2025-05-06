import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import xml.etree.ElementTree as ET

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Helper: Read config from environment
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Dummy device comms: emulate device with XML data/command
def fetch_device_data():
    # Simulate fetching XML data from device over proprietary protocol "dsad"
    # In real implementation, replace with device communication logic (sockets, etc.)
    xml_data = f"""
    <device>
        <data_point name="temperature" value="23.5"/>
        <data_point name="humidity" value="45"/>
        <status value="ok"/>
    </device>
    """
    return xml_data.strip()

def send_device_command(cmd_payload: str):
    # Simulate sending command via proprietary protocol, and receiving response in XML
    root = ET.Element("command_response")
    status = ET.SubElement(root, "status")
    status.text = "success"
    cmd = ET.SubElement(root, "echoed_command")
    cmd.text = cmd_payload
    return ET.tostring(root, encoding='utf-8', method='xml')

class ThreadingSimpleServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), "utf-8"))
        elif self.path == "/data":
            xml_data = fetch_device_data()
            self._set_headers(200, "application/xml")
            self.wfile.write(xml_data.encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b''
            payload = post_data.decode("utf-8")
            xml_response = send_device_command(payload)
            self._set_headers(200, "application/xml")
            self.wfile.write(xml_response)
        else:
            self._set_headers(404)
            self.wfile.write(b"Not Found")

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadingSimpleServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device driver HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()