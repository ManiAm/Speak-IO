
import pvporcupine
import sounddevice as sd
import struct
import signal
import sys

# AccessKey obtained from Picovoice Console (https://console.picovoice.ai/)
access_key = "W2Zuxd4SNsIgaU2zOyzwSuyKHTUFd7DwoGELP427YLhu1vlfBfcvnQ=="

# Graceful shutdown handler
def signal_handler(sig, frame):
    print("\n[INFO] Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Initialize Porcupine with multiple keywords
porcupine = pvporcupine.create(
    access_key=access_key,
    keywords=["picovoice", "bumblebee"]
)

# Open microphone stream
stream = sd.RawInputStream(
    samplerate=porcupine.sample_rate,
    blocksize=porcupine.frame_length,
    dtype="int16",
    channels=1
)

stream.start()

def get_next_audio_frame():
    data, _ = stream.read(porcupine.frame_length)
    return struct.unpack_from("h" * porcupine.frame_length, data)

# Hotword detection loop
print("[INFO] Listening for hotwords: picovoice, bumblebee... (Press Ctrl+C to stop)")

try:
    while True:
        audio_frame = get_next_audio_frame()
        keyword_index = porcupine.process(audio_frame)
        if keyword_index == 0:
            print("[HOTWORD] Detected `picovoice`")
        elif keyword_index == 1:
            print("[HOTWORD] Detected `bumblebee`")
except KeyboardInterrupt:
    pass
finally:
    stream.stop()
    stream.close()
    porcupine.delete()
    print("[INFO] Cleaned up resources.")
