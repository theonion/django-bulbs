FROM python:3.5
MAINTAINER Onion Tech <webtech@theonion.com>

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get update \
    && apt-get install -y \
        git-core \
        libmemcached-dev \
        libpq-dev \
        postgresql-client-9.4 \
        vim \
    && rm -rf /var/lib/apt/lists/*

# Setup app directory
WORKDIR /webapp

ADD . /webapp
RUN pip install -e ".[dev]"
