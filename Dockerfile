# --------------------
# Base image (Debian slim)
# --------------------
FROM python:3.9.6-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --------------------
# Stage 1: Build
# --------------------
FROM base AS builder

# Instala apenas dependências essenciais para build
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl jq bash \
        libffi-dev \
        libssl-dev \
        unixodbc-dev \
        python3-dev \
    && pip install --upgrade pip wheel \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia requirements.txt e cria versão sem ddtrace problemático
COPY requirements.txt requirements_original.txt

# Remove ddtrace problemático e instala dependências restantes
RUN grep -v "^ddtrace" requirements_original.txt > requirements_clean.txt && \
    pip install --no-cache-dir -r requirements_clean.txt

# Tenta instalar ddtrace de diferentes formas (do mais novo para mais antigo)
RUN pip install --no-cache-dir "ddtrace>=2.8.0" || \
    pip install --no-cache-dir "ddtrace>=2.0.0" || \
    pip install --no-cache-dir "ddtrace>=1.18.0" || \
    pip install --no-cache-dir "ddtrace==1.17.0" || \
    (echo "Instalando ddtrace sem AppSec..." && \
     pip install --no-cache-dir ddtrace==1.0.2 --no-binary ddtrace --install-option="--without-appsec") || \
    (echo "Fallback: ddtrace básico sem extensões C..." && \
     DD_COMPILE_DEBUG=1 pip install --no-cache-dir ddtrace==1.0.2 --no-deps --force-reinstall)

# Copia código da aplicação
COPY . .

# Executa make se existir
RUN make copy-envs || echo "make copy-envs falhou ou não existe"

# --------------------
# Stage 2: Runtime
# --------------------
FROM base AS runtime

# Instala apenas runtime dependencies mínimas
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl jq bash \
        unixodbc \
        libffi7 \
    && rm -rf /var/lib/apt/lists/* \
    && usermod -u 1000 www-data && usermod -aG staff www-data

# Copia apenas pacotes Python necessários
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia aplicação
COPY --from=builder /app /app

WORKDIR /app
USER www-data
