FROM docker.io/python:3.8-buster
MAINTAINER Galen Guyer <galen@galenguyer.com>

RUN mkdir /opt/rideboard

ADD requirements.txt /opt/rideboard

WORKDIR /opt/rideboard

RUN pip install -r requirements.txt

ADD . /opt/rideboard

ENTRYPOINT ["gunicorn", "rides:app"]
CMD ["--bind=0.0.0.0:8080", "--access-logfile=-"]
