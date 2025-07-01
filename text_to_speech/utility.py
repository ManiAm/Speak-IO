
import re
import io
import wave
import unicodedata
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
from contextlib import closing


def clean_tts_input(text: str):

    # Normalize to NFKC form to split combined characters
    text = unicodedata.normalize("NFKC", text)

    # Replace common special punctuation with ASCII equivalents
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "*",
        "´": "'",
        "͡": "",  # tie bar
    }

    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def print_cleaned_banner(text: str):

    banner_width = min(len(text), 20)
    print("\n" + "=" * banner_width)
    print(" CLEANED TTS INPUT ".center(banner_width, "-"))
    print(text)
    print("=" * banner_width + "\n")


def break_text(text: str, max_chars=250):

    # Ensure NLTK sentence tokenizer is available
    nltk.download("punkt_tab")

    # Break into sentences using NLTK
    sentences = sent_tokenize(text.strip())

    # Group short sentences together to avoid excessive splitting
    grouped_sentences = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += " " + sentence
        else:
            grouped_sentences.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        grouped_sentences.append(current_chunk.strip())

    return grouped_sentences


def write_normalized_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:

    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.90

    audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    return buf.getvalue()
