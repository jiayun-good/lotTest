import os
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

DEVICE_NAME = os.getenv("DEVICE_NAME", "sasdds")
DEVICE_MODEL = os.getenv("DEVICE_MODEL", "sasdds")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

app = FastAPI()

class CommandRequest(BaseModel):
    command: str = None
    params: dict = None

@app.get("/info")
async def get_info():
    return {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": "",
        "device_type": ""
    }

@app.post("/cmd")
async def send_command(cmd: CommandRequest):
    # Simulated command execution placeholder
    # The real device has no commands in provided info
    return {
        "status": "success",
        "message": f"Command '{cmd.command}' received.",
        "params": cmd.params
    }

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)