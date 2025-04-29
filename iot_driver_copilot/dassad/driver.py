import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

DEVICE_NAME = os.environ.get("DEVICE_NAME", "dassad")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "das")
MANUFACTURER = os.environ.get("MANUFACTURER", "sad")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "sad")

HTTP_HOST = os.environ.get("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.environ.get("HTTP_PORT", 8000))

app = FastAPI(title="das Driver")

@app.get("/info")
async def get_info():
    return JSONResponse({
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": MANUFACTURER,
        "device_type": DEVICE_TYPE
    })

if __name__ == "__main__":
    uvicorn.run(app, host=HTTP_HOST, port=HTTP_PORT)