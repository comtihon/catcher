FROM python:3.9-alpine

RUN apk update \
  && apk add gcc g++ linux-headers


COPY catcher catcher
COPY Readme.rst Readme.rst
COPY docs docs
COPY requirements.txt requirements.txt
COPY setup.py setup.py

RUN python setup.py install

WORKDIR /opt/catcher/
RUN mkdir tests
VOLUME /opt/catcher/tests
VOLUME /opt/catcher/resources
VOLUME /opt/catcher/inventory
VOLUME /opt/catcher/steps
VOLUME /opt/catcher/reports

ENTRYPOINT ["catcher"]