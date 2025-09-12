FROM python:3.12

WORKDIR /code

RUN apt-get update \
    && apt-get install -y ffmpeg

RUN apt-get install -y awscli


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

RUN mkdir -p /code/logs
