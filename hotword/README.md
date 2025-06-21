
# Hotword Detection

Hotword detection - also known as "wake word" detection - is a specialized speech processing technique used to identify a specific keyword or phrase (like "Hey Siri" "OK Google" or "Alexa") within a continuous audio stream. When the hotword is detected, the system transitions from a passive or low-power state into an active listening mode, ready to process full user commands or begin full transcription.

Although it is not full speech-to-text, hotword detection can be considered a lightweight, task-specific form of speech recognition with stricter constraints. It is designed to operate with:

- Low latency for instant responsiveness
- High accuracy, even across accents and noise
- Low computational footprint, suitable for edge devices
- Always-on capability, often running continuously in the background
- Offline operation, to preserve privacy and reduce reliance on cloud APIs

This design makes hotword detection especially valuable in voice-enabled applications where continuous transcription would be computationally expensive, power-intensive, or privacy-sensitive. By filtering for specific trigger phrases, hotword detectors enable efficient and intentional user engagement in smart assistants, mobile apps, automotive systems, and IoT devices.

## Techniques

There are several methods to implement hotword detection, with varying trade-offs in accuracy, latency, resource usage, and customizability.

- **Pattern Matching-Based Detection**: This approach uses traditional signal processing techniques to continuously analyze the audio stream for acoustic patterns that match a predefined keyword. Features such as MFCC (Mel-Frequency Cepstral Coefficients) are extracted and compared against a stored template using statistical models like Hidden Markov Models (HMMs) or rule-based matching. It’s lightweight and fast, making it suitable for simple or embedded systems, but often lacks robustness in noisy environments or with different speaker accents. Examples: PocketSphinx, early Kaldi-based systems, Vosk.

- **Transcription-Based Keyword Spotting**: This method uses a speech-to-text system to transcribe the incoming audio stream in real time or near real time. The resulting text is then scanned for the presence of keywords using exact, fuzzy, or semantic matching. It offers the highest flexibility (supporting arbitrary phrases without retraining) but tends to be more resource-intensive and has higher latency compared to dedicated hotword detectors. Examples: OpenAI Whisper, faster-whisper.

- **Per-Keyword Acoustic Modeling**: This method trains a separate acoustic model specifically for each hotword, often using a small set of user-provided audio samples. The system learns to distinguish the hotword from background noise and other speech patterns using models like GMMs or small neural networks. It allows for customizable, offline hotword detection with relatively low resource usage, but typically requires manual training and does not scale well to many keywords. Examples: [Snowboy](https://github.com/Kitt-AI/snowboy).

- **General-Purpose Neural Network Detection**: This approach employs a single, compact neural network trained to recognize one or more predefined hotwords across different speakers and environments. Rather than requiring separate training for each keyword, it uses compiled acoustic representations to match keywords efficiently in real time. These models are highly accurate, low-latency, and well-suited for deployment on mobile or embedded platforms. Examples: [Porcupine](https://github.com/Picovoice/porcupine).

## Speak-IO Hotword Detection

In the context of STT systems like Speak-IO, hotword detection can be used to trigger the start of recording or transcription automatically, reducing the need for manual interaction like clicking a "Start" button. This makes the experience more natural and streamlined, especially in hands-free or accessibility-focused scenarios. You can find an implemetation of hotword detection using Vosk engine in [here](main.py).
