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

WORKDIR /app

ENV VENV_PATH=/venv

RUN python3 -m venv $VENV_PATH && \
    $VENV_PATH/bin/pip install --upgrade pip && \
    $VENV_PATH/bin/pip install --no-cache-dir \
        setuptools  \
        fastapi \
        uvicorn \
        requests \
        numpy \
        scipy \
        python-dotenv \
        soundfile \
        cffi \
        webrtcvad \
        sounddevice \
        pydub \
        vosk

ENV PATH="$VENV_PATH/bin:$PATH"

EXPOSE 5600

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5600"]
