
import os
import numpy as np

from bark import SAMPLE_RATE, generate_audio
from bark.generation import load_model as load_model_bark, load_codec_model
from bark.generation import SUPPORTED_LANGS

import utility


class BarkEngine:

    def __init__(self):

        self.model_loaded = False


    def get_models(self):

        # https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683?v=bc67cff786b04b50b3ceb756fd05f68c
        speakers = {"announcer"}
        for _, lang in SUPPORTED_LANGS:
            for prefix in ("", f"v2{os.path.sep}"):
                for n in range(10):
                    speakers.add(f"{prefix}{lang}_speaker_{n}")

        sorted_speakers = sorted(list(speakers))

        return sorted_speakers


    def load_model(self, tts_model):

        _ = tts_model

        if not self.model_loaded:

            # Force PyTorch to allow full deserialization (fix for PyTorch 2.6+)
            os.environ['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'

            force_reload = False

            # ~/.cache/suno/bark_v0./...

            print("\nLoading text model...")

            _ = load_model_bark(
                model_type="text",
                use_gpu=True,
                use_small=False,
                force_reload=force_reload)

            print("\nLoading coarse model...")

            _ = load_model_bark(
                model_type="coarse",
                use_gpu=True,
                use_small=False,
                force_reload=force_reload,
            )

            print("\nLoading fine model...")

            _ = load_model_bark(
                model_type="fine",
                use_gpu=True,
                use_small=False,
                force_reload=force_reload
            )

            print("\nLoading codec model...")

            _ = load_codec_model(
                use_gpu=True,
                force_reload=force_reload)

            print("\nAll models loaded.\n")

            self.model_loaded = True

        return True, f"Loaded Bark TTS on cuda"


    def synthesize(self, text, tts_model, silence_second=0.5):

        if not self.model_loaded:
            return False, f"Model not loaded"

        grouped_sentences = utility.break_text(text)

        # Generate and concatenate audio for each chunk
        audio_segments = []
        for i, chunk in enumerate(grouped_sentences):
            print(f"\n[{i+1}/{len(grouped_sentences)}] Synthesizing: {chunk[:60]}...")
            audio = generate_audio(chunk, history_prompt=tts_model)
            audio_segments.append(audio)
            # insert silence between chunks
            audio_segments.append(np.zeros(int(SAMPLE_RATE * silence_second)))

        # Combine all segments into final output
        final_audio = np.concatenate(audio_segments)

        wav_data = utility.write_normalized_wav_bytes(final_audio, SAMPLE_RATE)
        return True, wav_data
