# Stage 1: Builder
FROM python:3.9-slim-buster as builder

WORKDIR /app

# Install build dependencies for ping3 (if any, though ping3 is pure python)
# and for pip itself
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.9-slim-buster

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the application code
COPY app.py .

CMD ["python", "app.py"]