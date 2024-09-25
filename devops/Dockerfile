FROM python:3.10 AS builder

WORKDIR /src

RUN apt-get update && apt-get install -y \
    git \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

WORKDIR /src/myop

CMD kopf run --liveness=http://0.0.0.0:5000/healthz -A --peering=mysql-operator
