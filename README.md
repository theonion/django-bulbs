# Django Bulbs [![Build Status](https://magnum.travis-ci.com/theonion/django-bulbs.png?token=cBZRscrrbcP3TYq87VqV&branch=indexable)](https://magnum.travis-ci.com/theonion/django-bulbs)

django-bulbs is a set of reusable apps developed at [The Onion](http://www.theonion.com) to assist with content, images and video.

You can read the documentation [here](http://jenkins.onion.com/view/All/job/bulbs-documentation/lastSuccessfulBuild/artifact/docs/_build/html/index.html).

## Running tests:

First, you'll need an ElasticSearch server running on http://localhost:9200, then just:

    > python runtests.py

## Building docs

    > cd docs
    > make html