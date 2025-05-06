import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import xml.etree.ElementTree as ET

DEVICE_NAME = os.environ.get("DEVICE_NAME", "d'sa")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "dsad'sa")
MANUFACTURER = os.environ.get("MANUFACTURER", "dasdasdas")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "dsa")

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulated device XML data and command response for demo purposes
def fetch_device_data():
    # In a real implementation, connect to DEVICE_IP:DEVICE_PORT and fetch data
    # For demonstration, return static XML
    root = ET.Element("DataPoints")
    dp = ET.SubElement(root, "Point")
    dp.set("name", "temperature")
    dp.text = "25.4"
    return ET.tostring(root, encoding='utf-8', method='xml')

def send_device_command(xml_payload):
    # In a real implementation, send the XML payload to the device and return response
    # Simulate success
    root = ET.Element("CommandResponse")
    root.text = "OK"
    return ET.tostring(root, encoding='utf-8', method='xml')

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/xml", code=200):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/data":
            self._set_headers("application/xml")
            data = fetch_device_data()
            self.wfile.write(data)
        elif self.path == "/info":
            self._set_headers("application/json")
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": MANUFACTURER,
                "device_type": DEVICE_TYPE
            }
            import json
            self.wfile.write(json.dumps(info).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(content_length)
            # Expecting XML payload
            try:
                ET.fromstring(payload)  # Validate XML
            except Exception:
                self._set_headers("application/xml", code=400)
                error_xml = "<Error>Invalid XML</Error>".encode("utf-8")
                self.wfile.write(error_xml)
                return
            resp = send_device_command(payload)
            self._set_headers("application/xml")
            self.wfile.write(resp)
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        return  # Silence default logging

def run_server():
    with socketserver.ThreadingTCPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()