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

# Install as much as possible before adding app directory, to take advantage of
# Docker's layer caching.

# Container includes all requirements (so it works in dev + prod)
# Add app as late as possibly (will always trigger cache miss and rebuild from here)
ADD . /webapp
RUN pip install -e .
RUN pip install -e ".[dev]"
