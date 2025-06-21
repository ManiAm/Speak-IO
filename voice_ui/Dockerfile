FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    jinja2

COPY main.py .
COPY static/ ./static/
COPY templates/ ./templates/

EXPOSE 5700

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5700"]
