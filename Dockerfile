FROM python:3.9.6-slim-bullseye

RUN apt-get update && apt-get install gcc g++ make curl jq -y \
    wait-for-it \
    && apt-get clean && rm -rf /var/lib/apt/lists/* &&\
    apt-get update -y && \
    apt-get install build-essential unixodbc-dev -y &&\
    pip install --no-cache-dir --upgrade pip

COPY . /server/
WORKDIR /server
RUN make copy-envs

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get clean

RUN usermod -u 1000 www-data
RUN usermod -G staff www-data
USER www-data
