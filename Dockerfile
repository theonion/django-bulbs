FROM buildpack-deps:wily

ARG PYTHON_VERSION='python2.7'
ARG EKS_PACKAGE_NAME='elasticsearch-1.4.4'

# remove several traces of debian python
RUN apt-get purge -y python.*

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8


RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:fkrull/deadsnakes
RUN add-apt-repository -y ppa:webupd8team/java

RUN apt-get update -y

RUN apt-get install -y $PYTHON_VERSION
RUN apt-get install -y python-pip python-dev build-essential

RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
RUN apt-get update -y
RUN apt-get install -y oracle-java8-installer

ENV ES_PKG_NAME elasticsearch-1.4.4

# Install ElasticSearch.
RUN \
  cd / && \
  wget https://download.elasticsearch.org/elasticsearch/elasticsearch/$ES_PKG_NAME.tar.gz && \
  tar xvzf $ES_PKG_NAME.tar.gz && \
  rm -f $ES_PKG_NAME.tar.gz && \
  mv /$ES_PKG_NAME /elasticsearch

# update pip
RUN pip install --upgrade pip

# Define mountable directories.
RUN mkdir /data
RUN mkdir /plugins

# Mount elasticsearch.yml config
ADD elasticsearch.yml /elasticsearch/config/elasticsearch.yml

ADD ./setup.py /django-bulbs/
ADD ./bulbs/__init__.py /django-bulbs/bulbs/
RUN mkdir /pip-cache
VOLUME /pip-cache
RUN pip install --cache-dir /pip-cache -e "/django-bulbs[dev]"
ADD ./ /django-bulbs
CMD /elasticsearch/bin/elasticsearch -d \
  && until curl -s http://localhost:9200/ > /dev/null; do sleep 1; done \
  && curl -s -XDELETE 'http://localhost:9200/django-bulbs_0001/' \
  && find /django-bulbs | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf \
  && py.test -x /django-bulbs/tests/
