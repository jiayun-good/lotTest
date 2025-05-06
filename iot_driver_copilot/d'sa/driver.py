import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import xml.etree.ElementTree as ET

# Device Info (hardcoded as per device spec)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Load config from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
SERVER_HTTP_PORT = SERVER_PORT  # Only HTTP is supported in this driver

# Simulated device connection
class SimulatedDeviceConnection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        # Simulate device state
        self.data_points = {
            "temperature": "22.5",
            "humidity": "40%",
            "status": "OK"
        }

    def fetch_data_points(self):
        # Simulate fetching XML data from a device
        root = ET.Element("DeviceData")
        for k, v in self.data_points.items():
            ET.SubElement(root, k).text = v
        return ET.tostring(root, encoding='utf-8', method='xml')

    def send_command(self, command_xml):
        # Parse command and simulate action
        try:
            root = ET.fromstring(command_xml)
            # Simulate a command structure: <Command><SetTemperature>25</SetTemperature></Command>
            for child in root:
                if child.tag == "SetTemperature":
                    self.data_points["temperature"] = child.text
                elif child.tag == "SetHumidity":
                    self.data_points["humidity"] = child.text
                elif child.tag == "SetStatus":
                    self.data_points["status"] = child.text
            return True, "<Result>Success</Result>"
        except Exception as e:
            return False, "<Result>Error: {}</Result>".format(str(e))

# Instantiate device connection
device_conn = SimulatedDeviceConnection(DEVICE_IP, DEVICE_PORT)

class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            # Fetch XML-formatted data points
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            data = device_conn.fetch_data_points()
            self.wfile.write(data)
        elif self.path == "/info":
            # Return device info as XML
            root = ET.Element("DeviceInfo")
            for k, v in DEVICE_INFO.items():
                ET.SubElement(root, k).text = v
            data = ET.tostring(root, encoding='utf-8', method='xml')
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            success, result_xml = device_conn.send_command(post_data.decode('utf-8'))
            self.send_response(200 if success else 400)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(result_xml.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        return  # Suppress default logging

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_HTTP_PORT)
    httpd = ThreadedHTTPServer(server_address, IoTDeviceHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()