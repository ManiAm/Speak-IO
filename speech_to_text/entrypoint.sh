#!/bin/bash
set -e

cd /opt

if [ ! -f whisper.cpp/build/bin/whisper-cli ]; then
    echo "[INFO] Building whisper.cpp at runtime..."
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp
    git checkout v1.7.5
    cmake -B build -DGGML_CUDA=ON
    cmake --build build --config Release -- -j$(nproc)
    cmake --install build
else
    echo "[INFO] whisper-cli already built. Skipping rebuild."
fi

cd /app

# Execute the CMD passed in Dockerfile
exec "$@"
