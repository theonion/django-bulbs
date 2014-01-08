************
Requirements
************

Base requirements
=================
- `Python`_ 2.5+
- `Django`_ 1.4+
- :ref:`indexable-requirements`
- :ref:`video-requirements`
  
.. _indexable-requirements:

Indexable
=========
The ``indexable`` app (and the ``content`` app, depends on it) requires an `Elasticsearch`_ server, as well as the `Elasticutils`_ and `django-polymorphic`_ python packages.


.. _video-requirements:

Video
=====
The ``video`` app requires access keys for an `Amazon S3`_ bucket, as well as a `Zencoder`_ account. You'll need your keys for both of these services in order to use this app.

.. _django-polymorphic: https://django-polymorphic.readthedocs.org/
.. _Django: http://www.djangoproject.com/
.. _Python: http://www.python.org/
.. _Elasticutils: https://elasticutils.readthedocs.org/
.. _Elasticsearch: http://www.elasticsearch.org
.. _Amazon S3: http://aws.amazon.com/s3/
.. _Zencoder: http://zencoder.com/
