
import torch
import whisper as openai_whisper


class OpenAIWhisperEngine:

    def __init__(self):

        self.models = {}


    def get_models(self):

        model_list = openai_whisper.available_models()
        return model_list


    def load_model(self, model_name):

        device = "cuda" if torch.cuda.is_available() else "cpu"

        if model_name not in self.models:

            try:
                self.models[model_name] = openai_whisper.load_model(model_name, device=device)
            except Exception as e:
                return False, str(e)

        model = self.models[model_name]
        dtype = next(model.parameters()).dtype

        return True, f"Loaded OpenAI Whisper model '{model_name}' on {device} with precision '{dtype}'"


    def transcribe(self, audio_path, model_name):

        if model_name not in self.models:
            return False, f"Model '{model_name}' not loaded"

        model = self.models[model_name]

        try:
            result = model.transcribe(audio_path, language=None, fp16=False)
            return True, result["text"].strip()
        except Exception as e:
            return False, f"Transcription failed: {str(e)}"
