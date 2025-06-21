
import json
import threading
import asyncio
import logging
import uvicorn
from pydantic import BaseModel
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

from engine_hotword import HotwordEngine

logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(
    title="Hotword API",
    description="Hotword Detection and Transcribtion API.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

hw_obj = HotwordEngine()

lock = asyncio.Lock()
running_lock = threading.Lock()


class ListenParams(BaseModel):
    hotwords: list[str] = ["hey jarvis", "hey agent"]
    dev_index: Optional[int] = None
    model_engine: Optional[str] = "vosq"
    model_name: Optional[str] = "vosk-model-en-us-0.22"


@router.get("/health")
def health_check():

    return {"status": "ok"}


async def safe_close(ws: WebSocket):

    try:
        await ws.close()
    except RuntimeError:
        pass


@router.websocket("/listen")
async def websocket_listen(websocket: WebSocket):

    await websocket.accept()

    if lock.locked():
        await websocket.send_text("Another session is already running.")
        await safe_close(websocket)
        return

    async with lock:

        try:

            params_raw = await websocket.receive_text()
            params = ListenParams(**json.loads(params_raw))

            status, output = hw_obj.init_hotword(
                dev_index=params.dev_index,
                model_engine=params.model_engine,
                model_name=params.model_name
            )

            if not status:
                await websocket.send_text(f"init_hotword failed: {output}")
                await safe_close(websocket)
                return

            await websocket.send_text("Hotword detection initialized. Listening...")

        except Exception as e:
            print(f"Error: {e}")
            await safe_close(websocket)
            hw_obj.stop_hotword_detection()
            return

        try:

            loop = asyncio.get_event_loop()

            def on_transcription(text):
                asyncio.run_coroutine_threadsafe(websocket.send_text(text), loop)

            future = loop.run_in_executor(None, hw_obj.detect_hotword_and_transcribe, params.hotwords, on_transcription)

            while not future.done():

                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
                except asyncio.TimeoutError:
                    continue
                except WebSocketDisconnect:
                    print("Client disconnected.")
                    break

        except Exception as e:
            print(f"Error: {e}")

        finally:
            await safe_close(websocket)
            hw_obj.stop_hotword_detection()


@router.post("/stop")
def stop():

    if not running_lock.acquire(blocking=False):
        return JSONResponse({"error": "Another session is in progress"}, status_code=423)

    try:

        print("Stoping hotword detection...")
        hw_obj.stop_hotword_detection()

        return {"text": "Hotword detection stopped."}

    finally:

        running_lock.release()


app.include_router(router, prefix="/api/hotword")


if __name__ == "__main__":

    print("Starting Hotword detection service on http://localhost:5600")
    uvicorn.run(app, host="0.0.0.0", port=5600)
