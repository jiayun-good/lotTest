import os
import asyncio
import json
from aiohttp import web
import socket
import struct

# --- Environment Configuration ---
DEVICE_IP = os.getenv("DEVICE_IP", "127.0.0.1")
ROS_MASTER_URI = os.getenv("ROS_MASTER_URI", "http://localhost:11311")
PEOPLE_TRACKING_UDP_PORT = int(os.getenv("PEOPLE_TRACKING_UDP_PORT", "15001"))
STATUS_UDP_PORT = int(os.getenv("STATUS_UDP_PORT", "15002"))
CMD_VEL_UDP_PORT = int(os.getenv("CMD_VEL_UDP_PORT", "15003"))
NAV_UDP_PORT = int(os.getenv("NAV_UDP_PORT", "15004"))
SERVER_HOST = os.getenv("HTTP_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("HTTP_SERVER_PORT", "8080"))
UDP_TIMEOUT = float(os.getenv("UDP_TIMEOUT", "0.5"))

# --- UDP Helper Functions ---
async def udp_request(ip, port, message=None, expect_reply=True):
    loop = asyncio.get_event_loop()
    def udp_send_recv():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDP_TIMEOUT)
        try:
            if message:
                sock.sendto(message, (ip, port))
            if expect_reply:
                data, _ = sock.recvfrom(65535)
                return data
            return b""
        except socket.timeout:
            return b""
        finally:
            sock.close()
    data = await loop.run_in_executor(None, udp_send_recv)
    return data

# --- /status Endpoint ---
async def handle_status(request):
    # Compose a UDP status request; protocol assumed: send nothing, receive JSON
    data = await udp_request(DEVICE_IP, STATUS_UDP_PORT, expect_reply=True)
    if not data:
        return web.json_response({"error": "No status reply from robot"}, status=504)
    try:
        status = json.loads(data.decode())
    except Exception:
        status = {"raw": data.decode(errors="ignore")}
    return web.json_response(status)

# --- /people Endpoint ---
async def handle_people(request):
    # Compose a UDP people tracking request; protocol assumed: send nothing, receive JSON
    data = await udp_request(DEVICE_IP, PEOPLE_TRACKING_UDP_PORT, expect_reply=True)
    if not data:
        return web.json_response({"error": "No people data reply from robot"}, status=504)
    try:
        people = json.loads(data.decode())
    except Exception:
        people = {"raw": data.decode(errors="ignore")}
    return web.json_response(people)

# --- /move Endpoint ---
async def handle_move(request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    # Compose ROS geometry_msgs/Twist message as JSON or simple structure
    # Here, we pack as JSON for the robot backend (linear and angular fields)
    cmd = {
        "linear": payload.get("linear", {"x": 0, "y": 0, "z": 0}),
        "angular": payload.get("angular", {"x": 0, "y": 0, "z": 0})
    }
    data = json.dumps(cmd).encode()
    await udp_request(DEVICE_IP, CMD_VEL_UDP_PORT, message=data, expect_reply=False)
    return web.json_response({"status": "sent"})

# --- /nav Endpoint ---
async def handle_nav(request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    # Expect { "action": "start"|"stop", ... }
    nav_cmd = {
        "action": payload.get("action", "start"),
        "params": payload.get("params", {})
    }
    data = json.dumps(nav_cmd).encode()
    await udp_request(DEVICE_IP, NAV_UDP_PORT, message=data, expect_reply=False)
    return web.json_response({"status": "sent"})

# --- HTTP Application Setup ---
app = web.Application()
app.add_routes([
    web.get('/status', handle_status),
    web.get('/people', handle_people),
    web.post('/move', handle_move),
    web.post('/nav', handle_nav),
])

if __name__ == '__main__':
    web.run_app(app, host=SERVER_HOST, port=SERVER_PORT)