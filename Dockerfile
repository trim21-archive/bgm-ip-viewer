FROM python:3.6-slim

COPY requirements-server.txt /

RUN pip install -r requirements-server.txt

ADD bgm /bgm
ADD server /server
ADD gunicorn.conf /

EXPOSE 8000
WORKDIR /
CMD gunicorn -c gunicorn.conf server.server:app