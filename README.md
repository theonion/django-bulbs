# Django Bulbs [![Build Status](https://travis-ci.org/theonion/django-bulbs.svg?branch=promotions)](https://travis-ci.org/theonion/django-bulbs) [![Coverage Status](https://img.shields.io/coveralls/theonion/django-bulbs.svg)](https://coveralls.io/r/theonion/django-bulbs?branch=master)


django-bulbs is a set of apps used to power content at [The Onion](http://www.theonion.com).

This project very much under active development, and is currently not as reusable as it could be.

## Configuring for Development

First, enter any virtualenv, etc, that you plan on developing in.

    > pip install -e .
    > pip install "file://$(pwd)#egg=django-bulbs[dev]"

## Running tests:

First, you'll need an ElasticSearch server running on http://localhost:9200, then install `requirements-dev.txt`, and:

    > py.test tests/

## Building docs

    > cd docs
    > make html
