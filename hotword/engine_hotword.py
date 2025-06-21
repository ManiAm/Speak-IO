
import os
import sys
import json
import queue
import time
import tempfile
import gc
import wave
import webrtcvad
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
from scipy.signal import resample

import utility
from speech_to_text_api import STT_REST_API_Client


class HotwordEngine():

    def __init__(self):

        self.stt_client = STT_REST_API_Client(url="http://speech_to_text:5000/api/stt")

        if not self.stt_client.check_health():
            print("SST service is not reachable")
            sys.exit(1)

        status, output = self.stt_client.load_model("openai_whisper", "small.en")
        if not status:
            print(f"loading STT model failed: {output}")
            sys.exit(1)

        self.input_dev_index = None
        self.input_dev_sample_rate = None
        self.input_dev_channels = None
        self.vosk_model = None
        self.vosk_recognizer = None
        self.hotword_list = []

        self.script_interrupted = False
        self.q = queue.Queue()

        self.vad = webrtcvad.Vad(3)
        self.target_rate = 16000

        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        sound_dir = os.path.join(script_dir, "sounds")
        self.hotword_sound = os.path.join(sound_dir, "bell_1.wav")


    def init_hotword(self, dev_index=None, model_engine="vosq", model_name="vosk-model-en-us-0.22"):

        status, output = self.__init_input_device(dev_index)
        if not status:
            return False, output

        status, output = self.__init_engine(model_engine, model_name)
        if not status:
            return False, output

        return True, None


    def __init_input_device(self, dev_index):

        dev_info_default = utility.get_default_input_device()
        print(f'\nDefault input device: [{dev_info_default["index"]}] {dev_info_default["name"]} (hostapi: {dev_info_default["hostapi_name"]})')

        if not dev_index:

            mic_only, _, _ = utility.get_audio_devices()

            dev_index = utility.select_best_microphone(mic_only)
            if dev_index is None:
                return False, "__init_input_device: No suitable input device found."

        dev_info = utility.get_device_info(dev_index)
        if not dev_info:
            return False, f"Cannot obtain device info with index {dev_index}."

        print(f'\nUsing input device: [{dev_info["index"]}] {dev_info["name"]} (hostapi: {dev_info["hostapi_name"]})')

        self.input_dev_index = dev_index
        self.input_dev_sample_rate = int(dev_info["rate"])
        self.input_dev_channels = dev_info["in_ch"]

        return True, None


    def __init_engine(self, model_engine, model_name):

        if model_engine != "vosk":
            return False, "Unsupported engine"

        print(f"\n🔄 Loading Vosk model '{model_name}'...")

        try:

            self.vosk_model = Model(model_name=model_name)
            self.vosk_recognizer = KaldiRecognizer(self.vosk_model, self.input_dev_sample_rate)
            self.vosk_recognizer.SetWords(True) # enable word-level recognition output

        except Exception as e:
            return False, str(e)

        return True, None


    def stop_hotword_detection(self):

        print("Stopping hotword detection...")

        self.script_interrupted = True

        # wait for loops to terminate
        time.sleep(3)

        self.vosk_recognizer = None
        self.vosk_model = None

        self.script_interrupted = False

        gc.collect()


    def detect_hotword_and_transcribe(self, hotword_list, on_transcription_callback=None, target_latency_ms=100):

        if self.input_dev_index is None:
            print("hotword detection is not initialized!")
            sys.exit(1)

        self.hotword_list = [x.lower() for x in hotword_list]
        blocksize = self.__choose_blocksize(target_latency_ms=target_latency_ms)

        while not self.script_interrupted:

            print(f"\nListening for hotwords '{self.hotword_list}'...")

            self.__start_hotword_detection(blocksize)

            if not self.script_interrupted:

                callback, audio_frames = self.__record_callback()

                with sd.RawInputStream(
                    device=self.input_dev_index,
                    samplerate=self.input_dev_sample_rate,
                    blocksize=blocksize,
                    dtype='int16',
                    channels=self.input_dev_channels,
                    callback=callback) as stream:

                    print("Recording started...")
                    while stream.active:
                        sd.sleep(100)

                if audio_frames:

                    status, output = self.__recording_done_callback(audio_frames)
                    if not status:
                        print(f"Error: {output}")
                    elif on_transcription_callback:
                        on_transcription_callback(output)


    def __choose_blocksize(self, target_latency_ms):

        block_duration_sec = target_latency_ms / 1000
        blocksize = int(self.input_dev_sample_rate * block_duration_sec)
        return blocksize


    def __start_hotword_detection(self, blocksize):

        with sd.RawInputStream(
            device=self.input_dev_index,
            samplerate=self.input_dev_sample_rate,
            blocksize=blocksize,
            dtype='int16',
            channels=self.input_dev_channels,
            callback=self.__audio_callback):

            while not self.script_interrupted:

                data = self.q.get()

                if self.vosk_recognizer.AcceptWaveform(data):

                    result = json.loads(self.vosk_recognizer.Result())
                    text = result.get("text", "").lower()

                    if not text:
                        continue

                    print(f"[VOICE] {text}")

                    for word in self.hotword_list:
                        if word in text:
                            print(f"🔊 Hotword detected: {word}")
                            utility.play_wav(self.hotword_sound)
                            return

                else:
                    # partial results:
                    # partial = json.loads(recognizer.PartialResult())["partial"]
                    pass


    def __audio_callback(self, indata, frames, time_info, status):

        if status:
            print(f"[STATUS] {status}", file=sys.stderr)
        self.q.put(bytes(indata))


    def __record_callback(self, frame_duration_ms=30, silence_duration=3):

        frame_size = int(self.input_dev_sample_rate * frame_duration_ms / 1000) * 2  # in bytes

        buffer = bytearray()
        audio_frames = []
        silence_start = None

        def callback(indata, frames, time_info, status):

            nonlocal buffer, silence_start, audio_frames

            pcm = bytes(indata)
            buffer.extend(pcm)
            audio_frames.append(pcm)

            while not self.script_interrupted and len(buffer) >= frame_size:
                frame_bytes = bytes(buffer[:frame_size])
                buffer = buffer[frame_size:]

                if self.__is_silence(frame_bytes, self.input_dev_sample_rate, frame_duration_ms):
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > silence_duration:
                        raise sd.CallbackStop()
                else:
                    silence_start = None

        return callback, audio_frames


    def __is_silence(self, pcm_bytes, original_rate, frame_duration_ms):

        # Convert bytes to int16 numpy array
        pcm_data = np.frombuffer(pcm_bytes, dtype=np.int16)

        # Compute how many samples are expected after resampling
        original_samples = len(pcm_data)
        target_samples = int(original_samples * self.target_rate / original_rate)

        # Resample to self.target_rate (16000 Hz)
        resampled = resample(pcm_data, target_samples).astype(np.int16)
        resampled_bytes = resampled.tobytes()

        # Ensure frame length matches allowed durations
        expected_bytes = int(self.target_rate * frame_duration_ms / 1000) * 2
        if len(resampled_bytes) != expected_bytes:
            return True  # Treat bad frames as silence

        return not self.vad.is_speech(resampled_bytes, self.target_rate)


    def __recording_done_callback(self, audio_frames):

        print("Recording stopped due to silence")

        temp_file = None

        try:

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(self.input_dev_channels)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(self.input_dev_sample_rate)
                wf.writeframes(b''.join(audio_frames))

            temp_file.close()

            print("Sending audio to backend for transcription...")

            status, output = self.stt_client.transcribe_file(temp_file.name, "openai_whisper", "small.en")
            if not status:
                return False, output

            return True, output.get("transcript", "")

        except Exception as e:
            return False, str(e)

        finally:

            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)
