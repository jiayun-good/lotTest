import os
import csv
import io
import asyncio
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Device configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))   # Port to connect to device for data/command
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
SERVER_HTTP_PORT = SERVER_PORT  # Only HTTP is used

# FastAPI app initialization
app = FastAPI(
    title="DSA Device HTTP Driver",
    description="HTTP driver for DSA device, proxying device data and commands over HTTP.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Device static info
DEVICE_INFO = {
    "device_name": "asd",
    "device_model": "sda",
    "manufacturer": "sad",
    "device_type": "asd"
}

# --- Helper functions to communicate with device over TCP ---

async def send_command_to_device(command: str) -> str:
    """
    Connects to the device via TCP, sends a command string, receives the response.
    Returns the raw response as string.
    """
    reader, writer = await asyncio.open_connection(DEVICE_IP, DEVICE_PORT)
    writer.write((command.strip() + "\n").encode("utf-8"))
    await writer.drain()
    data = await reader.readuntil(separator=b'\n')
    writer.close()
    await writer.wait_closed()
    return data.decode('utf-8').strip()

async def stream_device_data():
    """
    Connects to the device and yields real-time CSV data as it arrives.
    """
    reader, writer = await asyncio.open_connection(DEVICE_IP, DEVICE_PORT)
    # Send a command to start streaming data; using 'GET_DATA' as an example.
    writer.write(b"GET_DATA\n")
    await writer.drain()
    try:
        while True:
            line = await reader.readline()
            if not line:
                break
            yield line
    finally:
        writer.close()
        await writer.wait_closed()

# --- API Models ---

class CommandRequest(BaseModel):
    command: str

class CommandResponse(BaseModel):
    result: str

# --- Endpoints ---

@app.get("/info")
async def get_info():
    return JSONResponse(content=DEVICE_INFO)

@app.get("/data")
async def get_data():
    headers = {
        "Content-Disposition": "inline; filename=device_data.csv",
        "Content-Type": "text/csv",
        "Cache-Control": "no-cache"
    }
    return StreamingResponse(stream_device_data(), headers=headers, media_type="text/csv")

@app.post("/cmd")
async def post_cmd(req: CommandRequest):
    try:
        response = await send_command_to_device(req.command)
        return JSONResponse(content={"result": response})
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

# --- Entrypoint ---

if __name__ == "__main__":
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_HTTP_PORT)