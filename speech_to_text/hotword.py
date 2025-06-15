
import subprocess
import speech_recognition as sr

TRIGGER = "hey agent"
MODEL = "/app/whisper.cpp/models/ggml-tiny.en.bin"
WHISPER = "/app/whisper.cpp/main"


def listen_for_hotword():

    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:

        print("[HOTWORD] Calibrating mic...")

        r.adjust_for_ambient_noise(source)

        print("[HOTWORD] Listening for trigger...")

        while True:

            audio = r.listen(source)
            try:
                text = r.recognize_google(audio).lower()
                print(f"[HOTWORD] Heard: {text}")
                if TRIGGER in text:
                    print("[HOTWORD] Trigger detected!")
                    record_and_transcribe()
            except Exception as e:
                continue


def record_and_transcribe():

    print("[RECORD] Listening after hotword... (5s)")

    output_wav = "/tmp/triggered.wav"
    subprocess.run(["ffmpeg", "-y", "-f", "alsa", "-i", "default", "-t", "5", "-ac", "1", "-ar", "16000", output_wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("[WHISPER] Transcribing...")
    subprocess.run([WHISPER, "-m", MODEL, "-f", output_wav, "-nt", "-np", "-ml", "500", "-mc", "4"])


if __name__ == "__main__":

    listen_for_hotword()
