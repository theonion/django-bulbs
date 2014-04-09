# Django Bulbs [![Build Status](https://travis-ci.org/theonion/django-bulbs.svg?branch=promotions)](https://travis-ci.org/theonion/django-bulbs) [![Coverage Status](https://coveralls.io/repos/theonion/django-bulbs/badge.png)](https://coveralls.io/r/theonion/django-bulbs)

django-bulbs is a set of apps used to power content at [The Onion](http://www.theonion.com).

This project very much under active development, and is currently not as reusable as it could be.

## Running tests:

First, you'll need an ElasticSearch server running on http://localhost:9200, then install `requirements-dev.txt`, and:

    > py.test tests/

## Building docs

    > cd docs
    > make html
