import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import xml.etree.ElementTree as ET

# --- Device configuration from environment variables ---
DEVICE_NAME = os.environ.get("DEVICE_NAME", "tes")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "tt")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "ttt")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "ttt")
DEVICE_PROTOCOL = os.environ.get("DEVICE_PROTOCOL", "ttt")
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulated device XML response for /data endpoint
def get_device_xml_data():
    root = ET.Element("DeviceData")
    dp = ET.SubElement(root, "DataPoints")
    dp.text = "tt"
    st = ET.SubElement(root, "Status")
    st.text = "OK"
    return ET.tostring(root, encoding="utf-8", method="xml")

# Simulated command execution for /test endpoint
def run_device_test():
    root = ET.Element("TestResult")
    ET.SubElement(root, "Device").text = DEVICE_NAME
    ET.SubElement(root, "Result").text = "PASS"
    return ET.tostring(root, encoding="utf-8", method="xml")

# Simulated device information for /info endpoint
def get_device_info():
    info = {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "device_type": DEVICE_TYPE,
        "primary_protocol": DEVICE_PROTOCOL,
        "device_ip": DEVICE_IP,
        "device_port": DEVICE_PORT
    }
    return info

class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            import json
            self.wfile.write(json.dumps(get_device_info()).encode("utf-8"))
        elif self.path == "/data":
            self._set_headers(200, "application/xml")
            self.wfile.write(get_device_xml_data())
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        if self.path == "/test":
            self._set_headers(200, "application/xml")
            self.wfile.write(run_device_test())
        else:
            self.send_error(404, "Not found")

    def log_message(self, format, *args):
        return  # Silence default logging

def run():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadingHTTPServer(server_address, DeviceHTTPRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run()