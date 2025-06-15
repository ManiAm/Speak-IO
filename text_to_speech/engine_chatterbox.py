
import os
import io
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS


class ChatterBoxEngine:

    def __init__(self):

        self.model = None

        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        self.audio_prompts_dir = os.path.join(script_dir, "audio_prompts")


    def get_models(self):

        wav_files = [
            f for f in os.listdir(self.audio_prompts_dir)
            if f.lower().endswith(".wav") and os.path.isfile(os.path.join(self.audio_prompts_dir, f))
        ]

        return wav_files


    def load_model(self, tts_model):

        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

        if not self.model:
            self.model = ChatterboxTTS.from_pretrained(device=device)

        tts_model_full = os.path.join(self.audio_prompts_dir, tts_model)
        self.model.prepare_conditionals(tts_model_full, exaggeration=0.5)

        return True, f"Loaded Chatterbox TTS with audio prompt '{tts_model}' on {device}"


    def synthesize(self, text, tts_model):

        _ = tts_model

        if not self.model:
            return False, "Model not loaded"

        wav = self.model.generate(text)

        buffer = io.BytesIO()
        ta.save(buffer, wav, self.model.sr, format="wav")
        wav_data = buffer.getvalue()

        return True, wav_data
