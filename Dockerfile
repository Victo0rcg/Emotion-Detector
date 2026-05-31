FROM python:3.12-slim

WORKDIR /app

# System dependencies needed by OpenCV and DeepFace
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create folders the app expects
RUN mkdir -p uploads instance

ENV PORT=8080

# Use a threaded worker to allow concurrent requests without multiplying TF memory use
CMD ["python", "-m", "gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--timeout", "120", "--workers", "1", "--threads", "4", "--worker-class", "gthread"]


