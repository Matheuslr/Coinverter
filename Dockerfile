FROM python:3.9.6-slim-bullseye

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc g++ make cmake curl jq git \
    libtool autoconf automake pkg-config \
    build-essential unixodbc-dev \
    wait-for-it \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala libddwaf (necessária para ddtrace com AppSec)
RUN git clone https://github.com/DataDog/libddwaf.git /tmp/libddwaf && \
    cd /tmp/libddwaf && mkdir build && cd build && \
    cmake .. && make && make install && \
    ldconfig && rm -rf /tmp/libddwaf

# Atualiza pip
RUN pip install --no-cache-dir --upgrade pip

# Copia o código e entra no diretório
COPY . /server/
WORKDIR /server

# Copia variáveis de ambiente (caso use Makefile)
RUN make copy-envs || echo "make copy-envs falhou (ignorado para build local)"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Ajusta usuário para execução segura
RUN usermod -u 1000 www-data && usermod -G staff www-data
USER www-data
