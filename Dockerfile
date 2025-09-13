FROM python:3.12

WORKDIR /code

RUN apt-get update 

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

RUN mkdir -p /code/logs
