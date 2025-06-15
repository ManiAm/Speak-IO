
import re
import unicodedata


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
