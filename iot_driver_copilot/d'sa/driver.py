import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET
import threading

DEVICE_NAME = os.environ.get("DEVICE_NAME", "d'sa")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "dsad'sa")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "dasdasdas")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "dsa")
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "8081"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulated device state for demonstration
device_state = {
    "data_points": {
        "temperature": "22.5",
        "humidity": "45"
    },
    "status": "ok"
}

class DeviceSimulator(threading.Thread):
    # Simulates a device that listens on DEVICE_IP:DEVICE_PORT and serves XML
    def run(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer
        class SimDeviceHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/status":
                    root = ET.Element("DeviceData")
                    dp = ET.SubElement(root, "DataPoints")
                    for k, v in device_state["data_points"].items():
                        ET.SubElement(dp, k).text = v
                    ET.SubElement(root, "Status").text = device_state["status"]
                    xml_str = ET.tostring(root, encoding='utf-8')
                    self.send_response(200)
                    self.send_header("Content-Type", "application/xml")
                    self.send_header("Content-Length", str(len(xml_str)))
                    self.end_headers()
                    self.wfile.write(xml_str)
                else:
                    self.send_response(404)
                    self.end_headers()
            def do_POST(self):
                if self.path == "/command":
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    # Parse XML command (simulate)
                    try:
                        root = ET.fromstring(post_data)
                        cmd = root.findtext("Command")
                        if cmd == "reset":
                            device_state["status"] = "reset"
                        elif cmd == "update":
                            device_state["status"] = "updated"
                        else:
                            device_state["status"] = "unknown"
                        resp = ET.Element("CommandResult")
                        ET.SubElement(resp, "Status").text = device_state["status"]
                        xml_str = ET.tostring(resp, encoding='utf-8')
                        self.send_response(200)
                        self.send_header("Content-Type", "application/xml")
                        self.send_header("Content-Length", str(len(xml_str)))
                        self.end_headers()
                        self.wfile.write(xml_str)
                    except Exception:
                        self.send_response(400)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
        sim_server = HTTPServer((DEVICE_IP, DEVICE_PORT), SimDeviceHandler)
        sim_server.serve_forever()

class DriverHandler(BaseHTTPRequestHandler):
    def _set_json_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _set_xml_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/xml')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            self._set_json_headers()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": DEVICE_MANUFACTURER,
                "device_type": DEVICE_TYPE
            }
            self.wfile.write(bytes(str(info).replace("'", '"'), "utf-8"))
        elif parsed_path.path == '/data':
            # Connect to device, get XML, convert to JSON
            import http.client
            try:
                conn = http.client.HTTPConnection(DEVICE_IP, DEVICE_PORT, timeout=5)
                conn.request("GET", "/status")
                resp = conn.getresponse()
                if resp.status == 200:
                    xml_data = resp.read()
                    root = ET.fromstring(xml_data)
                    data = {}
                    dp_elem = root.find("DataPoints")
                    if dp_elem is not None:
                        data_points = {child.tag: child.text for child in dp_elem}
                        data["data_points"] = data_points
                    status = root.findtext("Status")
                    data["status"] = status
                    self._set_json_headers()
                    self.wfile.write(bytes(str(data).replace("'", '"'), "utf-8"))
                else:
                    self._set_json_headers(502)
                    self.wfile.write(b'{"error": "Failed to fetch data from device"}')
            except Exception as e:
                self._set_json_headers(502)
                self.wfile.write(bytes('{"error": "Device unreachable"}', "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Accept JSON payload {"command": "..."}
            try:
                import json
                payload = json.loads(post_data.decode('utf-8'))
                command = payload.get("command")
                # Send command to device in XML
                cmd_root = ET.Element("CommandRequest")
                ET.SubElement(cmd_root, "Command").text = command
                xml_cmd = ET.tostring(cmd_root, encoding='utf-8')
                import http.client
                conn = http.client.HTTPConnection(DEVICE_IP, DEVICE_PORT, timeout=5)
                conn.request("POST", "/command", body=xml_cmd, headers={"Content-Type": "application/xml"})
                resp = conn.getresponse()
                if resp.status == 200:
                    xml_resp = resp.read()
                    root = ET.fromstring(xml_resp)
                    status = root.findtext("Status")
                    self._set_json_headers()
                    self.wfile.write(bytes('{"result": "%s"}' % status, "utf-8"))
                else:
                    self._set_json_headers(502)
                    self.wfile.write(b'{"error": "Failed to send command to device"}')
            except Exception as e:
                self._set_json_headers(400)
                self.wfile.write(b'{"error": "Invalid request"}')
        else:
            self.send_response(404)
            self.end_headers()

def run():
    # Start device simulator for demonstration.
    sim_thread = DeviceSimulator()
    sim_thread.daemon = True
    sim_thread.start()
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DriverHandler)
    print(f"Driver HTTP Server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()