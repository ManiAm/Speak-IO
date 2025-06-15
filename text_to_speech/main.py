
import logging
import uvicorn
from pydantic import BaseModel

from fastapi import FastAPI, Request, Response, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from fastapi import APIRouter

import config
import utility
import tts_models

logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(
    title="Speak-IO TTS API",
    description="text-to-speech API supporting multiple engines and models.",
    version="1.0.0",
    docs_url="/api/docs",  # localhost:5500/api/docs
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

class SynthesizeParams(BaseModel):
    text: str = ""
    engine: str = "piper"
    model_name: str = "en_US-lessac-medium"


@router.get("/models")
async def get_models():

    status, output = tts_models.get_models()
    if not status:
        raise HTTPException(status_code=500, detail=output)

    return {"models": output}


@router.get("/models/{engine}")
async def get_models_engine(engine: str):

    status, output = tts_models.get_models_engine(engine)
    if not status:
        raise HTTPException(status_code=500, detail=output)

    return {"models": output}


@router.post("/models/load")
async def load_model(engine: str = Query(...), model_name: str = Query(...)):

    status, output = tts_models.load_model_for_engine(engine, model_name)
    if not status:
        raise HTTPException(status_code=500, detail=output)

    return {"message": output}


@router.get("/synthesize")
@router.post("/synthesize")
async def synthesize(request: Request, params: SynthesizeParams = Depends()):

    # If POST, try to read raw body
    if request.method == "POST":
        body = await request.body()
        text = body.decode("utf-8").strip()
    else:
        text = params.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    cleaned_text = utility.clean_tts_input(text)

    utility.print_cleaned_banner(cleaned_text)

    status, output = tts_models.synthesize(cleaned_text, params.engine, params.model_name)
    if not status:
        raise HTTPException(status_code=400, detail=output)

    return Response(content=output, media_type="audio/wav")


app.include_router(router, prefix="/api/tts")


if __name__ == "__main__":

    print("Starting Speak-IO TTS on http://localhost:5500")
    uvicorn.run(app, host="0.0.0.0", port=5500)
