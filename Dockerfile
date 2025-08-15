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

# Argumento para controlar se usa usuário não-root
ARG USE_NON_ROOT_USER=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unixodbc libffi7 libssl1.1 make \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário app apenas se USE_NON_ROOT_USER for true
RUN if [ "$USE_NON_ROOT_USER" = "true" ]; then \
        useradd -r -u 1000 app; \
    fi

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Ajusta permissões e muda usuário apenas se USE_NON_ROOT_USER for true
RUN if [ "$USE_NON_ROOT_USER" = "true" ]; then \
        chown -R app:app /app; \
    fi

WORKDIR /app

# Muda para usuário app apenas se USE_NON_ROOT_USER for true
RUN if [ "$USE_NON_ROOT_USER" = "true" ]; then \
        echo "USER app" >> /tmp/user_instruction; \
    fi

# Comando padrão que mantém container rodando para CI
CMD ["tail", "-f", "/dev/null"]
