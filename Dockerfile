FROM python:3.7-alpine

COPY catcher catcher
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