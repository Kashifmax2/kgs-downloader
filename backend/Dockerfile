FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends     ffmpeg     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000

# Use shell form so $PORT is expanded at container runtime by the shell.
# Provide a default of 8000 if PORT is not set by the environment.
ENTRYPOINT sh -c 'exec gunicorn main:app --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4'
