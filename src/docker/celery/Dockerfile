FROM python:3.9-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip  setuptools wheel \
    && pip install celery \
    && rm -rf /root/.cache/pip
