FROM python:3.12-slim
ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=America/Los_Angeles

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    git \
    git-lfs \
    poppler-utils

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
ENV PYTHONPATH /app/

CMD fastapi run --host 0.0.0.0 --port 8000 --workers 1 api.py
