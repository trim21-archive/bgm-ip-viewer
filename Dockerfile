FROM python:3.6-slim

COPY * /

RUN pip install -r requirements.txt && \
    pip install gunicorn gevent

EXPOSE 8000

CMD gunicorn -k gevent -c gunicorn.conf server.server:app