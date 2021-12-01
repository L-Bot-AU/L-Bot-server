# syntax=docker/dockerfile:1

# https://docs.docker.com/language/python/build-images/

FROM python:3.8.0-slim

WORKDIR /L-Bot-server-main

RUN pip install setuptools --upgrade
RUN pip3 install --upgrade pip
RUN pip3 install wheel

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# code is "baked" into docker image
# comment out if not required to be "baked" in
# COPY . .

ENTRYPOINT [ "python3" ]
