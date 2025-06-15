
import os
import wave
import io
from pathlib import Path
from collections import defaultdict

from piper import PiperVoice
from piper.download import get_voices, ensure_voice_exists


class PiperEngine:

    def __init__(self):

        self.models = {}


    def get_models(self):

        cwd = os.getcwd()
        voices = get_voices(download_dir=cwd, update_voices=True)

        grouped_models = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for model_name, details in voices.items():

            language = details.get("language", None)
            if not language:
                continue

            language_code = language.get("code", None)
            if not language_code:
                continue

            name = details.get("name", None)
            if not name:
                continue

            quality = details.get("quality", None)
            if not quality:
                continue

            grouped_models[language_code][name][quality].append(model_name)

        return grouped_models


    def load_model(self, tts_model, model_dir="~/.local/share/tts/piper"):

        if tts_model not in self.models:

            model_dir = Path(model_dir).expanduser()
            model_dir.mkdir(parents=True, exist_ok=True)

            voices = get_voices(download_dir=model_dir, update_voices=True)

            ensure_voice_exists(
                name=tts_model,
                data_dirs=[model_dir],
                download_dir=model_dir,
                voices_info=voices,
            )

            onnx_path = model_dir / f"{tts_model}.onnx"
            if not onnx_path.exists():
                return False, f"Model file not found after download: {onnx_path}"

            voice = PiperVoice.load(onnx_path)

            self.models[tts_model] = voice

        return True, f"Loaded Piper TTS voice '{tts_model}'"


    def synthesize(self, text, tts_model):

        if tts_model not in self.models:
            return False, f"Model '{tts_model}' not loaded"

        voice = self.models[tts_model]

        try:

            with io.BytesIO() as wav_io:

                with wave.open(wav_io, "wb") as wav_file:

                    wav_file.setnchannels(1)       # mono
                    wav_file.setsampwidth(2)       # 16-bit PCM = 2 bytes
                    wav_file.setframerate(22050)   # Common Piper sample rate (22,050 Hz)

                    voice.synthesize(text, wav_file)

                wav_data = wav_io.getvalue()

        except Exception as e:
            return False, f"synthesize failed: {e}"

        return True, wav_data
