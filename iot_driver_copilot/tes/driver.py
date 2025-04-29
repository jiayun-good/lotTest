import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DEVICE_INFO = {
    "device_name": "tes",
    "device_model": "tt",
    "manufacturer": "ttt",
    "device_type": "ttt",
    "connection_protocol": "ttt"
}

# Simulated device data function (replace with real protocol logic as needed)
def get_device_data():
    root = ET.Element("DeviceData")
    ET.SubElement(root, "DataPoint").text = "tt"
    ET.SubElement(root, "Status").text = "OK"
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def run_device_command():
    root = ET.Element("TestResult")
    ET.SubElement(root, "Command").text = "ttt"
    ET.SubElement(root, "Result").text = "Success"
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_xml_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/xml')
        self.end_headers()

    def _set_json_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _set_bad_request(self):
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_json_headers()
            self.wfile.write(bytes(
                '{{"device_name": "{}", "device_model": "{}", "manufacturer": "{}", "device_type": "{}", "connection_protocol": "{}"}}'.format(
                    DEVICE_INFO["device_name"],
                    DEVICE_INFO["device_model"],
                    DEVICE_INFO["manufacturer"],
                    DEVICE_INFO["device_type"],
                    DEVICE_INFO["connection_protocol"]
                ), "utf-8"
            ))
        elif self.path == "/data":
            # Proxy or convert device 'raw' data to HTTP (simulate here)
            # Real implementation: connect to DEVICE_IP:DEVICE_PORT, receive XML, stream it
            self._set_xml_headers()
            data = get_device_data()
            self.wfile.write(data)
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        if self.path == "/test":
            # Optionally, read POST body for command options; here we ignore it
            self._set_xml_headers()
            result = run_device_command()
            self.wfile.write(result)
        else:
            self.send_error(404, "Not found")

    def log_message(self, format, *args):
        return  # Silence log output

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == "__main__":
    run_server()