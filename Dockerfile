# syntax=docker/dockerfile:1

FROM python:3.11.2-slim-buster

WORKDIR /desse

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "emulator.py"]