FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV CUDACXX=/usr/local/cuda/bin/nvcc

###########

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    ccache \
    curl \
    sox \
    python3 \
    python3-pip \
    python3-venv \
    python3-pyaudio \
    ffmpeg \
    libsdl2-dev \
    portaudio19-dev \
    libopenblas-dev \
    libportaudio2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

###########

RUN mkdir -p /opt/whisper.cpp

COPY entrypoint.sh /opt/
RUN chmod +x /opt/entrypoint.sh

ENV WHISPER_CPP_PATH=/opt/whisper.cpp
ENV LD_LIBRARY_PATH="$WHISPER_CPP_PATH/build/src:$LD_LIBRARY_PATH"

###########

WORKDIR /app

ENV VENV_PATH=/venv

RUN python3 -m venv $VENV_PATH && \
    $VENV_PATH/bin/pip install --upgrade pip && \
    $VENV_PATH/bin/pip install --no-cache-dir \
        fastapi \
        uvicorn \
        python-multipart \
        websockets \
        sounddevice \
        pydub \
        openai-whisper \
        faster-whisper \
        vosk

ENV PATH="$VENV_PATH/bin:$PATH"

EXPOSE 5000

ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
