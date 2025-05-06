import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Device Info (static for /info endpoint)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Environment Variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulated device data fetch
def fetch_device_data():
    # In a real driver, connect to the device and fetch the latest XML data
    # Here, we simulate with sample XML
    sample_xml = """
    <DeviceData>
        <Temperature>22.5</Temperature>
        <Humidity>45</Humidity>
        <Status>OK</Status>
    </DeviceData>
    """
    return sample_xml.strip()

# Simulated command execution on device
def send_device_command(xml_payload):
    # In a real driver, send the XML payload to the device and get response
    # Here, we simulate a response
    try:
        ET.fromstring(xml_payload)
        response = "<Response><Result>Success</Result></Response>"
    except ET.ParseError:
        response = "<Response><Result>Invalid XML</Result></Response>"
    return response

class IoTHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(bytes(str(DEVICE_INFO), "utf-8"))
        elif self.path == "/data":
            xml_data = fetch_device_data()
            self._set_headers(content_type="application/xml")
            self.wfile.write(xml_data.encode('utf-8'))
        else:
            self._set_headers(status=404)
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length)
            xml_payload = post_body.decode("utf-8")
            response_xml = send_device_command(xml_payload)
            self._set_headers(content_type="application/xml")
            self.wfile.write(response_xml.encode("utf-8"))
        else:
            self._set_headers(status=404)
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        return  # Suppress default logging

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), IoTHTTPRequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()