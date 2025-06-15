
import re
import nltk
import unicodedata
from nltk.tokenize import sent_tokenize


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
