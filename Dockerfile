FROM python:3.9.6-slim-bullseye

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc g++ make curl jq wait-for-it \
    build-essential unixodbc-dev \
    git cmake libtool autoconf automake pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# (Opcional) Instala libddwaf se usar ddtrace com AppSec
RUN git clone https://github.com/DataDog/libddwaf.git /tmp/libddwaf && \
    cd /tmp/libddwaf && mkdir build && cd build && \
    cmake .. && make && make install && ldconfig && \
    rm -rf /tmp/libddwaf

# Atualiza pip
RUN pip install --no-cache-dir --upgrade pip

# Copia o código e entra no diretório
COPY . /server/
WORKDIR /server

# Copia variáveis de ambiente, se necessário
RUN make copy-envs

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Configura o usuário
RUN usermod -u 1000 www-data && usermod -G staff www-data
USER www-data
