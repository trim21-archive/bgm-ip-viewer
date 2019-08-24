FROM python:3.6-slim
WORKDIR /
EXPOSE 8000

COPY requirements.txt /

RUN pip install -r requirements.txt

ADD server /server
ADD gunicorn.conf /
ENV PYTHONPATH=/
CMD gunicorn -c gunicorn.conf server.server:app
