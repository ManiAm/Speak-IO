
import sys
import asyncio
import websockets
import json

async def main():

    uri = "ws://localhost:5600/api/hotword/listen"

    async with websockets.connect(uri) as websocket:

        params = {
            "dev_index": None,                                   # Audio input device index (None = default)
            "hotwords": ["hey jarvis", "hey agent"],             # List of trigger phrases to activate STT
            "model_engine_hotword": "vosk",                      # hotword detection engine to use
            "model_name_hotword": "vosk-model-en-us-0.22",       # Name of the specific model to load
            "model_engine_stt": "openai_whisper",                # STT engine to use
            "model_name_stt": "small.en",                        # Name of the specific model to load
            "target_latency": 100,                               # Desired processing latency (in milliseconds)
            "silence_duration": 3                                # Duration of silence (in seconds) to stop recording
        }

        print("Setting up hotword detection. Please wait...", flush=True)
        await websocket.send(json.dumps(params))

        while True:

            try:
                msg = await websocket.recv()
                print("SERVER:", msg, flush=True)
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed by server.", flush=True)
                break


def run():

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nForced shutdown.")
        sys.exit(1)


if __name__ == "__main__":

    run()
