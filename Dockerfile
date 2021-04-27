FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /ghcontrib

COPY . /ghcontrib/

RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb install
