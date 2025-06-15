
import torch
from faster_whisper import WhisperModel
from faster_whisper.utils import available_models


class FasterWhisperEngine:

    def __init__(self):

        self.models = {}


    def get_models(self):

        model_list = available_models()
        return model_list


    def load_model(self, model_name, compute_type="float32"):

        device = "cuda" if torch.cuda.is_available() else "cpu"

        if model_name not in self.models:

            try:
                self.models[model_name] = WhisperModel(model_name, device=device, compute_type=compute_type)
            except Exception as e:
                return False, str(e)

        return True, f"Loaded Faster-Whisper model '{model_name}' on '{device}' with precision '{compute_type}'"


    def transcribe(self, audio_path, model_name):

        if model_name not in self.models:
            return False, f"Model '{model_name}' not loaded"

        model = self.models[model_name]

        try:

            segments, _ = model.transcribe(
                audio_path,
                language=None,
                vad_filter=True,
                no_repeat_ngram_size=2
            )

            transcript = " ".join([s.text for s in segments])
            return True, transcript.strip()

        except Exception as e:
            return False, str(e)
