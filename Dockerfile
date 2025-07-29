# --------------------
# Base image (Debian slim)
# --------------------
FROM python:3.9.6-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LD_LIBRARY_PATH=/usr/local/lib

# --------------------
# Stage 1: Build
# --------------------
FROM base AS builder

# Instala ferramentas de build e libs necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc g++ make cmake git \
        curl jq bash \
        libffi-dev \
        libssl-dev \
        unixodbc-dev \
        libtool autoconf automake pkg-config \
        python3-dev \
        libstdc++6 \
    && pip install --upgrade pip wheel setuptools \
    && rm -rf /var/lib/apt/lists/*

# Diretório da aplicação
WORKDIR /app

# Copia apenas requirements.txt primeiro (melhor cache)
COPY requirements.txt .

# Cria requirements modificado sem ddtrace problemático
RUN cp requirements.txt requirements_backup.txt && \
    # Remove ddtrace problemático e adiciona versão mais recente
    sed -i '/^ddtrace==/d' requirements.txt && \
    echo "ddtrace>=2.0.0" >> requirements.txt

# Instala dependências Python (sem ddtrace problemático)
RUN pip install --no-cache-dir -r requirements.txt

# Instala ddtrace sem AppSec (evita compilação libddwaf)
RUN pip install --no-cache-dir "ddtrace[profiling]>=2.0.0" --no-deps || \
    pip install --no-cache-dir "ddtrace>=1.8.0" --no-deps || \
    pip install --no-cache-dir ddtrace==1.0.2 --no-build-isolation --force-reinstall

# Copia resto do código (depois das dependências para melhor cache)
COPY . .

# Executa make se existir
RUN make copy-envs || echo "make copy-envs falhou"

# --------------------
# Stage 2: Runtime
# --------------------
FROM base AS runtime

# Instala apenas runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl jq bash \
        unixodbc \
        libstdc++6 \
        libffi7 \
    && rm -rf /var/lib/apt/lists/* \
    && usermod -u 1000 www-data && usermod -aG staff www-data

# Copia pacotes Python instalados
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia o código da aplicação
COPY --from=builder /app /app

WORKDIR /app
USER www-data
