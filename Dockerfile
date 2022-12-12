FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /ghcontrib

COPY . /ghcontrib/

RUN pip install pybuilder==0.13.7
RUN pyb install_dependencies
RUN pyb install
