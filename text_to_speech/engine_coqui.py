
import torch
from collections import defaultdict

from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

import utility


torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    XttsArgs,
    BaseDatasetConfig
])


class CoquiEngine:

    def __init__(self):

        self.models = {}


    def get_models(self):

        model_mgr = TTS().list_models()
        model_list = model_mgr.list_models()

        grouped_models = defaultdict(lambda: defaultdict(list))

        for model in model_list:

            parts = model.split("/")
            if len(parts) < 4:
                continue

            model_type, lang, dataset, model_name = parts
            grouped_models[model_type][lang].append(model)

        return grouped_models


    def load_model(self, tts_model):

        device = "cuda" if torch.cuda.is_available() else "cpu"

        if tts_model not in self.models:

            try:
                self.models[tts_model] = TTS(tts_model).to(device)
            except Exception as e:
                return False, str(e)

        return True, f"Loaded Coqui TTS model '{tts_model}' on {device}"


    def synthesize(self, text, tts_model, vocoder_model=None):

        if tts_model not in self.models:
            return False, f"Model '{tts_model}' not loaded"

        model = self.models[tts_model]

        try:

            wav_array = model.tts(text=text, vocoder_path=vocoder_model)
            wav_data = utility.write_normalized_wav_bytes(wav_array, 22050)
            return True, wav_data

        except Exception as e:
            return False, f"synthesize failed: {e}"
