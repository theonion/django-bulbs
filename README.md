# Django Bulbs [![Build Status](https://magnum.travis-ci.com/theonion/django-bulbs.svg?token=cBZRscrrbcP3TYq87VqV&branch=indexable)](https://magnum.travis-ci.com/theonion/django-bulbs)

django-bulbs is a set of apps used to power content at [The Onion](http://www.theonion.com).

This project very much under active development, and is currently not as reusable as it could be.

## Running tests:

First, you'll need an ElasticSearch server running on http://localhost:9200, then install `requirements-dev.txt`, and:

    > py.test tests/

## Building docs

    > cd docs
    > make html
