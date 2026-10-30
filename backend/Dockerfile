FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY ingest.py ./ingest.py
# The trained food classifier (food_classifier.onnx + labels/meta JSON).
# Without this line the deployed Food Photo feature reports "model not configured".
COPY models ./models

EXPOSE 8000
# Render (and most hosts) assign the port dynamically via $PORT — binding to
# a fixed 8000 instead would make the deployed service unreachable. Falls
# back to 8000 for local `docker run` where $PORT isn't set.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
