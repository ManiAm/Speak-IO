
import os
import uuid
import tempfile
import logging
import uvicorn
import asyncio

from fastapi import FastAPI, WebSocket, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from fastapi import APIRouter

import config
import ffmpeg
import stt_models

logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(
    title="Speak-IO STT API",
    description="speech-to-text API supporting multiple engines and models.",
    version="1.0.0",
    docs_url="/api/docs",  # localhost:5000/api/docs
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


@router.get("/models")
async def get_models():

    status, output = stt_models.get_models()
    if not status:
        raise HTTPException(status_code=500, detail=output)

    return {"models": output}


@router.get("/models/{engine}")
async def get_models_engine(engine: str):

    status, output = stt_models.get_models_engine(engine)
    if not status:
        raise HTTPException(status_code=500, detail=output)

    return {"models": output}


@router.post("/models/load")
async def load_model(engine: str = Query(...), model_name: str = Query(...)):

    status, output = stt_models.load_model_for_engine(engine, model_name)
    if not status:
        raise HTTPException(status_code=500, detail=output)

    return {"message": output}


@router.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...), engine: str = Query("openai_whisper"), model_name: str = Query("small.en")):

    original_filename = file.filename or "uploaded_file"
    base, ext = os.path.splitext(original_filename)

    unique_id = uuid.uuid4().hex
    filename = f"{base}_{unique_id}{ext}"
    file_path = os.path.join(config.upload_dir, filename)

    try:

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        status, output = stt_models.transcribe(file_path, engine, model_name)
        if not status:
            raise HTTPException(status_code=400, detail=output)

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)

    return {"transcript": output}


@router.websocket("/transcribe/stream")
async def transcribe_stream(websocket: WebSocket, engine: str = Query("openai_whisper"), model_name: str = Query("small.en")):

    await websocket.accept()

    unique_id = uuid.uuid4().hex
    webm_path = os.path.join(tempfile.gettempdir(), f"upload_{unique_id}.webm")
    wav_path = webm_path.replace(".webm", ".wav")
    timeout = 60

    try:

        with open(webm_path, "wb") as f:

            try:
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=timeout)
                if data:
                    f.write(data)
                else:
                    print("Empty payload received.")
                    await websocket.close()
                    return
            except asyncio.TimeoutError:
                print(f"No audio received from client within {timeout}s.")
                await websocket.close()
                return

        print(f"Saved file size: {os.path.getsize(webm_path)}")

        status, output = ffmpeg.convert_to_wav(webm_path, wav_path)
        if not status:
            await websocket.send_text(f"❌ FFmpeg conversion error: {output}")
            await websocket.close()
            return

        status, output = stt_models.transcribe(wav_path, engine, model_name)
        if not status:
            await websocket.send_text(f"❌ Error: {output}")
            await websocket.close()
            return

        await websocket.send_text(output)

    except Exception as e:

        print(f"Exception: {e}")

    finally:

        for path in [webm_path, wav_path]:
            if os.path.exists(path):
                os.remove(path)


app.include_router(router, prefix="/api/stt")


if __name__ == "__main__":

    print("Starting Speak-IO STT on http://localhost:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)
