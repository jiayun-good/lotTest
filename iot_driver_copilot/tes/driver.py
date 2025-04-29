import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Device mock for demonstration (replace with actual device communication)
class TesDevice:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.info = {
            "device_name": "tes",
            "device_model": "tt",
            "manufacturer": "ttt",
            "device_type": "ttt",
            "primary_protocol": "ttt"
        }

    def get_info(self):
        return self.info

    def test_command(self):
        # Simulate executing a command on the device
        return {"result": "ok", "message": "Device test command executed successfully."}

    def get_data(self):
        # Simulate XML data from device
        root = ET.Element("DeviceData")
        point = ET.SubElement(root, "DataPoint")
        point.set("name", "tt")
        point.text = "23.5"
        status = ET.SubElement(root, "Status")
        status.text = "OK"
        return ET.tostring(root, encoding="utf-8", method="xml")


def get_env_var(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and val is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

DEVICE_IP = get_env_var("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(get_env_var("DEVICE_PORT", "9000"))
SERVER_HOST = get_env_var("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(get_env_var("SERVER_PORT", "8080"))

tes_device = TesDevice(DEVICE_IP, DEVICE_PORT)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/info":
            info = tes_device.get_info()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = {
                "device_name": info["device_name"],
                "device_model": info["device_model"],
                "manufacturer": info["manufacturer"],
                "primary_protocol": info["primary_protocol"],
            }
            self.wfile.write(bytes(str(data).replace("'", '"'), "utf-8"))
        elif self.path == "/data":
            xml_data = tes_device.get_data()
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            self.wfile.write(xml_data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/test":
            length = int(self.headers.get('Content-Length', 0))
            _ = self.rfile.read(length) if length > 0 else None
            result = tes_device.test_command()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(str(result).replace("'", '"'), "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress log output


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def run():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, Handler)
    print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT} (device at {DEVICE_IP}:{DEVICE_PORT})")
    httpd.serve_forever()

if __name__ == "__main__":
    run()