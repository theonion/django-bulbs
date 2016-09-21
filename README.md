# DEPRECATED: This project is now part of the [Mono Repo](https://github.com/theonion/omni)

# Django Bulbs [![Build Status](https://travis-ci.org/theonion/django-bulbs.svg?branch=promotions)](https://travis-ci.org/theonion/django-bulbs) [![Coverage Status](https://img.shields.io/coveralls/theonion/django-bulbs.svg)](https://coveralls.io/r/theonion/django-bulbs?branch=master)


django-bulbs is a set of apps used to power content at [The Onion](http://www.theonion.com).

This project very much under active development, and is currently not as reusable as it could be.

## Setting up virtual env
```
virtualenv .
source bin/activate
```

First, enter any virtualenv, etc, that you plan on developing in.
```bash
pip install -e .
pip install "file://$(pwd)#egg=django-bulbs[dev]"
```

## Running Tests

1. Clone, setup, and start [onion-services](https://github.com/theonion/onion-services/blob/master/README.md).
2. Run `./scripts/init_db`
3. Run `./scripts/test`

A relative path to a folder or file can be given to `./scripts/test` to run
only a specific subset of tests.

## Building Docs
```bash
cd docs
make html
```
