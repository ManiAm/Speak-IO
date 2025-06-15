
# Speak-IO

short description of the project: speech-to-text and text-to-speech

picture showing speak-io with different inputs


## Speech-to-Text (STT)

Speech-to-text (STT) is a technology that converts spoken language into written text. It's widely used in virtual assistants, transcription services, accessibility tools, voice-controlled systems, and more. By translating human speech into text, STT bridges the gap between audio communication and digital text-based systems.

There are many cloud-based services that offer high-quality STT solutions (like Google Speech, Amazon Transcribe, or Microsoft Azure Speech). However, these often require an internet connection, raise concerns about data privacy, and may not be suitable for real-time or offline scenarios.

### OpenAI Whisper

[Whisper](https://github.com/openai/whisper) by OpenAI is an open-source automatic speech recognition (ASR) system trained on 680,000 hours of multilingual and multitask supervised data. It supports multiple languages and tasks such as speech translation and language identification. It runs entirely on your local machine, and does not require any Internet or cloud connectivity, making it ideal for privacy-sensitive or offline applications.

Whisper provides several model sizes (from tiny to large) that trade off between speed, accuracy, and resource usage. All models are multilingual unless the name includes `.en`, which restricts them to English but offers improved performance for that language. This makes Whisper a strong candidate for local STT systems due to its versatility and high-quality transcriptions.

### Alternatives to OpenAI Whisper

#### whisper.cpp

The official implementation of OpenAI Whisper is based on PyTorch, which can be resource-intensive and challenging to run efficiently on lower-end or embedded systems without a GPU. [whisper.cpp](https://github.com/ggml-org/whisper.cpp), developed by Georgi Gerganov (also creator of llama.cpp), is a high-performance, dependency-free implementation of Whisper written in C/C++. It is designed to work without Python, PyTorch, or any heavyweight runtime, making it ideal for cross-platform deployment in constrained environments. It supports CPU execution by default, and GPU acceleration via OpenCL, CUDA, or Apple Metal.

#### faster-whisper

[faster-whisper](https://github.com/SYSTRAN/faster-whisper) is a GPU-accelerated version of Whisper using CTranslate2 as the inference engine. It's optimized for fast, efficient inference and works well with both NVIDIA CUDA and CPU backends. Its goal is to reduce inference latency and to offer better performance than the original PyTorch version with lower memory usage.

### Real-time Streaming


Neither OpenAI Whisper nor its variants (whisper.cpp, faster-whisper) natively support real-time or streaming speech-to-text out of the box. They require the complete audio segment to be available before transcription begins.

Workarounds for Streaming:

- Chunked audio processing: Stream audio in small overlapping windows and transcribe each window.

- Custom real-time pipelines: Use a microphone/audio stream to continuously feed short segments to the model and stitch the output.

- External audio handling: Combine these STT engines with real-time audio frameworks (like WebRTC or PortAudio) for continuous input handling.


In Speak-IO, you can build your own streaming interface on top of these models by:

- Capturing audio in small windows (e.g., 1–2 seconds)
- Passing them to the backend over WebSockets
- Returning the transcribed chunks progressively



### Audio Input Methods in Speak-IO

Speak-IO supports multiple audio ingestion methods, allowing it to integrate with various frontends and use cases:

- Pre-recorded Audio Files: Upload or reference `.wav`, `.mp3`, or `.flac` files from disk or web interface and send them to the backend for batch transcription.

- Browser Microphone Input (via WebSockets): Users can record live speech directly from the browser using the MediaRecorder API or Web Audio API. Audio chunks are streamed in real-time to the backend over WebSockets for processing.

- Live Mic Input (USB or system mic): When running locally, Speak-IO can capture audio from a USB or system microphone using Python libraries like pyaudio or sounddevice, then send it to the backend for continuous inference.

- Streaming: todo


## Text-to-Speech (TTS)



## Getting Started

docker compose up -d

wait for the containers to get initialized


Endpoints speech-to-text


curl -X POST "http://localhost:5000/api/stt/models/load?engine=openai_whisper&model_name=small.en"
curl -X POST "http://localhost:5000/api/stt/models/load?engine=faster_whisper&model_name=small.en"
curl -X POST "http://localhost:5000/api/stt/models/load?engine=whisper.cpp&model_name=small.en"


curl -X POST "http://localhost:5000/api/stt/transcribe/file?engine=openai_whisper&model_name=small.en" -F "file=@/home/maniam/whisper.cpp/samples/jfk.wav"
curl -X POST "http://localhost:5000/api/stt/transcribe/file?engine=faster_whisper&model_name=small.en" -F "file=@/home/maniam/whisper.cpp/samples/jfk.wav"
curl -X POST "http://localhost:5000/api/stt/transcribe/file?engine=whisper.cpp&model_name=small.en" -F "file=@/home/maniam/whisper.cpp/samples/jfk.wav"


Endpoints text-to-speech

curl "http://localhost:5500/api/tts/models"
curl -X POST "http://localhost:5500/api/tts/models/load?engine=piper&model_name=en_US-lessac-medium"
curl "http://localhost:5500/api/tts/synthesize?text=Hello%20world&engine=piper&model_name=en_US-lessac-medium" --output hello.wav


## voice-ui

uses web socket to send audio

also it can read text


[sample.mp4](https://github.com/ManiAm/SpeakIO/raw/master/preview/tik-tok.mp4)


-------------

Most TTS models have a limited input vocabulary, especially when working in phoneme mode or using graphemes with predefined token sets.

The errors you're seeing:

[!] Character '͡' not found in the vocabulary. Discarding it.
[!] Character '—' not found in the vocabulary. Discarding it.
[!] Character '“' not found in the vocabulary. Discarding it.

are due to special or non-ASCII characters not being part of the model’s accepted input range.



------------

faster-whisper is ideal if you have a GPU and want better-than-real-time transcription speeds, especially on larger models.

filter stage prepare audio file before being fed to whisper - check manual - i think audo should be wave?

