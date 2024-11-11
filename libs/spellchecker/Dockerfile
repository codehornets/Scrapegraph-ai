ARG FROM_IMAGE=public.ecr.aws/bitnami/python:3.11-debian-12
FROM --platform=linux/amd64 $FROM_IMAGE

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev gcc g++ wget git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Configure apt to exclude Python updates
RUN apt-mark hold python3 python3-dev python3-pip

# Install hunspell dependencies
RUN apt-get update && apt-get install -y --fix-missing \
    build-essential \
    libhdf5-serial-dev \
    libhunspell-dev \
    hunspell \
    hunspell-en-us \
    hunspell-de-at\
    hunspell-de-ch \
    hunspell-de-de \
    hunspell-de-med \
    hunspell-en-au \
    hunspell-en-gb \
    hunspell-en-ca \
    hunspell-en-us \
    hunspell-en-za \
    hunspell-en-med \
    hunspell-es \
    hunspell-fr \
    hunspell-fr-classical \
    hunspell-ko \
    hunspell-pt-br \
    hunspell-pt-pt \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools

ENV PYTHONUNBUFFERED=TRUE \
    PYTHONDONTWRITEBYTECODE=TRUE \
    PATH="/opt/program:${PATH}"

# Create necessary directories
RUN mkdir -p /opt/program/data

# Set up the program in the image
COPY . /opt/program
WORKDIR /opt/program

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir hunspell

CMD ["python", "-v"]
