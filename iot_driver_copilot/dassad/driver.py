import os
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import uvicorn

DEVICE_NAME = os.environ.get("DEVICE_NAME", "dassad")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "das")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "sad")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "sad")

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

app = FastAPI()

@app.get("/info")
def get_info():
    return JSONResponse(
        content={
            "device_name": DEVICE_NAME,
            "device_model": DEVICE_MODEL,
            "manufacturer": DEVICE_MANUFACTURER,
            "device_type": DEVICE_TYPE
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)