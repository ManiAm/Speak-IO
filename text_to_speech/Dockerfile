FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV CUDACXX=/usr/local/cuda/bin/nvcc

RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    libespeak-ng-dev

WORKDIR /app

ENV VENV_PATH=/venv

RUN python3 -m venv $VENV_PATH && \
    $VENV_PATH/bin/pip install --upgrade pip && \
    $VENV_PATH/bin/pip install --no-cache-dir \
        fastapi \
        uvicorn \
        jinja2 \
        numpy \
        TTS \
        piper-tts \
        git+https://github.com/suno-ai/bark.git \
        py-espeak-ng

RUN $VENV_PATH/bin/pip install --no-cache-dir \
        chatterbox-tts

ENV PATH="$VENV_PATH/bin:$PATH"

EXPOSE 5500

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5500"]
