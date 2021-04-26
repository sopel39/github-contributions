FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /ghcontrib

COPY . /ghcontrib/

RUN pip install github3api
RUN pip install mp4ansi
