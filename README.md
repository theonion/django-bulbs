# Django Bulbs [![Build Status](https://travis-ci.org/theonion/django-bulbs.svg?branch=promotions)](https://travis-ci.org/theonion/django-bulbs) [![Coverage Status](https://img.shields.io/coveralls/theonion/django-bulbs.svg)](https://coveralls.io/r/theonion/django-bulbs?branch=master)


django-bulbs is a set of apps used to power content at [The Onion](http://www.theonion.com).

This project very much under active development, and is currently not as reusable as it could be.

## Configuring for Development

First, enter any virtualenv, etc, that you plan on developing in.
```bash
$ pip install -e .
$ pip install "file://$(pwd)#egg=django-bulbs[dev]"
```

## Running Tests

1. Clone [django-elastimorphic](https://github.com/theonion/django-elastimorphic) into a sibiling directory
2. Install dev requirements
```bash
$ pip install -e ".[dev]"
```
3. Run tests
```bash
$ py.test tests/
```

## Building Docs
```bash
$ cd docs
$ make html
```
