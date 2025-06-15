
import os
import json
import requests
import wave
from vosk import Model, KaldiRecognizer

import utility
import ffmpeg

MODEL_PRE_URL = "https://alphacephei.com/vosk/models/"
MODEL_LIST_URL = MODEL_PRE_URL + "model-list.json"


class VoskEngine:

    def __init__(self):

        self.models = {}


    def get_models(self):

        try:
            response = requests.get(MODEL_LIST_URL, timeout=10)
            model_list = response.json()
            models = [entry["name"] for entry in model_list if "name" in entry]
            return models
        except Exception as e:
            print(f"Error: getting vosk models failed: {e}")
            return []


    def load_model(self, model_name):

        if model_name not in self.models:

            try:
                self.models[model_name] = Model(model_name=model_name)
            except Exception as e:
                return False, str(e)

        return True, f"Loaded Vosk model '{model_name}'"


    def transcribe(self, audio_path, model_name, chunk_size=4000):

        if model_name not in self.models:
            return False, f"Model '{model_name}' not loaded"

        model = self.models[model_name]

        if not utility.is_wav_file(audio_path):

            directory = os.path.dirname(audio_path)
            basename = os.path.splitext(os.path.basename(audio_path))[0]
            wav_path = os.path.join(directory, f"{basename}.wav")

            status, output = ffmpeg.convert_to_wav(audio_path, wav_path)
            if not status:
                return False, f"FFmpeg conversion error: {output}"

            audio_path = wav_path

        try:
            wf = wave.open(audio_path, "rb")
            if wf.getnchannels() != 1 or wf.getframerate() != 16000:
                return False, "Audio must be mono and 16kHz."
        except Exception as e:
            return False, f"Opening audio file failed: {str(e)}"

        try:

            recognizer = KaldiRecognizer(model, wf.getframerate())

            results = []

            while True:

                data = wf.readframes(chunk_size)
                if len(data) == 0:
                    break

                if recognizer.AcceptWaveform(data):
                    result_json = json.loads(recognizer.Result())
                    results.append(result_json.get("text", ""))

            final_result_json = json.loads(recognizer.FinalResult())
            results.append(final_result_json.get("text", ""))

            full_transcript = " ".join(results)
            return True, full_transcript.strip()

        except Exception as e:
            return False, f"Transcription failed: {str(e)}"
