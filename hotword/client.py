
import sys
import asyncio
import websockets
import json

async def main():

    uri = "ws://localhost:5600/api/hotword/listen"

    async with websockets.connect(uri) as websocket:

        params = {
            "hotwords": ["hey jarvis", "hey agent"],
            "model_engine": "vosk",
            "model_name": "vosk-model-en-us-0.22",
            "dev_index": None
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
