# Build stage
FROM python:3.9.6-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libffi-dev libssl-dev unixodbc-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Instala dependências com fallback inteligente
RUN pip install --no-cache-dir -U pip wheel && \
    pip install --no-cache-dir -r requirements.txt || \
    (sed '/^ddtrace/d' requirements.txt > r.txt && \
     pip install --no-cache-dir -r r.txt && \
     pip install --no-cache-dir "ddtrace>=2.0.0" 2>/dev/null || true)

COPY . .

# Runtime stage
FROM python:3.9.6-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unixodbc libffi7 libssl1.1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -r -u 1000 app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

RUN chown -R app:app /app
WORKDIR /app
USER app

